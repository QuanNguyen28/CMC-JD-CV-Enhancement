import { NavLink } from "react-router-dom";
import { Icon } from "@iconify/react";
import NeomorphCard from "./NeomorphCard";

const links = [
  { to:"/", label:"Dashboard", icon:"solar:widget-6-bold-duotone" },
  { to:"/compose", label:"JD Composer", icon:"solar:document-text-bold-duotone" },
  { to:"/interview", label:"Interview Q", icon:"solar:chat-square-like-bold-duotone" },
  { to:"/versions", label:"Versions", icon:"solar:clock-square-bold-duotone" },
  { to:"/retrieve", label:"Retriever", icon:"solar:target-bold-duotone" },
  { to:"/roles", label:"Roles", icon:"solar:shield-user-bold-duotone" },
];

export default function Sidebar(){
  return (
    <div className="px-6 pt-6">
      <NeomorphCard className="p-3">
        {links.map(l=>(
          <NavLink key={l.to} to={l.to}
            className={({isActive}) =>
              `flex items-center gap-3 px-3 py-2 rounded-xl mb-1 hover:bg-surface transition
               ${isActive ? "bg-surface text-primary" : "text-ink/80"}`
            }>
            <Icon icon={l.icon} width="20"/>
            <span className="text-sm font-medium">{l.label}</span>
          </NavLink>
        ))}
      </NeomorphCard>
    </div>
  );
}