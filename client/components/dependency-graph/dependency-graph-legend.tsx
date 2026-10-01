export function DependencyGraphLegend() {
  const items = [
    { label: "Presentation", color: "bg-[#3B82F6]" },
    { label: "Application", color: "bg-[#8B5CF6]" },
    { label: "Domain", color: "bg-[#10B981]" },
    { label: "Infrastructure", color: "bg-[#F59E0B]" },
    { label: "External", color: "bg-[#64748B]" },
  ];

  return (
    <div className="flex flex-wrap gap-3">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-1.5">
          <span className={`h-2.5 w-2.5 rounded-full ${item.color}`} />
          <span className="text-[10px] font-medium text-[#94A3B8] uppercase tracking-wider">{item.label}</span>
        </div>
      ))}
    </div>
  );
}
