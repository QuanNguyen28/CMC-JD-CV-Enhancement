// src/pages/ComposePage.jsx
import React, { useState } from 'react'
import { motion } from 'framer-motion'
import Layout from '../components/Layout'
import RoleSelector from '../components/RoleSelector'
import JDComposerEditor from '../components/JDComposerEditor'
import PreviewPanel from '../components/PreviewPanel'
import AIPromptsSidebar from '../components/AIPromptsSidebar'
import JDVersionHistory from '../components/JDVersionHistory'
import InterviewQuestionGenerator from '../components/InterviewQuestionGenerator'
import api from '../api'

export default function ComposePage() {
  const [meta, setMeta] = useState({ title: '', level: 'Mid', department: '', seed: '' })
  const [markdown, setMarkdown] = useState('')
  const [jdId, setJdId] = useState(null)
  const [saving, setSaving] = useState(false)

  const generateJD = async () => {
    setSaving(true)
    try {
      const payload = { title: meta.title, level: meta.level, department: meta.department, chunks: [] }
      const res = await api.post('/v1/jd/generate', payload)
      setJdId(res.data.jd_id)
      setMarkdown(res.data.content_md)
    } catch (e) { /* ignore */ }
    finally { setSaving(false) }
  }

  const updateJD = async () => {
    if (!jdId) return
    setSaving(true)
    try {
      await api.put('/v1/jd/update', { jd_id: jdId, content_md: markdown, change_summary: 'Updated via UI' })
    } catch (e) { /* ignore */ }
    finally { setSaving(false) }
  }

  return (
    <Layout>
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 md:col-span-8 space-y-4">
          <RoleSelector value={meta} onChange={setMeta} />
          <div className="flex gap-3">
            <button className="btn-primary" onClick={generateJD}>Generate JD</button>
            <button className="btn-ghost" onClick={updateJD} disabled={!jdId || saving}>{saving ? 'Saving…' : 'Save Version'}</button>
          </div>
          <JDComposerEditor value={markdown} onChange={setMarkdown} />
          <JDVersionHistory jdId={jdId} />
        </div>
        <div className="col-span-12 md:col-span-4 space-y-4">
          <AIPromptsSidebar onInsert={(txt)=>setMarkdown(m=>m + txt)} />
          <PreviewPanel markdown={markdown} />
          <InterviewQuestionGenerator seed={meta.seed} jdId={jdId} meta={meta} />
        </div>
      </div>
    </Layout>
  )
}