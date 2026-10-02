import { NotificationSettings, NotificationFrequency } from "@/types/settings-ui";
import { Bell } from "lucide-react";

interface Props {
  settings: NotificationSettings;
  onChange: (updates: Partial<NotificationSettings>) => void;
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

export function NotificationSettingsPanel({ settings, onChange }: Props) {

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4 border-b border-[#1E293B] pb-4">
        <div className="p-2 bg-[#EAB308]/10 text-[#EAB308] rounded-md border border-[#EAB308]/20">
          <Bell className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-[#F8FAFC]">Notification Settings</h2>
          <p className="text-xs text-[#94A3B8]">Configure alerts and summary frequency.</p>
        </div>
      </div>
      
      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <div className="space-y-1.5 mb-6">
          <label className="text-xs font-semibold text-[#94A3B8]">Notification Frequency</label>
          <select 
            value={settings.notificationFrequency}
            onChange={(e) => onChange({ notificationFrequency: e.target.value as NotificationFrequency })}
            className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
          >
            <option value="Immediate">Immediate</option>
            <option value="Daily">Daily Digest</option>
            <option value="Weekly">Weekly Digest</option>
            <option value="Disabled">Disabled</option>
          </select>
        </div>

        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-2 pt-4 border-t border-[#1E293B]">Alert Preferences</h3>
        <div className="flex flex-col">
          <Toggle 
            label="Analysis Completed" 
            checked={settings.analysisCompleted} 
            onChange={(v: boolean) => onChange({ analysisCompleted: v })} 
          />
          <Toggle 
            label="Critical Violations" 
            checked={settings.criticalViolations} 
            onChange={(v: boolean) => onChange({ criticalViolations: v })} 
          />
          <Toggle 
            label="Architecture Drift" 
            checked={settings.architectureDrift} 
            onChange={(v: boolean) => onChange({ architectureDrift: v })} 
          />
          <Toggle 
            label="Governance Changes" 
            checked={settings.governanceChanges} 
            onChange={(v: boolean) => onChange({ governanceChanges: v })} 
          />
          <Toggle 
            label="AI Review Completed" 
            checked={settings.aiReviewCompleted} 
            onChange={(v: boolean) => onChange({ aiReviewCompleted: v })} 
          />
          <Toggle 
            label="Weekly Engineering Summary" 
            checked={settings.weeklyEngineeringSummary} 
            onChange={(v: boolean) => onChange({ weeklyEngineeringSummary: v })} 
          />
        </div>
      </div>
    </div>
  );
}




