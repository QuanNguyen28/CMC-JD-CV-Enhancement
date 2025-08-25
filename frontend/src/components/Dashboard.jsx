import { ArrowRight, Sparkles, Database, Tags, FileText } from "lucide-react";
import { Link } from "react-router-dom";

function Stat({ label, value, icon: Icon }) {
  return (
    <div className="neo-soft p-4 flex items-center gap-3">
      <div className="size-9 rounded-lg grid place-items-center bg-[#121d36] border border-[var(--ring)]">
        <Icon className="size-4 text-[var(--brand)]" />
      </div>
      <div>
        <div className="text-xl font-semibold leading-5">{value}</div>
        <div className="text-xs text-[var(--muted)]">{label}</div>
      </div>
    </div>
  );
}

function Quick({ title, desc, to }) {
  return (
    <Link to={to} className="neo-soft p-4 block group">
      <div className="flex items-center justify-between">
        <div className="font-medium">{title}</div>
        <ArrowRight className="size-4 opacity-60 group-hover:translate-x-0.5 transition" />
      </div>
      <div className="text-xs text-[var(--muted)] mt-1">{desc}</div>
    </Link>
  );
}

export default function Dashboard() {
  return (
    <div className="grid grid-cols-12 gap-6">
      {/* Hero */}
      <section className="col-span-12 xl:col-span-8 neo p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="chip mb-3">
              <Sparkles className="size-3.5" />
              AI Assistant
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
              SmartHire Composer
            </h1>
            <p className="mt-2 text-sm text-[var(--muted)] max-w-2xl">
              Create polished Job Descriptions, generate interview questions, manage
              versions & search company knowledge — all in one place.
            </p>

            <div className="mt-5 flex flex-wrap gap-3">
              <Link to="/compose" className="btn btn-primary">
                <FileText className="size-4" /> Compose JD
              </Link>
              <Link to="/retrieve" className="btn">
                <Database className="size-4" /> Retrieve
              </Link>
            </div>
          </div>

          <div className="hidden md:grid grid-cols-1 gap-3 min-w-[220px] w-[260px]">
            <Stat label="JD Library" value="109" icon={FileText} />
            <Stat label="Milvus Chunks" value="2,580" icon={Database} />
            <Stat label="Roles" value="8" icon={Tags} />
          </div>
        </div>
      </section>

      {/* Quick actions */}
      <section className="col-span-12 xl:col-span-4 grid grid-cols-2 gap-4">
        <Quick title="New JD" desc="Generate from title & role" to="/compose" />
        <Quick title="Interview Q" desc="Tech/behavioral sets" to="/interview" />
        <Quick title="Semantic Retrieve" desc="Cosine search in Milvus" to="/retrieve" />
        <Quick title="Role Taxonomy" desc="Browse & manage roles" to="/roles" />
      </section>

      {/* Activity */}
      <section className="col-span-12 md:col-span-6 xl:col-span-4 neo-soft p-5">
        <div className="font-semibold">Recent Activity</div>
        <ul className="mt-3 space-y-3 text-sm">
          <li className="flex justify-between">
            <span className="opacity-90">Updated JD: Data Engineer</span>
            <span className="text-[var(--muted)]">2m ago</span>
          </li>
          <li className="flex justify-between">
            <span className="opacity-90">Generated Interview (FE)</span>
            <span className="text-[var(--muted)]">1h ago</span>
          </li>
          <li className="flex justify-between">
            <span className="opacity-90">Embedded 45 chunks</span>
            <span className="text-[var(--muted)]">yesterday</span>
          </li>
        </ul>
      </section>

      {/* Library overview (placeholder mini chart) */}
      <section className="col-span-12 md:col-span-6 xl:col-span-4 neo-soft p-5">
        <div className="font-semibold mb-3">Library Overview</div>
        <div className="h-28 grid grid-cols-24 items-end gap-1">
          {Array.from({ length: 24 }).map((_, i) => (
            <div
              key={i}
              className="rounded-sm bg-[var(--brand)]/50"
              style={{ height: `${30 + Math.abs(Math.sin(i)) * 70}%` }}
              title={`${i}`}
            />
          ))}
        </div>
        <div className="text-xs text-[var(--muted)] mt-2">
          Daily chunks embedded (last 24 days)
        </div>
      </section>

      {/* Tips */}
      <section className="col-span-12 xl:col-span-4 neo-soft p-5">
        <div className="font-semibold">Tips</div>
        <ul className="mt-3 list-disc pl-5 text-sm text-[var(--muted)] space-y-2">
          <li>Use <b>Compose JD</b> to draft, then refine with AI suggestions.</li>
          <li><b>Retrieve</b> brings similar snippets (cosine) from your library.</li>
          <li>All edits are tracked in <b>Version History</b>.</li>
        </ul>
      </section>
    </div>
  );
}