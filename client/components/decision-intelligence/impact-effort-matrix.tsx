import { ImpactEffortPoint } from "@/types/decision-intelligence-ui";
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from "recharts";

interface ImpactEffortMatrixProps {
  points: ImpactEffortPoint[];
  onSelect: (id: string) => void;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomTooltip = ({ active, payload }: { active?: boolean, payload?: any[] }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload as ImpactEffortPoint;
    return (
      <div className="bg-[#0F1726] border border-[#1E293B] p-3 rounded-lg shadow-xl text-xs z-50">
        <div className="font-bold text-[#F8FAFC] mb-1">{data.label}</div>
        <div className="text-[#94A3B8]">Priority: <span className="text-[#CBD5E1]">{data.priority}</span></div>
        <div className="text-[#94A3B8]">Impact: <span className="text-[#CBD5E1]">{data.impactScore}</span></div>
        <div className="text-[#94A3B8]">Effort: <span className="text-[#CBD5E1]">{data.effortScore}</span></div>
      </div>
    );
  }
  return null;
};

export function ImpactEffortMatrix({ points, onSelect }: ImpactEffortMatrixProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "CRITICAL": return "#EF4444";
      case "HIGH": return "#F59E0B";
      case "MEDIUM": return "#3B82F6";
      case "LOW": return "#10B981";
      default: return "#94A3B8";
    }
  };

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <h3 className="text-sm font-bold text-[#F8FAFC] mb-4 uppercase tracking-wider">Impact vs Effort</h3>
      <div className="h-[300px] w-full relative">
        {/* Background quadrants */}
        <div className="absolute inset-0 grid grid-cols-2 grid-rows-2 opacity-5 pointer-events-none z-0">
          <div className="bg-[#10B981] border-r border-b border-[#F8FAFC]" />
          <div className="bg-[#F59E0B] border-b border-[#F8FAFC]" />
          <div className="bg-[#94A3B8] border-r border-[#F8FAFC]" />
          <div className="bg-[#EF4444]" />
        </div>
        
        {/* Quadrant Labels */}
        <div className="absolute inset-0 pointer-events-none z-10 flex">
          <div className="w-1/2 h-full flex flex-col justify-between p-2">
            <div className="text-[10px] text-[#10B981]/50 font-bold tracking-widest uppercase">Quick Wins</div>
            <div className="text-[10px] text-[#64748B]/50 font-bold tracking-widest uppercase">Low Priority</div>
          </div>
          <div className="w-1/2 h-full flex flex-col justify-between items-end p-2">
            <div className="text-[10px] text-[#F59E0B]/50 font-bold tracking-widest uppercase">Strategic</div>
            <div className="text-[10px] text-[#EF4444]/50 font-bold tracking-widest uppercase">Expensive</div>
          </div>
        </div>

        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
            <XAxis 
              type="number" 
              dataKey="effortScore" 
              name="Effort" 
              domain={[0, 100]} 
              stroke="#64748B" 
              fontSize={12} 
              tickLine={false} 
              axisLine={{ stroke: '#334155' }}
              label={{ value: 'EFFORT', position: 'insideBottom', offset: -10, fill: '#64748B', fontSize: 10, fontWeight: 700 }}
            />
            <YAxis 
              type="number" 
              dataKey="impactScore" 
              name="Impact" 
              domain={[0, 100]} 
              stroke="#64748B" 
              fontSize={12} 
              tickLine={false} 
              axisLine={{ stroke: '#334155' }}
              label={{ value: 'IMPACT', angle: -90, position: 'insideLeft', offset: 10, fill: '#64748B', fontSize: 10, fontWeight: 700 }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3', stroke: '#334155' }} />
            <Scatter 
              name="Recommendations" 
              data={points} 
              onClick={(e) => {
                if (e && e.payload && e.payload.recommendationId) {
                  onSelect(e.payload.recommendationId);
                }
              }}
              className="cursor-pointer z-20"
            >
              {points.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getPriorityColor(entry.priority)} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
