// src/components/ExportOptions.jsx
import React, { useState } from 'react'
import api from '../api'
import { downloadBlob } from '../utils/download'
import NeumorphicCard from './NeumorphicCard'

export default function ExportOptions({ jdId }) {
  const [downloading, setDownloading] = useState(false)

  const exportAs = async (format) => {
    setDownloading(true)
    try {
      const res = await api.get(`/v1/jd/export/${jdId}?format=${format}`, { responseType: 'arraybuffer' })
      const type = format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      downloadBlob(res.data, `jd_${jdId}.${format}`, type)
    } catch (e) {
      // swallow
    } finally { setDownloading(false) }
  }

  return (
    <NeumorphicCard>
      <div className="font-medium mb-2">Export</div>
      <div className="flex gap-2">
        <button disabled={!jdId || downloading} onClick={() => exportAs('pdf')} className="btn-ghost">PDF</button>
        <button disabled={!jdId || downloading} onClick={() => exportAs('docx')} className="btn-ghost">DOCX</button>
      </div>
    </NeumorphicCard>
  )
}