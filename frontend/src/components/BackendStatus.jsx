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
    <div className={`hidden items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ring-1 ring-inset md:flex ${
      online
        ? pipelineReady
          ? 'bg-emerald-50 text-emerald-700 ring-emerald-200'
          : 'bg-amber-50 text-amber-700 ring-amber-200'
        : 'bg-red-50 text-red-700 ring-red-200'
    }`}>
      <span className={`h-2 w-2 rounded-full ${online ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
      {online ? (pipelineReady ? 'Pipeline ready' : 'Backend online') : 'Backend offline'}
    </div>
  )
}
