// frontend/src/components/AISidebar.jsx
import { useState } from 'react';
import { suggestJD } from '../api';
import { motion } from 'framer-motion';

export default function AISidebar({
  ctx,
  onInsert,            // (text: string) => void
  className = ''
}) {
  const [mode, setMode] = useState('outline'); // outline | bullets | rewrite
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState([]);

  const runSuggest = async () => {
    try {
      setLoading(true);
      const payload = {
        ...ctx,
        mode,
        max_tokens: 512
      };
      const { suggestions } = await suggestJD(payload);
      setItems(suggestions || []);
    } catch (e) {
      console.error(e);
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className={`w-full h-full p-4 bg-gradient-to-b from-slate-50 to-white border-l border-slate-200 ${className}`}>
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-800">AI Suggestions</h3>
        <select
          className="text-sm border rounded px-2 py-1 bg-white"
          value={mode}
          onChange={(e)=>setMode(e.target.value)}
        >
          <option value="outline">Outline</option>
          <option value="bullets">Bullets</option>
          <option value="rewrite">Rewrite</option>
        </select>
      </div>

      <button
        onClick={runSuggest}
        className="mt-3 w-full rounded-xl bg-slate-900 text-white py-2 text-sm hover:bg-slate-800"
        disabled={loading}
      >
        {loading ? 'Generating...' : 'Generate'}
      </button>

      <div className="mt-4 space-y-3 overflow-auto max-h-[70vh] pr-1">
        {items.length === 0 && !loading && (
          <p className="text-sm text-slate-500">
            Select a mode & click <b>Generate</b> to get contextual suggestions from current content.
          </p>
        )}
        {items.map((s, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className="group p-3 rounded-2xl border border-slate-200 bg-white shadow-sm hover:shadow-md transition"
          >
            <pre className="whitespace-pre-wrap text-sm text-slate-800">{s}</pre>
            <div className="text-right mt-2">
              <button
                onClick={()=>onInsert(s)}
                className="text-xs px-3 py-1 rounded-full bg-slate-100 hover:bg-slate-200"
              >
                Insert
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </aside>
  );
}