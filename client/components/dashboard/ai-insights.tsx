"use client";

import { Sparkles, ArrowRight, CheckCircle, BarChart2 } from "lucide-react";
import { AIInsightItem, AIImpact } from "@/types/dashboard";

interface AIInsightsProps {
  insights: AIInsightItem[];
  onSelectInsight?: (insight: AIInsightItem) => void;
}

function getImpactBadge(impact: AIImpact) {
  switch (impact) {
    case "High":
      return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20";
    case "Medium":
      return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20";
    default:
      return "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/20";
  }
}

export function AIInsights({ insights, onSelectInsight }: AIInsightsProps) {
  return (
    <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4.5 shadow-xs">
      <div className="flex items-center justify-between pb-2.5 border-b border-[#1E293B]">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-[#3B82F6]/10 text-[#3B82F6]">
            <Sparkles className="h-3.5 w-3.5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold tracking-tight text-[#F8FAFC]">
              AI Architecture Insights
            </h2>
            <p className="text-xs text-[#94A3B8]">
              Automated structural intelligence & optimization guidance
            </p>
          </div>
        </div>
      </div>

      <div className="mt-3 space-y-3">
        {insights.map((insight) => {
          const impactClass = getImpactBadge(insight.impact);
          return (
            <div
              key={insight.id}
              className="rounded-md border border-[#1E293B] bg-[#0B1220] p-3.5 transition-colors hover:border-[#334155]"
            >
              {/* Top Row: Recommendation Header & Badges */}
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-1.5">
                <h3 className="text-xs font-semibold text-[#F8FAFC]">
                  {insight.recommendation}
                </h3>

                <div className="flex items-center gap-1.5 shrink-0">
                  <span className="inline-flex items-center gap-1 rounded bg-[#3B82F6]/10 border border-[#3B82F6]/20 px-2 py-0.5 text-[10px] font-mono text-[#3B82F6]">
                    <BarChart2 className="h-3 w-3" />
                    {insight.confidence}% Confidence
                  </span>
                  <span
                    className={`inline-flex items-center rounded border px-2 py-0.5 text-[10px] font-mono font-medium ${impactClass}`}
                  >
                    {insight.impact} Impact
                  </span>
                </div>
              </div>

              {/* Explanation */}
              <p className="mt-1.5 text-xs text-[#94A3B8] leading-relaxed">
                {insight.explanation}
              </p>

              {/* Evidence Section */}
              <div className="mt-2.5 rounded bg-[#080D18] border border-[#172235] p-2">
                <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B] mb-1">
                  Evidence
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {insight.evidence.map((ev, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 rounded bg-[#0F1726] border border-[#1E293B] px-1.5 py-0.5 text-[11px] font-mono text-[#CBD5E1]"
                    >
                      <CheckCircle className="h-3 w-3 text-[#22D3EE]" />
                      {ev}
                    </span>
                  ))}
                </div>
              </div>

              {/* Action Button */}
              <div className="mt-2.5 flex justify-end">
                <button
                  type="button"
                  onClick={() => onSelectInsight?.(insight)}
                  className="inline-flex items-center gap-1 text-xs font-medium text-[#3B82F6] hover:text-[#2563EB] transition-colors"
                >
                  <span>{insight.actionLabel}</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
