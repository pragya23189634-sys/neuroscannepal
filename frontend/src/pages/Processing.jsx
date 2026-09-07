import React, { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { CheckCircleIcon, ClockIcon } from '@heroicons/react/24/outline'
import { PIPELINE_STEPS } from '../config'
import { PAGES } from '../content/siteCopy'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'
import { formatConfidencePercent } from '../utils/jobResult'
import { authFetch } from '../utils/api'

export default function Processing() {
  const [search] = useSearchParams()
  const jobId = search.get('job')
  const [job, setJob] = useState(null)

  useEffect(() => {
    if (!jobId) return
    let mounted = true
    const fetchJob = async () => {
      try {
        const res = await authFetch(`/jobs/${jobId}`)
        if (!res.ok) throw new Error('not found')
        const data = await res.json()
        if (mounted) setJob(data)
      } catch {
        if (mounted) setJob(null)
      }
    }
    fetchJob()
    const timer = setInterval(fetchJob, 2000)
    return () => { mounted = false; clearInterval(timer) }
  }, [jobId])

  if (!jobId) {
    return (
      <div className="card p-8 text-center">
        <p className="text-slate-600">No job selected.</p>
        <Link to="/upload" className="btn-primary mt-4 inline-flex">Upload a scan</Link>
      </div>
    )
  }

  const latestByStep = {}
  for (const stage of job?.stages || []) latestByStep[stage.step] = stage

  const completedCount = PIPELINE_STEPS.filter(({ key }) => latestByStep[key]?.status === 'OK').length
  const progressPct = Math.round((completedCount / PIPELINE_STEPS.length) * 100)

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow={PAGES.processing.eyebrow}
        title={PAGES.processing.title}
        description={PAGES.processing.description}
        action={job?.status === 'completed' && (
          <Link to={`/results?job=${jobId}`} className="btn-primary">View results</Link>
        )}
      />

      {job ? (
        <>
          <div className="card p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-sm text-slate-500">Job reference</p>
                <p className="font-mono text-sm text-slate-800">{job.id}</p>
              </div>
              <StatusBadge status={job.status} />
            </div>
            <div className="mt-4">
              <div className="mb-1 flex justify-between text-xs text-slate-500"><span>Pipeline progress</span><span>{progressPct}%</span></div>
              <div className="h-2 overflow-hidden rounded-full bg-slate-200">
                <div className="h-full rounded-full bg-gradient-to-r from-primary to-accent transition-all" style={{ width: `${progressPct}%` }} />
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="mb-4 text-lg font-semibold text-slate-900">Stage breakdown</h3>
            <div className="space-y-3">
              {PIPELINE_STEPS.map(({ key, label }, index) => {
                const stage = latestByStep[key]
                const status = stage?.status || (job.status === 'completed' ? 'OK' : 'pending')
                const done = status === 'OK'
                const running = status === 'RUNNING'
                return (
                  <div key={key} className={`flex items-start gap-4 rounded-xl border px-4 py-3 ${
                    done ? 'border-emerald-200 bg-emerald-50/50' :
                    running ? 'border-sky-200 bg-sky-50/50' :
                    status === 'WARNING' ? 'border-amber-200 bg-amber-50/50' :
                    status === 'FAILED' ? 'border-red-200 bg-red-50/50' :
                    'border-slate-200 bg-white'
                  }`}>
                    <div className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                      done ? 'bg-emerald-100 text-emerald-700' : running ? 'bg-sky-100 text-sky-700' : 'bg-slate-100 text-slate-500'
                    }`}>
                      {done ? <CheckCircleIcon className="h-5 w-5" /> : running ? <ClockIcon className="h-5 w-5 animate-pulse" /> : index + 1}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p className="font-medium text-slate-900">{label}</p>
                        <StatusBadge status={status} />
                      </div>
                      {stage?.detail && <p className="mt-1 text-sm text-slate-600">{stage.detail}</p>}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {job.result && (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-slate-900">Preliminary output</h3>
              <p className="mt-2 text-sm capitalize text-slate-700">
                Classification: <strong>{job.result.label}</strong> ({formatConfidencePercent(job.result)}% confidence)
              </p>
              {job.result.rag_advisory?.summary && (
                <p className="mt-3 rounded-xl bg-slate-50 p-4 text-sm leading-relaxed text-slate-600">{job.result.rag_advisory.summary}</p>
              )}
            </div>
          )}
        </>
      ) : (
        <div className="card p-8 text-center text-sm text-slate-500">Loading job details…</div>
      )}
    </div>
  )
}
