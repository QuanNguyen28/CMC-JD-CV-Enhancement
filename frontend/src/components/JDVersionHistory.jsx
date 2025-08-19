// src/components/JDVersionHistory.jsx
import React, { useEffect, useState } from 'react'
import api from '../api'
import NeumorphicCard from './NeumorphicCard'

export default function JDVersionHistory({ jdId }) {
  const [items, setItems] = useState([])

  useEffect(() => {
    if (!jdId) return
    api.get(`/v1/jd/version-history/${jdId}`).then(res => setItems(res.data || [])).catch(()=>{})
  }, [jdId])

  return (
    <NeumorphicCard>
      <div className="font-medium mb-2">Version History</div>
      <div className="space-y-2 max-h-80 overflow-auto pr-2">
        {items.map(v => (
          <div key={v.version || v.version_number} className="neo-in p-3 rounded-xl">
            <div className="text-sm">v{v.version || v.version_number}</div>
            <div className="text-xs text-gray-500">{new Date(v.updated_at || v.edited_at).toLocaleString()} · {v.updated_by || v.edited_by}</div>
          </div>
        ))}
        {!items.length && <div className="text-sm text-gray-500">No versions yet.</div>}
      </div>
    </NeumorphicCard>
  )
}