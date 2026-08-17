import React, { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { authFetch, fetchScanImageBlob } from '../utils/api'
import { formatConfidencePercent, getJobConfidence } from '../utils/jobResult'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'

function inferLabel(result) {
  if (result?.label) return result.label
  return getJobConfidence(result) >= 0.5 ? 'abnormal' : 'normal'
}

export default function DoctorReview() {
  const [search] = useSearchParams()
  const selectedJobId = search.get('job')
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)
  const [scanUrl, setScanUrl] = useState('')
  const [recommendation, setRecommendation] = useState('')
  const [clinicalNotes, setClinicalNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    authFetch('/jobs')
      .then((r) => r.json())
      .then((data) => setJobs((Array.isArray(data) ? data : []).filter((j) => j.status === 'completed')))
      .catch(() => setJobs([]))
  }, [])

  useEffect(() => {
    if (!selectedJobId) {
      setSelectedJob(null)
      return
    }
    authFetch(`/jobs/${selectedJobId}`)
      .then((r) => r.json())
      .then(setSelectedJob)
      .catch(() => setSelectedJob(null))
  }, [selectedJobId])

  useEffect(() => {
    if (!selectedJobId) {
      setScanUrl('')
      return undefined
    }
    let cancelled = false
    let objectUrl = ''
    fetchScanImageBlob(selectedJobId)
      .then((url) => {
        if (!cancelled) {
          objectUrl = url
          setScanUrl(url)
        } else URL.revokeObjectURL(url)
      })
      .catch(() => { if (!cancelled) setScanUrl('') })
    return () => {
      cancelled = true
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [selectedJobId])

  useEffect(() => {
    if (selectedJob?.doctor_recommendation) {
      setRecommendation(selectedJob.doctor_recommendation.recommendation || '')
      setClinicalNotes(selectedJob.doctor_recommendation.clinical_notes || '')
    } else {
      setRecommendation('')
      setClinicalNotes('')
    }
  }, [selectedJob])

  const submitReview = async () => {
    if (!selectedJobId || recommendation.trim().length < 10) return
    setSaving(true)
    setMessage('')
    try {
      const res = await authFetch(`/jobs/${selectedJobId}/doctor-review`, {
        method: 'POST',
        body: JSON.stringify({ recommendation, clinical_notes: clinicalNotes || null }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to save review')
      }
      const data = await res.json()
      setSelectedJob((prev) => ({ ...prev, doctor_recommendation: data.doctor_recommendation }))
      setMessage('Doctor recommendation saved for the patient.')
    } catch (err) {
      setMessage(err.message)
    } finally {
      setSaving(false)
    }
  }

  const r = selectedJob?.result || {}

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Doctor portal"
        title="MRI review & recommendations"
        description="Review patient MRI scans, read AI-generated results, and provide your clinical recommendation."
      />

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <aside className="card p-4">
          <h3 className="px-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Completed scans</h3>
          <ul className="mt-3 space-y-1">
            {jobs.map((job) => (
              <li key={job.id}>
                <Link
                  to={`/doctor-review?job=${job.id}`}
                  className={`block rounded-xl px-3 py-2.5 text-sm transition ${
                    selectedJobId === job.id ? 'bg-blue-50 text-primary' : 'text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <p className="truncate font-medium">{job.original_filename || job.filename}</p>
                  <p className="text-xs text-slate-500">{job.patient_name || job.patient_unique_id || 'Unknown patient'}</p>
                  {job.radiologist_notes && (
                    <span className="mt-1 inline-block text-xs text-blue-600">Radiologist noted</span>
                  )}
                  {job.doctor_recommendation && (
                    <span className="mt-1 inline-block text-xs text-emerald-600">Review submitted</span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </aside>

        <div className="space-y-6">
          {!selectedJob ? (
            <div className="card flex min-h-[320px] items-center justify-center p-8 text-sm text-slate-500">
              Select a completed scan to review.
            </div>
          ) : (
            <>
              <div className="card p-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase text-slate-500">Patient</p>
                    <p className="font-medium text-slate-900">{selectedJob.patient_name}</p>
                    <p className="font-mono text-sm text-primary">{selectedJob.patient_unique_id}</p>
                  </div>
                  <StatusBadge status={selectedJob.status} />
                </div>

                {scanUrl && (
                  <div className="mt-4 overflow-hidden rounded-xl border border-slate-200 bg-slate-900">
                    <img src={scanUrl} alt="MRI scan" className="mx-auto max-h-96 w-full object-contain" />
                  </div>
                )}
              </div>

              <div className="card p-6">
                <h3 className="text-lg font-semibold text-slate-900">AI analysis summary</h3>
                <div className="mt-3 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-xl bg-slate-50 p-4">
                    <p className="text-xs uppercase text-slate-500">Classification</p>
                    <p className="mt-1 text-lg font-semibold capitalize text-slate-900">{inferLabel(r)}</p>
                  </div>
                  <div className="rounded-xl bg-slate-50 p-4">
                    <p className="text-xs uppercase text-slate-500">AI confidence</p>
                    <p className="mt-1 text-lg font-semibold text-slate-900">{formatConfidencePercent(r)}%</p>
                  </div>
                </div>
                {r.rag_advisory?.summary && (
                  <p className="mt-4 rounded-xl border border-sky-100 bg-sky-50 p-4 text-sm text-sky-900">{r.rag_advisory.summary}</p>
                )}
              </div>

              {selectedJob.radiologist_notes && (
                <div className="card p-6">
                  <h3 className="text-lg font-semibold text-slate-900">Radiologist recommendation</h3>
                  <p className="mt-1 text-sm text-slate-500">By {selectedJob.radiologist_notes.radiologist_name}</p>
                  <p className="mt-3 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900">
                    {selectedJob.radiologist_notes.recommendation}
                  </p>
                  {selectedJob.radiologist_notes.clinical_notes && (
                    <p className="mt-3 rounded-xl bg-slate-50 p-4 text-sm text-slate-700">
                      <span className="font-medium">Notes for doctor:</span> {selectedJob.radiologist_notes.clinical_notes}
                    </p>
                  )}
                </div>
              )}

              <div className="card p-6">
                <h3 className="text-lg font-semibold text-slate-900">Doctor recommendation</h3>
                <p className="mt-1 text-sm text-slate-600">This will be visible to the patient in their portal.</p>

                <label className="mt-4 block text-sm">
                  <span className="font-medium text-slate-700">Recommendation for patient *</span>
                  <textarea
                    required
                    rows={5}
                    className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm"
                    placeholder="Describe your clinical assessment and next steps for the patient…"
                    value={recommendation}
                    onChange={(e) => setRecommendation(e.target.value)}
                  />
                </label>

                <label className="mt-3 block text-sm">
                  <span className="font-medium text-slate-700">Clinical notes (optional)</span>
                  <textarea
                    rows={3}
                    className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm"
                    value={clinicalNotes}
                    onChange={(e) => setClinicalNotes(e.target.value)}
                  />
                </label>

                {message && (
                  <p className={`mt-3 text-sm ${message.includes('saved') ? 'text-emerald-700' : 'text-red-700'}`}>{message}</p>
                )}

                <button type="button" className="btn-primary mt-4" onClick={submitReview} disabled={saving || recommendation.trim().length < 10}>
                  {saving ? 'Saving…' : 'Submit recommendation'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
