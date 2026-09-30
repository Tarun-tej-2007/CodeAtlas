import { AppShell } from "@/components/layout/app-shell";
import { Construction } from "lucide-react";
import Link from "next/link";

interface RoutePlaceholderProps {
  title: string;
  description: string;
  sprintTarget?: string;
}

export function RoutePlaceholder({
  title,
  description,
  sprintTarget = "Sprint 31",
}: RoutePlaceholderProps) {
  return (
    <AppShell breadcrumb={title}>
      <div className="flex flex-col items-center justify-center rounded-lg border border-[#1E293B] bg-[#0F1726] p-12 text-center my-8">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#3B82F6]/10 text-[#3B82F6] mb-4">
          <Construction className="h-6 w-6" />
        </div>
        <h1 className="text-base font-semibold text-[#F8FAFC]">{title}</h1>
        <p className="mt-1 max-w-md text-xs text-[#94A3B8] leading-relaxed">
          {description}
        </p>
        <div className="mt-3 inline-flex items-center rounded-md bg-[#141E2E] border border-[#1E293B] px-2.5 py-1 text-[11px] font-mono text-[#CBD5E1]">
          Scheduled for {sprintTarget}
        </div>
        <div className="mt-6">
          <Link
            href="/dashboard"
            className="inline-flex items-center rounded-md bg-[#3B82F6] px-3.5 py-1.5 text-xs font-medium text-white hover:bg-[#2563EB] transition-colors"
          >
            Return to Dashboard
          </Link>
        </div>
      </div>
    </AppShell>
  );
}
