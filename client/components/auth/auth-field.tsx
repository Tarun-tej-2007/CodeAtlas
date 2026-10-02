import { InputHTMLAttributes, forwardRef } from "react";
import { AlertCircle } from "lucide-react";

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string | null;
  rightElement?: React.ReactNode;
}

export const AuthField = forwardRef<HTMLInputElement, Props>(
  ({ label, error, rightElement, className = "", id, ...props }, ref) => {
    return (
      <div className="space-y-1 mb-3">
        <label htmlFor={id} className="block text-[13px] font-semibold text-[#CBD5E1]">
          {label}
        </label>
        <div className="relative">
          <input
            id={id}
            ref={ref}
            className={`w-full bg-[#0F1726] border rounded-md px-3 py-[7px] text-[14px] text-[#F8FAFC] placeholder:text-[#64748B] transition-colors focus:outline-none focus:ring-1 ${
              error 
                ? "border-[#EF4444] focus:border-[#EF4444] focus:ring-[#EF4444]" 
                : "border-[#1E293B] focus:border-[#3B82F6] focus:ring-[#3B82F6]"
            } ${rightElement ? "pr-10" : ""} ${className}`}
            aria-invalid={!!error}
            aria-describedby={error ? `${id}-error` : undefined}
            {...props}
          />
          {rightElement && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-[#64748B]">
              {rightElement}
            </div>
          )}
        </div>
        {error && (
          <div className="flex items-start gap-1.5 mt-1 text-[#EF4444]" id={`${id}-error`}>
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
            <p className="text-xs font-medium">{error}</p>
          </div>
        )}
      </div>
    );
  }
);
AuthField.displayName = "AuthField";
