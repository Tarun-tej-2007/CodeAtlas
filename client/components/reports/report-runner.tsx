import { Loader2, Check, FileText } from "lucide-react";
import { useEffect, useState } from "react";

const GENERATION_STEPS = [
  { id: "ready", label: "Ready", duration: 500 },
  { id: "collecting", label: "Collecting Analysis Data", duration: 800 },
  { id: "building", label: "Building Report Sections", duration: 1000 },
  { id: "calculating", label: "Calculating Metrics", duration: 700 },
  { id: "compiling", label: "Compiling Findings", duration: 900 },
  { id: "recommendations", label: "Generating Recommendations", duration: 1000 },
  { id: "formatting", label: "Formatting Report", duration: 800 },
];

interface ReportRunnerProps {
  isRunning: boolean;
  onComplete: () => void;
}

export function ReportRunner({ isRunning, onComplete }: ReportRunnerProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(-1);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isRunning) {
      const t = setTimeout(() => {
        setCurrentStepIndex(-1);
        setProgress(0);
      }, 0);
      return () => clearTimeout(t);
    }

    let isCancelled = false;
    let currentProgress = 0;
    const progressIncrement = 100 / GENERATION_STEPS.length;

    const runSequence = async () => {
      for (let i = 0; i < GENERATION_STEPS.length; i++) {
        if (isCancelled) break;
        
        setCurrentStepIndex(i);
        await new Promise(resolve => setTimeout(resolve, GENERATION_STEPS[i].duration));
        
        if (!isCancelled) {
          currentProgress += progressIncrement;
          setProgress(currentProgress);
        }
      }

      if (!isCancelled) {
        setCurrentStepIndex(GENERATION_STEPS.length); // Complete
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

  if (!isRunning && currentStepIndex === -1) return null;

  const isComplete = currentStepIndex === GENERATION_STEPS.length;

  return (
    <>
      <div className="fixed inset-0 z-50 bg-[#080D18]/80 backdrop-blur-sm flex items-center justify-center">
        <div className="bg-[#0B1220] border border-[#1E293B] shadow-2xl rounded-lg p-8 max-w-md w-full mx-4">
          <div className="flex flex-col items-center text-center mb-6">
            <div className="h-16 w-16 bg-[#3B82F6]/10 rounded-full flex items-center justify-center mb-4 border border-[#3B82F6]/20 relative">
              {isComplete ? (
                <Check className="h-8 w-8 text-[#10B981]" />
              ) : (
                <>
                  <FileText className="h-8 w-8 text-[#3B82F6] animate-pulse" />
                  <Loader2 className="absolute -right-2 -bottom-2 h-6 w-6 text-[#64748B] animate-spin" />
                </>
              )}
            </div>
            <h2 className="text-xl font-bold text-[#F8FAFC]">
              {isComplete ? "Generation Complete" : "Generating Report"}
            </h2>
          </div>

          <div className="w-full bg-[#1E293B] rounded-full h-2 mb-6 overflow-hidden">
            <div 
              className="bg-[#3B82F6] h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>

          <div className="space-y-3">
            {GENERATION_STEPS.map((step, index) => {
              const isPast = isComplete || index < currentStepIndex;
              const isCurrent = index === currentStepIndex;

              return (
                <div 
                  key={step.id} 
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
