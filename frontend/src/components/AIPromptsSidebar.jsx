// src/components/AIPromptsSidebar.jsx
import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Lightbulb } from 'lucide-react'
import api from '../api'
import NeumorphicCard from './NeumorphicCard'

export default function AIPromptsSidebar({ query, onInsert }) {
  const [q, setQ] = useState('data pipeline airflow spark')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)

  const runRetrieve = async () => {
    setLoading(true)
    try {
      const res = await api.post('/v1/retrieve/similar', { query: q, top_k: 5 })
      setItems(res.data)
    } catch (e) {
      setItems([])
    } finally { setLoading(false) }
  }

  return (
    <div className="space-y-4">
      <NeumorphicCard>
        <div className="flex items-center gap-2">
          <Search size={18} />
          <input className="input" value={q} onChange={e=>setQ(e.target.value)} placeholder="Search internal chunks…" />
        </div>
        <button onClick={runRetrieve} className="btn-ghost mt-3">Retrieve</button>
      </NeumorphicCard>

      <NeumorphicCard>
        <div className="flex items-center gap-2 mb-2"><Lightbulb size={18} />
          <div className="font-medium">Suggestions</div></div>
        {loading && <div className="text-sm text-gray-600">Loading…</div>}
        <div className="space-y-2">
          {items.map((it, idx) => (
            <motion.button key={idx} whileTap={{ scale: 0.98 }} onClick={() => onInsert(`\n\n> Reference: ${it.object_path || it.chunk_id}\n`)} className="w-full text-left px-3 py-2 rounded-xl hover:bg-white/50">
              #{idx+1} · score {it.score.toFixed(3)} · chunk {it.chunk_index}
            </motion.button>
          ))}
          {!items.length && <div className="text-sm text-gray-500">No suggestions yet. Try searching.</div>}
        </div>
      </NeumorphicCard>
    </div>
  )
}
