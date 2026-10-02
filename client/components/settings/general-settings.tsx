import { GeneralSettings } from "@/types/settings-ui";
import { Briefcase } from "lucide-react";

interface Props {
  settings: GeneralSettings;
  onChange: (updates: Partial<GeneralSettings>) => void;
  
}

export function GeneralSettingsPanel({ settings, onChange, }: Props) {
  // A helper to highlight matching text or decide visibility could go here,
  // but for simplicity, we will rely on the page logic or just show everything
  // if this section is selected. If we implement full search, we might hide non-matching rows.
  
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4 border-b border-[#1E293B] pb-4">
        <div className="p-2 bg-[#3B82F6]/10 text-[#3B82F6] rounded-md border border-[#3B82F6]/20">
          <Briefcase className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-[#F8FAFC]">General Settings</h2>
          <p className="text-xs text-[#94A3B8]">Configure your workspace basics.</p>
        </div>
      </div>
      
      <div className="space-y-6">
        <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5 space-y-4">
          <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-2">Workspace Information</h3>
          
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#94A3B8]">Workspace Name</label>
              <input 
                type="text" 
                value={settings.workspaceName}
                onChange={(e) => onChange({ workspaceName: e.target.value })}
                className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
              />
            </div>
            
            <div className="space-y-1.5 sm:col-span-2">
              <label className="text-xs font-semibold text-[#94A3B8]">Workspace Description</label>
              <textarea 
                value={settings.workspaceDescription}
                onChange={(e) => onChange({ workspaceDescription: e.target.value })}
                rows={2}
                className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6] resize-none"
              />
            </div>
          </div>
        </div>

        <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5 space-y-4">
          <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-2">Project Defaults</h3>
          
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#94A3B8]">Default Project</label>
              <input 
                type="text" 
                value={settings.defaultProject}
                onChange={(e) => onChange({ defaultProject: e.target.value })}
                className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
              />
            </div>
            
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#94A3B8]">Default Branch</label>
              <input 
                type="text" 
                value={settings.defaultBranch}
                onChange={(e) => onChange({ defaultBranch: e.target.value })}
                className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
              />
            </div>
            
            <div className="space-y-1.5 sm:col-span-2">
              <label className="text-xs font-semibold text-[#94A3B8]">Repository Root</label>
              <input 
                type="text" 
                value={settings.repositoryRoot}
                onChange={(e) => onChange({ repositoryRoot: e.target.value })}
                className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6] font-mono text-xs"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

