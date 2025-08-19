// src/components/PreviewPanel.jsx
import React, { useMemo } from 'react'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import NeumorphicCard from './NeumorphicCard'

export default function PreviewPanel({ markdown }) {
  const html = useMemo(() => {
    const raw = marked.parse(markdown || '')
    return DOMPurify.sanitize(raw)
  }, [markdown])

  return (
    <NeumorphicCard>
      <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: html }} />
    </NeumorphicCard>
  )
}