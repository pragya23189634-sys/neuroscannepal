import React from 'react'
import { FOOTER } from '../content/siteCopy'

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-surface-line bg-surface-card">
      <div className="container-app flex flex-col gap-1 py-5 text-sm text-brand-600 sm:flex-row sm:items-center sm:justify-between">
        <div>{FOOTER.left}</div>
        <div className="text-xs">{FOOTER.right}</div>
      </div>
    </footer>
  )
}
