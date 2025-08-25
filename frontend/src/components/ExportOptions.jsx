import { JDAPI } from '../api';

export default function ExportOptions({ jdId }) {
  const download = async (fmt) => {
    if (!jdId) return;
    const blob = await JDAPI.export(jdId, fmt);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `JD-${jdId}.${fmt}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white border rounded-xl p-4">
      <div className="font-semibold mb-3">Export</div>
      <div className="flex gap-2">
        <button
          disabled={!jdId}
          onClick={() => download('pdf')}
          className="px-3 py-1.5 rounded-md bg-gray-800 text-white disabled:opacity-50"
        >
          PDF
        </button>
        <button
          disabled={!jdId}
          onClick={() => download('docx')}
          className="px-3 py-1.5 rounded-md bg-gray-700 text-white disabled:opacity-50"
        >
          DOCX
        </button>
      </div>
    </div>
  );
}