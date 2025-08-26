// src/components/PreviewPanel.jsx
import React, { useMemo } from 'react'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import NeumorphicCard from './NeumorphicCard'
import ExportButtons from './ExportButtons'

export default function PreviewPanel({ markdown, jd, title }) {
  const html = useMemo(() => {
    const raw = marked.parse(markdown || '')
    return DOMPurify.sanitize(raw)
  }, [markdown])

  const headerTitle = title || jd?.title || 'Preview'

  return (
    <NeumorphicCard>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">{headerTitle}</h2>
        <ExportButtons
          jdId={jd?.jd_id}
          title={jd?.title || headerTitle}
          disabled={!jd?.jd_id}
        />
      </div>
      <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: html }} />
    </NeumorphicCard>
  )
}
