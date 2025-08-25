import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  FileText,
  MessagesSquare,
  Search,
  UsersRound,
  Settings,
  LogOut,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import { useMemo } from "react";

function NavItem({ to, icon: Icon, label }) {
  const base =
    "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-[15px] transition-all";
  const rest =
    "text-slate-300 hover:text-white hover:bg-white/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400";
  const active =
    "bg-white/10 text-white shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]";

  return (
    <NavLink
      to={to}
      className={({ isActive }) => `${base} ${isActive ? active : rest}`}
    >
      <span className="grid h-8 w-8 place-content-center rounded-lg bg-white/5 text-slate-200 group-hover:bg-white/10">
        <Icon size={18} />
      </span>
      <span className="truncate">{label}</span>
    </NavLink>
  );
}

function SectionTitle({ children }) {
  return (
    <div className="px-1 pb-2 text-[12px] font-semibold uppercase tracking-wide text-slate-400/70">
      {children}
    </div>
  );
}

function UpgradeCard() {
  return (
    <div className="rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 p-4 text-indigo-50 shadow-lg ring-1 ring-white/10">
      <div className="mb-1 flex items-center gap-2">
        <Sparkles size={16} />
        <span className="text-sm font-semibold">Upgrade to Pro</span>
      </div>
      <p className="text-[12.5px] leading-5 opacity-90">
        Unlock bulk generation, export templates & advanced search.
      </p>
      <button
        className="mt-3 inline-flex items-center gap-1 rounded-lg bg-white/95 px-3 py-1.5 text-[13px] font-semibold text-slate-900 shadow hover:bg-white"
        onClick={() => window.open("https://example.com", "_blank")}
      >
        Upgrade <ArrowRight size={16} />
      </button>
    </div>
  );
}

export default function Sidebar() {
  const navigate = useNavigate();

  const menu = useMemo(
    () => [
      { to: "/", icon: LayoutDashboard, label: "Dashboard" },
      { to: "/compose", icon: FileText, label: "Compose JD" },
      { to: "/interview", icon: MessagesSquare, label: "Interview Q" },
      { to: "/retrieve", icon: Search, label: "Retrieve" },
      { to: "/roles", icon: UsersRound, label: "Roles" },
    ],
    []
  );

  const logout = () => {
    localStorage.removeItem("access_token");
    sessionStorage.removeItem("access_token");
    navigate("/login", { replace: true });
  };

  return (
    <div className="sticky top-0 flex h-screen w-[320px] flex-col border-r border-white/5 bg-[radial-gradient(1200px_600px_at_-200px_-200px,rgba(99,102,241,0.10),transparent_40%),linear-gradient(#0b1220,#0b1220)] px-4 py-5 text-slate-100 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.02)]">
      {/* Brand */}
      <div className="mb-5 flex items-center gap-3 px-1">
        <div className="relative">
          <span className="inline-block h-6 w-6 rounded-md bg-indigo-500 shadow-md" />
          <span className="relative -ml-1 inline-block h-6 w-6 rounded-full bg-cyan-400/90 shadow-md ring-2 ring-indigo-900/40" />
          <span className="relative -ml-1 inline-block h-6 w-6 rounded-full bg-white/90 shadow-md ring-2 ring-indigo-900/40" />
        </div>
        <div className="leading-tight">
          <div className="text-[15px] font-extrabold tracking-tight">SmartHire</div>
          <div className="text-[12px] text-slate-400">@Composer</div>
        </div>
      </div>

      {/* Search hint (visual balance) */}
      <div className="mb-4 hidden rounded-xl border border-white/5 bg-white/[0.03] px-3 py-2 text-[12.5px] text-slate-300/80 backdrop-blur-sm lg:block">
        Press <kbd className="rounded bg-white/10 px-1.5 py-0.5">/</kbd> to search
      </div>

      {/* Navigation */}
      <div className="flex-1 space-y-5 overflow-y-auto pr-1">
        <div>
          <SectionTitle>Main</SectionTitle>
          <nav className="space-y-1.5">
            {menu.map((m) => (
              <NavItem key={m.to} {...m} />
            ))}
          </nav>
        </div>

        <div>
          <SectionTitle>Boost</SectionTitle>
          <UpgradeCard />
        </div>

        <div>
          <SectionTitle>Account</SectionTitle>
          <button
            className="group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-[15px] text-slate-300 hover:bg-white/5 hover:text-white"
            onClick={() => navigate("/settings")}
          >
            <span className="grid h-8 w-8 place-content-center rounded-lg bg-white/5 text-slate-200 group-hover:bg-white/10">
              <Settings size={18} />
            </span>
            Settings
          </button>

          <button
            className="group mt-1.5 flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-[15px] text-red-300 hover:bg-red-500/10 hover:text-red-200"
            onClick={logout}
          >
            <span className="grid h-8 w-8 place-content-center rounded-lg bg-white/5 text-red-300 group-hover:bg-red-500/15">
              <LogOut size={18} />
            </span>
            Log out
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-4 border-t border-white/5 pt-3 text-[11.5px] text-slate-400/70">
        v1.0 • Neumorphism
      </div>
    </div>
  );
}