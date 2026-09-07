import React from 'react'

export default function StatCard({ label, value, hint, icon: Icon }) {
  return (
    <div className="card-accent p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="section-label">{label}</p>
          <p className="mt-2 font-display text-3xl font-semibold text-brand-900">{value}</p>
          {hint && <p className="mt-1 text-xs text-brand-600">{hint}</p>}
        </div>
        {Icon && (
          <div className="border border-surface-line bg-surface p-2">
            <Icon className="h-5 w-5 text-brand-700" strokeWidth={1.75} />
          </div>
        )}
      </div>
    </div>
  )
}
