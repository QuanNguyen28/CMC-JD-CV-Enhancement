// src/components/JDComposerEditor.jsx
import React from 'react'
import NeumorphicCard from './NeumorphicCard'

export default function JDComposerEditor({ value, onChange }) {
  return (
    <NeumorphicCard>
      <label className="label">Markdown Editor</label>
      <textarea className="input h-[420px] font-mono" value={value} onChange={e=>onChange(e.target.value)} placeholder={"## Job Summary\nDescribe the role…"} />
    </NeumorphicCard>
  )
}