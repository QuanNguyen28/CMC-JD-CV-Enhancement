import { useState } from 'react';
import { RetrieverAPI } from '../api';

export default function RetrievePage() {
  const [q, setQ] = useState('');
  const [topK, setTopK] = useState(5);
  const [items, setItems] = useState([]);
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);

  const run = async () => {
    setBusy(true); setErr('');
    try {
      const data = await RetrieverAPI.similar(q, Number(topK) || 5);
      setItems(data || []);
    } catch (e) {
      setErr(e?.response?.data?.detail || String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-white border rounded-xl p-4 flex gap-3">
        <input
          className="flex-1 border rounded-md px-3 py-2"
          placeholder="Search JD chunks…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <input
          className="w-24 border rounded-md px-3 py-2"
          type="number"
          value={topK}
          onChange={(e) => setTopK(e.target.value)}
        />
        <button
          onClick={run}
          className="px-4 py-2 rounded-md bg-blue-600 text-white"
          disabled={busy}
        >
          {busy ? 'Searching…' : 'Search'}
        </button>
      </div>

      {err && <div className="text-sm text-red-600">{err}</div>}

      <ul className="space-y-2">
        {items.map((it) => (
          <li key={it.chunk_id} className="bg-white border rounded-md p-3">
            <div className="text-sm">
              <b>JD:</b> {it.jd_id} • <b>Chunk:</b> {it.chunk_index} • <b>Score:</b> {it.score?.toFixed(4)}
            </div>
            {it.object_url && (
              <a href={it.object_url} target="_blank" rel="noreferrer" className="text-blue-600 text-sm">
                Open source
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}