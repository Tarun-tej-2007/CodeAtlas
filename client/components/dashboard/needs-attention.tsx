"use client";

import { AlertTriangle, ArrowRight, ShieldAlert, AlertCircle, Info } from "lucide-react";
import { NeedsAttentionItem, IssueSeverity } from "@/types/dashboard";

interface NeedsAttentionProps {
  items: NeedsAttentionItem[];
  onViewDetails?: (item: NeedsAttentionItem) => void;
}

function getSeverityBadge(severity: IssueSeverity) {
  switch (severity) {
    case "Critical":
      return {
        badgeClass: "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20",
        icon: ShieldAlert,
      };
    case "High":
      return {
        badgeClass: "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20",
        icon: AlertTriangle,
      };
    case "Medium":
      return {
        badgeClass: "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/20",
        icon: AlertCircle,
      };
    default:
      return {
        badgeClass: "bg-[#64748B]/10 text-[#94A3B8] border-[#64748B]/20",
        icon: Info,
      };
  }
}

export function NeedsAttention({ items, onViewDetails }: NeedsAttentionProps) {
  return (
    <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4.5 shadow-xs">
      <div className="flex items-center justify-between pb-2.5 border-b border-[#1E293B]">
        <div>
          <h2 className="text-sm font-semibold tracking-tight text-[#F8FAFC]">
            Needs Attention
          </h2>
          <p className="text-xs text-[#94A3B8] mt-0.5">
            Architecture boundary & policy violations
          </p>
        </div>
        <span className="rounded bg-[#EF4444]/10 border border-[#EF4444]/20 px-2 py-0.5 text-[11px] font-mono text-[#EF4444] font-medium">
          {items.length} issues
        </span>
      </div>

      <div className="divide-y divide-[#1E293B]">
        {items.map((item) => {
          const { badgeClass, icon: Icon } = getSeverityBadge(item.severity);
          return (
            <div
              key={item.id}
              className="py-3 first:pt-3.5 last:pb-0 flex flex-col gap-1.5 group"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[10px] font-medium font-mono ${badgeClass}`}
                  >
                    <Icon className="h-3 w-3" />
                    {item.severity}
                  </span>
                  <h3 className="text-xs font-semibold text-[#F8FAFC]">
                    {item.title}
                  </h3>
                </div>

                <button
                  type="button"
                  onClick={() => onViewDetails?.(item)}
                  className="inline-flex items-center gap-1 text-[11px] font-medium text-[#3B82F6] hover:text-[#2563EB] opacity-90 group-hover:opacity-100 transition-opacity shrink-0"
                >
                  <span>View details</span>
                  <ArrowRight className="h-3 w-3" />
                </button>
              </div>

              <div className="text-xs text-[#94A3B8] font-mono pl-0.5">
                {item.explanation}
              </div>

              <div className="flex items-center gap-2 text-[11px] text-[#64748B] pl-0.5">
                <span>Affected component:</span>
                <span className="rounded bg-[#0B1220] border border-[#1E293B] px-1.5 py-0.5 font-mono text-[#CBD5E1]">
                  {item.affectedComponent}
                </span>
                {item.ruleCategory && (
                  <>
                    <span className="text-[#334155]">•</span>
                    <span className="text-[#64748B]">{item.ruleCategory}</span>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
