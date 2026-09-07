import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CloudArrowUpIcon, DocumentIcon } from '@heroicons/react/24/outline'
import { API_BASE } from '../config'
import { PAGES } from '../content/siteCopy'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'
import { authFetch, getToken } from '../utils/api'
import { formatConfidencePercent } from '../utils/jobResult'

export default function Upload() {
  const [file, setFile] = useState(null)
  const [patients, setPatients] = useState([])
  const [patientId, setPatientId] = useState('')
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [previewUrl, setPreviewUrl] = useState('')
  const [statusMessage, setStatusMessage] = useState('')
  const [jobId, setJobId] = useState('')
  const [jobStatus, setJobStatus] = useState('')
  const [jobResult, setJobResult] = useState(null)
  const inputRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    authFetch('/auth/patients')
      .then((r) => r.json())
      .then((data) => setPatients(Array.isArray(data) ? data : []))
      .catch(() => setPatients([]))
  }, [])

  useEffect(() => {
    if (!jobId) return
    let cancelled = false
    const pollJob = async () => {
      try {
        const res = await authFetch(`/jobs/${jobId}`)
        if (!res.ok) return
        const data = await res.json()
        if (!cancelled) {
          setJobStatus(data.status || 'pending')
          setJobResult(data.result || null)
          if (data.status === 'completed') setStatusMessage('Pipeline complete — results are ready to review.')
          else if (data.status === 'running') setStatusMessage('Running full AI pipeline (8 stages)...')
          else if (data.status === 'failed') setStatusMessage(data.error || 'Processing failed.')
        }
      } catch {
        if (!cancelled) setStatusMessage('Waiting for backend response...')
      }
    }
    pollJob()
    const timer = setInterval(pollJob, 2000)
    return () => { cancelled = true; clearInterval(timer) }
  }, [jobId])

  useEffect(() => () => { if (previewUrl) URL.revokeObjectURL(previewUrl) }, [previewUrl])

  const handleSelectedFile = (selectedFile) => {
    if (!selectedFile) return
    setFile(selectedFile)
    setStatusMessage('')
    setJobId('')
    setJobStatus('')
    setJobResult(null)
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(selectedFile.type.startsWith('image/') ? URL.createObjectURL(selectedFile) : '')
  }

  const doUpload = () => {
    if (!file || !patientId) return
    setUploading(true)
    setProgress(0)
    setStatusMessage('Uploading scan to server...')
    const form = new FormData()
    form.append('file', file)
    form.append('patient_id', patientId)
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_BASE}/upload`)
    xhr.timeout = 60000
    const token = getToken()
    if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) setProgress(Math.round((e.loaded / e.total) * 100))
    }
    xhr.onload = () => {
      setUploading(false)
      if (xhr.status === 201) {
        try {
          const data = JSON.parse(xhr.responseText)
          setJobId(data.job_id)
          setStatusMessage(`Upload complete for patient ${data.patient_unique_id}. Pipeline started.`)
        } catch {
          setStatusMessage('Upload succeeded but response could not be parsed.')
        }
      } else {
        setStatusMessage(`Upload failed (${xhr.status}). Check patient selection and login.`)
      }
    }
    xhr.ontimeout = () => { setUploading(false); setStatusMessage('Upload timed out.') }
    xhr.onerror = () => { setUploading(false); setStatusMessage('Cannot reach backend at port 8000.') }
    xhr.send(form)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow={PAGES.upload.eyebrow}
        title={PAGES.upload.title}
        description={PAGES.upload.description}
      />

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="card p-6">
          <label className="block text-sm">
            <span className="font-medium text-slate-700">Assign to patient *</span>
            <select
              className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
            >
              <option value="">Select patient…</option>
              {patients.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.full_name} — {p.patient_unique_id}
                </option>
              ))}
            </select>
          </label>

          <input ref={inputRef} type="file" className="hidden" accept="image/*,.nii,.nii.gz" onChange={(e) => handleSelectedFile(e.target.files?.[0])} />
          <button type="button" className="input-file-zone mt-4 w-full" onClick={() => inputRef.current?.click()}>
            <CloudArrowUpIcon className="h-10 w-10 text-primary/70" />
            <p className="mt-3 text-sm font-medium text-slate-800">{file ? file.name : 'Click to select an MRI image'}</p>
            <p className="mt-1 text-xs text-slate-500">JPEG, PNG, BMP, NIfTI (.nii, .nii.gz)</p>
          </button>

          {previewUrl && (
            <div className="mt-4 overflow-hidden rounded-xl border border-slate-200 bg-slate-900">
              <img src={previewUrl} alt="MRI preview" className="mx-auto max-h-72 w-full object-contain" />
            </div>
          )}
        </section>

        <section className="card p-6">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Upload status</h3>
          <div className="mt-3 rounded-xl border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-900">
            {statusMessage || 'Select a patient and scan to begin.'}
          </div>

          {uploading && (
            <div className="mt-4">
              <div className="mb-1 flex justify-between text-xs text-slate-500"><span>Uploading</span><span>{progress}%</span></div>
              <div className="h-2 overflow-hidden rounded-full bg-slate-200">
                <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${progress}%` }} />
              </div>
            </div>
          )}

          {jobId && (
            <div className="mt-4 space-y-2 text-sm">
              <div className="flex items-center justify-between"><span className="text-slate-500">Job ID</span><code className="text-xs">{jobId.slice(0, 8)}…</code></div>
              <div className="flex items-center justify-between"><span className="text-slate-500">Status</span><StatusBadge status={jobStatus} /></div>
            </div>
          )}

          {jobResult && (
            <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm">
              <p className="font-semibold capitalize text-emerald-900">{jobResult.label || 'Analyzed'} — {formatConfidencePercent(jobResult)}% confidence</p>
              {jobResult.low_quality && <p className="mt-1 text-amber-700">Low-contrast image flagged during QC</p>}
              {jobResult.review_required && <p className="mt-1 font-medium text-amber-700">Uncertain result — clinician review is required.</p>}
            </div>
          )}

          <div className="mt-6 flex flex-wrap gap-2">
            <button type="button" className="btn-primary" onClick={doUpload} disabled={!file || !patientId || uploading}>
              {uploading ? 'Uploading…' : 'Start analysis'}
            </button>
            {jobId && (
              <>
                <button type="button" className="btn-secondary" onClick={() => navigate(`/processing?job=${jobId}`)}>View pipeline</button>
                {jobStatus === 'completed' && (
                  <button type="button" className="btn-secondary" onClick={() => navigate(`/results?job=${jobId}`)}>Open results</button>
                )}
              </>
            )}
          </div>

          <div className="mt-6 flex items-start gap-2 rounded-xl bg-slate-50 p-3 text-xs text-slate-600">
            <DocumentIcon className="mt-0.5 h-4 w-4 shrink-0" />
            <p>Patients must register first to receive a unique ID (e.g. NSN-PAT-000001) before you can upload their scan.</p>
          </div>
        </section>
      </div>
    </div>
  )
}
