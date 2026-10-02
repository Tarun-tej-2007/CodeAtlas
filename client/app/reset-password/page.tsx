"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AuthShell } from "@/components/auth/auth-shell";
import { AuthBranding } from "@/components/auth/auth-branding";
import { ResetPasswordForm } from "@/components/auth/reset-password-form";
import { CheckCircle2 } from "lucide-react";

function ResetPasswordSuccess() {
  const router = useRouter();
  
  return (
    <div className="flex flex-col items-center justify-center text-center py-8">
      <div className="h-16 w-16 bg-[#10B981]/10 rounded-full flex items-center justify-center mb-6 border border-[#10B981]/20">
        <CheckCircle2 className="h-8 w-8 text-[#10B981]" />
      </div>
      
      <h2 className="text-[26px] md:text-[28px] font-bold text-[#F8FAFC] mb-2 leading-tight">Password reset successfully</h2>
      <p className="text-[13px] md:text-[14px] text-[#94A3B8] max-w-sm mb-6">
        Your password has been updated in this demo flow.
      </p>
      
      <div className="flex flex-col gap-3 w-full max-w-xs mt-4">
        <button 
          onClick={() => router.push("/login")}
          className="w-full flex items-center justify-center gap-2 px-4 py-[9px] bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-md text-sm font-medium transition-colors shadow focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-[#080D18] focus-visible:ring-[#3B82F6]"
        >
          Continue to Login
        </button>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  const [success, setSuccess] = useState(false);

  return (
    <AuthShell branding={<AuthBranding />}>
      {success ? (
        <ResetPasswordSuccess />
      ) : (
        <ResetPasswordForm onSuccess={() => setSuccess(true)} />
      )}
    </AuthShell>
  );
}
