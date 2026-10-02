import { AISettings, AIProvider } from "@/types/settings-ui";
import { Brain, Info } from "lucide-react";

interface Props {
  settings: AISettings;
  onChange: (updates: Partial<AISettings>) => void;
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

export function AISettingsPanel({ settings, onChange }: Props) {

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4 border-b border-[#1E293B] pb-4">
        <div className="p-2 bg-[#8B5CF6]/10 text-[#8B5CF6] rounded-md border border-[#8B5CF6]/20">
          <Brain className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-[#F8FAFC]">AI Configuration</h2>
          <p className="text-xs text-[#94A3B8]">Configure AI assistance and context scope.</p>
        </div>
      </div>
      
      <div className="bg-[#3B82F6]/10 border border-[#3B82F6]/20 rounded-md p-4 flex gap-3 mb-6">
        <Info className="h-5 w-5 text-[#3B82F6] shrink-0" />
        <p className="text-sm text-[#CBD5E1]">
          AI configuration is currently local to this workspace. Provider integration will be connected when backend AI services are enabled.
        </p>
      </div>
      
      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <div className="flex flex-col mb-4">
          <Toggle 
            label="AI Assistance" 
            checked={settings.aiAssistance} 
            onChange={(v: boolean) => onChange({ aiAssistance: v })} 
          />
        </div>
        
        <div className="space-y-1.5 mb-6 pt-4 border-t border-[#1E293B]">
          <label className="text-xs font-semibold text-[#94A3B8]">Provider</label>
          <select 
            value={settings.provider}
            onChange={(e) => onChange({ provider: e.target.value as AIProvider })}
            className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
          >
            <option value="OPENAI">OpenAI</option>
            <option value="LOCAL">Local / On-Premise</option>
            <option value="DISABLED">Disabled</option>
          </select>
        </div>

        <div className="flex flex-col border-t border-[#1E293B]">
          <Toggle 
            label="Architecture Review" 
            checked={settings.architectureReview} 
            onChange={(v: boolean) => onChange({ architectureReview: v })} 
          />
          <Toggle 
            label="Recommendation Generation" 
            checked={settings.recommendationGeneration} 
            onChange={(v: boolean) => onChange({ recommendationGeneration: v })} 
          />
        </div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-4">Context & Thresholds</h3>
        
        <div className="grid gap-4 sm:grid-cols-2 mb-6">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#94A3B8]">Confidence Threshold (%)</label>
            <input 
              type="number" 
              value={settings.confidenceThreshold}
              onChange={(e) => onChange({ confidenceThreshold: parseInt(e.target.value) || 80 })}
              className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
            />
          </div>
          
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#94A3B8]">Maximum Context Files</label>
            <input 
              type="number" 
              value={settings.maximumContextFiles}
              onChange={(e) => onChange({ maximumContextFiles: parseInt(e.target.value) || 50 })}
              className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
            />
          </div>
        </div>
        
        <div className="flex flex-col border-t border-[#1E293B]">
          <Toggle 
            label="Include Architecture Context" 
            checked={settings.includeArchitectureContext} 
            onChange={(v: boolean) => onChange({ includeArchitectureContext: v })} 
          />
          <Toggle 
            label="Include Governance Context" 
            checked={settings.includeGovernanceContext} 
            onChange={(v: boolean) => onChange({ includeGovernanceContext: v })} 
          />
          <Toggle 
            label="Include Dependency Context" 
            checked={settings.includeDependencyContext} 
            onChange={(v: boolean) => onChange({ includeDependencyContext: v })} 
          />
        </div>
      </div>
    </div>
  );
}




