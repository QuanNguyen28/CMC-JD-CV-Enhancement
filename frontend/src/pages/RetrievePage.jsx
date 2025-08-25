import { useState } from "react";
import api from "../api";
import { Database, RefreshCcw } from "lucide-react";

export default function RetrievePage() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(8);
  const [useSimilar, setUseSimilar] = useState(true);
  const [loading, setLoading] = useState(false);
  const [rows, setRows] = useState([]);

  async function run() {
    setLoading(true);
    try {
      const url = useSimilar ? "/v1/retrieve/similar" : "/v1/retrieve";
      const { data } = await api.post(url, { query, top_k: topK });
      setRows(data || []);
    } catch (e) {
      console.error(e);
      alert(e?.response?.data?.detail || "Retrieve failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-12 gap-6">
      <section className="col-span-12 neo p-5">
        <div className="flex items-center gap-2 mb-4">
          <Database className="size-5 text-[var(--brand)]" />
          <h2 className="font-semibold text-lg">Semantic Retrieve</h2>
        </div>

        <div className="grid md:grid-cols-[1fr_120px_160px_auto] gap-3">
          <input
            className="input"
            placeholder="Search company JD knowledge (semantic)…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <input
            type="number"
            min={1}
            max={50}
            className="input"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
          />
          <select className="input" value={useSimilar ? "similar" : "raw"} onChange={(e) => setUseSimilar(e.target.value === "similar")}>
            <option value="similar">/v1/retrieve/similar (COSINE)</option>
            <option value="raw">/v1/retrieve (legacy)</option>
          </select>
          <button className="btn btn-primary" onClick={run} disabled={loading || !query}>
            {loading ? <RefreshCcw className="size-4 animate-spin" /> : "Search"}
          </button>
        </div>
      </section>

      <section className="col-span-12 neo-soft p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="text-left bg-[#0f1a31]">
            <tr>
              <Th>Score</Th>
              <Th>JD ID</Th>
              <Th>Chunk</Th>
              <Th>Path</Th>
              <Th>Preview</Th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} className="border-t border-[var(--ring)]">
                <Td className="font-mono">{r.score?.toFixed?.(4) ?? r.distance?.toFixed?.(4) ?? "-"}</Td>
                <Td>{r.jd_id ?? "-"}</Td>
                <Td>#{r.chunk_index ?? "-"}</Td>
                <Td className="truncate max-w-[420px]">
                  {r.object_path || r.object_url || r.path || "-"}
                </Td>
                <Td className="text-[var(--muted)]">
                  {r.snippet ? r.snippet.slice(0, 140) + "…" : "—"}
                </Td>
              </tr>
            ))}
            {!rows.length && (
              <tr>
                <Td colSpan={5} className="text-[var(--muted)]">No results.</Td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function Th({ children }) {
  return <th className="px-4 py-2 text-xs font-semibold text-[var(--muted)]">{children}</th>;
}
function Td({ children, className = "", ...rest }) {
  return <td className={`px-4 py-2 ${className}`} {...rest}>{children}</td>;
}