import { ActivityTimelineGroup, ActivityEvent, ActivitySeverity } from "@/types/activity-ui";
import { 
  FileCode2, Boxes, Network, ShieldCheck, 
  BrainCircuit, Brain, FileText, Settings, 
  FolderOpen, Code2, AlertTriangle, CheckCircle2,
  Info, ShieldAlert, Bot
} from "lucide-react";

interface Props {
  groups: ActivityTimelineGroup[];
  selectedEventId: string | null;
  onSelect: (event: ActivityEvent) => void;
}

export function ActivityTimeline({ groups, selectedEventId, onSelect }: Props) {
  if (groups.length === 0) {
    return (
      <div className="bg-[#0F1726] border border-[#1E293B] border-dashed rounded-lg p-12 text-center">
        <p className="text-[#F8FAFC] font-medium mb-1">No activity matches the current filters.</p>
        <p className="text-sm text-[#64748B]">Try adjusting your search or clear all filters.</p>
      </div>
    );
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "ANALYSIS": return <FileCode2 className="h-4 w-4" />;
      case "ARCHITECTURE": return <Boxes className="h-4 w-4" />;
      case "DEPENDENCY": return <Network className="h-4 w-4" />;
      case "GOVERNANCE": return <ShieldCheck className="h-4 w-4" />;
      case "AI_REVIEW": return <BrainCircuit className="h-4 w-4" />;
      case "DECISION": return <Brain className="h-4 w-4" />;
      case "REPORT": return <FileText className="h-4 w-4" />;
      case "SETTINGS": return <Settings className="h-4 w-4" />;
      case "PROJECT": return <FolderOpen className="h-4 w-4" />;
      case "SYSTEM": return <Code2 className="h-4 w-4" />;
      default: return <Info className="h-4 w-4" />;
    }
  };

  const getSeverityIcon = (severity: ActivitySeverity) => {
    switch (severity) {
      case "INFO": return <Info className="h-3 w-3 text-[#3B82F6]" />;
      case "SUCCESS": return <CheckCircle2 className="h-3 w-3 text-[#10B981]" />;
      case "WARNING": return <AlertTriangle className="h-3 w-3 text-[#F59E0B]" />;
      case "CRITICAL": return <ShieldAlert className="h-3 w-3 text-[#EF4444]" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "ANALYSIS": return "text-[#3B82F6] bg-[#3B82F6]/10 border-[#3B82F6]/20";
      case "ARCHITECTURE": return "text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/20";
      case "DEPENDENCY": return "text-[#10B981] bg-[#10B981]/10 border-[#10B981]/20";
      case "GOVERNANCE": return "text-[#F43F5E] bg-[#F43F5E]/10 border-[#F43F5E]/20";
      case "AI_REVIEW": return "text-[#8B5CF6] bg-[#8B5CF6]/10 border-[#8B5CF6]/20";
      case "DECISION": return "text-[#06B6D4] bg-[#06B6D4]/10 border-[#06B6D4]/20";
      case "REPORT": return "text-[#EAB308] bg-[#EAB308]/10 border-[#EAB308]/20";
      case "SETTINGS": return "text-[#CBD5E1] bg-[#CBD5E1]/10 border-[#CBD5E1]/20";
      case "PROJECT": return "text-[#14B8A6] bg-[#14B8A6]/10 border-[#14B8A6]/20";
      case "SYSTEM": return "text-[#64748B] bg-[#64748B]/10 border-[#64748B]/20";
      default: return "text-[#64748B] bg-[#64748B]/10 border-[#64748B]/20";
    }
  };

  return (
    <div className="space-y-8">
      {groups.map((group) => (
        <div key={group.dateLabel}>
          <h3 className="text-sm font-semibold text-[#F8FAFC] uppercase tracking-wider mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#1E293B]"></span>
            {group.dateLabel}
          </h3>
          
          <div className="space-y-3 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-[#1E293B] before:to-transparent">
            {group.events.map((event) => {
              const isSelected = selectedEventId === event.id;
              
              return (
                <div 
                  key={event.id}
                  onClick={() => onSelect(event)}
                  className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group cursor-pointer transition-all ${isSelected ? "opacity-100" : "opacity-90 hover:opacity-100"}`}
                >
                  <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-[#080D18] bg-[#0F1726] shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-[0_0_0_1px_#1E293B] z-10 mx-auto absolute left-0 md:left-1/2 -translate-x-0">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center ${getTypeColor(event.type)}`}>
                      {getTypeIcon(event.type)}
                    </div>
                  </div>
                  
                  <div className={`w-[calc(100%-3rem)] md:w-[calc(50%-2rem)] p-4 rounded-xl border transition-colors ${isSelected ? "bg-[#1E293B]/50 border-[#3B82F6]" : "bg-[#0F1726] border-[#1E293B] group-hover:border-[#3B82F6]/50"}`}>
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getSeverityIcon(event.severity)}
                        <span className="text-xs font-semibold text-[#94A3B8]">{event.type.replace(/_/g, ' ')}</span>
                      </div>
                      <span className="text-xs text-[#64748B]">{event.timestamp}</span>
                    </div>
                    
                    <h4 className="text-sm font-bold text-[#F8FAFC] mb-1">{event.title}</h4>
                    <p className="text-xs text-[#94A3B8] line-clamp-2">{event.description}</p>
                    
                    <div className="flex items-center gap-4 mt-3 pt-3 border-t border-[#1E293B]/50 text-xs">
                      <div className="flex items-center gap-1.5 text-[#64748B]">
                        {event.actor.type === "USER" ? (
                          <div className="w-4 h-4 rounded-full bg-[#1E293B] flex items-center justify-center text-[8px] font-bold text-[#CBD5E1]">
                            {event.actor.name.charAt(0)}
                          </div>
                        ) : event.actor.type === "SYSTEM" ? (
                          <Code2 className="h-3 w-3" />
                        ) : event.actor.type === "AUTOMATION" ? (
                          <Bot className="h-3 w-3" />
                        ) : (
                          <Brain className="h-3 w-3" />
                        )}
                        <span>{event.actor.name}</span>
                      </div>
                      
                      <div className={`px-1.5 py-0.5 rounded text-[10px] font-semibold tracking-wider ${
                        event.status === "COMPLETED" || event.status === "RESOLVED" || event.status === "UPDATED" 
                          ? "bg-[#10B981]/10 text-[#10B981]" 
                          : event.status === "FAILED" 
                            ? "bg-[#EF4444]/10 text-[#EF4444]" 
                            : "bg-[#3B82F6]/10 text-[#3B82F6]"
                      }`}>
                        {event.status}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

