"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { SignupSubmissionState, SignupFormData, SignupValidationState } from "@/types/auth-ui";
import { AuthField } from "./auth-field";
import { PasswordRequirements, REQUIREMENTS } from "./password-requirements";
import { PasswordStrengthIndicator } from "./password-strength";
import { MOCK_AUTH_CONFIG } from "@/lib/mock-data/auth";

interface Props {
  onSuccess: () => void;
}

export function SignupForm({ onSuccess }: Props) {
  const [formData, setFormData] = useState<SignupFormData>({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
    termsAccepted: false,
  });

  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [submissionState, setSubmissionState] = useState<SignupSubmissionState>("IDLE");
  const [globalError, setGlobalError] = useState<string | null>(null);
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Validation
  const validateField = (field: keyof SignupFormData): string | null => {
    const value = formData[field];
    
    if (field === "fullName") {
      const trimmed = (value as string).trim();
      if (!trimmed) return "Please enter your full name.";
      if (trimmed.length < 2) return "Name must be at least 2 characters.";
    }
    
    if (field === "email") {
      const trimmed = (value as string).trim();
      if (!trimmed) return "Please enter your email address.";
      // Basic email regex
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
        return "Enter a valid email address.";
      }
    }
    
    if (field === "password") {
      const val = value as string;
      if (!val) return "Please enter a password.";
      const isMetAll = REQUIREMENTS.every(req => req.test(val));
      if (!isMetAll) return "Password does not meet requirements.";
    }
    
    if (field === "confirmPassword") {
      if (value !== formData.password) {
        return "Passwords do not match.";
      }
    }
    
    return null;
  };

  const validationState: SignupValidationState = {
    fullNameError: touched.fullName ? validateField("fullName") : null,
    emailError: touched.email ? validateField("email") : null,
    passwordError: touched.password ? validateField("password") : null,
    confirmPasswordError: touched.confirmPassword ? validateField("confirmPassword") : null,
  };

  const isValid = 
    validateField("fullName") === null &&
    validateField("email") === null &&
    validateField("password") === null &&
    validateField("confirmPassword") === null &&
    formData.termsAccepted;

  const handleBlur = (field: keyof SignupFormData) => {
    setTouched(prev => ({ ...prev, [field]: true }));
  };

  const handleChange = (field: keyof SignupFormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (globalError) setGlobalError(null);
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    // Mark all touched
    setTouched({
      fullName: true,
      email: true,
      password: true,
      confirmPassword: true,
    });

    if (!isValid) return;

    setSubmissionState("SUBMITTING");
    setGlobalError(null);

    // Mock submission
    setTimeout(() => {
      if (formData.email.trim().toLowerCase() === MOCK_AUTH_CONFIG.existingEmail.toLowerCase()) {
        setSubmissionState("ERROR");
        setGlobalError("An account with this email already exists.");
      } else {
        setSubmissionState("SUCCESS");
        onSuccess();
      }
    }, MOCK_AUTH_CONFIG.simulatedDelayMs);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full" noValidate>
      <div className="mb-4">
        <h2 className="text-[26px] md:text-[28px] font-bold text-[#F8FAFC] mb-1 leading-tight">Create account</h2>
        <p className="text-[13px] md:text-[14px] text-[#94A3B8]">Start analyzing your codebase.</p>
      </div>

      {globalError && (
        <div className="mb-4 p-3 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-md text-sm text-[#EF4444] font-medium" role="alert">
          {globalError}
        </div>
      )}

      <AuthField
        id="fullName"
        label="Full name"
        type="text"
        autoComplete="name"
        value={formData.fullName}
        onChange={(e) => handleChange("fullName", e.target.value)}
        onBlur={() => handleBlur("fullName")}
        error={validationState.fullNameError}
        disabled={submissionState === "SUBMITTING"}
      />

      <AuthField
        id="email"
        label="Email address"
        type="email"
        autoComplete="email"
        value={formData.email}
        onChange={(e) => handleChange("email", e.target.value)}
        onBlur={() => handleBlur("email")}
        error={validationState.emailError}
        disabled={submissionState === "SUBMITTING"}
      />

      <div className="mb-2">
        <AuthField
          id="password"
          label="Password"
          type={showPassword ? "text" : "password"}
          autoComplete="new-password"
          value={formData.password}
          onChange={(e) => handleChange("password", e.target.value)}
          onBlur={() => handleBlur("password")}
          error={validationState.passwordError}
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
        <PasswordRequirements passwordValue={formData.password} />
        <PasswordStrengthIndicator passwordValue={formData.password} />
      </div>

      <AuthField
        id="confirmPassword"
        label="Confirm password"
        type={showConfirmPassword ? "text" : "password"}
        autoComplete="new-password"
        value={formData.confirmPassword}
        onChange={(e) => handleChange("confirmPassword", e.target.value)}
        onBlur={() => handleBlur("confirmPassword")}
        error={validationState.confirmPasswordError}
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

      <div className="flex items-start gap-2.5 my-4">
        <div className="flex h-5 items-center">
          <input
            id="terms"
            type="checkbox"
            checked={formData.termsAccepted}
            onChange={(e) => handleChange("termsAccepted", e.target.checked)}
            disabled={submissionState === "SUBMITTING"}
            className="h-3.5 w-3.5 rounded border-[#1E293B] bg-[#0F1726] text-[#3B82F6] focus:ring-[#3B82F6] focus:ring-offset-[#080D18]"
          />
        </div>
        <div className="text-[13px]">
          <label htmlFor="terms" className="font-medium text-[#CBD5E1]">
            I agree to the{" "}
            <Link href="#" className="text-[#3B82F6] hover:underline" onClick={(e) => e.preventDefault()}>
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link href="#" className="text-[#3B82F6] hover:underline" onClick={(e) => e.preventDefault()}>
              Privacy Policy
            </Link>.
          </label>
        </div>
      </div>

      <button
        type="submit"
        disabled={!isValid || submissionState === "SUBMITTING"}
        className="w-full flex items-center justify-center gap-2 px-4 py-[9px] bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-md text-sm font-medium transition-colors shadow disabled:bg-[#3B82F6]/20 disabled:text-[#3B82F6]/70 disabled:shadow-none disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-[#080D18] focus-visible:ring-[#3B82F6]"
      >
        {submissionState === "SUBMITTING" && <Loader2 className="h-4 w-4 animate-spin" />}
        {submissionState === "SUBMITTING" ? "Creating Account..." : "Create Account"}
      </button>

      <p className="mt-4 text-center text-[13px] text-[#94A3B8]">
        Already have an account?{" "}
        <Link href="/login" className="font-semibold text-[#3B82F6] hover:text-[#2563EB] transition-colors">
          Sign in
        </Link>
      </p>
    </form>
  );
}
