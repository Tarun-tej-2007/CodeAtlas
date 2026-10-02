import { ArchitectureSettings, SeverityLevel } from "@/types/settings-ui";
import { Hexagon } from "lucide-react";

interface Props {
  settings: ArchitectureSettings;
  onChange: (updates: Partial<ArchitectureSettings>) => void;
}

const Toggle = ({ label, checked, onChange, desc }: { label: string; checked: boolean; onChange: (checked: boolean) => void; desc?: string; }) => (
    <label className="flex items-start justify-between cursor-pointer py-3 border-b border-[#1E293B] last:border-0">
      <div className="pr-4">
        <div className="text-sm font-medium text-[#F8FAFC]">{label}</div>
        {desc && <div className="text-xs text-[#64748B] mt-1">{desc}</div>}
      </div>
      <div className="relative inline-flex items-center shrink-0 mt-1">
        <input type="checkbox" className="sr-only peer" checked={checked} onChange={(e) => onChange(e.target.checked)} />
        <div className="w-9 h-5 bg-[#1E293B] rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#3B82F6]"></div>
      </div>
    </label>
  );

export function ArchitectureSettingsPanel({ settings, onChange }: Props) {

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4 border-b border-[#1E293B] pb-4">
        <div className="p-2 bg-[#F59E0B]/10 text-[#F59E0B] rounded-md border border-[#F59E0B]/20">
          <Hexagon className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-[#F8FAFC]">Architecture Settings</h2>
          <p className="text-xs text-[#94A3B8]">Configure architecture and dependency evaluation.</p>
        </div>
      </div>
      
      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-2">Boundary Analysis</h3>
        <div className="flex flex-col">
          <Toggle 
            label="Layer Boundary Detection" 
            checked={settings.layerBoundaryDetection} 
            onChange={(v: boolean) => onChange({ layerBoundaryDetection: v })} 
          />
          <Toggle 
            label="Architecture Drift Detection" 
            checked={settings.architectureDriftDetection} 
            onChange={(v: boolean) => onChange({ architectureDriftDetection: v })} 
          />
        </div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-2">Dependency Analysis</h3>
        <div className="flex flex-col">
          <Toggle 
            label="Circular Dependency Detection" 
            checked={settings.circularDependencyDetection} 
            onChange={(v: boolean) => onChange({ circularDependencyDetection: v })} 
          />
          <Toggle 
            label="Cross-Layer Dependency Detection" 
            checked={settings.crossLayerDependencyDetection} 
            onChange={(v: boolean) => onChange({ crossLayerDependencyDetection: v })} 
          />
        </div>
      </div>
      
      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-4">Risk Detection</h3>
        
        <div className="grid gap-4 sm:grid-cols-2 mb-6">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#94A3B8]">Complexity Threshold</label>
            <input 
              type="number" 
              value={settings.complexityThreshold}
              onChange={(e) => onChange({ complexityThreshold: parseInt(e.target.value) || 15 })}
              className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
            />
          </div>
          
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#94A3B8]">Dependency Threshold</label>
            <input 
              type="number" 
              value={settings.dependencyThreshold}
              onChange={(e) => onChange({ dependencyThreshold: parseInt(e.target.value) || 20 })}
              className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
            />
          </div>
        </div>

        <div className="space-y-1.5 mb-6 pt-4 border-t border-[#1E293B]">
          <label className="text-xs font-semibold text-[#94A3B8]">Architecture Violation Severity</label>
          <select 
            value={settings.architectureViolationSeverity}
            onChange={(e) => onChange({ architectureViolationSeverity: e.target.value as SeverityLevel })}
            className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
          >
            <option value="INFO">Info</option>
            <option value="WARNING">Warning</option>
            <option value="BLOCKING">Blocking</option>
          </select>
        </div>
        
        <div className="flex flex-col border-t border-[#1E293B]">
          <Toggle 
            label="Show Architecture Suggestions" 
            checked={settings.showArchitectureSuggestions} 
            onChange={(v: boolean) => onChange({ showArchitectureSuggestions: v })} 
          />
        </div>
      </div>
    </div>
  );
}




