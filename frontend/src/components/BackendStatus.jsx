import React, { useEffect, useState } from 'react'
import { API_BASE } from '../config'

export default function BackendStatus() {
  const [online, setOnline] = useState(null)
  const [pipelineReady, setPipelineReady] = useState(false)

  useEffect(() => {
    let mounted = true
    const check = async () => {
      try {
        const res = await fetch(`${API_BASE}/health`)
        const data = await res.json()
        if (mounted) {
          setOnline(true)
          setPipelineReady(Boolean(data.pipeline_ready))
        }
      } catch {
        if (mounted) {
          setOnline(false)
          setPipelineReady(false)
        }
      }
    }
    check()
    const timer = setInterval(check, 15000)
    return () => {
      mounted = false
      clearInterval(timer)
    }
  }, [])

  if (online === null) return null

  return (
    <div className={`hidden items-center gap-2 rounded-sm border px-2 py-1 font-mono text-[10px] uppercase tracking-wide md:flex ${
      online
        ? pipelineReady
          ? 'border-emerald-400/30 bg-emerald-900/40 text-emerald-100'
          : 'border-amber-400/30 bg-amber-900/40 text-amber-100'
        : 'border-red-400/30 bg-red-900/40 text-red-100'
    }`}>
      <span className={`h-1.5 w-1.5 rounded-full ${online ? 'bg-emerald-400' : 'bg-red-400'}`} />
      {online ? (pipelineReady ? 'Pipeline ready' : 'Backend online') : 'Backend offline'}
    </div>
  )
}
