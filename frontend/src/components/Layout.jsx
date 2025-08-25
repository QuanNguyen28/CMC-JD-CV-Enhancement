import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

export default function Layout({ children }){
  return (
    <div className="min-h-screen grid lg:grid-cols-[260px,1fr]">
      <aside className="hidden lg:block">
        <Sidebar/>
      </aside>
      <main>
        <Topbar/>
        <div className="px-6 pb-10">{children}</div>
      </main>
    </div>
  );
}