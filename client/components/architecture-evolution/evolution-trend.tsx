import { useState, useMemo } from "react";
import { EvolutionSnapshot } from "@/types/architecture-evolution-ui";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface EvolutionTrendProps {
  snapshots: EvolutionSnapshot[];
}

export function EvolutionTrend({ snapshots }: EvolutionTrendProps) {
  const [showHealth, setShowHealth] = useState(true);
  const [showDrift, setShowDrift] = useState(true);
  const [showViolations, setShowViolations] = useState(true);
  
  const [timeRange, setTimeRange] = useState<"7D" | "30D" | "90D" | "1Y">("30D");

  const data = useMemo(() => {
    // In a real app, we'd filter by timeRange. Here we just show available mock snapshots
    // Since mock data only has 9 points, we show all of them.
    return snapshots.map(s => ({
      timestamp: s.timestamp,
      health: s.healthScore,
      drift: s.driftScore,
      violations: s.violationCount,
      components: s.componentCount,
      dependencies: s.dependencyCount,
    }));
  }, [snapshots, timeRange]);

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col h-80">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-[#F8FAFC]">Architecture Trend</h2>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center bg-[#080D18] rounded-md p-1 border border-[#1E293B]">
            <button onClick={() => setTimeRange("7D")} className={`px-2 py-1 text-xs rounded-sm ${timeRange === "7D" ? "bg-[#1E293B] text-white" : "text-[#64748B] hover:text-[#94A3B8]"}`}>7D</button>
            <button onClick={() => setTimeRange("30D")} className={`px-2 py-1 text-xs rounded-sm ${timeRange === "30D" ? "bg-[#1E293B] text-white" : "text-[#64748B] hover:text-[#94A3B8]"}`}>30D</button>
            <button onClick={() => setTimeRange("90D")} className={`px-2 py-1 text-xs rounded-sm ${timeRange === "90D" ? "bg-[#1E293B] text-white" : "text-[#64748B] hover:text-[#94A3B8]"}`}>90D</button>
            <button onClick={() => setTimeRange("1Y")} className={`px-2 py-1 text-xs rounded-sm ${timeRange === "1Y" ? "bg-[#1E293B] text-white" : "text-[#64748B] hover:text-[#94A3B8]"}`}>1Y</button>
          </div>
          
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-1.5 cursor-pointer">
              <input type="checkbox" checked={showHealth} onChange={(e) => setShowHealth(e.target.checked)} className="rounded border-[#1E293B] bg-[#080D18] text-[#22C55E]" />
              <span className="text-xs text-[#94A3B8] font-medium">Health</span>
            </label>
            <label className="flex items-center gap-1.5 cursor-pointer">
              <input type="checkbox" checked={showDrift} onChange={(e) => setShowDrift(e.target.checked)} className="rounded border-[#1E293B] bg-[#080D18] text-[#EF4444]" />
              <span className="text-xs text-[#94A3B8] font-medium">Drift</span>
            </label>
            <label className="flex items-center gap-1.5 cursor-pointer">
              <input type="checkbox" checked={showViolations} onChange={(e) => setShowViolations(e.target.checked)} className="rounded border-[#1E293B] bg-[#080D18] text-[#F59E0B]" />
              <span className="text-xs text-[#94A3B8] font-medium">Violations</span>
            </label>
          </div>
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis dataKey="timestamp" stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
            <Tooltip 
              contentStyle={{ backgroundColor: "#0F1726", borderColor: "#1E293B", color: "#F8FAFC", borderRadius: "8px" }}
              itemStyle={{ color: "#F8FAFC" }}
            />
            {showHealth && <Line type="monotone" dataKey="health" stroke="#22C55E" strokeWidth={2} dot={{ r: 4, fill: "#0F1726", strokeWidth: 2 }} activeDot={{ r: 6 }} name="Health" />}
            {showDrift && <Line type="monotone" dataKey="drift" stroke="#EF4444" strokeWidth={2} dot={{ r: 4, fill: "#0F1726", strokeWidth: 2 }} activeDot={{ r: 6 }} name="Drift" />}
            {showViolations && <Line type="monotone" dataKey="violations" stroke="#F59E0B" strokeWidth={2} dot={{ r: 4, fill: "#0F1726", strokeWidth: 2 }} activeDot={{ r: 6 }} name="Violations" />}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
