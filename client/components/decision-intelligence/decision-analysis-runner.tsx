import { DecisionAnalysisState } from "@/types/decision-intelligence-ui";
import { Check, Loader2 } from "lucide-react";

interface DecisionAnalysisRunnerProps {
  state: DecisionAnalysisState;
  isVisible: boolean;
}

export function DecisionAnalysisRunner({ state, isVisible }: DecisionAnalysisRunnerProps) {
  if (!isVisible) return null;

  const steps: DecisionAnalysisState[] = [
    "Analyzing Architecture",
    "Analyzing Dependencies",
    "Analyzing Governance",
    "Analyzing Technical Debt",
    "Calculating Impact",
    "Generating Recommendations",
  ];

  const currentIndex = steps.indexOf(state);
  const isComplete = state === "Complete";

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-[#080D18]/80 backdrop-blur-sm transition-opacity">
      <div className="w-full max-w-md bg-[#0F1726] border border-[#1E293B] shadow-2xl rounded-xl p-6">
        <h2 className="text-lg font-bold text-[#F8FAFC] mb-6">Running Decision Analysis</h2>
        
        <div className="space-y-4">
          {steps.map((step, i) => {
            const isPast = currentIndex > i || isComplete;
            const isCurrent = currentIndex === i && !isComplete;
            
            return (
              <div key={step} className={`flex items-center gap-3 transition-opacity duration-300 ${isPast || isCurrent ? "opacity-100" : "opacity-40"}`}>
                <div className={`flex h-6 w-6 items-center justify-center rounded-full border ${isPast ? "bg-[#10B981]/20 border-[#10B981]/30 text-[#10B981]" : isCurrent ? "bg-[#3B82F6]/20 border-[#3B82F6]/30 text-[#3B82F6]" : "border-[#334155] text-[#64748B]"}`}>
                  {isPast ? <Check className="h-3.5 w-3.5" /> : isCurrent ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <div className="h-1.5 w-1.5 rounded-full bg-[#64748B]" />}
                </div>
                <span className={`text-sm font-medium ${isPast ? "text-[#CBD5E1]" : isCurrent ? "text-[#F8FAFC]" : "text-[#64748B]"}`}>
                  {step}
                </span>
              </div>
            );
          })}
        </div>
        
        {isComplete && (
          <div className="mt-8 p-3 rounded bg-[#10B981]/10 border border-[#10B981]/20 flex items-center justify-center text-[#10B981] text-sm font-medium">
            Analysis Complete
          </div>
        )}
      </div>
    </div>
  );
}
