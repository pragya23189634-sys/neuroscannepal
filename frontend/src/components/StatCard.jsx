import React from 'react'

export default function StatCard({ label, value, hint, icon: Icon, accent = 'primary' }) {
  const accents = {
    primary: 'from-blue-500/10 to-blue-600/5 border-blue-100',
    accent: 'from-teal-500/10 to-teal-600/5 border-teal-100',
    amber: 'from-amber-500/10 to-amber-600/5 border-amber-100',
  }
  return (
    <div className={`card p-5 bg-gradient-to-br ${accents[accent] || accents.primary}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">{value}</p>
          {hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
        </div>
        {Icon && (
          <div className="rounded-xl bg-white/80 p-2 shadow-sm ring-1 ring-slate-200/60">
            <Icon className="h-5 w-5 text-primary" />
          </div>
        )}
      </div>
    </div>
  )
}
