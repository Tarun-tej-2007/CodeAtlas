import { EvolutionEvent } from "@/types/architecture-evolution-ui";
import { X, Calendar, LayoutTemplate, AlertTriangle, ArrowRight, Layers, Box } from "lucide-react";
import Link from "next/link";

interface EvolutionChangeDetailsProps {
  event: EvolutionEvent;
  onClose: () => void;
}

export function EvolutionChangeDetails({ event, onClose }: EvolutionChangeDetailsProps) {
  return (
    <div className="flex flex-col h-full bg-[#0F1726] border-l border-[#1E293B] w-80 shrink-0">
      <div className="flex items-center justify-between p-4 border-b border-[#1E293B]">
        <h2 className="text-sm font-semibold text-[#F8FAFC]">Event Details</h2>
        <button 
          onClick={onClose}
          className="p-1 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 flex flex-col gap-6">
        <div>
          <h3 className="text-lg font-semibold text-[#F8FAFC] mb-2">{event.title}</h3>
          <p className="text-sm text-[#94A3B8] leading-relaxed">{event.description}</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Date</span>
            <div className="flex items-center gap-2 text-sm text-[#F8FAFC]">
              <Calendar className="w-4 h-4 text-[#3B82F6]" />
              {event.timestamp}
            </div>
          </div>
          <div>
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Category</span>
            <div className="flex items-center gap-2 text-sm text-[#F8FAFC]">
              <LayoutTemplate className="w-4 h-4 text-[#8B5CF6]" />
              <span className="capitalize">{event.category}</span>
            </div>
          </div>
          {event.severity && (
            <div>
              <span className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Severity</span>
              <div className="flex items-center gap-2 text-sm text-[#F8FAFC]">
                <AlertTriangle className={`w-4 h-4 ${
                  event.severity === "Critical" ? "text-[#EF4444]" :
                  event.severity === "High" ? "text-[#F59E0B]" :
                  "text-[#22C55E]"
                }`} />
                {event.severity}
              </div>
            </div>
          )}
        </div>

        {event.affectedComponents.length > 0 && (
          <div>
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-2 block">Affected Components</span>
            <div className="flex flex-col gap-2">
              {event.affectedComponents.map(comp => (
                <div key={comp} className="flex items-center gap-2 bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2">
                  <Box className="w-4 h-4 text-[#94A3B8]" />
                  <span className="text-sm text-[#CBD5E1]">{comp}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {event.changes.length > 0 && (
          <div>
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-2 block">Detailed Changes</span>
            <div className="flex flex-col gap-3">
              {event.changes.map(change => (
                <div key={change.id} className="bg-[#080D18] border border-[#1E293B] rounded-md p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-[#F8FAFC]">{change.title}</span>
                    <span className="text-[10px] uppercase text-[#94A3B8] px-1.5 py-0.5 rounded border border-[#1E293B] bg-[#0F1726]">
                      {change.type.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-xs text-[#94A3B8]">{change.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-auto pt-4 flex flex-col gap-2">
          <Link href="/architecture" className="flex items-center justify-center gap-2 w-full py-2 bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] text-sm font-medium rounded-lg transition-colors">
            <Layers className="w-4 h-4" /> View Architecture
          </Link>
          <Link href="/graph" className="flex items-center justify-center gap-2 w-full py-2 bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] text-sm font-medium rounded-lg transition-colors">
            <ArrowRight className="w-4 h-4" /> View Dependency Graph
          </Link>
        </div>
      </div>
    </div>
  );
}
