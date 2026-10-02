import { ActivityEvent } from "@/types/activity-ui";
import { X, ExternalLink, Activity, Info, CheckCircle2, AlertTriangle, ShieldAlert } from "lucide-react";
import Link from "next/link";
import { useEffect } from "react";

interface Props {
  event: ActivityEvent | null;
  onClose: () => void;
}

export function ActivityDetails({ event, onClose }: Props) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape" && event) onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [event, onClose]);

  if (!event) return null;

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "INFO": return "text-[#3B82F6]";
      case "SUCCESS": return "text-[#10B981]";
      case "WARNING": return "text-[#F59E0B]";
      case "CRITICAL": return "text-[#EF4444]";
      default: return "text-[#94A3B8]";
    }
  };
  
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "INFO": return <Info className="h-4 w-4 text-[#3B82F6]" />;
      case "SUCCESS": return <CheckCircle2 className="h-4 w-4 text-[#10B981]" />;
      case "WARNING": return <AlertTriangle className="h-4 w-4 text-[#F59E0B]" />;
      case "CRITICAL": return <ShieldAlert className="h-4 w-4 text-[#EF4444]" />;
      default: return <Info className="h-4 w-4 text-[#94A3B8]" />;
    }
  };

  const getActionLink = () => {
    switch (event.type) {
      case "ANALYSIS": return { label: "View Analysis", href: "/analysis" };
      case "ARCHITECTURE": return { label: "View Architecture", href: "/architecture" };
      case "DEPENDENCY": return { label: "View Dependency Graph", href: "/graph" };
      case "GOVERNANCE": return { label: "View Governance", href: "/governance" };
      case "AI_REVIEW": return { label: "View AI Review", href: "/ai-review" };
      case "DECISION": return { label: "View Decision", href: "/decisions" };
      case "REPORT": return { label: "View Report", href: "/reports" };
      case "SETTINGS": return { label: "View Settings", href: "/settings" };
      case "PROJECT": return { label: "View Project", href: "/projects" };
      default: return null;
    }
  };

  const actionLink = getActionLink();

  return (
    <>
      <div 
        className="fixed inset-0 z-40 bg-[#080D18]/80 backdrop-blur-sm lg:hidden"
        onClick={onClose}
      />
      
      <div className="fixed inset-y-0 right-0 z-50 w-full lg:w-[400px] bg-[#0B1220] border-l border-[#1E293B] shadow-2xl flex flex-col transform transition-transform">
        <div className="flex items-center justify-between p-4 border-b border-[#1E293B]">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-[#64748B]" />
            <h2 className="text-sm font-bold text-[#F8FAFC]">Event Details</h2>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded-md transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          <div>
            <div className="flex items-center gap-2 mb-2">
              {getSeverityIcon(event.severity)}
              <span className={`text-xs font-bold ${getSeverityColor(event.severity)}`}>{event.severity}</span>
            </div>
            <h3 className="text-lg font-bold text-[#F8FAFC] mb-2">{event.title}</h3>
            <p className="text-sm text-[#CBD5E1] leading-relaxed">{event.description}</p>
          </div>
          
          <div className="grid grid-cols-2 gap-4 pt-6 border-t border-[#1E293B]">
            <div>
              <div className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider mb-1">Status</div>
              <div className="text-sm font-medium text-[#F8FAFC]">{event.status}</div>
            </div>
            <div>
              <div className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider mb-1">Type</div>
              <div className="text-sm font-medium text-[#F8FAFC]">{event.type}</div>
            </div>
            <div>
              <div className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider mb-1">Timestamp</div>
              <div className="text-sm font-medium text-[#F8FAFC]">{event.timestamp}</div>
            </div>
            <div>
              <div className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider mb-1">Actor</div>
              <div className="text-sm font-medium text-[#F8FAFC]">{event.actor.name} <span className="text-xs text-[#64748B]">({event.actor.type})</span></div>
            </div>
          </div>
          
          {(event.relatedProject || event.relatedComponent || event.relatedModule) && (
            <div className="pt-6 border-t border-[#1E293B]">
              <h4 className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-3">Related Entities</h4>
              <div className="space-y-2">
                {event.relatedProject && (
                  <div className="flex justify-between items-center bg-[#0F1726] p-2 rounded-md border border-[#1E293B]">
                    <span className="text-xs text-[#64748B]">Project</span>
                    <span className="text-xs font-medium text-[#F8FAFC]">{event.relatedProject}</span>
                  </div>
                )}
                {event.relatedComponent && (
                  <div className="flex justify-between items-center bg-[#0F1726] p-2 rounded-md border border-[#1E293B]">
                    <span className="text-xs text-[#64748B]">Component</span>
                    <span className="text-xs font-medium text-[#F8FAFC]">{event.relatedComponent}</span>
                  </div>
                )}
                {event.relatedModule && (
                  <div className="flex justify-between items-center bg-[#0F1726] p-2 rounded-md border border-[#1E293B]">
                    <span className="text-xs text-[#64748B]">Module</span>
                    <span className="text-xs font-medium text-[#F8FAFC]">{event.relatedModule}</span>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {event.metadata && Object.keys(event.metadata).length > 0 && (
            <div className="pt-6 border-t border-[#1E293B]">
              <h4 className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-3">Metadata</h4>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(event.metadata).map(([key, value]) => (
                  <div key={key} className="bg-[#0F1726] p-3 rounded-md border border-[#1E293B]">
                    <div className="text-[10px] text-[#64748B] uppercase tracking-wider mb-1">
                      {key.replace(/([A-Z])/g, ' $1').trim()}
                    </div>
                    <div className="text-sm font-medium text-[#F8FAFC]">{String(value)}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {actionLink && (
          <div className="p-4 border-t border-[#1E293B] bg-[#0F1726]">
            <Link 
              href={actionLink.href}
              className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-[#3B82F6]/10 text-[#3B82F6] hover:bg-[#3B82F6]/20 border border-[#3B82F6]/30 rounded-md text-sm font-medium transition-colors"
            >
              {actionLink.label}
              <ExternalLink className="h-4 w-4" />
            </Link>
          </div>
        )}
      </div>
    </>
  );
}


