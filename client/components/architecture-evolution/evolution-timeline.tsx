import { EvolutionEvent } from "@/types/architecture-evolution-ui";
import { CircleDot, AlertTriangle, ShieldCheck, Database, LayoutTemplate } from "lucide-react";

interface EvolutionTimelineProps {
  events: EvolutionEvent[];
  onSelectEvent: (event: EvolutionEvent) => void;
  selectedEventId: string | null;
}

export function EvolutionTimeline({ events, onSelectEvent, selectedEventId }: EvolutionTimelineProps) {
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "structure": return <LayoutTemplate className="w-4 h-4" />;
      case "dependency": return <CircleDot className="w-4 h-4" />;
      case "boundary": return <Database className="w-4 h-4" />;
      case "quality": return <ShieldCheck className="w-4 h-4" />;
      case "risk": return <AlertTriangle className="w-4 h-4" />;
      default: return <CircleDot className="w-4 h-4" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "structure": return "text-[#3B82F6] bg-[#3B82F6]/10 border-[#3B82F6]/20";
      case "dependency": return "text-[#8B5CF6] bg-[#8B5CF6]/10 border-[#8B5CF6]/20";
      case "boundary": return "text-[#10B981] bg-[#10B981]/10 border-[#10B981]/20";
      case "quality": return "text-[#22C55E] bg-[#22C55E]/10 border-[#22C55E]/20";
      case "risk": return "text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/20";
      default: return "text-[#94A3B8] bg-[#94A3B8]/10 border-[#94A3B8]/20";
    }
  };

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col h-96">
      <h2 className="text-sm font-semibold text-[#F8FAFC] mb-4 shrink-0">Significant Changes Timeline</h2>
      
      <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 relative">
        <div className="absolute left-3 top-0 bottom-0 w-px bg-[#1E293B]" />
        
        <div className="flex flex-col gap-6 relative">
          {events.map((event) => {
            const isSelected = selectedEventId === event.id;
            return (
              <div 
                key={event.id} 
                className="flex gap-4 relative group cursor-pointer"
                onClick={() => onSelectEvent(event)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onSelectEvent(event); }}
              >
                <div className={`w-6 h-6 shrink-0 rounded-full flex items-center justify-center border relative z-10 transition-colors ${getCategoryColor(event.category)} ${isSelected ? 'ring-2 ring-white/20' : ''}`}>
                  {getCategoryIcon(event.category)}
                </div>
                
                <div className={`flex-1 pb-1 transition-all ${isSelected ? 'opacity-100' : 'opacity-70 group-hover:opacity-100'}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-[#F8FAFC]">{event.timestamp}</span>
                    <span className={`text-[10px] uppercase px-1.5 py-0.5 rounded border ${getCategoryColor(event.category)}`}>
                      {event.category}
                    </span>
                    {event.severity && (
                      <span className={`text-[10px] uppercase px-1.5 py-0.5 rounded border ${
                        event.severity === "Critical" ? "text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/20" :
                        event.severity === "High" ? "text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/20" :
                        "text-[#94A3B8] bg-[#94A3B8]/10 border-[#94A3B8]/20"
                      }`}>
                        {event.severity}
                      </span>
                    )}
                  </div>
                  <h3 className={`text-sm font-medium mb-1 ${isSelected ? 'text-[#3B82F6]' : 'text-[#F8FAFC]'}`}>{event.title}</h3>
                  <p className="text-xs text-[#94A3B8] line-clamp-2">{event.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
