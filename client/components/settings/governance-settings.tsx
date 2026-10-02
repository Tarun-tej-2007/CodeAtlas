import { GovernanceSettings, GovernanceEnforcement, ViolationSeverity, ExceptionDuration } from "@/types/settings-ui";
import { ShieldCheck } from "lucide-react";

interface Props {
  settings: GovernanceSettings;
  onChange: (updates: Partial<GovernanceSettings>) => void;
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

export function GovernanceSettingsPanel({ settings, onChange }: Props) {

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4 border-b border-[#1E293B] pb-4">
        <div className="p-2 bg-[#F43F5E]/10 text-[#F43F5E] rounded-md border border-[#F43F5E]/20">
          <ShieldCheck className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-[#F8FAFC]">Governance Settings</h2>
          <p className="text-xs text-[#94A3B8]">Configure policy enforcement and exception handling.</p>
        </div>
      </div>
      
      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-2">Evaluation</h3>
        <div className="flex flex-col">
          <Toggle 
            label="Automatic Governance Evaluation" 
            checked={settings.automaticGovernanceEvaluation} 
            onChange={(v: boolean) => onChange({ automaticGovernanceEvaluation: v })} 
          />
          <Toggle 
            label="Evaluate Architecture" 
            checked={settings.evaluateArchitecture} 
            onChange={(v: boolean) => onChange({ evaluateArchitecture: v })} 
          />
          <Toggle 
            label="Evaluate Dependencies" 
            checked={settings.evaluateDependencies} 
            onChange={(v: boolean) => onChange({ evaluateDependencies: v })} 
          />
          <Toggle 
            label="Evaluate Security" 
            checked={settings.evaluateSecurity} 
            onChange={(v: boolean) => onChange({ evaluateSecurity: v })} 
          />
        </div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-4">Enforcement</h3>
        
        <div className="grid gap-4 sm:grid-cols-2 mb-6">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#94A3B8]">Policy Enforcement</label>
            <select 
              value={settings.policyEnforcement}
              onChange={(e) => onChange({ policyEnforcement: e.target.value as GovernanceEnforcement })}
              className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
            >
              <option value="WARNING">Warning</option>
              <option value="BLOCKING">Blocking</option>
            </select>
          </div>
          
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#94A3B8]">Critical Violations</label>
            <select 
              value={settings.criticalViolations}
              onChange={(e) => onChange({ criticalViolations: e.target.value as GovernanceEnforcement })}
              className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
            >
              <option value="WARNING">Warning</option>
              <option value="BLOCKING">Blocking</option>
            </select>
          </div>
          
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#94A3B8]">High Violations</label>
            <select 
              value={settings.highViolations}
              onChange={(e) => onChange({ highViolations: e.target.value as ViolationSeverity })}
              className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
            >
              <option value="IGNORE">Ignore</option>
              <option value="WARNING">Warning</option>
              <option value="BLOCKING">Blocking</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-2">Exceptions</h3>
        <div className="flex flex-col mb-4">
          <Toggle 
            label="Require Exception for Violations" 
            checked={settings.requireExceptionForViolations} 
            onChange={(v: boolean) => onChange({ requireExceptionForViolations: v })} 
          />
        </div>
        
        <div className="space-y-1.5 border-t border-[#1E293B] pt-4">
          <label className="text-xs font-semibold text-[#94A3B8]">Default Exception Duration</label>
          <select 
            value={settings.defaultExceptionDuration}
            onChange={(e) => onChange({ defaultExceptionDuration: e.target.value as ExceptionDuration })}
            className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
          >
            <option value="7 days">7 days</option>
            <option value="14 days">14 days</option>
            <option value="30 days">30 days</option>
            <option value="90 days">90 days</option>
          </select>
        </div>
      </div>
    </div>
  );
}




