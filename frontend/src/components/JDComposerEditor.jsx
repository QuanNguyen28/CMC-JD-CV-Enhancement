import { useState, useEffect } from 'react';
import { JDAPI } from '../api';

export default function JDComposerEditor({
  jdId,
  content,
  version,
  onGenerated,
  onContentChange,
  onSaved,
}) {
  // ---- local form state ----
  const [form, setForm] = useState({
    title: '',
    department: '',
    level: '',
    job_family: '',
    chunks: '', // optional: comma/line separated chunk ids or keywords (for RAG-assisted prompt)
  });

  const [busy, setBusy] = useState(false);
  const [saveBusy, setSaveBusy] = useState(false);
  const [err, setErr] = useState('');
  const [msg, setMsg] = useState('');

  // If parent ever provides new metadata in the future, sync here (optional hook-in point)
  useEffect(() => {
    setMsg('');
    setErr('');
  }, [jdId, version]);

  // ---- helpers ----
  const normalizePayload = () => {
    // trim all string fields
    const payload = {
      title: (form.title || '').trim(),
      department: (form.department || '').trim(),
      level: (form.level || '').trim(),
      job_family: (form.job_family || '').trim(),
    };

    // optional chunks -> list[str]
    const raw = (form.chunks || '').trim();
    if (raw.length > 0) {
      const list = raw
        .split(/[\n,]/g)
        .map(s => s.trim())
        .filter(Boolean);
      if (list.length) {
        payload.chunks = list;
      }
    }

    return payload;
  };

  const handleChange = (k) => (e) => {
    setForm((prev) => ({ ...prev, [k]: e.target.value }));
  };

  // ---- actions ----
  const generate = async () => {
    setBusy(true);
    setErr('');
    setMsg('');
    try {
      const payload = normalizePayload();

      if (!payload.title) {
        throw new Error('Vui lòng nhập Title trước khi Generate.');
      }

      const res = await JDAPI.generate(payload);
      // Expecting { jd_id, content_md, version }
      onGenerated?.(res);
      setMsg(`✅ Generated JD #${res?.jd_id ?? ''} v${res?.version ?? ''}`);
    } catch (e) {
      setErr(e?.response?.data?.detail || String(e));
    } finally {
      setBusy(false);
    }
  };

  const save = async () => {
    if (!jdId) {
      setErr('Không có JD ID để lưu phiên bản.');
      return;
    }
    setSaveBusy(true);
    setErr('');
    setMsg('');
    try {
      const res = await JDAPI.update({
        jd_id: jdId,
        content_md: content,
        change_summary: 'Edited in UI',
      });
      // Optional: fetch version history to get latest version number
      try {
        const versions = await JDAPI.versions(jdId);
        const latest = versions?.[0] || versions?.[versions.length - 1];
        const nextVersion = latest?.version_number ?? latest?.version ?? null;
        onSaved?.(nextVersion);
      } catch {
        // if versions endpoint not available, still consider save ok
        onSaved?.(null);
      }
      setMsg('💾 Đã lưu phiên bản mới.');
    } catch (e) {
      setErr(e?.response?.data?.detail || String(e));
    } finally {
      setSaveBusy(false);
    }
  };

  const exportJD = async (format = 'pdf') => {
    if (!jdId) {
      setErr('Không có JD ID để export.');
      return;
    }
    setErr('');
    setMsg('');
    try {
      const blob = await JDAPI.exportJD(jdId, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `JD_${jdId}.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setMsg(`⬇️ Đã tải JD #${jdId} (${format.toUpperCase()}).`);
    } catch (e) {
      setErr(e?.response?.data?.detail || String(e));
    }
  };

  return (
    <div className="rounded-2xl p-5 bg-white ring-1 ring-black/5 shadow-sm space-y-5">
      {/* Form */}
      <div className="grid md:grid-cols-2 gap-4">
        {[
          { key: 'title', label: 'Title', placeholder: 'e.g., Software Engineer' },
          { key: 'department', label: 'Department', placeholder: 'e.g., Engineering, Data' },
          { key: 'level', label: 'Level', placeholder: 'e.g., Junior / Mid / Senior' },
          { key: 'job_family', label: 'Job Family', placeholder: 'e.g., Backend, Data Platform' },
        ].map(({ key, label, placeholder }) => (
          <div key={key}>
            <label className="block text-sm mb-1 text-gray-700">{label}</label>
            <input
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              value={form[key]}
              onChange={handleChange(key)}
              placeholder={placeholder}
            />
          </div>
        ))}
        {/* Optional chunks (RAG assist) */}
        <div className="md:col-span-2">
          <label className="block text-sm mb-1 text-gray-700">
            Chunks (tuỳ chọn) – nhập theo dòng hoặc ngăn cách bởi dấu phẩy
          </label>
          <textarea
            className="w-full border rounded-lg px-3 py-2 text-sm h-20 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            value={form.chunks}
            onChange={handleChange('chunks')}
            placeholder="VD: chunk_123, chunk_456
Hoặc:
chunk_123
chunk_456"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap items-center gap-3">
        <button
          onClick={generate}
          disabled={busy}
          className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {busy ? 'Generating…' : 'Generate JD'}
        </button>

        <button
          onClick={save}
          disabled={!jdId || saveBusy}
          className="px-4 py-2 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-60"
        >
          {saveBusy ? 'Saving…' : 'Save Version'}
        </button>

        {/* Export controls (always visible; disabled until JD exists) */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Export:</span>
          <button
            onClick={() => exportJD('pdf')}
            disabled={!jdId}
            title={!jdId ? 'Generate & save JD first' : ''}
            className="px-3 py-1.5 rounded-md bg-gray-800 text-white text-xs hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            PDF
          </button>
          <button
            onClick={() => exportJD('docx')}
            disabled={!jdId}
            title={!jdId ? 'Generate & save JD first' : ''}
            className="px-3 py-1.5 rounded-md bg-gray-800 text-white text-xs hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            DOCX
          </button>
        </div>

        {jdId && (
          <div className="text-sm text-gray-500 ml-auto">
            JD #{jdId} {version ? `• v${version}` : ''}
          </div>
        )}
      </div>

      {/* Feedback */}
      {(err || msg) && (
        <div className="text-sm">
          {err && <div className="text-red-600">{err}</div>}
          {msg && <div className="text-emerald-600">{msg}</div>}
        </div>
      )}

      {/* Editor */}
      <div>
        <label className="block text-sm mb-1 text-gray-700">Content (Markdown)</label>
        <textarea
          className="w-full h-[440px] border rounded-lg p-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          value={content}
          onChange={(e) => onContentChange?.(e.target.value)}
          placeholder="Generated JD will appear here…"
        />
      </div>
    </div>
  );
}