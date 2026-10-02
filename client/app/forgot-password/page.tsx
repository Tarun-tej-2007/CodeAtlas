"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AuthShell } from "@/components/auth/auth-shell";
import { AuthBranding } from "@/components/auth/auth-branding";
import { ForgotPasswordForm } from "@/components/auth/forgot-password-form";
import { MailCheck } from "lucide-react";

function ForgotPasswordSuccess() {
  const router = useRouter();
  
  return (
    <div className="flex flex-col items-center justify-center text-center py-8">
      <div className="h-16 w-16 bg-[#10B981]/10 rounded-full flex items-center justify-center mb-6 border border-[#10B981]/20">
        <MailCheck className="h-8 w-8 text-[#10B981]" />
      </div>
      
      <h2 className="text-[26px] md:text-[28px] font-bold text-[#F8FAFC] mb-2 leading-tight">Check your email</h2>
      <p className="text-[13px] md:text-[14px] text-[#94A3B8] max-w-sm mb-6">
        Reset link request submitted. If this were production, a reset link would be sent to your email.
      </p>
      
      <div className="flex flex-col gap-3 w-full max-w-xs mt-4">
        <button 
          onClick={() => router.push("/reset-password")}
          className="w-full flex items-center justify-center gap-2 px-4 py-[9px] bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-md text-sm font-medium transition-colors shadow focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-[#080D18] focus-visible:ring-[#3B82F6]"
        >
          Continue to Reset Password
        </button>
        
        <button 
          onClick={() => router.push("/login")}
          className="w-full flex items-center justify-center gap-2 px-4 py-[9px] bg-[#0F1726] border border-[#1E293B] hover:bg-[#1E293B] text-[#CBD5E1] hover:text-[#F8FAFC] rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-[#080D18] focus-visible:ring-[#3B82F6]"
        >
          Back to Login
        </button>
      </div>
    </div>
  );
}

export default function ForgotPasswordPage() {
  const [success, setSuccess] = useState(false);

  return (
    <AuthShell branding={<AuthBranding />}>
      {success ? (
        <ForgotPasswordSuccess />
      ) : (
        <ForgotPasswordForm onSuccess={() => setSuccess(true)} />
      )}
    </AuthShell>
  );
}
