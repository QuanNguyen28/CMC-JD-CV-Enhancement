import { useState } from "react";
import api from "../api";
import { MessageSquare, Loader2 } from "lucide-react";

const MIXES = ["technical", "behavioral", "situational"];

export default function InterviewPage() {
  const [form, setForm] = useState({
    jd_id: 0,
    title: "",
    level: "Mid",
    department: "",
    focus: [],
    count: 8,
    mix: [...MIXES],
    language: "vi",
  });
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState([]);

  const onChange = (k, v) => setForm((s) => ({ ...s, [k]: v }));

  const toggleMix = (m) =>
    setForm((s) => ({
      ...s,
      mix: s.mix.includes(m) ? s.mix.filter((x) => x !== m) : [...s.mix, m],
    }));

  async function generate() {
    setLoading(true);
    try {
      const { data } = await api.post("/v1/interview/generate", form);
      setQuestions(data?.questions || data || []);
    } catch (e) {
      console.error(e);
      alert(e?.response?.data?.detail || "Generate failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-12 gap-6">
      <section className="col-span-12 xl:col-span-4 neo p-5 space-y-3">
        <div className="flex items-center gap-2">
          <MessageSquare className="size-5 text-[var(--brand)]" />
          <h2 className="font-semibold text-lg">Interview Generator</h2>
        </div>

        <Field label="Title">
          <input className="input" value={form.title} onChange={(e) => onChange("title", e.target.value)} />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Level">
            <input className="input" value={form.level} onChange={(e) => onChange("level", e.target.value)} />
          </Field>
          <Field label="Department">
            <input className="input" value={form.department} onChange={(e) => onChange("department", e.target.value)} />
          </Field>
        </div>
        <Field label="Focus (comma separated)">
          <input
            className="input"
            placeholder="e.g. system design, API, culture"
            onChange={(e) => onChange("focus", e.target.value.split(",").map((x) => x.trim()).filter(Boolean))}
          />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Count">
            <input
              type="number"
              min={3}
              max={20}
              className="input"
              value={form.count}
              onChange={(e) => onChange("count", Number(e.target.value))}
            />
          </Field>
          <Field label="Language">
            <select className="input" value={form.language} onChange={(e) => onChange("language", e.target.value)}>
              <option value="vi">Vietnamese</option>
              <option value="en">English</option>
            </select>
          </Field>
        </div>

        <div className="text-xs text-[var(--muted)] mt-2">Mix types</div>
        <div className="flex flex-wrap gap-2">
          {MIXES.map((m) => (
            <button
              type="button"
              key={m}
              className={`chip ${form.mix.includes(m) ? "ring-1 ring-[var(--brand)] text-white" : ""}`}
              onClick={() => toggleMix(m)}
            >
              {m}
            </button>
          ))}
        </div>

        <div className="pt-3">
          <button className="btn btn-primary w-full" onClick={generate} disabled={loading}>
            {loading ? <Loader2 className="size-4 animate-spin" /> : "Generate"}
          </button>
        </div>
      </section>

      <section className="col-span-12 xl:col-span-8 neo p-5">
        <div className="font-semibold mb-3">Questions</div>
        {!questions.length && <div className="text-[var(--muted)] text-sm">No questions yet.</div>}
        <ol className="space-y-4">
          {questions.map((q, i) => (
            <li key={i} className="neo-soft p-4">
              <div className="flex items-center justify-between">
                <div className="text-sm uppercase tracking-wide text-[var(--muted)]">{q.type || "general"}</div>
                <div className="text-xs chip">{q.competency || "—"} • {q.difficulty || "—"}</div>
              </div>
              <div className="mt-2 font-medium">{q.question || q.text}</div>
              {q.rubric && (
                <div className="mt-2 text-sm text-[var(--muted)]">
                  <b>Rubric:</b> {q.rubric}
                </div>
              )}
            </li>
          ))}
        </ol>
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