import { Hexagon } from "lucide-react";

export function AuthBranding() {
  return (
    <div className="flex flex-col">
      <div className="flex items-center gap-3 mb-2 md:mb-6">
        <div className="flex h-8 w-8 md:h-10 md:w-10 items-center justify-center rounded-lg bg-[#3B82F6]/10 border border-[#3B82F6]/30 text-[#3B82F6]">
          <Hexagon className="h-5 w-5 md:h-6 md:w-6 stroke-[2.2]" />
        </div>
        <span className="font-mono text-lg md:text-xl tracking-wider font-bold text-[#F8FAFC]">
          CODE<span className="text-[#3B82F6]">ATLAS</span>
        </span>
      </div>
      
      <div className="space-y-2 md:space-y-4">
        <h1 className="text-lg md:text-3xl font-bold tracking-tight text-[#F8FAFC] hidden md:block">
          Architecture intelligence for modern engineering.
        </h1>
        <p className="text-[#94A3B8] leading-relaxed text-sm md:text-base hidden md:block">
          Start analyzing your codebase, discovering dependencies, and governing architectural integrity.
        </p>
      </div>
    </div>
  );
}
