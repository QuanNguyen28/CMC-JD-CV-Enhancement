// src/pages/LoginPage.jsx
import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import LoginForm from '../components/LoginForm'

export default function LoginPage() {
  const { token } = useAuth()
  const navigate = useNavigate()
  useEffect(() => { if (token) navigate('/compose') }, [token])
  return <LoginForm />
}