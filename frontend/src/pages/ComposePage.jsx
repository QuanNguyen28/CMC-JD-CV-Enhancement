import { useRef, useState } from "react";
import api from "../api";
import DOMPurify from "dompurify";
import { marked } from "marked";
import { FileText, Save, History, Download, Wand2, Lightbulb } from "lucide-react";

/**
 * ComposePage
 * - Generate JD
 * - Live edit (Markdown)
 * - Improve JD (LLM)
 * - Version history
 * - Export PDF/DOCX
 * - AI Suggestions (click to insert at cursor)
 */
export default function ComposePage() {
  const [form, setForm] = useState({
    title: "",
    department: "",
    job_family: "",
    level: "Mid",
    employment_type: "",
    location: "",
  });

  const [loading, setLoading] = useState(false);
  const [jdId, setJdId] = useState(null);
  const [version, setVersion] = useState(null);
  const [content, setContent] = useState("");
  const [versions, setVersions] = useState([]);
  const [exporting, setExporting] = useState(false);

  // --- AI Suggestion state ---
  const [suggesting, setSuggesting] = useState(false);
  const [suggestMode, setSuggestMode] = useState("outline"); // outline | bullets | rewrite
  const [suggestions, setSuggestions] = useState([]);

  const onChange = (k, v) => setForm((s) => ({ ...s, [k]: v }));

  // --- Textarea ref for insert-at-caret ---
  const editorRef = useRef(null);
  const insertAtCaret = (text) => {
    const el = editorRef.current;
    if (!el) {
      setContent((prev) => (prev ? prev + "\n" + text : text));
      return;
    }
    const start = el.selectionStart ?? content.length;
    const end = el.selectionEnd ?? content.length;
    const before = content.slice(0, start);
    const after = content.slice(end);
    const next = (before ? before + "\n" : "") + text + (after ? "\n" + after : "");
    setContent(next);
    // restore caret near inserted block
    requestAnimationFrame(() => {
      el.focus();
      const caret = (before ? before.length + 1 : 0) + text.length + 1;
      el.selectionStart = el.selectionEnd = caret;
    });
  };

  async function generateJD() {
    setLoading(true);
    try {
      const { data } = await api.post("/v1/jd/generate", form);
      setJdId(data.jd_id);
      setVersion(data.version);
      setContent(data.content_md || "");
      setSuggestions([]); // clear old suggs

      // load history
      const his = await api.get(`/v1/jd/version-history/${data.jd_id}`);
      setVersions(his.data || []);
    } catch (e) {
      console.error(e);
      alert(e?.response?.data?.detail || "Generate failed");
    } finally {
      setLoading(false);
    }
  }

  async function saveNewVersion() {
    if (!jdId) return;
    setLoading(true);
    try {
      await api.put("/v1/jd/update", { jd_id: jdId, content_md: content });
      const his = await api.get(`/v1/jd/version-history/${jdId}`);
      setVersions(his.data || []);
      // optimistic: if BE returns nothing, bump local
      setVersion((v) => (v ? v + 1 : 2));
    } catch (e) {
      console.error(e);
      alert(e?.response?.data?.detail || "Update failed");
    } finally {
      setLoading(false);
    }
  }

  function downloadBlob(data, filename) {
    const url = window.URL.createObjectURL(new Blob([data]));
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }

  async function exportJD(format = "pdf") {
    if (!jdId) return;
    setExporting(true);
    try {
      const res = await api.get(`/v1/jd/export/${jdId}`, {
        params: { format },
        responseType: "blob",
      });
      const safeTitle = (form.title || `jd-${jdId}`)
        .toLowerCase()
        .replace(/\s+/g, "-")
        .replace(/[^a-z0-9-_]/g, "");
      const filename = `${safeTitle}-v${version || ""}.${format}`;
      downloadBlob(res.data, filename);
    } catch (e) {
      console.error(e);
      alert(e?.response?.data?.detail || "Export failed");
    } finally {
      setExporting(false);
    }
  }

  // --- Improve (LLM) ---
  async function improveJD() {
    if (!content.trim()) return;
    setLoading(true);
    try {
      const payload = {
        jd_id: jdId || 0,
        content_md: content,
        style: "concise",
        change_summary: "improve from UI",
      };
      const { data } = await api.post("/v1/jd/improve", payload);
      // Expect: { content_md, version }
      if (data?.content_md) setContent(data.content_md);
      if (data?.version) setVersion(data.version);
      if (jdId) {
        const his = await api.get(`/v1/jd/version-history/${jdId}`);
        setVersions(his.data || []);
      }
    } catch (e) {
      console.error(e);
      alert(e?.response?.data?.detail || "Improve failed");
    } finally {
      setLoading(false);
    }
  }

  // --- Suggest (LLM) ---
  async function fetchSuggestions() {
    setSuggesting(true);
    try {
      const payload = {
        title: form.title,
        department: form.department,
        job_family: form.job_family,
        level: form.level,
        current_md: content,
        cursor_section: "",  // optionally set current heading user is in
        mode: suggestMode,   // outline | bullets | rewrite
        rag_context: null,   // set if you have RAG results on UI
        max_tokens: 512,
      };
      const { data } = await api.post("/v1/jd/suggest", payload);
      setSuggestions(data?.suggestions || []);
    } catch (e) {
      console.error(e);
      setSuggestions([]);
      alert(e?.response?.data?.detail || "Suggest failed");
    } finally {
      setSuggesting(false);
    }
  }

  const html = DOMPurify.sanitize(marked.parse(content || ""));

  return (
    <div className="grid grid-cols-12 gap-6">
      {/* Left: Form & actions */}
      <section className="col-span-12 xl:col-span-4 neo p-5 space-y-4">
        <div className="flex items-center gap-2">
          <FileText className="size-5 text-[var(--brand)]" />
          <h2 className="font-semibold text-lg">Compose Job Description</h2>
        </div>

        <div className="space-y-3">
          <Field label="Title">
            <input
              className="input"
              value={form.title}
              onChange={(e) => onChange("title", e.target.value)}
              placeholder="e.g., Backend Engineer"
            />
          </Field>
          <Field label="Department">
            <input
              className="input"
              value={form.department}
              onChange={(e) => onChange("department", e.target.value)}
              placeholder="e.g., Engineering"
            />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Job family">
              <input
                className="input"
                value={form.job_family}
                onChange={(e) => onChange("job_family", e.target.value)}
                placeholder="e.g., Platform"
              />
            </Field>
            <Field label="Level">
              <input
                className="input"
                value={form.level}
                onChange={(e) => onChange("level", e.target.value)}
                placeholder="e.g., Mid / Senior"
              />
            </Field>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Employment type">
              <input
                className="input"
                value={form.employment_type}
                onChange={(e) => onChange("employment_type", e.target.value)}
                placeholder="e.g., Full-time"
              />
            </Field>
            <Field label="Location">
              <input
                className="input"
                value={form.location}
                onChange={(e) => onChange("location", e.target.value)}
                placeholder="e.g., HCMC / Remote"
              />
            </Field>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <button className="btn btn-primary" onClick={generateJD} disabled={loading}>
            {loading ? "Generating…" : "Generate"}
          </button>

          <button className="btn" onClick={saveNewVersion} disabled={!jdId || loading}>
            <Save className="size-4" /> Save version
          </button>

          <button className="btn" onClick={improveJD} disabled={loading || !content.trim()}>
            <Wand2 className="size-4" /> Improve
          </button>

          <div className="ml-auto flex gap-2">
            <button
              className="btn"
              onClick={() => exportJD("pdf")}
              disabled={!jdId || exporting}
              title={!jdId ? "Generate or load a JD first" : "Export as PDF"}
            >
              <Download className="size-4" /> {exporting ? "Exporting…" : "PDF"}
            </button>
            <button
              className="btn"
              onClick={() => exportJD("docx")}
              disabled={!jdId || exporting}
              title={!jdId ? "Generate or load a JD first" : "Export as DOCX"}
            >
              <Download className="size-4" /> {exporting ? "Exporting…" : "DOCX"}
            </button>
          </div>
        </div>

        <div className="neo-soft p-3 text-xs text-[var(--muted)]">
          JD ID: <b>{jdId ?? "-"}</b> • Version: <b>{version ?? "-"}</b>
        </div>

        <div className="neo-soft p-3">
          <div className="flex items-center gap-2 mb-2">
            <History className="size-4" />
            <div className="font-medium">Version History</div>
          </div>
          <ul className="space-y-1 text-sm max-h-56 overflow-auto pr-1">
            {(versions || []).map((v) => {
              const when =
                v.edited_at || v.updated_at || v.created_at || v.timestamp || null;
              return (
                <li
                  key={`${v.version_number}-${when || v.version_number}`}
                  className="flex items-center justify-between border-b border-[var(--ring)]/60 py-1"
                >
                  <span>v{v.version_number}</span>
                  <span className="text-[var(--muted)]">
                    {when ? new Date(when).toLocaleString() : "-"}
                  </span>
                  <span className="text-[var(--muted)]">{v.edited_by || v.updated_by || "-"}</span>
                </li>
              );
            })}
            {!versions?.length && <li className="text-[var(--muted)]">No history yet.</li>}
          </ul>
        </div>
      </section>

      {/* Right: Editor + Preview + Suggestions */}
      <section className="col-span-12 xl:col-span-8 grid grid-rows-[auto_1fr_auto] gap-6">
        {/* Editor & Preview */}
        <div className="neo p-4 grid grid-cols-2 gap-4 min-h-[520px]">
          <div className="flex flex-col">
            <div className="text-sm text-[var(--muted)] mb-2">Markdown</div>
            <textarea
              ref={editorRef}
              className="input h-full resize-none"
              placeholder="Write or edit JD in Markdown…"
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>

          <div className="flex flex-col">
            <div className="text-sm text-[var(--muted)] mb-2">Preview</div>
            <div
              className="h-full overflow-auto border border-[var(--ring)] rounded-lg p-4 prose prose-slate max-w-none"
              dangerouslySetInnerHTML={{ __html: html }}
            />
          </div>
        </div>

        {/* AI Suggestions */}
        <div className="neo p-4">
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb className="size-4 text-amber-500" />
            <div className="font-medium">AI Suggestions</div>
            <select
              className="ml-auto input !py-1 !h-9 !text-sm w-40"
              value={suggestMode}
              onChange={(e) => setSuggestMode(e.target.value)}
            >
              <option value="outline">Outline</option>
              <option value="bullets">Bullets</option>
              <option value="rewrite">Rewrite</option>
            </select>
            <button className="btn" onClick={fetchSuggestions} disabled={suggesting}>
              {suggesting ? "Generating…" : "Generate"}
            </button>
          </div>

          <div className="grid md:grid-cols-2 gap-3">
            {suggestions.length === 0 && !suggesting && (
              <div className="text-sm text-[var(--muted)]">
                Chọn chế độ và bấm <b>Generate</b> để nhận gợi ý theo ngữ cảnh từ nội dung hiện tại.
              </div>
            )}
            {suggestions.map((s, idx) => (
              <div
                key={`${idx}-${s.slice(0, 16)}`}
                className="p-3 rounded-xl border border-[var(--ring)] bg-white/90 hover:shadow-sm transition"
              >
                <pre className="whitespace-pre-wrap text-sm">{s}</pre>
                <div className="text-right mt-2">
                  <button className="btn" onClick={() => insertAtCaret(s)}>
                    Insert
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block">
      <div className="text-xs mb-1 text-[var(--muted)]">{label}</div>
      {children}
    </label>
  );
}