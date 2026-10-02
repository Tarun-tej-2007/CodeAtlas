import { ReportHistoryEntry } from "@/types/reports-ui";
import { History } from "lucide-react";

interface ReportHistoryProps {
  history: ReportHistoryEntry[];
}

export function ReportHistory({ history }: ReportHistoryProps) {
  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg overflow-hidden">
      <div className="flex items-center gap-2 p-4 border-b border-[#1E293B] bg-[#141E2E]">
        <History className="h-5 w-5 text-[#94A3B8]" />
        <h3 className="text-sm font-bold text-[#F8FAFC] uppercase tracking-wider">Report History</h3>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-[10px] text-[#64748B] uppercase tracking-wider bg-[#0F1726] border-b border-[#1E293B]">
            <tr>
              <th className="px-4 py-3 font-semibold">Date</th>
              <th className="px-4 py-3 font-semibold">Report</th>
              <th className="px-4 py-3 font-semibold">Score</th>
              <th className="px-4 py-3 font-semibold">Findings</th>
              <th className="px-4 py-3 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1E293B] bg-[#0F1726]">
            {history.map((entry) => (
              <tr key={entry.id} className="hover:bg-[#141E2E] transition-colors group">
                <td className="px-4 py-3 text-xs text-[#CBD5E1] whitespace-nowrap">{entry.date}</td>
                <td className="px-4 py-3 font-medium text-[#F8FAFC]">{entry.reportTitle}</td>
                <td className="px-4 py-3 font-bold text-[#10B981]">{entry.score}</td>
                <td className="px-4 py-3 text-xs text-[#94A3B8]">{entry.findings}</td>
                <td className="px-4 py-3">
                  <span className="text-[10px] px-2 py-0.5 rounded border uppercase font-mono tracking-wide text-[#10B981] bg-[#10B981]/10 border-[#10B981]/20">
                    {entry.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
