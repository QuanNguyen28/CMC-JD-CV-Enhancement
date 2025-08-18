// src/components/ProtectedRoute.jsx
import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'

export default function ProtectedRoute({ children }) {
  const { token, loading } = useAuth()
  if (loading) return <div className="p-10 text-center">Loading…</div>
  if (!token) return <Navigate to="/login" replace />
  return children
}
