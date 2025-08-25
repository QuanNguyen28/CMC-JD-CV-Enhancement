import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Users, Shield, Search, RefreshCcw, AlertCircle } from "lucide-react";
import api from "../api";

function SkeletonCard() {
  return (
    <div className="neo animate-pulse p-4 rounded-xl">
      <div className="h-5 w-1/3 bg-white/10 rounded-md mb-3" />
      <div className="h-4 w-2/3 bg-white/10 rounded-md" />
    </div>
  );
}

export default function Roles() {
  const [roles, setRoles] = useState([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const fetchRoles = async () => {
    setErr("");
    setLoading(true);
    try {
      const { data } = await api.get("/v1/roles/list");
      // API trả dạng [{role_name, description?}]
      setRoles(Array.isArray(data) ? data : []);
    } catch (e) {
      setErr(e?.response?.data?.detail || e.message || "Failed to load roles");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoles();
  }, []);

  const filtered = useMemo(() => {
    if (!q) return roles;
    const term = q.toLowerCase();
    return roles.filter(
      (r) =>
        r.role_name?.toLowerCase().includes(term) ||
        r.description?.toLowerCase().includes(term)
    );
  }, [roles, q]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="neo aspect-square w-11 flex items-center justify-center rounded-xl">
            <Users className="size-5 text-[var(--muted)]" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Roles</h1>
            <p className="text-[var(--muted)] text-sm">
              Quản lý vai trò truy cập cho SmartHire Composer.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="neo flex items-center gap-2 px-3 py-2 rounded-xl">
            <Search className="size-4 text-[var(--muted)]" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search roles…"
              className="bg-transparent outline-none placeholder:text-[var(--muted)] text-sm w-52"
            />
          </div>
          <button
            onClick={fetchRoles}
            className="neo px-3 py-2 rounded-xl text-sm hover:bg-white/5 flex items-center gap-2"
            title="Refresh"
          >
            <RefreshCcw className="size-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="neo p-4 rounded-xl">
          <div className="text-xs text-[var(--muted)]">Total roles</div>
          <div className="text-2xl font-semibold mt-1">{roles.length}</div>
        </div>
        <div className="neo p-4 rounded-xl">
          <div className="text-xs text-[var(--muted)]">Showing</div>
          <div className="text-2xl font-semibold mt-1">{filtered.length}</div>
        </div>
        <div className="neo p-4 rounded-xl">
          <div className="text-xs text-[var(--muted)]">Search</div>
          <div className="text-2xl font-semibold mt-1">{q ? `"${q}"` : "—"}</div>
        </div>
      </div>

      {/* Error state */}
      {err && (
        <div className="neo p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-300 flex items-center gap-2">
          <AlertCircle className="size-5" />
          <span className="text-sm">{err}</span>
        </div>
      )}

      {/* List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="neo p-10 rounded-xl text-center">
          <div className="mx-auto mb-3 w-10 h-10 rounded-full bg-white/5 flex items-center justify-center">
            <Search className="size-5 text-[var(--muted)]" />
          </div>
          <p className="font-medium">No roles found</p>
          <p className="text-sm text-[var(--muted)]">
            Thử xoá bộ lọc hoặc tìm kiếm bằng từ khoá khác.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <AnimatePresence>
            {filtered.map((r, idx) => (
              <motion.div
                key={r.role_name + idx}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.18 }}
                className="neo p-4 rounded-xl"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="aspect-square w-9 rounded-lg bg-white/5 flex items-center justify-center">
                      <Shield className="size-4 text-[var(--muted)]" />
                    </div>
                    <div>
                      <div className="font-semibold">{r.role_name}</div>
                      <div className="text-xs text-[var(--muted)]">
                        {r.description || "No description"}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}