import { useEffect, useState } from 'react';
import { JDAPI } from '../api';

export default function JDVersionHistory({ jdId, onSelect }) {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState('');

  useEffect(() => {
    let mounted = true;
    const run = async () => {
      if (!jdId) { setItems([]); return; }
      try {
        const data = await JDAPI.versions(jdId);
        // sort desc by version/version_number
        const normalized = (data || []).map(v => ({
          version: v.version_number ?? v.version,
          content_md: v.content_md,
          edited_by: v.edited_by ?? v.updated_by,
          edited_at: v.edited_at ?? v.updated_at,
        })).sort((a,b) => (b.version ?? 0) - (a.version ?? 0));
        if (mounted) setItems(normalized);
      } catch (e) {
        setErr(e?.response?.data?.detail || String(e));
      }
    };
    run();
    return () => { mounted = false; };
  }, [jdId]);

  if (!jdId) return (
    <div className="bg-white border rounded-xl p-4 text-sm text-gray-500">Version history will appear here after generating a JD.</div>
  );
  if (err) return <div className="text-red-600 text-sm">{err}</div>;

  return (
    <div className="bg-white border rounded-xl p-4">
      <div className="font-semibold mb-3">Version History</div>
      <ul className="space-y-2 max-h-[360px] overflow-auto">
        {items.map((v) => (
          <li
            key={v.version}
            className="p-3 border rounded-md hover:bg-gray-50 cursor-pointer"
            onClick={() => onSelect?.(v)}
          >
            <div className="text-sm font-medium">v{v.version}</div>
            <div className="text-xs text-gray-500">
              {v.edited_by} • {new Date(v.edited_at).toLocaleString()}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}