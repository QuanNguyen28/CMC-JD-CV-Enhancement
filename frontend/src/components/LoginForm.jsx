// src/components/LoginForm.jsx
import React, { useState } from 'react'
import { motion } from 'framer-motion'
import NeumorphicCard from './NeumorphicCard'
import { useAuth } from '../AuthContext'

export default function LoginForm() {
  const { login } = useAuth()
  const [username, setUsername] = useState('alice')
  const [password, setPassword] = useState('alice')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      await login(username, password)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto mt-24">
      <NeumorphicCard className="p-8">
        <h1 className="text-2xl font-semibold mb-6">Welcome back</h1>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="label">Username</label>
            <input className="input" value={username} onChange={e=>setUsername(e.target.value)} placeholder="alice" />
          </div>
          <div>
            <label className="label">Password</label>
            <input className="input" type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="••••••" />
          </div>
          {error && <div className="text-red-600 text-sm">{error}</div>}
          <motion.button whileTap={{ scale: 0.98 }} disabled={loading} className="btn-primary w-full">
            {loading ? 'Signing in…' : 'Sign in'}
          </motion.button>
        </form>
      </NeumorphicCard>
    </div>
  )
}
