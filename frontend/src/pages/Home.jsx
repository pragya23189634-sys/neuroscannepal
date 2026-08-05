import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowUpTrayIcon,
  CheckCircleIcon,
  ClockIcon,
  QueueListIcon,
} from '@heroicons/react/24/outline'
import { API_BASE } from '../config'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import StatusBadge from '../components/StatusBadge'

export default function Home() {
  const [jobs, setJobs] = useState([])
  const [backendOnline, setBackendOnline] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/jobs`)
      .then((r) => r.json())
      .then((data) => {
        setJobs(Array.isArray(data) ? data : [])
        setBackendOnline(true)
      })
      .catch(() => setBackendOnline(false))
  }, [])

  const total = jobs.length
  const running = jobs.filter((j) => j.status === 'running').length
  const completed = jobs.filter((j) => j.status === 'completed').length
  const recent = jobs.slice().reverse().slice(0, 6)

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Clinical AI Dashboard"
        title="NeuroScan Nepal"
        description="Upload brain MRI scans, run the full AI pipeline, and review classification results with explainability and clinical support outputs."
        action={<Link to="/upload" className="btn-primary gap-2"><ArrowUpTrayIcon className="h-4 w-4" /> Upload MRI scan</Link>}
      />

      {!backendOnline && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Backend is offline. Start it with <code className="rounded bg-white/70 px-1">py -3.11 -m uvicorn backend:app --port 8000</code>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Total scans processed" value={total} hint="All uploaded jobs" icon={QueueListIcon} accent="primary" />
        <StatCard label="Currently running" value={running} hint="Active pipeline jobs" icon={ClockIcon} accent="amber" />
        <StatCard label="Completed" value={completed} hint="Ready for review" icon={CheckCircleIcon} accent="accent" />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Recent activity</h2>
            <Link to="/results" className="text-sm font-medium text-primary hover:underline">View all</Link>
          </div>
          {recent.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-6 py-10 text-center">
              <p className="text-sm text-slate-600">No scans processed yet.</p>
              <Link to="/upload" className="btn-primary mt-4 inline-flex">Upload your first scan</Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recent.map((job) => (
                <Link
                  key={job.id}
                  to={job.status === 'completed' ? `/results?job=${job.id}` : `/processing?job=${job.id}`}
                  className="flex items-center justify-between rounded-xl border border-slate-200 px-4 py-3 transition hover:border-primary/30 hover:bg-blue-50/30"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium text-slate-900">{job.original_filename || job.filename}</p>
                    <p className="text-xs text-slate-500">Job {job.id?.slice(0, 8)}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    {job.result?.label && (
                      <span className="hidden text-sm capitalize text-slate-600 sm:inline">{job.result.label}</span>
                    )}
                    <StatusBadge status={job.status} />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="card p-6">
          <h2 className="text-lg font-semibold text-slate-900">Pipeline overview</h2>
          <p className="mt-2 text-sm text-slate-600">Each upload runs through eight integrated stages:</p>
          <ol className="mt-4 space-y-2 text-sm text-slate-700">
            {['Upload', 'CLAHE preprocessing + QC', 'CNN classification', 'Grad-CAM heatmap', 'RAG advisory', 'Bilingual chatbot', 'Hospital finder', 'Report export'].map((step, i) => (
              <li key={step} className="flex gap-3">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-50 text-xs font-semibold text-primary">{i + 1}</span>
                <span className="pt-0.5">{step}</span>
              </li>
            ))}
          </ol>
        </section>
      </div>
    </div>
  )
}
