"use client";

import { ReactNode, useState } from "react";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

interface AppShellProps {
  children: ReactNode;
  breadcrumb?: string;
}

export function AppShell({ children, breadcrumb }: AppShellProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="h-screen w-screen overflow-hidden flex bg-[#080D18] text-[#F8FAFC]">
      {/* Sidebar: Permanently fixed 240px width (w-60), 100vh height */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* Main Content Area: Offset by sidebar width on desktop, 100vh height */}
      <div className="flex flex-1 flex-col h-screen overflow-hidden lg:pl-60 min-w-0">
        {/* Topbar: Stationary at top of main area, 56px height (h-14), shrink-0 */}
        <Topbar
          onOpenSidebar={() => setIsSidebarOpen(true)}
          breadcrumb={breadcrumb}
        />
        {/* Main scroll container: ONLY this element scrolls vertically */}
        <main
          className="flex-1 overflow-y-auto overflow-x-hidden min-h-0 w-full"
          data-testid="main-scroll-container"
        >
          <div className="px-4 py-5 sm:px-6 lg:px-8 max-w-7xl w-full mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
