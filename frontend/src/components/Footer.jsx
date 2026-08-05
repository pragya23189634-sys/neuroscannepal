import React from 'react'

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-slate-200 bg-white">
      <div className="container-app flex flex-col gap-2 py-6 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
        <div>© {new Date().getFullYear()} NeuroScan Nepal · Final Year Project</div>
        <div className="text-xs">Research prototype — not for clinical diagnosis</div>
      </div>
    </footer>
  )
}
