export default function ProgressBar({ value=0 }){
  return (
    <div className="h-2 w-full bg-surface rounded-full overflow-hidden">
      <div className="h-full bg-success rounded-full transition-all" style={{ width: `${value}%` }} />
    </div>
  );
}