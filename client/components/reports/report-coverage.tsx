import { Activity } from "lucide-react";

export function ReportCoverage() {
  const coverageData = [
    { label: "Repository Analysis", value: 96 },
    { label: "Architecture", value: 92 },
    { label: "Dependencies", value: 94 },
    { label: "Governance", value: 91 },
    { label: "Security", value: 88 },
    { label: "Code Quality", value: 90 },
    { label: "Decision Intelligence", value: 86 },
    { label: "AI Architecture Review", value: 93 },
  ];

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-[#10B981]" />
          <h3 className="text-sm font-bold text-[#F8FAFC] uppercase tracking-wider">Report Coverage</h3>
        </div>
        <div className="text-xs font-bold text-[#10B981] bg-[#10B981]/10 px-2 py-0.5 rounded">
          94% OVERALL
        </div>
      </div>
      
      <div className="space-y-4">
        {coverageData.map((item) => (
          <div key={item.label}>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="font-semibold text-[#CBD5E1] tracking-wide">{item.label}</span>
              <span className="font-bold text-[#F8FAFC]">{item.value}%</span>
            </div>
            <div className="w-full bg-[#1E293B] rounded-full h-1.5 overflow-hidden">
              <div 
                className="bg-[#3B82F6] h-1.5 rounded-full" 
                style={{ width: `${item.value}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
