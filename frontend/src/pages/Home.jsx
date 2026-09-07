import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowUpTrayIcon,
  CheckCircleIcon,
  ClockIcon,
  QueueListIcon,
} from '@heroicons/react/24/outline'
import { PAGES } from '../content/siteCopy'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import StatusBadge from '../components/StatusBadge'
import { authFetch } from '../utils/api'

export default function Home() {
  const [jobs, setJobs] = useState([])
  const [backendOnline, setBackendOnline] = useState(true)

  useEffect(() => {
    authFetch('/jobs')
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
        eyebrow={PAGES.home.eyebrow}
        title={PAGES.home.title}
        description={PAGES.home.description}
        action={<Link to="/upload" className="btn-primary gap-2"><ArrowUpTrayIcon className="h-4 w-4" /> Upload scan</Link>}
      />

      {!backendOnline && (
        <div className="rounded-md border border-amber-700/30 bg-amber-50 px-4 py-3 text-sm text-amber-950">
          Backend is offline. Start it with <code className="rounded bg-white/70 px-1">py -3.11 -m uvicorn backend:app --port 8000</code>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Total scans" value={total} hint="All jobs" icon={QueueListIcon} />
        <StatCard label="Running" value={running} hint="In progress" icon={ClockIcon} />
        <StatCard label="Completed" value={completed} hint="Ready to review" icon={CheckCircleIcon} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Recent activity</h2>
            <Link to="/results" className="text-sm font-medium text-accent hover:underline">View all</Link>
          </div>
          {recent.length === 0 ? (
            <div className="rounded-md border border-dashed border-surface-line bg-surface px-6 py-10 text-center">
              <p className="text-sm text-slate-600">No scans yet.</p>
              <Link to="/upload" className="btn-primary mt-4 inline-flex">Upload a scan</Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recent.map((job) => (
                <Link
                  key={job.id}
                  to={job.status === 'completed' ? `/results?job=${job.id}` : `/processing?job=${job.id}`}
                  className="flex items-center justify-between border border-surface-line px-4 py-3 transition hover:border-brand-600/25 hover:bg-surface"
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
          <h2 className="text-lg font-semibold text-slate-900">Pipeline</h2>
          <p className="mt-2 text-sm text-slate-600">8 steps per upload:</p>
          <ol className="mt-4 space-y-2 text-sm text-slate-700">
            {['Upload', 'Preprocessing', 'CNN detection', 'Grad-CAM', 'RAG advisory', 'Chatbot', 'Hospitals', 'Report'].map((step, i) => (
              <li key={step} className="flex gap-3">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center border border-surface-line bg-surface font-mono text-xs font-semibold text-brand-700">{i + 1}</span>
                <span className="pt-0.5">{step}</span>
              </li>
            ))}
          </ol>
        </section>
      </div>
    </div>
  )
}
