import React from 'react'

export default function PageHeader({ eyebrow, title, description, action }) {
  return (
    <div className="flex flex-col gap-4 border-b border-surface-line pb-5 md:flex-row md:items-end md:justify-between">
      <div>
        {eyebrow && <p className="section-label">{eyebrow}</p>}
        <h1 className="page-title mt-1">{title}</h1>
        {description && <p className="mt-2 max-w-2xl text-sm leading-relaxed text-brand-600">{description}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  )
}
