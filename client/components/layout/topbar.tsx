"use client";

import { useState } from "react";
import { Search, Bell, HelpCircle, Menu, ChevronRight } from "lucide-react";

interface TopbarProps {
  onOpenSidebar?: () => void;
  breadcrumb?: string;
}

export function Topbar({ onOpenSidebar, breadcrumb = "Dashboard" }: TopbarProps) {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <header className="shrink-0 flex h-14 w-full items-center justify-between border-b border-[#1E293B] bg-[#0B1220]/95 px-4 backdrop-blur-xs sm:px-6 z-20">
      {/* Left side: Hamburger + Breadcrumb */}
      <div className="flex items-center gap-3">
        {onOpenSidebar && (
          <button
            onClick={onOpenSidebar}
            className="lg:hidden p-1.5 rounded-md text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#141E2E]"
            aria-label="Open navigation menu"
          >
            <Menu className="h-5 w-5" />
          </button>
        )}

        <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-xs">
          <span className="text-[#64748B] hover:text-[#94A3B8] transition-colors">Workspace</span>
          <ChevronRight className="h-3 w-3 text-[#64748B]" />
          <span className="font-medium text-[#F8FAFC]">{breadcrumb}</span>
        </nav>
      </div>

      {/* Right side: Search, Notifications, Help, User */}
      <div className="flex items-center gap-3">
        {/* Global Search Bar */}
        <div className="relative hidden md:block w-64 lg:w-72">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[#64748B]" />
          <input
            type="text"
            placeholder="Search anything..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-md border border-[#1E293B] bg-[#0F1726] py-1.5 pl-8 pr-12 text-xs text-[#F8FAFC] placeholder-[#64748B] focus:border-[#3B82F6] focus:outline-hidden transition-colors"
          />
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-0.5 rounded border border-[#1E293B] bg-[#141E2E] px-1.5 py-0.5 text-[10px] font-mono text-[#94A3B8]">
            <span>⌘</span>
            <span>K</span>
          </div>
        </div>

        {/* Action icons */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            className="relative rounded-md p-1.5 text-[#94A3B8] hover:bg-[#141E2E] hover:text-[#F8FAFC] transition-colors"
            aria-label="View notifications"
          >
            <Bell className="h-4 w-4" />
            <span className="absolute top-1 right-1 h-1.5 w-1.5 rounded-full bg-[#3B82F6]" />
          </button>

          <button
            type="button"
            className="rounded-md p-1.5 text-[#94A3B8] hover:bg-[#141E2E] hover:text-[#F8FAFC] transition-colors"
            aria-label="Documentation and help"
          >
            <HelpCircle className="h-4 w-4" />
          </button>
        </div>

        {/* Divider */}
        <div className="h-4 w-px bg-[#1E293B]" />

        {/* User Profile avatar */}
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-[#141E2E] border border-[#1E293B] text-xs font-mono font-medium text-[#F8FAFC]">
            CA
          </div>
          <div className="hidden xl:flex flex-col text-left">
            <span className="text-xs font-medium text-[#F8FAFC] leading-none">Engineering</span>
            <span className="text-[10px] text-[#64748B] font-mono leading-none mt-1">team@codeatlas.dev</span>
          </div>
        </div>
      </div>
    </header>
  );
}
