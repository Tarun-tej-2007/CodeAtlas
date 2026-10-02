import { ReactNode } from "react";

interface Props {
  branding: ReactNode;
  children: ReactNode;
}

export function AuthShell({ branding, children }: Props) {
  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: `html, body { height: 100%; overflow: hidden; margin: 0; padding: 0; }` }} />
      <div className="h-[100dvh] w-full flex flex-col md:flex-row bg-[#080D18] text-[#F8FAFC] overflow-hidden">
      {/* Branding Side */}
      <div className="md:w-[38%] lg:w-[38%] xl:w-[36%] shrink-0 border-b md:border-b-0 md:border-r border-[#1E293B] bg-[#0B1220] flex flex-col justify-center p-6 md:p-8 lg:p-12 relative overflow-hidden">
        {/* Subtle background element */}
        <div className="absolute inset-0 z-0 opacity-[0.03] pointer-events-none hidden md:block" style={{ backgroundImage: "linear-gradient(#3B82F6 1px, transparent 1px), linear-gradient(90deg, #3B82F6 1px, transparent 1px)", backgroundSize: "40px 40px" }} />
        <div className="relative z-10 w-full max-w-[400px] mx-auto md:mx-0">
          {branding}
        </div>
      </div>

      {/* Form Side */}
      <div className="flex-1 flex flex-col p-4 md:p-8 lg:p-12 overflow-hidden">
        <div className="flex-1 flex flex-col justify-center w-full max-w-[440px] mx-auto min-h-fit py-2 md:py-4">
          {children}
        </div>
      </div>
    </div>
    </>
  );
}
