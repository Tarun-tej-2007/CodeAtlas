"use client";

import { useState, useMemo, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { SettingsState, SettingsSection } from "@/types/settings-ui";
import { DEFAULT_SETTINGS } from "@/lib/mock-data/settings";

import { SettingsHeader } from "@/components/settings/settings-header";
import { SettingsNavigation } from "@/components/settings/settings-navigation";
import { SettingsSearch } from "@/components/settings/settings-search";
import { GeneralSettingsPanel } from "@/components/settings/general-settings";
import { AnalysisSettingsPanel } from "@/components/settings/analysis-settings";
import { ArchitectureSettingsPanel } from "@/components/settings/architecture-settings";
import { AISettingsPanel } from "@/components/settings/ai-settings";
import { GovernanceSettingsPanel } from "@/components/settings/governance-settings";
import { NotificationSettingsPanel } from "@/components/settings/notification-settings";
import { AppearanceSettingsPanel } from "@/components/settings/appearance-settings";
import { DeveloperSettingsPanel } from "@/components/settings/developer-settings";
import { SettingsSummary } from "@/components/settings/settings-summary";
import { SettingsResetDialog } from "@/components/settings/settings-reset-dialog";

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState<SettingsSection>("General");
  const [searchQuery, setSearchQuery] = useState("");
  const [isResetOpen, setIsResetOpen] = useState(false);
  const [lastSavedText, setLastSavedText] = useState("Just now");
  
  // The truly saved state
  const [savedSettings, setSavedSettings] = useState<SettingsState>(DEFAULT_SETTINGS);
  
  // The current working state (can be dirty)
  const [settings, setSettings] = useState<SettingsState>(DEFAULT_SETTINGS);
  
  const isDirty = useMemo(() => {
    return JSON.stringify(savedSettings) !== JSON.stringify(settings);
  }, [savedSettings, settings]);

  const handleUpdate = useCallback(<K extends keyof SettingsState>(section: K, updates: Partial<SettingsState[K]>) => {
    setSettings(prev => ({
      ...prev,
      [section]: { ...prev[section], ...updates }
    }));
  }, []);

  const handleSave = () => {
    setSavedSettings(settings);
    
    const now = new Date();
    setLastSavedText(
      now.toLocaleDateString('en-US', { month: 'short', day: '2-digit' }) + ', ' + 
      now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
    );
  };

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS);
    setSavedSettings(DEFAULT_SETTINGS);
    setLastSavedText("Just now");
  };

  // Very basic semantic matching for the search demo
  const matchesSearch = (text: string) => {
    if (!searchQuery) return true;
    return text.toLowerCase().includes(searchQuery.toLowerCase());
  };

  // If searching, we might want to automatically switch sections or just highlight
  // Here we just render the active section normally. 
  // If we wanted to, we could render a combined list of matching fields.
  // For Sprint 40, we will just show a "No settings found" if the active section doesn't match the search.
  
  // A crude way to see if current section matches query:
  const sectionContentMap: Record<SettingsSection, string> = {
    "General": JSON.stringify(settings.general) + " workspace branch repository",
    "Analysis": JSON.stringify(settings.analysis) + " quick deep dependency architecture security incremental",
    "Architecture": JSON.stringify(settings.architecture) + " layer boundary circular drift complexity",
    "AI": JSON.stringify(settings.ai) + " provider openai local context recommendation",
    "Governance": JSON.stringify(settings.governance) + " policy blocking warning exception",
    "Notifications": JSON.stringify(settings.notifications) + " email alert weekly daily",
    "Appearance": JSON.stringify(settings.appearance) + " light dark system theme compact animation",
    "Developer": JSON.stringify(settings.developer) + " debug log error info warn metric",
  };

  const hasSearchMatch = matchesSearch(sectionContentMap[activeSection]);

  return (
    <AppShell breadcrumb="Settings">
      <div className="p-6 max-w-[1400px] mx-auto min-h-full pb-20">
        <SettingsHeader 
          isDirty={isDirty} 
          onSave={handleSave}
          onReset={() => setIsResetOpen(true)}
          lastSavedText={lastSavedText}
        />
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Left Column - Navigation */}
          <div className="lg:col-span-1 space-y-6">
            <SettingsSearch query={searchQuery} onChange={setSearchQuery} />
            <div className="sticky top-6">
              <SettingsNavigation 
                activeSection={activeSection} 
                onSelect={setActiveSection} 
              />
            </div>
          </div>
          
          {/* Right Column - Active Settings Panel */}
          <div className="lg:col-span-2">
            {!hasSearchMatch && searchQuery ? (
              <div className="bg-[#0F1726]/50 border border-[#1E293B] border-dashed rounded-lg p-12 text-center">
                <p className="text-[#F8FAFC] font-medium mb-1">No settings found</p>
                <p className="text-sm text-[#64748B]">No matching settings in the &quot;{activeSection}&quot; section.</p>
              </div>
            ) : (
              <>
                {activeSection === "General" && (
                  <GeneralSettingsPanel 
                    settings={settings.general} 
                    onChange={(u) => handleUpdate("general", u)} 
                  />
                )}
                {activeSection === "Analysis" && (
                  <AnalysisSettingsPanel 
                    settings={settings.analysis} 
                    onChange={(u) => handleUpdate("analysis", u)} 
                  />
                )}
                {activeSection === "Architecture" && (
                  <ArchitectureSettingsPanel 
                    settings={settings.architecture} 
                    onChange={(u) => handleUpdate("architecture", u)} 
                  />
                )}
                {activeSection === "AI" && (
                  <AISettingsPanel 
                    settings={settings.ai} 
                    onChange={(u) => handleUpdate("ai", u)} 
                  />
                )}
                {activeSection === "Governance" && (
                  <GovernanceSettingsPanel 
                    settings={settings.governance} 
                    onChange={(u) => handleUpdate("governance", u)} 
                  />
                )}
                {activeSection === "Notifications" && (
                  <NotificationSettingsPanel 
                    settings={settings.notifications} 
                    onChange={(u) => handleUpdate("notifications", u)} 
                  />
                )}
                {activeSection === "Appearance" && (
                  <AppearanceSettingsPanel 
                    settings={settings.appearance} 
                    onChange={(u) => handleUpdate("appearance", u)} 
                  />
                )}
                {activeSection === "Developer" && (
                  <DeveloperSettingsPanel 
                    settings={settings.developer} 
                    onChange={(u) => handleUpdate("developer", u)} 
                  />
                )}
              </>
            )}
          </div>
          
          {/* Third Column - Summary */}
          <div className="lg:col-span-1">
            <div className="sticky top-6">
              <SettingsSummary settings={settings} isDirty={isDirty} />
            </div>
          </div>
        </div>
      </div>
      
      <SettingsResetDialog 
        isOpen={isResetOpen} 
        onClose={() => setIsResetOpen(false)} 
        onConfirm={handleReset} 
      />
    </AppShell>
  );
}

