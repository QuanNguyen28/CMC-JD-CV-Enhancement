import { useAuth } from "../AuthContext";
import { LogOut, Search } from "lucide-react";

export default function Topbar() {
  const { user, logout } = useAuth();
  return (
    <div className="flex items-center gap-4">
      <div className="relative max-w-xl w-full">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-[var(--muted)]" />
        <input className="input pl-9" placeholder="Quick search…" />
      </div>

      <div className="ml-auto chip">
        <div className="size-6 rounded-full grid place-items-center bg-[var(--brand)] text-[#0b1222] text-xs font-bold">
          {user?.full_name?.[0] ?? "A"}
        </div>
        <span>{user?.full_name ?? "User"}</span>
        <span className="opacity-60">({user?.roles?.[0] ?? "member"})</span>
      </div>

      <button className="btn" onClick={logout}>
        <LogOut className="size-4" /> Logout
      </button>
    </div>
  );
}