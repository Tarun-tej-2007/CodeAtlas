"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FolderOpen,
  FileCode2,
  Network,
  Boxes,
  TrendingUp,
  ShieldCheck,
  BrainCircuit,
  Sparkles,
  FileText,
  Settings,
  X,
  Hexagon,
  Activity,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  disabled?: boolean;
  badge?: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const NAV_SECTIONS: NavSection[] = [
  {
    title: "OVERVIEW",
    items: [
      { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
      { name: "Projects", href: "/projects", icon: FolderOpen },
    ],
  },
  {
    title: "ANALYSIS",
    items: [
      { name: "Repository Analysis", href: "/analysis", icon: FileCode2 },
      { name: "Dependency Graph", href: "/graph", icon: Network },
      { name: "Architecture", href: "/architecture", icon: Boxes },
      { name: "Architecture Evolution", href: "/evolution", icon: TrendingUp },
    ],
  },
  {
    title: "INTELLIGENCE",
    items: [
      { name: "Governance", href: "/governance", icon: ShieldCheck },
      { name: "Decision Intelligence", href: "/decisions", icon: BrainCircuit },
      { name: "AI Architecture Review", href: "/ai-review", icon: Sparkles },
    ],
  },
  {
    title: "OUTPUT",
    items: [{ name: "Reports", href: "/reports", icon: FileText }],
  },
  {
    title: "SYSTEM",
    items: [
      { name: "Activity", href: "/activity", icon: Activity },
      { name: "Settings", href: "/settings", icon: Settings }
    ],
  },
];

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile overlay backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-xs lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Permanently fixed sidebar on desktop, off-canvas drawer on mobile */}
      <aside
        className={cn(
          "fixed top-0 bottom-0 left-0 z-50 flex h-screen w-60 flex-col bg-[#0B1220] border-r border-[#1E293B] transition-transform duration-200 ease-in-out lg:translate-x-0 lg:z-30",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Brand Header */}
        <div className="flex h-14 shrink-0 items-center justify-between px-5 border-b border-[#1E293B]">
          <Link
            href="/dashboard"
            className="flex items-center gap-2.5 text-sm font-semibold tracking-wider text-[#F8FAFC] group"
          >
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-[#3B82F6]/10 border border-[#3B82F6]/30 text-[#3B82F6] transition-colors group-hover:bg-[#3B82F6]/20">
              <Hexagon className="h-4 w-4 stroke-[2.2]" />
            </div>
            <span className="font-mono text-sm tracking-wider font-bold text-[#F8FAFC]">
              CODE<span className="text-[#3B82F6]">ATLAS</span>
            </span>
          </Link>
          {onClose && (
            <button
              onClick={onClose}
              className="lg:hidden p-1 rounded text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#141E2E]"
              aria-label="Close navigation"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Navigation Item Groups - Independently scrollable if needed */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {NAV_SECTIONS.map((section) => (
            <div key={section.title} className="space-y-1">
              <div className="px-2.5 pb-1 text-[10px] font-semibold tracking-wider text-[#64748B] uppercase font-mono">
                {section.title}
              </div>
              <div className="space-y-0.5">
                {section.items.map((item) => {
                  const isActive =
                    pathname === item.href ||
                    (item.href === "/dashboard" && pathname === "/");
                  const Icon = item.icon;

                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      onClick={onClose}
                      className={cn(
                        "group flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors",
                        isActive
                          ? "bg-[#3B82F6]/10 text-[#3B82F6] font-semibold"
                          : "text-[#94A3B8] hover:bg-[#141E2E] hover:text-[#CBD5E1]"
                      )}
                    >
                      <Icon
                        className={cn(
                          "h-4 w-4 transition-colors shrink-0",
                          isActive
                            ? "text-[#3B82F6]"
                            : "text-[#64748B] group-hover:text-[#94A3B8]"
                        )}
                      />
                      <span className="truncate">{item.name}</span>
                      {item.badge && (
                        <span className="ml-auto rounded bg-[#1E293B] px-1.5 py-0.5 text-[9px] font-mono text-[#94A3B8]">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Workspace info footer */}
        <div className="p-3 shrink-0 border-t border-[#1E293B] bg-[#080D18]/50">
          <div className="flex items-center gap-2.5 rounded-md px-2 py-1.5 text-xs text-[#94A3B8]">
            <div className="h-2 w-2 rounded-full bg-[#22C55E]" />
            <div className="flex flex-col min-w-0">
              <span className="text-[11px] font-medium text-[#CBD5E1] truncate font-mono">
                Sprint 30 Core
              </span>
              <span className="text-[10px] text-[#64748B] font-mono">Engine v1.0.0</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
