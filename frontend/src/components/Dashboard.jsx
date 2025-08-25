import NeomorphCard from "./NeomorphCard";
import ProgressBar from "./ProgressBar";
import LineMicroChart from "./LineMicroChart";
import { motion } from "framer-motion";

const micro = Array.from({length:28}, (_,i)=>({ v: 60 + Math.sin(i/2)*20 + (i%5)}));

export default function Dashboard(){
  return (
    <div className="grid gap-6 xl:grid-cols-3">
      {/* Left big hero card */}
      <NeomorphCard className="xl:col-span-2 overflow-hidden">
        <div className="grid md:grid-cols-2 gap-6 items-center">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold">
              Hey, <span className="text-primary">Recruiter</span> 👋
            </h1>
            <p className="mt-2 text-muted">
              Let’s compose high-quality Job Descriptions and interview kits.
            </p>

            <div className="grid sm:grid-cols-3 gap-4 mt-6">
              <NeomorphCard className="p-4">
                <div className="card-title">JD completed</div>
                <div className="text-2xl font-bold mt-1">86%</div>
                <div className="mt-3"><ProgressBar value={86}/></div>
              </NeomorphCard>
              <NeomorphCard className="p-4">
                <div className="card-title">Open roles</div>
                <div className="text-2xl font-bold mt-1">12</div>
                <div className="text-muted text-xs mt-1">this month</div>
              </NeomorphCard>
              <NeomorphCard className="p-4">
                <div className="card-title">Interview kits</div>
                <div className="text-2xl font-bold mt-1">34</div>
                <div className="text-muted text-xs mt-1">auto generated</div>
              </NeomorphCard>
            </div>
          </div>
          <motion.img
            initial={{ scale:.9, opacity:0 }} animate={{ scale:1, opacity:1 }}
            transition={{ type:"spring", stiffness:120, damping:14 }}
            className="w-full"
            src="https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=1200&auto=format&fit=crop"
            alt="hero"
          />
        </div>
      </NeomorphCard>

      {/* Right column small panels */}
      <div className="grid gap-6">
        <NeomorphCard className="p-5">
          <div className="card-title mb-2">Blood Pressure (metaphor → activity)</div>
          <LineMicroChart data={micro}/>
          <div className="flex justify-between items-center mt-2 text-sm">
            <span className="text-muted">Generation velocity</span>
            <span className="font-semibold text-primary">130/82 “mmHg”</span>
          </div>
        </NeomorphCard>

        <NeomorphCard className="p-5">
          <div className="card-title mb-2">Upcoming</div>
          <div className="space-y-3">
            {["Screening Engineer", "QA Lead", "Product Manager"].map((t,i)=>(
              <div key={t} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-surface neo grid place-items-center text-primary font-semibold">{i+1}</div>
                  <div>
                    <div className="font-medium">{t}</div>
                    <div className="text-xs text-muted">Tomorrow • 3:00 PM</div>
                  </div>
                </div>
                <button className="pill">view</button>
              </div>
            ))}
          </div>
        </NeomorphCard>
      </div>
    </div>
  );
}