import { Settings, Save, RotateCcw } from "lucide-react";

interface SettingsHeaderProps {
  isDirty: boolean;
  onSave: () => void;
  onReset: () => void;
  lastSavedText: string;
}

export function SettingsHeader({ isDirty, onSave, onReset, lastSavedText }: SettingsHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6 pb-6 border-b border-[#1E293B]">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Settings className="h-5 w-5 text-[#3B82F6]" />
          <h1 className="text-2xl font-bold tracking-tight text-[#F8FAFC]">Settings</h1>
        </div>
        <p className="text-sm text-[#94A3B8]">
          Configure your CodeAtlas workspace, analysis behavior, and engineering preferences.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="flex flex-col items-start sm:items-end mr-4 hidden sm:flex">
          <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">
            Configuration Status
          </span>
          <div className="text-sm font-bold text-[#F8FAFC]">
            {isDirty ? (
              <span className="text-[#F59E0B]">Unsaved changes</span>
            ) : (
              <span className="text-[#10B981]">Configured</span>
            )}
          </div>
          <div className="text-[10px] text-[#94A3B8]">
            {isDirty ? "Action required" : lastSavedText}
          </div>
        </div>
        
        <button 
          onClick={onReset}
          className="px-3 py-2 bg-[#0F1726] border border-[#1E293B] text-[#CBD5E1] rounded-md hover:bg-[#1E293B] hover:text-[#F8FAFC] transition-colors flex items-center gap-2 text-sm font-medium"
        >
          <RotateCcw className="h-4 w-4" />
          <span className="hidden sm:inline">Reset Defaults</span>
        </button>
        
        <button
          onClick={onSave}
          disabled={!isDirty}
          className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] disabled:bg-[#1E293B] disabled:text-[#64748B] text-white rounded-md text-sm font-medium transition-colors shadow focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#3B82F6]"
        >
          <Save className="h-4 w-4" />
          Save Changes
        </button>
      </div>
    </div>
  );
}
