import React from 'react'

const styles = {
  completed: 'border-emerald-700/30 bg-emerald-50 text-emerald-900',
  running: 'border-sky-700/30 bg-sky-50 text-sky-900',
  pending: 'border-surface-line bg-surface text-brand-600',
  failed: 'border-red-700/30 bg-red-50 text-red-900',
  OK: 'border-emerald-700/30 bg-emerald-50 text-emerald-900',
  WARNING: 'border-amber-700/30 bg-amber-50 text-amber-900',
  FAILED: 'border-red-700/30 bg-red-50 text-red-900',
  RUNNING: 'border-sky-700/30 bg-sky-50 text-sky-900',
}

export default function StatusBadge({ status, className = '' }) {
  const key = (status || 'pending').toLowerCase()
  const tone = styles[status] || styles[key] || styles.pending
  return (
    <span className={`inline-flex items-center rounded-sm border px-2 py-0.5 font-mono text-[11px] font-medium uppercase tracking-wide ${tone} ${className}`}>
      {status || 'pending'}
    </span>
  )
}
