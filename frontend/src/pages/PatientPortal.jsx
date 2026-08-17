import React, { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { authFetch, fetchScanImageBlob } from '../utils/api'
import { formatConfidencePercent, getJobConfidence } from '../utils/jobResult'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'

function inferLabel(result) {
  if (result?.label) return result.label
  return getJobConfidence(result) >= 0.5 ? 'abnormal' : 'normal'
}

export default function PatientPortal() {
  const { user } = useAuth()
  const [search] = useSearchParams()
  const selectedJobId = search.get('job')
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)
  const [scanUrl, setScanUrl] = useState('')

  useEffect(() => {
    authFetch('/jobs')
      .then((r) => r.json())
      .then((data) => setJobs(Array.isArray(data) ? data : []))
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

  const r = selectedJob?.result || {}

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Patient portal"
        title="My MRI records"
        description="View your scanned MRI images, AI analysis reports, and your doctor's recommendations."
      />

      <div className="card border-primary/20 bg-gradient-to-r from-blue-50 to-slate-50 p-6">
        <p className="text-sm font-semibold uppercase tracking-wide text-primary">Your unique patient ID</p>
        <p className="mt-1 font-mono text-2xl font-bold text-slate-900">{user?.patient_unique_id || '—'}</p>
        <p className="mt-2 text-sm text-slate-600">Share this ID with your radiologist when scheduling an MRI scan.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <aside className="card p-4">
          <h3 className="px-2 text-sm font-semibold uppercase tracking-wide text-slate-500">My scans</h3>
          {jobs.length === 0 ? (
            <p className="mt-4 px-2 text-sm text-slate-500">No scans linked to your account yet.</p>
          ) : (
            <ul className="mt-3 space-y-1">
              {jobs.map((job) => (
                <li key={job.id}>
                  <Link
                    to={`/my-records?job=${job.id}`}
                    className={`block rounded-xl px-3 py-2.5 text-sm transition ${
                      selectedJobId === job.id ? 'bg-blue-50 text-primary' : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <p className="truncate font-medium">{job.original_filename || job.filename}</p>
                    <div className="mt-1 flex items-center justify-between gap-2">
                      <StatusBadge status={job.status} />
                      {job.radiologist_notes && (
                        <span className="text-xs text-blue-600">Radiologist noted</span>
                      )}
                      {job.doctor_recommendation && (
                        <span className="text-xs text-emerald-600">Doctor reviewed</span>
                      )}
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </aside>

        <div>
          {!selectedJob ? (
            <div className="card flex min-h-[320px] flex-col items-center justify-center p-8 text-center">
              <p className="text-slate-600">Select a scan to view your MRI and reports.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {scanUrl && (
                <div className="card overflow-hidden p-4">
                  <h3 className="mb-3 text-lg font-semibold text-slate-900">Your MRI scan</h3>
                  <div className="overflow-hidden rounded-xl border border-slate-200 bg-slate-900">
                    <img src={scanUrl} alt="Your MRI scan" className="mx-auto max-h-96 w-full object-contain" />
                  </div>
                </div>
              )}

              {selectedJob.status === 'completed' && (
                <>
                  <div className="card p-6">
                    <h3 className="text-lg font-semibold text-slate-900">AI-generated report</h3>
                    <div className="mt-4 grid gap-3 sm:grid-cols-2">
                      <div className="rounded-xl bg-emerald-50 p-4">
                        <p className="text-xs uppercase text-emerald-700">AI classification</p>
                        <p className="mt-1 text-xl font-semibold capitalize text-emerald-900">{inferLabel(r)}</p>
                      </div>
                      <div className="rounded-xl bg-blue-50 p-4">
                        <p className="text-xs uppercase text-blue-700">Confidence score</p>
                        <p className="mt-1 text-xl font-semibold text-blue-900">{formatConfidencePercent(r)}%</p>
                      </div>
                    </div>
                    {r.rag_advisory?.summary && (
                      <div className="mt-4 rounded-xl bg-slate-50 p-4">
                        <p className="text-xs font-semibold uppercase text-slate-500">AI recommendation</p>
                        <p className="mt-2 text-sm leading-relaxed text-slate-700">{r.rag_advisory.summary}</p>
                      </div>
                    )}
                    {r.chatbot && (
                      <div className="mt-4 space-y-2 rounded-xl border border-slate-200 p-4 text-sm text-slate-700">
                        <p><span className="font-medium">Guidance (English):</span> {r.chatbot.language_en}</p>
                        <p><span className="font-medium">Guidance (Nepali):</span> {r.chatbot.language_ne}</p>
                      </div>
                    )}
                  </div>

                  <div className="card p-6">
                    <h3 className="text-lg font-semibold text-slate-900">Radiologist recommendation</h3>
                    {selectedJob.radiologist_notes ? (
                      <div className="mt-4 space-y-3">
                        <p className="text-sm text-slate-500">
                          By {selectedJob.radiologist_notes.radiologist_name}
                        </p>
                        <p className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm leading-relaxed text-blue-900">
                          {selectedJob.radiologist_notes.recommendation}
                        </p>
                        {selectedJob.radiologist_notes.clinical_notes && (
                          <p className="text-sm text-slate-600">{selectedJob.radiologist_notes.clinical_notes}</p>
                        )}
                      </div>
                    ) : (
                      <p className="mt-4 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                        The radiologist has not yet added an investigation recommendation for this scan.
                      </p>
                    )}
                  </div>

                  <div className="card p-6">
                    <h3 className="text-lg font-semibold text-slate-900">Doctor's recommendation</h3>
                    {selectedJob.doctor_recommendation ? (
                      <div className="mt-4 space-y-3">
                        <p className="text-sm text-slate-500">
                          Reviewed by {selectedJob.doctor_recommendation.doctor_name}
                        </p>
                        <p className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm leading-relaxed text-emerald-900">
                          {selectedJob.doctor_recommendation.recommendation}
                        </p>
                        {selectedJob.doctor_recommendation.clinical_notes && (
                          <p className="text-sm text-slate-600">{selectedJob.doctor_recommendation.clinical_notes}</p>
                        )}
                      </div>
                    ) : (
                      <p className="mt-4 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                        Your doctor has not yet submitted a recommendation for this scan. Please check back later.
                      </p>
                    )}
                  </div>
                </>
              )}

              {selectedJob.status !== 'completed' && (
                <div className="card p-6 text-sm text-slate-600">
                  This scan is still being processed. Reports will appear here when analysis is complete.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
