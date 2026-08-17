import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { authFetch, clearToken, getToken, setToken } from '../utils/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    const token = getToken()
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const res = await authFetch('/auth/me')
      if (!res.ok) throw new Error('session expired')
      setUser(await res.json())
    } catch {
      clearToken()
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshUser()
    const onLogout = () => setUser(null)
    window.addEventListener('neuroscan:logout', onLogout)
    return () => window.removeEventListener('neuroscan:logout', onLogout)
  }, [refreshUser])

  const login = useCallback(async (email, password) => {
    const res = await fetch(`${import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Login failed')
    setToken(data.access_token)
    setUser(data.user)
    return data.user
  }, [])

  const register = useCallback(async (payload) => {
    const res = await fetch(`${import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Registration failed')
    setToken(data.access_token)
    setUser(data.user)
    return data.user
  }, [])

  const logout = useCallback(() => {
    clearToken()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, register, logout, refreshUser, isAuthenticated: !!user }),
    [user, loading, login, register, logout, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
