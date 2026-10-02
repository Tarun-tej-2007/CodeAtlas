import { CheckCircle2 } from "lucide-react";
import Link from "next/link";

export function AuthSuccess() {
  return (
    <div className="flex flex-col items-center justify-center text-center py-8">
      <div className="h-16 w-16 bg-[#10B981]/10 rounded-full flex items-center justify-center mb-6 border border-[#10B981]/20">
        <CheckCircle2 className="h-8 w-8 text-[#10B981]" />
      </div>
      
      <h2 className="text-2xl font-bold text-[#F8FAFC] mb-2">Account Created</h2>
      <p className="text-[#94A3B8] text-sm mb-8 max-w-sm">
        Your CodeAtlas account has been created successfully. You can now sign in to start analyzing your codebase.
      </p>
      
      <div className="flex flex-col gap-3 w-full max-w-xs">
        <Link 
          href="/login"
          className="flex items-center justify-center w-full px-4 py-2.5 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-md text-sm font-medium transition-colors shadow"
        >
          Continue to Login
        </Link>
        
        <button 
          onClick={() => window.location.reload()}
          className="flex items-center justify-center w-full px-4 py-2.5 bg-[#0F1726] border border-[#1E293B] hover:bg-[#1E293B] text-[#CBD5E1] hover:text-[#F8FAFC] rounded-md text-sm font-medium transition-colors"
        >
          Back to Signup
        </button>
      </div>
    </div>
  );
}
