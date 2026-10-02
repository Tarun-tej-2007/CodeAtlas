import { GovernanceViolation, Severity } from "@/types/governance-ui";

interface GovernanceViolationsProps {
  violations: GovernanceViolation[];
  onSelectViolation: (v: GovernanceViolation) => void;
}

export function GovernanceViolations({ violations, onSelectViolation }: GovernanceViolationsProps) {
  const getSeverityColor = (sev: Severity) => {
    switch (sev) {
      case "Critical": return "text-[#EF4444] border-[#EF4444]/20 bg-[#EF4444]/10";
      case "High": return "text-[#F59E0B] border-[#F59E0B]/20 bg-[#F59E0B]/10";
      case "Medium": return "text-[#3B82F6] border-[#3B82F6]/20 bg-[#3B82F6]/10";
      case "Low": return "text-[#94A3B8] border-[#94A3B8]/20 bg-[#94A3B8]/10";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Open": return "text-[#F59E0B]";
      case "Resolved": return "text-[#22C55E]";
      case "Ignored": return "text-[#94A3B8]";
    }
  };

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-0 flex flex-col overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead>
            <tr className="text-[#64748B] border-b border-[#1E293B] bg-[#0B1220]/50">
              <th className="py-3 px-4 font-medium">Severity</th>
              <th className="py-3 px-4 font-medium">Message</th>
              <th className="py-3 px-4 font-medium">Component</th>
              <th className="py-3 px-4 font-medium">Status</th>
              <th className="py-3 px-4 font-medium">Detected</th>
            </tr>
          </thead>
          <tbody>
            {violations.length > 0 ? (
              violations.map((violation) => (
                <tr 
                  key={violation.id} 
                  className="border-b border-[#1E293B]/50 hover:bg-[#141E2E] cursor-pointer transition-colors"
                  onClick={() => onSelectViolation(violation)}
                  data-testid="violation-row"
                >
                  <td className="py-3 px-4">
                    <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${getSeverityColor(violation.severity)}`}>
                      {violation.severity}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-medium text-[#F8FAFC] block max-w-md truncate">{violation.message}</span>
                  </td>
                  <td className="py-3 px-4 text-[#CBD5E1]">{violation.component}</td>
                  <td className="py-3 px-4">
                    <span className={`font-medium ${getStatusColor(violation.status)}`}>{violation.status}</span>
                  </td>
                  <td className="py-3 px-4 text-[#64748B]">{violation.date}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="py-8 text-center text-[#64748B]">
                  No violations found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
