"use client";

import { useState } from "react";
import { AuthShell } from "@/components/auth/auth-shell";
import { AuthBranding } from "@/components/auth/auth-branding";
import { SignupForm } from "@/components/auth/signup-form";
import { AuthSuccess } from "@/components/auth/auth-success";

export default function SignupPage() {
  const [success, setSuccess] = useState(false);

  return (
    <AuthShell branding={<AuthBranding />}>
      {success ? (
        <AuthSuccess />
      ) : (
        <SignupForm onSuccess={() => setSuccess(true)} />
      )}
    </AuthShell>
  );
}
