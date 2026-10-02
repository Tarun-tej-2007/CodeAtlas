"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { Loader2 } from "lucide-react";
import { SignupSubmissionState } from "@/types/auth-ui";
import { AuthField } from "./auth-field";
import { MOCK_AUTH_CONFIG } from "@/lib/mock-data/auth";

interface Props {
  onSuccess: () => void;
}

export function ForgotPasswordForm({ onSuccess }: Props) {
  const [email, setEmail] = useState("");
  const [touched, setTouched] = useState(false);
  const [submissionState, setSubmissionState] = useState<SignupSubmissionState>("IDLE");

  const validateEmail = (val: string): string | null => {
    const trimmed = val.trim();
    if (!trimmed) return "Please enter your email address.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
      return "Please enter a valid email address.";
    }
    return null;
  };

  const emailError = touched ? validateEmail(email) : null;
  const isValid = validateEmail(email) === null;

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setTouched(true);

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
      <div className="mb-6">
        <h2 className="text-[26px] md:text-[28px] font-bold text-[#F8FAFC] mb-1 leading-tight">Forgot your password?</h2>
        <p className="text-[13px] md:text-[14px] text-[#94A3B8]">Enter your email and we&apos;ll help you reset your password.</p>
      </div>

      <AuthField
        id="email"
        label="Email address"
        type="email"
        autoComplete="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        onBlur={() => setTouched(true)}
        error={emailError}
        disabled={submissionState === "SUBMITTING"}
      />

      <button
        type="submit"
        disabled={!isValid || submissionState === "SUBMITTING"}
        className="w-full flex items-center justify-center gap-2 px-4 py-[9px] bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-md text-sm font-medium transition-colors shadow disabled:bg-[#3B82F6]/20 disabled:text-[#3B82F6]/70 disabled:shadow-none disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-[#080D18] focus-visible:ring-[#3B82F6] mt-6"
      >
        {submissionState === "SUBMITTING" && <Loader2 className="h-4 w-4 animate-spin" />}
        {submissionState === "SUBMITTING" ? "Sending..." : "Send Reset Link"}
      </button>

      <p className="mt-5 text-center text-[13px] text-[#94A3B8]">
        Remember your password?{" "}
        <Link href="/login" className="font-semibold text-[#3B82F6] hover:text-[#2563EB] transition-colors focus:outline-none focus:underline">
          Sign in
        </Link>
      </p>
    </form>
  );
}
