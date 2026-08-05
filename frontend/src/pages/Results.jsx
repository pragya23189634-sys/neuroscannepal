import React, { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { ArrowDownTrayIcon, BuildingOffice2Icon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline'
import { API_BASE } from '../config'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'

function JobDetail({ job }) {
  const r = job.result || {}
  const confidence = Math.round((r.confidence || 0) * 100)
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
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="card p-6">
          <h3 className="flex items-center gap-2 text-lg font-semibold text-slate-900">
            <ChatBubbleLeftRightIcon className="h-5 w-5 text-primary" /> Medical advisory (RAG)
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
    fetch(`${API_BASE}/jobs`)
      .then((r) => r.json())
      .then((data) => setJobs((Array.isArray(data) ? data : []).filter((j) => j.status === 'completed').reverse()))
      .catch(() => setJobs([]))
  }, [])

  useEffect(() => {
    if (!selectedJobId) { setSelectedJob(null); return }
    fetch(`${API_BASE}/jobs/${selectedJobId}`)
      .then((r) => r.json())
      .then(setSelectedJob)
      .catch(() => setSelectedJob(null))
  }, [selectedJobId])

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Clinical output"
        title="Analysis results"
        description="Review classification outcomes, RAG advisory text, hospital recommendations, and exported reports."
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
                      <StatusBadge status={job.status} />
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </aside>

        <div>
          {selectedJob ? (
            <JobDetail job={selectedJob} />
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
