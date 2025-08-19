// src/components/RoleSelector.jsx
import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import api from '../api'
import NeumorphicCard from './NeumorphicCard'

export default function RoleSelector({ value, onChange }) {
  const [roles, setRoles] = useState([])

  useEffect(() => {
    api.get('/v1/roles/list').then(res => setRoles(res.data || [])).catch(()=>{})
  }, [])

  return (
    <NeumorphicCard>
      <div className="grid md:grid-cols-3 gap-4">
        <div>
          <label className="label">Job Title</label>
          <input className="input" value={value.title} onChange={e=>onChange({ ...value, title: e.target.value })} placeholder="Software Engineer" />
        </div>
        <div>
          <label className="label">Level</label>
          <select className="input" value={value.level} onChange={e=>onChange({ ...value, level: e.target.value })}>
            <option>Junior</option>
            <option>Mid</option>
            <option>Senior</option>
            <option>Lead</option>
          </select>
        </div>
        <div>
          <label className="label">Department</label>
          <input className="input" value={value.department} onChange={e=>onChange({ ...value, department: e.target.value })} placeholder="Engineering" />
        </div>
        <div className="md:col-span-3">
          <label className="label">(Optional) Seed chunks / context</label>
          <textarea className="input h-24" value={value.seed} onChange={e=>onChange({ ...value, seed: e.target.value })} placeholder="Paste short snippets to bias the generation…" />
        </div>
      </div>
    </NeumorphicCard>
  )
}
