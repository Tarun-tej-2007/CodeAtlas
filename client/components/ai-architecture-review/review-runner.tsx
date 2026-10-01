import { Sparkles, Check, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

export type RunnerState = 
  | "IDLE"
  | "LOADING_SNAPSHOT"
  | "ANALYZING_COMPONENTS"
  | "ANALYZING_DEPENDENCIES"
  | "EVALUATING_BOUNDARIES"
  | "EVALUATING_SECURITY"
  | "EVALUATING_MAINTAINABILITY"
  | "GENERATING_FINDINGS"
  | "GENERATING_RECOMMENDATIONS"
  | "COMPLETE";

const RUNNER_STEPS = [
  { state: "LOADING_SNAPSHOT", label: "Loading Architecture Snapshot", duration: 800 },
  { state: "ANALYZING_COMPONENTS", label: "Analyzing Components", duration: 1200 },
  { state: "ANALYZING_DEPENDENCIES", label: "Analyzing Dependencies", duration: 1500 },
  { state: "EVALUATING_BOUNDARIES", label: "Evaluating Boundaries", duration: 1000 },
  { state: "EVALUATING_SECURITY", label: "Evaluating Security", duration: 900 },
  { state: "EVALUATING_MAINTAINABILITY", label: "Evaluating Maintainability", duration: 800 },
  { state: "GENERATING_FINDINGS", label: "Generating Findings", duration: 1200 },
  { state: "GENERATING_RECOMMENDATIONS", label: "Generating Recommendations", duration: 1000 },
];

interface ReviewRunnerProps {
  isRunning: boolean;
  onComplete: () => void;
}

export function ReviewRunner({ isRunning, onComplete }: ReviewRunnerProps) {
  const [currentState, setCurrentState] = useState<RunnerState>("IDLE");
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isRunning) {
      const t = setTimeout(() => {
        setCurrentState("IDLE");
        setProgress(0);
      }, 0);
      return () => clearTimeout(t);
    }

    let isCancelled = false;
    
    const runSequence = async () => {
      let currentProgress = 0;
      const progressIncrement = 100 / RUNNER_STEPS.length;

      for (const step of RUNNER_STEPS) {
        if (isCancelled) break;
        
        setCurrentState(step.state as RunnerState);
        
        // Wait for the simulated duration
        await new Promise(resolve => setTimeout(resolve, step.duration));
        
        if (!isCancelled) {
          currentProgress += progressIncrement;
          setProgress(currentProgress);
        }
      }

      if (!isCancelled) {
        setCurrentState("COMPLETE");
        setProgress(100);
        setTimeout(() => {
          if (!isCancelled) onComplete();
        }, 800);
      }
    };

    runSequence();

    return () => {
      isCancelled = true;
    };
  }, [isRunning, onComplete]);

  if (!isRunning && currentState === "IDLE") return null;

  return (
    <>
      <div className="fixed inset-0 z-50 bg-[#080D18]/80 backdrop-blur-sm flex items-center justify-center">
        <div className="bg-[#0B1220] border border-[#1E293B] shadow-2xl rounded-lg p-8 max-w-md w-full mx-4">
          <div className="flex flex-col items-center text-center mb-6">
            <div className="h-16 w-16 bg-[#3B82F6]/10 rounded-full flex items-center justify-center mb-4 border border-[#3B82F6]/20 relative">
              {currentState === "COMPLETE" ? (
                <Check className="h-8 w-8 text-[#10B981]" />
              ) : (
                <>
                  <Sparkles className="h-8 w-8 text-[#3B82F6] animate-pulse" />
                  <Loader2 className="absolute -right-2 -bottom-2 h-6 w-6 text-[#64748B] animate-spin" />
                </>
              )}
            </div>
            <h2 className="text-xl font-bold text-[#F8FAFC]">
              {currentState === "COMPLETE" ? "Review Complete" : "AI Architecture Review"}
            </h2>
            <p className="text-sm text-[#94A3B8] mt-2">
              {currentState === "COMPLETE" 
                ? "Architecture analysis finished successfully." 
                : "Analyzing repository structure, dependencies, and boundaries..."}
            </p>
          </div>

          <div className="w-full bg-[#1E293B] rounded-full h-2 mb-6 overflow-hidden">
            <div 
              className="bg-[#3B82F6] h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>

          <div className="space-y-3">
            {RUNNER_STEPS.map((step, index) => {
              const stepIndex = RUNNER_STEPS.findIndex(s => s.state === currentState);
              const isPast = currentState === "COMPLETE" || index < stepIndex;
              const isCurrent = currentState === step.state;
              

              return (
                <div 
                  key={step.state} 
                  className={`flex items-center gap-3 text-sm transition-opacity duration-300 ${
                    isPast ? "text-[#10B981]" : isCurrent ? "text-[#F8FAFC]" : "text-[#64748B] opacity-50"
                  }`}
                >
                  <div className="w-5 flex justify-center">
                    {isPast ? (
                      <Check className="h-4 w-4" />
                    ) : isCurrent ? (
                      <Loader2 className="h-4 w-4 animate-spin text-[#3B82F6]" />
                    ) : (
                      <div className="h-1.5 w-1.5 rounded-full bg-[#64748B]" />
                    )}
                  </div>
                  <span className={isCurrent ? "font-medium" : ""}>{step.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </>
  );
}
