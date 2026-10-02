import { PasswordStrength } from "@/types/auth-ui";
import { REQUIREMENTS } from "./password-requirements";

interface Props {
  passwordValue: string;
}

export function PasswordStrengthIndicator({ passwordValue }: Props) {
  if (passwordValue.length === 0) return null;

  const metCount = REQUIREMENTS.filter(req => req.test(passwordValue)).length;
  
  let strength: PasswordStrength = "WEAK";
  let colorClass = "bg-[#EF4444]"; // Weak
  let label = "Weak";

  if (metCount === REQUIREMENTS.length) {
    strength = "STRONG";
    colorClass = "bg-[#10B981]";
    label = "Strong";
  } else if (metCount >= 3) {
    strength = "FAIR";
    colorClass = "bg-[#F59E0B]";
    label = "Fair";
  }

  return (
    <div className="flex items-center gap-2 mb-2">
      <div className="flex-1 flex gap-1 h-1.5">
        <div className={`flex-1 rounded-l-full transition-colors ${passwordValue.length > 0 ? colorClass : "bg-[#1E293B]"}`} />
        <div className={`flex-1 transition-colors ${strength === "FAIR" || strength === "STRONG" ? colorClass : "bg-[#1E293B]"}`} />
        <div className={`flex-1 rounded-r-full transition-colors ${strength === "STRONG" ? colorClass : "bg-[#1E293B]"}`} />
      </div>
      <span className="text-[10px] font-semibold tracking-wider uppercase text-[#94A3B8] w-12 text-right">
        {label}
      </span>
    </div>
  );
}
