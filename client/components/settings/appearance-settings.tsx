import { AppearanceSettings, InterfaceDensity } from "@/types/settings-ui";
import { Palette, Moon, Sun, Monitor } from "lucide-react";

interface Props {
  settings: AppearanceSettings;
  onChange: (updates: Partial<AppearanceSettings>) => void;
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

export function AppearanceSettingsPanel({ settings, onChange }: Props) {

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4 border-b border-[#1E293B] pb-4">
        <div className="p-2 bg-[#EC4899]/10 text-[#EC4899] rounded-md border border-[#EC4899]/20">
          <Palette className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-[#F8FAFC]">Appearance Settings</h2>
          <p className="text-xs text-[#94A3B8]">Customize the visual style of CodeAtlas.</p>
        </div>
      </div>
      
      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-4">Theme</h3>
        
        <div className="grid grid-cols-3 gap-3 mb-6">
          <button
            onClick={() => onChange({ theme: "LIGHT" })}
            className={`flex flex-col items-center justify-center p-4 rounded-md border transition-colors ${
              settings.theme === "LIGHT" 
                ? "bg-[#3B82F6]/10 border-[#3B82F6] text-[#3B82F6]" 
                : "bg-[#080D18] border-[#1E293B] text-[#94A3B8] hover:border-[#64748B] hover:text-[#CBD5E1]"
            }`}
          >
            <Sun className="h-6 w-6 mb-2" />
            <span className="text-xs font-semibold">Light</span>
          </button>
          
          <button
            onClick={() => onChange({ theme: "DARK" })}
            className={`flex flex-col items-center justify-center p-4 rounded-md border transition-colors ${
              settings.theme === "DARK" 
                ? "bg-[#3B82F6]/10 border-[#3B82F6] text-[#3B82F6]" 
                : "bg-[#080D18] border-[#1E293B] text-[#94A3B8] hover:border-[#64748B] hover:text-[#CBD5E1]"
            }`}
          >
            <Moon className="h-6 w-6 mb-2" />
            <span className="text-xs font-semibold">Dark</span>
          </button>
          
          <button
            onClick={() => onChange({ theme: "SYSTEM" })}
            className={`flex flex-col items-center justify-center p-4 rounded-md border transition-colors ${
              settings.theme === "SYSTEM" 
                ? "bg-[#3B82F6]/10 border-[#3B82F6] text-[#3B82F6]" 
                : "bg-[#080D18] border-[#1E293B] text-[#94A3B8] hover:border-[#64748B] hover:text-[#CBD5E1]"
            }`}
          >
            <Monitor className="h-6 w-6 mb-2" />
            <span className="text-xs font-semibold">System</span>
          </button>
        </div>

        <div className="space-y-1.5 mb-6 pt-4 border-t border-[#1E293B]">
          <label className="text-xs font-semibold text-[#94A3B8]">Interface Density</label>
          <select 
            value={settings.interfaceDensity}
            onChange={(e) => onChange({ interfaceDensity: e.target.value as InterfaceDensity })}
            className="w-full bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
          >
            <option value="COMPACT">Compact</option>
            <option value="COMFORTABLE">Comfortable</option>
          </select>
        </div>

        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-2 pt-4 border-t border-[#1E293B]">Preferences</h3>
        <div className="flex flex-col">
          <Toggle 
            label="Compact Mode" 
            checked={settings.compactMode} 
            onChange={(v: boolean) => onChange({ compactMode: v })} 
          />
          <Toggle 
            label="Enable Animations" 
            checked={settings.animations} 
            onChange={(v: boolean) => onChange({ animations: v })} 
          />
          <Toggle 
            label="Reduce Motion" 
            checked={settings.reduceMotion} 
            onChange={(v: boolean) => onChange({ reduceMotion: v })} 
          />
          <Toggle 
            label="Show Grid Background" 
            checked={settings.showGridBackground} 
            onChange={(v: boolean) => onChange({ showGridBackground: v })} 
          />
        </div>
      </div>
      
      <div className="bg-[#080D18] border border-[#1E293B] rounded-lg p-5">
        <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-4">Preview</h3>
        <div className={`border border-[#1E293B] rounded-md overflow-hidden ${settings.theme === "LIGHT" ? "bg-white text-gray-900" : "bg-[#0B1220] text-[#F8FAFC]"}`}>
          <div className={`p-3 border-b ${settings.theme === "LIGHT" ? "border-gray-200" : "border-[#1E293B]"}`}>
            <div className="flex gap-2">
              <div className="h-3 w-3 rounded-full bg-red-500"></div>
              <div className="h-3 w-3 rounded-full bg-yellow-500"></div>
              <div className="h-3 w-3 rounded-full bg-green-500"></div>
            </div>
          </div>
          <div className={`p-4 ${settings.compactMode ? "space-y-2" : "space-y-4"} ${settings.interfaceDensity === "COMFORTABLE" ? "p-6" : ""}`}>
            <div className={`h-4 w-1/3 rounded ${settings.theme === "LIGHT" ? "bg-gray-200" : "bg-[#1E293B]"}`}></div>
            <div className={`h-12 w-full rounded ${settings.theme === "LIGHT" ? "bg-blue-50 border border-blue-200" : "bg-[#3B82F6]/10 border border-[#3B82F6]/20"}`}></div>
            <div className={`h-8 w-2/3 rounded ${settings.theme === "LIGHT" ? "bg-gray-100" : "bg-[#141E2E]"}`}></div>
          </div>
        </div>
      </div>
    </div>
  );
}





