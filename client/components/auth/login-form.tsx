"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { SignupSubmissionState } from "@/types/auth-ui";
import { AuthField } from "./auth-field";
import { MOCK_AUTH_CONFIG } from "@/lib/mock-data/auth";

interface Props {
  onSuccess: () => void;
}

export function LoginForm({ onSuccess }: Props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);

  const [touched, setTouched] = useState({ email: false, password: false });
  const [submissionState, setSubmissionState] = useState<SignupSubmissionState>("IDLE");
  const [globalError, setGlobalError] = useState<string | null>(null);
  
  const [showPassword, setShowPassword] = useState(false);

  const validateEmail = (val: string): string | null => {
    const trimmed = val.trim();
    if (!trimmed) return "Please enter your email address.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
      return "Please enter a valid email address.";
    }
    return null;
  };

  const validatePassword = (val: string): string | null => {
    if (!val) return "Please enter your password.";
    return null;
  };

  const emailError = touched.email ? validateEmail(email) : null;
  const passwordError = touched.password ? validatePassword(password) : null;

  const isValid = validateEmail(email) === null && validatePassword(password) === null;

  const handleBlur = (field: "email" | "password") => {
    setTouched(prev => ({ ...prev, [field]: true }));
  };

  const handleChange = (field: "email" | "password", value: string) => {
    if (field === "email") setEmail(value);
    if (field === "password") setPassword(value);
    if (globalError) setGlobalError(null);
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    setTouched({ email: true, password: true });

    if (!isValid) return;

    setSubmissionState("SUBMITTING");
    setGlobalError(null);

    // Mock submission
    setTimeout(() => {
      const emailMatch = email.trim().toLowerCase() === MOCK_AUTH_CONFIG.validLoginEmail.toLowerCase();
      const passwordMatch = password === MOCK_AUTH_CONFIG.validLoginPassword;

      if (emailMatch && passwordMatch) {
        setSubmissionState("SUCCESS");
        onSuccess();
      } else {
        setSubmissionState("ERROR");
        setGlobalError("Invalid email or password.");
        setPassword(""); // Clear password field on error
      }
    }, MOCK_AUTH_CONFIG.simulatedDelayMs);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full" noValidate>
      <div className="mb-6">
        <h2 className="text-[26px] md:text-[28px] font-bold text-[#F8FAFC] mb-1 leading-tight">Welcome back</h2>
        <p className="text-[13px] md:text-[14px] text-[#94A3B8]">Continue analyzing your codebase and architecture.</p>
      </div>

      {globalError && (
        <div className="mb-4 p-3 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-md text-[13px] md:text-sm text-[#EF4444] font-medium" role="alert">
          {globalError}
        </div>
      )}

      <AuthField
        id="email"
        label="Email address"
        type="email"
        autoComplete="email"
        value={email}
        onChange={(e) => handleChange("email", e.target.value)}
        onBlur={() => handleBlur("email")}
        error={emailError}
        disabled={submissionState === "SUBMITTING"}
      />

      <div className="mb-2">
        <AuthField
          id="password"
          label="Password"
          type={showPassword ? "text" : "password"}
          autoComplete="current-password"
          value={password}
          onChange={(e) => handleChange("password", e.target.value)}
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
      </div>

      <div className="flex items-center justify-between my-4 text-[13px]">
        <div className="flex items-center gap-2">
          <input
            id="rememberMe"
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            disabled={submissionState === "SUBMITTING"}
            className="h-3.5 w-3.5 rounded border-[#1E293B] bg-[#0F1726] text-[#3B82F6] focus:ring-[#3B82F6] focus:ring-offset-[#080D18]"
          />
          <label htmlFor="rememberMe" className="font-medium text-[#CBD5E1]">
            Remember me
          </label>
        </div>
        <Link 
          href="/forgot-password" 
          className="font-semibold text-[#3B82F6] hover:text-[#2563EB] transition-colors focus:outline-none focus:underline"
        >
          Forgot password?
        </Link>
      </div>

      <button
        type="submit"
        disabled={!isValid || submissionState === "SUBMITTING"}
        className="w-full flex items-center justify-center gap-2 px-4 py-[9px] bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-md text-sm font-medium transition-colors shadow disabled:bg-[#3B82F6]/20 disabled:text-[#3B82F6]/70 disabled:shadow-none disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-[#080D18] focus-visible:ring-[#3B82F6] mt-6"
      >
        {submissionState === "SUBMITTING" && <Loader2 className="h-4 w-4 animate-spin" />}
        {submissionState === "SUBMITTING" ? "Signing In..." : "Sign In"}
      </button>

      <p className="mt-5 text-center text-[13px] text-[#94A3B8]">
        Don&apos;t have an account?{" "}
        <Link href="/signup" className="font-semibold text-[#3B82F6] hover:text-[#2563EB] transition-colors focus:outline-none focus:underline">
          Sign up
        </Link>
      </p>
    </form>
  );
}
