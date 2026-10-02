import { EvolutionSnapshot } from "@/types/architecture-evolution-ui";

interface EvolutionSnapshotSelectorProps {
  snapshots: EvolutionSnapshot[];
  selectedBaselineId: string;
  onBaselineChange: (id: string) => void;
  selectedCurrentId: string;
  onCurrentChange: (id: string) => void;
}

export function EvolutionSnapshotSelector({
  snapshots,
  selectedBaselineId,
  onBaselineChange,
  selectedCurrentId,
  onCurrentChange
}: EvolutionSnapshotSelectorProps) {
  // Mock simplified baseline selector logic as requested
  return (
    <div className="flex items-center gap-4 bg-[#0F1726] border border-[#1E293B] rounded-lg p-3">
      <div className="flex items-center gap-2">
        <span className="text-xs text-[#94A3B8] font-semibold uppercase">Baseline:</span>
        <select
          value={selectedBaselineId}
          onChange={(e) => onBaselineChange(e.target.value)}
          className="bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] px-2 py-1 focus:outline-none focus:border-[#3B82F6]"
        >
          {snapshots.map(s => (
            <option key={s.id} value={s.id}>{s.timestamp} (Snapshot)</option>
          ))}
        </select>
      </div>

      <span className="text-[#64748B]">vs</span>

      <div className="flex items-center gap-2">
        <span className="text-xs text-[#94A3B8] font-semibold uppercase">Current:</span>
        <select
          value={selectedCurrentId}
          onChange={(e) => onCurrentChange(e.target.value)}
          className="bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] px-2 py-1 focus:outline-none focus:border-[#3B82F6]"
        >
          {snapshots.map(s => (
            <option key={s.id} value={s.id}>{s.timestamp} (Snapshot)</option>
          ))}
        </select>
      </div>
    </div>
  );
}
