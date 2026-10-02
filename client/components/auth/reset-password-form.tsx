"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { SignupSubmissionState } from "@/types/auth-ui";
import { AuthField } from "./auth-field";
import { PasswordRequirements, REQUIREMENTS } from "./password-requirements";
import { PasswordStrengthIndicator } from "./password-strength";
import { MOCK_AUTH_CONFIG } from "@/lib/mock-data/auth";

interface Props {
  onSuccess: () => void;
}

export function ResetPasswordForm({ onSuccess }: Props) {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  
  const [touched, setTouched] = useState({ password: false, confirmPassword: false });
  const [submissionState, setSubmissionState] = useState<SignupSubmissionState>("IDLE");
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const validatePassword = (val: string): string | null => {
    if (!val) return "Please enter a new password.";
    const allRequirementsMet = REQUIREMENTS.every(req => req.test(val));
    if (!allRequirementsMet) return "Password does not meet all requirements.";
    return null;
  };

  const validateConfirmPassword = (val: string, currentPassword: string): string | null => {
    if (!val) return "Please confirm your password.";
    if (val !== currentPassword) return "Passwords do not match.";
    return null;
  };

  const passwordError = touched.password ? validatePassword(password) : null;
  const confirmPasswordError = touched.confirmPassword ? validateConfirmPassword(confirmPassword, password) : null;

  const isValid = validatePassword(password) === null && validateConfirmPassword(confirmPassword, password) === null;

  const handleBlur = (field: "password" | "confirmPassword") => {
    setTouched(prev => ({ ...prev, [field]: true }));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setTouched({ password: true, confirmPassword: true });

    if (!isValid) return;

    setSubmissionState("SUBMITTING");

    // Mock submission
    setTimeout(() => {
      setSubmissionState("SUCCESS");
      onSuccess();
    }, MOCK_AUTH_CONFIG.simulatedDelayMs);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full" noValidate>
      <div className="mb-4">
        <h2 className="text-[26px] md:text-[28px] font-bold text-[#F8FAFC] mb-1 leading-tight">Reset your password</h2>
        <p className="text-[13px] md:text-[14px] text-[#94A3B8]">Create a new password for your CodeAtlas account.</p>
      </div>

      <div className="mb-2">
        <AuthField
          id="password"
          label="New password"
          type={showPassword ? "text" : "password"}
          autoComplete="new-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onBlur={() => handleBlur("password")}
          error={passwordError}
          disabled={submissionState === "SUBMITTING"}
          rightElement={
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? "Hide password" : "Show password"}
              className="p-1 hover:text-[#F8FAFC] transition-colors focus:outline-none rounded"
              disabled={submissionState === "SUBMITTING"}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          }
        />
        <PasswordRequirements passwordValue={password} />
        <PasswordStrengthIndicator passwordValue={password} />
      </div>

      <AuthField
        id="confirmPassword"
        label="Confirm password"
        type={showConfirmPassword ? "text" : "password"}
        autoComplete="new-password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        onBlur={() => handleBlur("confirmPassword")}
        error={confirmPasswordError}
        disabled={submissionState === "SUBMITTING"}
        rightElement={
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            aria-label={showConfirmPassword ? "Hide password" : "Show password"}
            className="p-1 hover:text-[#F8FAFC] transition-colors focus:outline-none rounded"
            disabled={submissionState === "SUBMITTING"}
          >
            {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        }
      />

      <button
        type="submit"
        disabled={!isValid || submissionState === "SUBMITTING"}
        className="w-full flex items-center justify-center gap-2 px-4 py-[9px] bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-md text-sm font-medium transition-colors shadow disabled:bg-[#3B82F6]/20 disabled:text-[#3B82F6]/70 disabled:shadow-none disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-[#080D18] focus-visible:ring-[#3B82F6] mt-6"
      >
        {submissionState === "SUBMITTING" && <Loader2 className="h-4 w-4 animate-spin" />}
        {submissionState === "SUBMITTING" ? "Resetting Password..." : "Reset Password"}
      </button>

      <p className="mt-5 text-center text-[13px] text-[#94A3B8]">
        <Link href="/login" className="font-semibold text-[#3B82F6] hover:text-[#2563EB] transition-colors focus:outline-none focus:underline">
          Back to Login
        </Link>
      </p>
    </form>
  );
}
