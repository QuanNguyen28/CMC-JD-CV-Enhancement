import { useState } from "react";
import api from "../api";
import DOMPurify from "dompurify";
import { marked } from "marked";
import { FileText, Save, History } from "lucide-react";

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

  const onChange = (k, v) => setForm((s) => ({ ...s, [k]: v }));

  async function generateJD() {
    setLoading(true);
    try {
      const { data } = await api.post("/v1/jd/generate", form);
      setJdId(data.jd_id);
      setVersion(data.version);
      setContent(data.content_md || "");
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
      setVersion((v) => (v ? v + 1 : 2));
    } catch (e) {
      console.error(e);
      alert(e?.response?.data?.detail || "Update failed");
    } finally {
      setLoading(false);
    }
  }

  const html = DOMPurify.sanitize(marked.parse(content || ""));

  return (
    <div className="grid grid-cols-12 gap-6">
      {/* Left: Form */}
      <section className="col-span-12 xl:col-span-4 neo p-5 space-y-4">
        <div className="flex items-center gap-2">
          <FileText className="size-5 text-[var(--brand)]" />
          <h2 className="font-semibold text-lg">Compose Job Description</h2>
        </div>

        <div className="space-y-3">
          <Field label="Title">
            <input className="input" value={form.title} onChange={(e) => onChange("title", e.target.value)} />
          </Field>
          <Field label="Department">
            <input className="input" value={form.department} onChange={(e) => onChange("department", e.target.value)} />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Job family">
              <input className="input" value={form.job_family} onChange={(e) => onChange("job_family", e.target.value)} />
            </Field>
            <Field label="Level">
              <input className="input" value={form.level} onChange={(e) => onChange("level", e.target.value)} />
            </Field>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Employment type">
              <input className="input" value={form.employment_type} onChange={(e) => onChange("employment_type", e.target.value)} />
            </Field>
            <Field label="Location">
              <input className="input" value={form.location} onChange={(e) => onChange("location", e.target.value)} />
            </Field>
          </div>
        </div>

        <div className="flex gap-3 pt-2">
          <button className="btn btn-primary" onClick={generateJD} disabled={loading}>
            {loading ? "Generating…" : "Generate"}
          </button>
          <button className="btn" onClick={saveNewVersion} disabled={!jdId || loading}>
            <Save className="size-4" /> Save new version
          </button>
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
            {(versions || []).map((v) => (
              <li key={`${v.version_number}-${v.edited_at}`} className="flex items-center justify-between border-b border-[var(--ring)]/60 py-1">
                <span>v{v.version_number}</span>
                <span className="text-[var(--muted)]">{new Date(v.edited_at).toLocaleString()}</span>
                <span className="text-[var(--muted)]">{v.edited_by}</span>
              </li>
            ))}
            {!versions?.length && <li className="text-[var(--muted)]">No history yet.</li>}
          </ul>
        </div>
      </section>

      {/* Right: Editor + Preview */}
      <section className="col-span-12 xl:col-span-8 grid grid-rows-[1fr] gap-6">
        <div className="neo p-4 grid grid-cols-2 gap-4 min-h-[520px]">
          <div className="flex flex-col">
            <div className="text-sm text-[var(--muted)] mb-2">Markdown</div>
            <textarea
              className="input h-full resize-none"
              placeholder="Write or edit JD in Markdown…"
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>

          <div className="flex flex-col">
            <div className="text-sm text-[var(--muted)] mb-2">Preview</div>
            <div className="neo-soft p-4 overflow-auto prose prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: html }} />
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