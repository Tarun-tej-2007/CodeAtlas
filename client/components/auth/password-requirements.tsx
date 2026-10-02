import { PasswordRequirement } from "@/types/auth-ui";
import { Check, X } from "lucide-react";

interface Props {
  passwordValue: string;
}

export const REQUIREMENTS: PasswordRequirement[] = [
  { id: "length", label: "At least 8 characters", test: (p) => p.length >= 8 },
  { id: "uppercase", label: "One uppercase letter", test: (p) => /[A-Z]/.test(p) },
  { id: "lowercase", label: "One lowercase letter", test: (p) => /[a-z]/.test(p) },
  { id: "number", label: "One number", test: (p) => /[0-9]/.test(p) },
  { id: "special", label: "One special character", test: (p) => /[^A-Za-z0-9]/.test(p) },
];

export function PasswordRequirements({ passwordValue }: Props) {
  // Only show validation if they started typing something
  const isPristine = passwordValue.length === 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-1 gap-x-4 mt-1 mb-2">
      {REQUIREMENTS.map((req) => {
        const isMet = req.test(passwordValue);
        return (
          <div 
            key={req.id} 
            className={`flex items-center gap-1.5 text-xs transition-colors ${
              isPristine ? "text-[#64748B]" : isMet ? "text-[#10B981]" : "text-[#94A3B8]"
            }`}
          >
            {isMet && !isPristine ? (
              <Check className="h-3 w-3 shrink-0" />
            ) : !isMet && !isPristine ? (
              <X className="h-3 w-3 shrink-0" />
            ) : (
              <div className="h-3 w-3 rounded-full border border-[#1E293B] shrink-0" />
            )}
            <span className="leading-tight">{req.label}</span>
          </div>
        );
      })}
    </div>
  );
}
