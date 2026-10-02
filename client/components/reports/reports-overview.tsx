import { ReportStats } from "@/types/reports-ui";
import { FileBarChart, CheckCircle2, Loader2, CalendarClock, ShieldCheck, Activity } from "lucide-react";

interface ReportsOverviewProps {
  stats: ReportStats;
}

export function ReportsOverview({ stats }: ReportsOverviewProps) {
  const metrics = [
    { label: "Total Reports", value: stats.total, icon: FileBarChart, color: "text-[#3B82F6]", bg: "bg-[#3B82F6]/10", border: "border-[#3B82F6]/20" },
    { label: "Completed", value: stats.completed, icon: CheckCircle2, color: "text-[#10B981]", bg: "bg-[#10B981]/10", border: "border-[#10B981]/20" },
    { label: "In Progress", value: stats.inProgress, icon: Loader2, color: "text-[#F59E0B]", bg: "bg-[#F59E0B]/10", border: "border-[#F59E0B]/20" },
    { label: "Scheduled", value: stats.scheduled, icon: CalendarClock, color: "text-[#8B5CF6]", bg: "bg-[#8B5CF6]/10", border: "border-[#8B5CF6]/20" },
    { label: "Latest Score", value: `${stats.latestScore} / 100`, icon: ShieldCheck, color: "text-[#10B981]", bg: "bg-[#10B981]/10", border: "border-[#10B981]/20" },
    { label: "Coverage", value: `${stats.coverage}%`, icon: Activity, color: "text-[#3B82F6]", bg: "bg-[#3B82F6]/10", border: "border-[#3B82F6]/20" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      {metrics.map((m, i) => (
        <div key={i} className="flex flex-col p-4 rounded-lg bg-[#0F1726] border border-[#1E293B]">
          <div className="flex items-center gap-3 mb-2">
            <div className={`flex h-8 w-8 items-center justify-center rounded-md border ${m.bg} ${m.color} ${m.border}`}>
              <m.icon className="h-4 w-4" />
            </div>
            <div className="text-xs font-semibold uppercase tracking-wider text-[#64748B] whitespace-nowrap overflow-hidden text-ellipsis">{m.label}</div>
          </div>
          <div className="mt-1 text-2xl font-bold text-[#F8FAFC]">{m.value}</div>
        </div>
      ))}
    </div>
  );
}
