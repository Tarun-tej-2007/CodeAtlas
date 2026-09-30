import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { AppShell } from "@/components/layout/app-shell";

describe("AppShell Component", () => {
  it("renders sidebar navigation groups and branding", () => {
    render(
      <AppShell breadcrumb="Dashboard">
        <div data-testid="test-child">Child Content</div>
      </AppShell>
    );

    // Verify brand
    expect(screen.getByText("ATLAS")).toBeInTheDocument();

    // Verify sections
    expect(screen.getByText("OVERVIEW")).toBeInTheDocument();
    expect(screen.getByText("ANALYSIS")).toBeInTheDocument();
    expect(screen.getByText("INTELLIGENCE")).toBeInTheDocument();
    expect(screen.getByText("OUTPUT")).toBeInTheDocument();
    expect(screen.getByText("SYSTEM")).toBeInTheDocument();

    // Verify nav links
    expect(screen.getAllByText("Dashboard").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Projects")).toBeInTheDocument();
    expect(screen.getByText("Repository Analysis")).toBeInTheDocument();
    expect(screen.getByText("Dependency Graph")).toBeInTheDocument();
    expect(screen.getByText("Architecture Evolution")).toBeInTheDocument();
    expect(screen.getByText("Governance")).toBeInTheDocument();
    expect(screen.getByText("Decision Intelligence")).toBeInTheDocument();
    expect(screen.getByText("AI Architecture Review")).toBeInTheDocument();
    expect(screen.getByText("Reports")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();

    // Verify child content
    expect(screen.getByTestId("test-child")).toBeInTheDocument();
  });

  it("renders topbar search and breadcrumb", () => {
    render(
      <AppShell breadcrumb="Architecture Overview">
        <div>Content</div>
      </AppShell>
    );

    expect(screen.getByPlaceholderText("Search anything...")).toBeInTheDocument();
    expect(screen.getByText("Architecture Overview")).toBeInTheDocument();
  });

  it("isolates vertical scroll strictly to the main content container", () => {
    render(
      <AppShell breadcrumb="Dashboard">
        <div>Scrollable Content</div>
      </AppShell>
    );

    const mainContainer = screen.getByTestId("main-scroll-container");
    expect(mainContainer).toBeInTheDocument();
    expect(mainContainer).toHaveClass("overflow-y-auto");
    expect(mainContainer).toHaveClass("flex-1");
  });
});
