import { SettingsState } from "@/types/settings-ui";
import { CheckCircle2, AlertCircle } from "lucide-react";

interface SettingsSummaryProps {
  settings: SettingsState;
  isDirty: boolean;
}

export function SettingsSummary({ settings, isDirty }: SettingsSummaryProps) {
  // Calculate active notifications
  const notificationCount = [
    settings.notifications.analysisCompleted,
    settings.notifications.criticalViolations,
    settings.notifications.architectureDrift,
    settings.notifications.governanceChanges,
    settings.notifications.aiReviewCompleted,
    settings.notifications.weeklyEngineeringSummary
  ].filter(Boolean).length;

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-4">Settings Summary</h3>
      
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-[#94A3B8]">Workspace</span>
            <span className="text-[#F8FAFC] font-medium">{settings.general.workspaceName}</span>
          </div>
        </div>
        
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-[#94A3B8]">Analysis</span>
            <span className="text-[#F8FAFC] font-medium">{settings.analysis.defaultAnalysisDepth}</span>
          </div>
        </div>
        
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-[#94A3B8]">Architecture</span>
            <span className="text-[#F8FAFC] font-medium">
              {settings.architecture.layerBoundaryDetection || settings.architecture.circularDependencyDetection 
                ? "Enabled" 
                : "Disabled"}
            </span>
          </div>
        </div>
        
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-[#94A3B8]">AI Assistance</span>
            <span className="text-[#F8FAFC] font-medium">
              {settings.ai.aiAssistance ? `Enabled (${settings.ai.provider})` : "Disabled"}
            </span>
          </div>
        </div>
        
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-[#94A3B8]">Governance</span>
            <span className={`font-medium ${settings.governance.policyEnforcement === "BLOCKING" ? "text-[#EF4444]" : "text-[#F59E0B]"}`}>
              {settings.governance.policyEnforcement}
            </span>
          </div>
        </div>
        
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-[#94A3B8]">Notifications</span>
            <span className="text-[#F8FAFC] font-medium">{notificationCount} enabled</span>
          </div>
        </div>
        
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-[#94A3B8]">Interface</span>
            <span className="text-[#F8FAFC] font-medium">
              {settings.appearance.theme} / {settings.appearance.interfaceDensity}
            </span>
          </div>
        </div>
      </div>
      
      <div className="mt-6 pt-4 border-t border-[#1E293B]">
        <div className="flex items-center gap-2">
          {isDirty ? (
            <>
              <AlertCircle className="h-4 w-4 text-[#F59E0B]" />
              <span className="text-xs font-semibold text-[#F59E0B]">Unsaved changes exist</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="h-4 w-4 text-[#10B981]" />
              <span className="text-xs font-semibold text-[#10B981]">All changes saved</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
