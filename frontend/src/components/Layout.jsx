// src/components/Layout.jsx
import React from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { LogOut, FileText, Edit3, History, MessageSquare } from 'lucide-react'

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const menu = [
    { to: '/compose', label: 'Compose JD', icon: <Edit3 size={18} /> },
  ]

  return (
    <div className="min-h-screen grid grid-cols-[260px_1fr] gap-6 p-6">
      <aside className="neo p-4 flex flex-col justify-between">
        <div>
          <Link to="/" className="block text-xl font-semibold mb-6">SmartHire<span className="text-accent">·</span>Composer</Link>
          <nav className="space-y-2">
            {menu.map(m => (
              <NavLink key={m.to} to={m.to} className={({ isActive }) => `flex items-center gap-2 px-3 py-2 rounded-xl ${isActive ? 'bg-white/60 shadow' : 'hover:bg-white/40'}`}>
                {m.icon}
                {m.label}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="mt-6 p-3 neo-in rounded-xl">
          <div className="text-sm text-gray-600">Logged in</div>
          <div className="font-medium">{user?.full_name || user?.username}</div>
          <button className="btn-ghost mt-3 w-full flex items-center justify-center gap-2" onClick={() => { logout(); navigate('/login') }}>
            <LogOut size={16} /> Logout
          </button>
        </div>
      </aside>

      <main>
        {children}
      </main>
    </div>
  )
}