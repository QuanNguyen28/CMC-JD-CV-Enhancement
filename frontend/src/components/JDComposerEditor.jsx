import { useState } from 'react';
import { JDAPI } from '../api';

export default function JDComposerEditor({
  jdId,
  content,
  version,
  onGenerated,
  onContentChange,
  onSaved,
}) {
  const [form, setForm] = useState({
    title: '',
    department: '',
    level: '',
    job_family: '',
  });
  const [busy, setBusy] = useState(false);
  const [saveBusy, setSaveBusy] = useState(false);
  const [err, setErr] = useState('');

  const generate = async () => {
    setBusy(true);
    setErr('');
    try {
      const res = await JDAPI.generate(form);
      onGenerated?.(res);
    } catch (e) {
      setErr(e?.response?.data?.detail || String(e));
    } finally {
      setBusy(false);
    }
  };

  const save = async () => {
    if (!jdId) return;
    setSaveBusy(true);
    setErr('');
    try {
      const res = await JDAPI.update({
        jd_id: jdId,
        content_md: content,
        change_summary: 'Edited in UI',
      });
      // backend trả {status:'updated'} hoặc version mới; ta fetch lại versions hoặc trả về số version nếu có.
      // ở đây xử lý mềm:
      const versions = await JDAPI.versions(jdId);
      const last = versions?.[0] || versions?.[versions.length - 1];
      const nextVersion = last?.version_number ?? last?.version ?? null;
      onSaved?.(nextVersion);
    } catch (e) {
      setErr(e?.response?.data?.detail || String(e));
    } finally {
      setSaveBusy(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border p-4 space-y-4">
      <div className="grid md:grid-cols-2 gap-3">
        {['title','department','level','job_family'].map((k) => (
          <div key={k}>
            <label className="block text-sm mb-1 capitalize">{k.replace('_',' ')}</label>
            <input
              className="w-full border rounded-md px-3 py-2"
              value={form[k]}
              onChange={(e) => setForm({ ...form, [k]: e.target.value })}
              placeholder={k === 'job_family' ? 'e.g., Data Platform, Backend…' : ''}
            />
          </div>
        ))}
      </div>

      <div className="flex gap-3">
        <button
          onClick={generate}
          disabled={busy}
          className="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {busy ? 'Generating…' : 'Generate JD'}
        </button>

        <button
          onClick={save}
          disabled={!jdId || saveBusy}
          className="px-4 py-2 rounded-md bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-60"
        >
          {saveBusy ? 'Saving…' : 'Save Version'}
        </button>

        {jdId && (
          <div className="text-sm text-gray-500 self-center">
            JD #{jdId} {version ? `• v${version}` : ''}
          </div>
        )}
      </div>

      {err && <div className="text-sm text-red-600">{err}</div>}

      <label className="block text-sm mb-1">Content (Markdown)</label>
      <textarea
        className="w-full h-[420px] border rounded-md p-3 font-mono text-sm"
        value={content}
        onChange={(e) => onContentChange?.(e.target.value)}
        placeholder="Generated JD will appear here…"
      />
    </div>
  );
}