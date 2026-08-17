import { API_BASE } from '../config'

const TOKEN_KEY = 'neuroscan_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export async function authFetch(path, options = {}) {
  const token = getToken()
  const headers = { ...(options.headers || {}) }
  if (token) headers.Authorization = `Bearer ${token}`
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  if (res.status === 401) {
    clearToken()
    window.dispatchEvent(new Event('neuroscan:logout'))
  }
  return res
}

export async function fetchScanImageBlob(jobId) {
  const res = await authFetch(`/jobs/${jobId}/scan-image`)
  if (!res.ok) throw new Error('Failed to load scan image')
  return URL.createObjectURL(await res.blob())
}
