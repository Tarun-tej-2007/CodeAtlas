import { AnalysisSettings, AnalysisDepth } from "@/types/settings-ui";
import { Activity } from "lucide-react";

interface Props {
  settings: AnalysisSettings;
  onChange: (updates: Partial<AnalysisSettings>) => void;
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

export function AnalysisSettingsPanel({ settings, onChange }: Props) {

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4 border-b border-[#1E293B] pb-4">
        <div className="p-2 bg-[#10B981]/10 text-[#10B981] rounded-md border border-[#10B981]/20">
          <Activity className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-[#F8FAFC]">Analysis Settings</h2>
          <p className="text-xs text-[#94A3B8]">Configure how CodeAtlas analyzes your repository.</p>
        </div>
      </div>
      
      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <div className="space-y-1.5 mb-6">
          <label className="text-xs font-semibold text-[#94A3B8]">Analysis Depth</label>
          <select 
            value={settings.defaultAnalysisDepth}
            onChange={(e) => onChange({ defaultAnalysisDepth: e.target.value as AnalysisDepth })}
            className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
          >
            <option value="QUICK">Quick - Basic syntax and structure only</option>
            <option value="STANDARD">Standard - Full structural analysis</option>
            <option value="DEEP">Deep - Semantic and architectural checks</option>
          </select>
          <p className="text-xs text-[#64748B] pt-1">Deep analysis performs additional semantic and architectural checks and may increase analysis time.</p>
        </div>

        <div className="space-y-4 pt-4 border-t border-[#1E293B]">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#94A3B8]">Maximum Analysis Files</label>
              <input 
                type="number" 
                value={settings.maximumAnalysisFiles}
                onChange={(e) => onChange({ maximumAnalysisFiles: parseInt(e.target.value) || 10000 })}
                className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
              />
            </div>
            
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#94A3B8]">Analysis Timeout (seconds)</label>
              <input 
                type="number" 
                value={settings.analysisTimeout}
                onChange={(e) => onChange({ analysisTimeout: parseInt(e.target.value) || 120 })}
                className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-2">Analysis Scope</h3>
        <div className="flex flex-col">
          <Toggle 
            label="Automatic Analysis" 
            desc="Run analysis automatically when changes are detected."
            checked={settings.automaticAnalysis} 
            onChange={(v: boolean) => onChange({ automaticAnalysis: v })} 
          />
          <Toggle 
            label="Analyze Dependencies" 
            checked={settings.analyzeDependencies} 
            onChange={(v: boolean) => onChange({ analyzeDependencies: v })} 
          />
          <Toggle 
            label="Analyze Architecture" 
            checked={settings.analyzeArchitecture} 
            onChange={(v: boolean) => onChange({ analyzeArchitecture: v })} 
          />
          <Toggle 
            label="Analyze Security" 
            checked={settings.analyzeSecurity} 
            onChange={(v: boolean) => onChange({ analyzeSecurity: v })} 
          />
          <Toggle 
            label="Incremental Analysis" 
            desc="Only analyze changed files to speed up subsequent runs."
            checked={settings.incrementalAnalysis} 
            onChange={(v: boolean) => onChange({ incrementalAnalysis: v })} 
          />
        </div>
      </div>
    </div>
  );
}




