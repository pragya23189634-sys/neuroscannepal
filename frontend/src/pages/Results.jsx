import React, { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { ArrowDownTrayIcon, BuildingOffice2Icon, ChatBubbleLeftRightIcon, PencilSquareIcon } from '@heroicons/react/24/outline'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'
import { formatConfidencePercent } from '../utils/jobResult'
import { authFetch } from '../utils/api'

function RadiologistNotesForm({ job, onSaved }) {
  const existing = job.radiologist_notes
  const [recommendation, setRecommendation] = useState(existing?.recommendation || '')
  const [clinicalNotes, setClinicalNotes] = useState(existing?.clinical_notes || '')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    setRecommendation(existing?.recommendation || '')
    setClinicalNotes(existing?.clinical_notes || '')
  }, [job.id, existing])

  const submitNotes = async () => {
    if (recommendation.trim().length < 10) return
    setSaving(true)
    setMessage('')
    try {
      const res = await authFetch(`/jobs/${job.id}/radiologist-notes`, {
        method: 'POST',
        body: JSON.stringify({ recommendation, clinical_notes: clinicalNotes || null }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to save notes')
      }
      const data = await res.json()
      onSaved(data.radiologist_notes)
      setMessage('Radiologist recommendation saved. The doctor can now review it.')
    } catch (err) {
      setMessage(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="card p-6">
      <h3 className="flex items-center gap-2 text-lg font-semibold text-slate-900">
        <PencilSquareIcon className="h-5 w-5 text-primary" /> Radiologist recommendation
      </h3>
      <p className="mt-1 text-sm text-slate-600">
        Add your clinical recommendation for further investigation. This will be visible to the doctor and patient alongside the AI report.
      </p>

      <label className="mt-4 block text-sm">
        <span className="font-medium text-slate-700">Investigation recommendation *</span>
        <textarea
          required
          rows={4}
          className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm"
          placeholder="e.g. Recommend contrast-enhanced MRI and neurology referral for further evaluation…"
          value={recommendation}
          onChange={(e) => setRecommendation(e.target.value)}
        />
      </label>

      <label className="mt-3 block text-sm">
        <span className="font-medium text-slate-700">Notes for doctor (optional)</span>
        <textarea
          rows={3}
          className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm"
          placeholder="Internal notes or context for the reviewing doctor…"
          value={clinicalNotes}
          onChange={(e) => setClinicalNotes(e.target.value)}
        />
      </label>

      {message && (
        <p className={`mt-3 text-sm ${message.includes('saved') ? 'text-emerald-700' : 'text-red-700'}`}>{message}</p>
      )}

      <button type="button" className="btn-primary mt-4" onClick={submitNotes} disabled={saving || recommendation.trim().length < 10}>
        {saving ? 'Saving…' : existing ? 'Update recommendation' : 'Save recommendation'}
      </button>
    </section>
  )
}

function JobDetail({ job, onJobUpdate }) {
  const r = job.result || {}
  const confidence = formatConfidencePercent(r)
  const isAbnormal = r.label === 'abnormal'

  return (
    <div className="space-y-6">
      <div className="card overflow-hidden">
        <div className={`px-6 py-5 ${isAbnormal ? 'bg-gradient-to-r from-amber-500 to-orange-500' : 'bg-gradient-to-r from-emerald-500 to-teal-500'} text-white`}>
          <p className="text-sm font-medium uppercase tracking-wide opacity-90">Classification result</p>
          <p className="mt-1 text-3xl font-semibold capitalize">{r.label || 'Unknown'}</p>
          <p className="mt-1 text-sm opacity-90">{confidence}% model confidence · processed in {r.elapsed_seconds || '—'}s</p>
        </div>
        <div className="grid gap-4 p-6 md:grid-cols-2">
          <div>
            <p className="text-xs font-semibold uppercase text-slate-500">Scan file</p>
            <p className="mt-1 text-sm text-slate-800">{job.original_filename || job.filename}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase text-slate-500">Patient</p>
            <p className="mt-1 text-sm text-slate-800">{job.patient_name || '—'}</p>
            <p className="font-mono text-xs text-primary">{job.patient_unique_id || '—'}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase text-slate-500">Probabilities</p>
            <p className="mt-1 text-sm text-slate-800">
              Normal {Math.round((r.probabilities?.normal || 0) * 100)}% · Abnormal {Math.round((r.probabilities?.abnormal || 0) * 100)}%
            </p>
          </div>
        </div>
        {r.low_quality && (
          <div className="mx-6 mb-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            This image was flagged as low-contrast during preprocessing. Results may be less reliable.
          </div>
        )}
        {r.review_required && (
          <div className="mx-6 mb-6 rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-900">
            Confidence is below the validated 70% review threshold. Treat this result as uncertain and require clinician review.
          </div>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="card p-6">
          <h3 className="flex items-center gap-2 text-lg font-semibold text-slate-900">
            <ChatBubbleLeftRightIcon className="h-5 w-5 text-primary" /> AI advisory (automated)
          </h3>
          <p className="mt-3 text-sm leading-relaxed text-slate-600">{r.rag_advisory?.summary}</p>
          <p className="mt-3 text-xs text-slate-500">{r.rag_advisory?.disclaimer}</p>
          {r.chatbot && (
            <div className="mt-4 space-y-2 rounded-xl bg-slate-50 p-4 text-sm">
              <p><span className="font-medium">EN:</span> {r.chatbot.language_en}</p>
              <p><span className="font-medium">NE:</span> {r.chatbot.language_ne}</p>
            </div>
          )}
        </section>

        <section className="card p-6">
          <h3 className="flex items-center gap-2 text-lg font-semibold text-slate-900">
            <BuildingOffice2Icon className="h-5 w-5 text-accent" /> Recommended hospitals
          </h3>
          <ul className="mt-4 space-y-3">
            {(r.hospitals || []).map((h) => (
              <li key={h.name} className="rounded-xl border border-slate-200 px-4 py-3 text-sm">
                <p className="font-medium text-slate-900">{h.name}</p>
                <p className="text-slate-500">{h.city} · {h.department}</p>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <RadiologistNotesForm
        job={job}
        onSaved={(notes) => onJobUpdate({ ...job, radiologist_notes: notes })}
      />

      {job.doctor_recommendation && (
        <section className="card p-6">
          <h3 className="text-lg font-semibold text-slate-900">Doctor recommendation (submitted)</h3>
          <p className="mt-2 text-sm text-slate-500">By {job.doctor_recommendation.doctor_name}</p>
          <p className="mt-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900">
            {job.doctor_recommendation.recommendation}
          </p>
        </section>
      )}

      {r.reports && (
        <section className="card p-6">
          <h3 className="text-lg font-semibold text-slate-900">Download reports</h3>
          <p className="mt-1 text-sm text-slate-600">Reports are generated on the server under results/jobs/</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {Object.entries(r.reports).map(([kind, path]) => (
              <span key={kind} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-700">
                <ArrowDownTrayIcon className="h-4 w-4" /> {kind.toUpperCase()}: {path.split('\\').pop()}
              </span>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

export default function Results() {
  const [search] = useSearchParams()
  const selectedJobId = search.get('job')
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)

  useEffect(() => {
    authFetch('/jobs')
      .then((r) => r.json())
      .then((data) => setJobs((Array.isArray(data) ? data : []).filter((j) => j.status === 'completed').reverse()))
      .catch(() => setJobs([]))
  }, [])

  useEffect(() => {
    if (!selectedJobId) { setSelectedJob(null); return }
    authFetch(`/jobs/${selectedJobId}`)
      .then((r) => r.json())
      .then(setSelectedJob)
      .catch(() => setSelectedJob(null))
  }, [selectedJobId])

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Clinical output"
        title="Analysis results"
        description="Review AI outputs, add your investigation recommendation, and track doctor follow-up."
      />

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <aside className="card p-4">
          <h3 className="px-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Completed scans</h3>
          {jobs.length === 0 ? (
            <p className="mt-4 px-2 text-sm text-slate-500">No completed jobs yet.</p>
          ) : (
            <ul className="mt-3 space-y-1">
              {jobs.map((job) => (
                <li key={job.id}>
                  <Link
                    to={`/results?job=${job.id}`}
                    className={`block rounded-xl px-3 py-2.5 text-sm transition ${
                      selectedJobId === job.id ? 'bg-blue-50 text-primary' : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <p className="truncate font-medium">{job.original_filename || job.filename}</p>
                    <div className="mt-1 flex items-center justify-between gap-2">
                      <span className="capitalize text-xs text-slate-500">{job.result?.label}</span>
                      <div className="flex gap-1">
                        {job.radiologist_notes && <span className="text-xs text-blue-600">Noted</span>}
                        {job.doctor_recommendation && <span className="text-xs text-emerald-600">Reviewed</span>}
                      </div>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </aside>

        <div>
          {selectedJob ? (
            <JobDetail
              job={selectedJob}
              onJobUpdate={(updated) => {
                setSelectedJob(updated)
                setJobs((prev) => prev.map((j) => (j.id === updated.id ? updated : j)))
              }}
            />
          ) : (
            <div className="card flex min-h-[320px] flex-col items-center justify-center p-8 text-center">
              <p className="text-slate-600">Select a completed scan from the list to view full results.</p>
              <Link to="/upload" className="btn-primary mt-4">Upload new scan</Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
