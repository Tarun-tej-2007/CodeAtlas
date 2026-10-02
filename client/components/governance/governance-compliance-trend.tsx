import { ComplianceTrendPoint } from "@/types/governance-ui";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface GovernanceComplianceTrendProps {
  data: ComplianceTrendPoint[];
}

export function GovernanceComplianceTrend({ data }: GovernanceComplianceTrendProps) {
  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col h-[300px]">
      <h2 className="text-sm font-semibold text-[#F8FAFC] mb-4">Compliance Trend</h2>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis dataKey="timestamp" stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} domain={['dataMin - 5', 100]} />
            <Tooltip 
              contentStyle={{ backgroundColor: "#0F1726", borderColor: "#1E293B", color: "#F8FAFC", borderRadius: "8px" }}
              itemStyle={{ color: "#F8FAFC" }}
              labelStyle={{ color: "#94A3B8", marginBottom: "4px" }}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              formatter={(value: any, name: any) => {
                if (name === "compliance") return [`${value}%`, "Compliance"];
                if (name === "health") return [value, "Health"];
                if (name === "openViolations") return [value, "Open Violations"];
                if (name === "criticalViolations") return [value, "Critical Violations"];
                return [value, name];
              }}
            />
            <Line 
              type="monotone" 
              dataKey="compliance" 
              stroke="#3B82F6" 
              strokeWidth={2} 
              dot={{ r: 4, fill: "#0F1726", strokeWidth: 2 }} 
              activeDot={{ r: 6 }} 
              name="compliance" 
            />
            <Line 
              type="monotone" 
              dataKey="health" 
              stroke="#10B981" 
              strokeWidth={2} 
              dot={{ r: 4, fill: "#0F1726", strokeWidth: 2 }} 
              activeDot={{ r: 6 }} 
              name="health" 
            />
            {/* These are hidden from the lines but available for tooltip data */}
            <Line type="monotone" dataKey="openViolations" stroke="none" dot={false} activeDot={false} name="openViolations" />
            <Line type="monotone" dataKey="criticalViolations" stroke="none" dot={false} activeDot={false} name="criticalViolations" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
