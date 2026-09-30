import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { AppQueryProvider } from "@/lib/query/providers";
import { ProjectResponse } from "@/types/project";

const mockProjects: ProjectResponse[] = [
  {
    id: "proj-101",
    owner_id: "user-1",
    name: "CodeAtlas Core",
    slug: "codeatlas-core",
    description: "Core intelligence engine",
    visibility: "private",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

describe("DashboardHeader Component", () => {
  it("renders header title and Run Analysis button", () => {
    render(
      <AppQueryProvider>
        <DashboardHeader
          lastAnalysisTimestamp="12m ago"
          projects={mockProjects}
        />
      </AppQueryProvider>
    );

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(
      screen.getByText("Architecture intelligence across your projects.")
    ).toBeInTheDocument();
    expect(screen.getByText("12m ago")).toBeInTheDocument();
    expect(screen.getByText("Run analysis")).toBeInTheDocument();
  });

  it("handles Run Analysis button click", () => {
    render(
      <AppQueryProvider>
        <DashboardHeader
          lastAnalysisTimestamp="5m ago"
          projects={mockProjects}
        />
      </AppQueryProvider>
    );

    const button = screen.getByText("Run analysis");
    expect(button).toBeInTheDocument();
    fireEvent.click(button);
  });
});
