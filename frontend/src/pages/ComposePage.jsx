import { useRef, useState, useMemo } from "react";
import api from "../api";
import DOMPurify from "dompurify";
import { marked } from "marked";
import { FileText, Save, History, Download, Wand2, Lightbulb, ChevronDown, ChevronRight } from "lucide-react";


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

  // Language control
  const [lang, setLang] = useState("vi");

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
  const [suggOpen, setSuggOpen] = useState(true);

  const onChange = (k, v) => setForm((s) => ({ ...s, [k]: v }));

  // Add language header for backend
  const headersWithLang = useMemo(() => ({ "X-Gen-Lang": lang }), [lang]);

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
      const payload = { ...form, language: lang };
      const { data } = await api.post("/v1/jd/generate", payload);
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
      await api.put(
        "/v1/jd/update",
        { jd_id: jdId, content_md: content, change_summary: "manual edit" }
      );
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
        content_md: content,
        instruction: "Polish for clarity, keep Markdown, concise and consistent tone.",
        language: lang,
      };
      const { data } = await api.post("/v1/jd/improve", payload);
      if (data?.content_md) setContent(data.content_md);
      // version may or may not be returned; refresh history if we have a jdId
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

  // Normalize various backend shapes into a string[] of bullets
  function normalizeBullets(payload) {
    if (!payload) return [];
    // direct array
    if (Array.isArray(payload)) {
      return payload.map((s) => String(s).trim()).filter(Boolean);
    }
    // common wrapped keys
    if (Array.isArray(payload.bullets)) {
      return payload.bullets.map((s) => String(s).trim()).filter(Boolean);
    }
    if (Array.isArray(payload.suggestions)) {
      return payload.suggestions.map((s) => String(s).trim()).filter(Boolean);
    }
    // text-like fields
    let text = "";
    if (typeof payload === "string") text = payload;
    else if (typeof payload.text === "string") text = payload.text;
    else if (typeof payload.content === "string") text = payload.content;
    else if (typeof payload.message === "string") text = payload.message;

    text = String(text || "");
    if (!text) return [];

    // split lines, strip leading bullets/dots, remove empties
    return text
      .split(/\r?\n+/)
      .map((line) => line.replace(/^\s*[-*•]\s?/, "").trim())
      .filter(Boolean);
  }

  // --- Suggest (LLM) ---
  async function fetchSuggestions() {
    setSuggesting(true);
    try {
      // ensure panel is open so user sees results
      setSuggOpen(true);

      let section = "Responsibilities";
      let goal = "Suggest 6–10 concise bullets aligned with the current JD.";
      if (suggestMode === "outline") {
        section = "Outline";
        goal = "Propose a clean JD outline (headings) that fits this role.";
      } else if (suggestMode === "rewrite") {
        section = "Summary";
        goal = "Rewrite the summary for clarity and impact (3–5 short paragraphs).";
      }

      const payload = {
        content_md: content || "",
        section,
        goal,
        language: lang,
        chunks_text: null, // optionally pass RAG context here
      };

      const { data } = await api.post("/v1/jd/suggest", payload);
      const bullets = normalizeBullets(data);
      setSuggestions(bullets);

      // If nothing returned, show a gentle hint instead of blank area
      if (!bullets.length) {
        console.warn("Suggest API returned no items. Raw payload:", data);
      }
    } catch (e) {
      console.error(e);
      setSuggestions([
        "⚠️ Could not fetch suggestions. Please try again.",
      ]);
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
          <Field label="Language">
            <select
              className="input"
              value={lang}
              onChange={(e) => setLang(e.target.value)}
            >
              <option value="vi">Tiếng Việt</option>
              <option value="en">English</option>
            </select>
          </Field>
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
      <section className="col-span-12 xl:col-span-8 flex flex-col gap-6">
        {/* Editor & Preview */}
        <div className="neo p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex flex-col">
            <div className="text-sm text-[var(--muted)] mb-2">Markdown</div>
            <textarea
              ref={editorRef}
              className="input h-[520px] md:h-[560px] resize-y"
              placeholder="Write or edit JD in Markdown…"
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>

          <div className="flex flex-col">
            <div className="text-sm text-[var(--muted)] mb-2">Preview</div>
            <div
              className="h-[520px] md:h-[560px] overflow-auto border border-[var(--ring)] rounded-lg p-4 prose prose-slate max-w-none bg-white/5"
              dangerouslySetInnerHTML={{ __html: html }}
            />
          </div>
        </div>

        {/* AI Suggestions (collapsible, fixed height) */}
        <div className="neo p-4">
          <button
            type="button"
            onClick={() => setSuggOpen((v) => !v)}
            className="w-full flex items-center gap-2 text-left"
            aria-expanded={suggOpen}
          >
            {suggOpen ? (
              <ChevronDown className="size-4 text-amber-500" />
            ) : (
              <ChevronRight className="size-4 text-amber-500" />
            )}
            <span className="font-medium">AI Suggestions</span>
            <div className="ml-auto flex items-center gap-2">
              <select
                className="input !py-1 !h-9 !text-sm w-40"
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
          </button>

          {suggOpen && (
            <div className="mt-3 grid md:grid-cols-2 gap-3 max-h-[320px] overflow-auto pr-1">
              {suggestions.length === 0 && !suggesting && (
                <div className="text-sm text-[var(--muted)]">
                  Select a mode and click <b>Generate</b> to receive contextual suggestions based on the current content.
                </div>
              )}
              {suggestions.map((s, idx) => (
                <div
                  key={`${idx}-${s.slice(0, 16)}`}
                  className="neo-soft p-3 hover:shadow-sm transition text-[var(--fg)]"
                >
                  <pre className="whitespace-pre-wrap text-sm text-[var(--fg)]">{s}</pre>
                  <div className="text-right mt-2">
                    <button className="btn" onClick={() => insertAtCaret(s)}>
                      Insert
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
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