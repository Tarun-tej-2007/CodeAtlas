import { DeveloperSettings, LogLevel } from "@/types/settings-ui";
import { Code2, AlertTriangle } from "lucide-react";

interface Props {
  settings: DeveloperSettings;
  onChange: (updates: Partial<DeveloperSettings>) => void;
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

export function DeveloperSettingsPanel({ settings, onChange }: Props) {

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4 border-b border-[#1E293B] pb-4">
        <div className="p-2 bg-[#64748B]/10 text-[#94A3B8] rounded-md border border-[#64748B]/20">
          <Code2 className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-[#F8FAFC]">Developer Settings</h2>
          <p className="text-xs text-[#94A3B8]">Configure advanced diagnostics and experimental features.</p>
        </div>
      </div>
      
      <div className="bg-[#F59E0B]/10 border border-[#F59E0B]/20 rounded-md p-4 flex gap-3 mb-6">
        <AlertTriangle className="h-5 w-5 text-[#F59E0B] shrink-0" />
        <p className="text-sm text-[#CBD5E1]">
          Developer settings can expose internal diagnostic information and should normally remain disabled in production environments.
        </p>
      </div>
      
      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <div className="space-y-1.5 mb-6">
          <label className="text-xs font-semibold text-[#94A3B8]">Log Level</label>
          <select 
            value={settings.logLevel}
            onChange={(e) => onChange({ logLevel: e.target.value as LogLevel })}
            className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
          >
            <option value="ERROR">Error - Only critical issues</option>
            <option value="WARN">Warning - Important issues</option>
            <option value="INFO">Info - Standard operational logging</option>
            <option value="DEBUG">Debug - Verbose diagnostic output</option>
          </select>
        </div>

        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-2 pt-4 border-t border-[#1E293B]">Diagnostics & Features</h3>
        <div className="flex flex-col">
          <Toggle 
            label="Show Debug Information" 
            checked={settings.showDebugInformation} 
            onChange={(v: boolean) => onChange({ showDebugInformation: v })} 
          />
          <Toggle 
            label="Show Performance Metrics" 
            checked={settings.showPerformanceMetrics} 
            onChange={(v: boolean) => onChange({ showPerformanceMetrics: v })} 
          />
          <Toggle 
            label="Show Experimental Features" 
            checked={settings.showExperimentalFeatures} 
            onChange={(v: boolean) => onChange({ showExperimentalFeatures: v })} 
          />
          <Toggle 
            label="Enable Development Diagnostics" 
            checked={settings.enableDevelopmentDiagnostics} 
            onChange={(v: boolean) => onChange({ enableDevelopmentDiagnostics: v })} 
          />
        </div>
      </div>
    </div>
  );
}




