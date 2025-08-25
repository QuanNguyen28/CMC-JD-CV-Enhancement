import { Icon } from "@iconify/react";
import NeomorphCard from "./NeomorphCard";
import { useAuth } from "../AuthContext";

export default function Topbar(){
  const { user, logout } = useAuth();
  return (
    <div className="sticky top-0 z-20 px-6 pt-6">
      <NeomorphCard className="flex items-center justify-between p-4">
        <div className="flex items-center gap-3">
          <Icon icon="solar:home-2-bold-duotone" className="text-primary" width="22"/>
          <span className="font-semibold">SmartHire Composer</span>
          <span className="pill ml-2">Dashboard</span>
        </div>
        <div className="flex items-center gap-3">
          <button className="neo px-3 py-2 hover:shadow-ring transition-shadow">
            <Icon icon="solar:bell-bing-bold-duotone" width="20"/>
          </button>
          <div className="flex items-center gap-3 neo px-3 py-2">
            <img className="w-8 h-8 rounded-full object-cover"
              src={`https://i.pravatar.cc/96?u=${user?.username||"guest"}`} />
            <div className="text-sm leading-tight">
              <div className="font-semibold">{user?.full_name||"Guest"}</div>
              <div className="text-muted text-xs">{user?.roles?.[0]||"viewer"}</div>
            </div>
            <button onClick={logout} className="ml-2 text-danger hover:underline text-sm">Logout</button>
          </div>
        </div>
      </NeomorphCard>
    </div>
  );
}