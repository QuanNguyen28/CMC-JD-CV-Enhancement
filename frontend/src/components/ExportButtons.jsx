import { useState } from 'react';
import { JDAPI } from '../api';
import { downloadBlob } from '../utils/download';

export default function ExportButtons({ jdId, title = 'job-description', disabled }) {
  const [loading, setLoading] = useState(null); // 'pdf' | 'docx' | null

  const handleExport = async (fmt) => {
    if (!jdId) return;
    try {
      setLoading(fmt);
      const blob = await JDAPI.export(jdId, fmt);
      const clean = (title || 'job-description')
        .toLowerCase()
        .replace(/[^a-z0-9\-]+/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '');
      downloadBlob(blob, `${clean}.${fmt}`);
    } catch (e) {
      console.error(e);
      alert(`Export ${fmt.toUpperCase()} failed: ${e?.response?.data || e.message}`);
    } finally {
      setLoading(null);
    }
  };

  const base =
    'inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium ' +
    'transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 ' +
    'disabled:opacity-50 disabled:pointer-events-none';
  const neumo =
    'shadow-[8px_8px_16px_rgba(0,0,0,0.1),_-8px_-8px_16px_rgba(255,255,255,0.8)] ' +
    'hover:shadow-[4px_4px_10px_rgba(0,0,0,0.12),_-4px_-4px_10px_rgba(255,255,255,0.9)]';

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        className={`${base} ${neumo} bg-white text-gray-900`}
        onClick={() => handleExport('pdf')}
        disabled={disabled || loading !== null}
        title="Export as PDF"
      >
        {loading === 'pdf' ? 'Exporting…' : 'Export PDF'}
      </button>

      <button
        type="button"
        className={`${base} ${neumo} bg-white text-gray-900`}
        onClick={() => handleExport('docx')}
        disabled={disabled || loading !== null}
        title="Export as DOCX"
      >
        {loading === 'docx' ? 'Exporting…' : 'Export DOCX'}
      </button>
    </div>
  );
}