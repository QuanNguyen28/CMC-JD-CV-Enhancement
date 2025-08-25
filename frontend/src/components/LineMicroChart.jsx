import { LineChart, Line, ResponsiveContainer } from "recharts";
export default function LineMicroChart({ data }){
  return (
    <div className="h-24">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <Line type="monotone" dataKey="v" stroke="#4F8EF7" strokeWidth={3} dot={false}/>
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}