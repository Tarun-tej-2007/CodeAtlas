import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeAll } from "vitest";

// Mock ResizeObserver for React Flow
beforeAll(() => {
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
});

import { ArchitectureHeader } from "@/components/architecture/architecture-header";
import { ArchitectureOverviewMetrics } from "@/components/architecture/architecture-overview";
import { ArchitectureToolbar } from "@/components/architecture/architecture-toolbar";
import { ArchitectureBoundaries } from "@/components/architecture/architecture-boundaries";
import { ArchitectureViolations } from "@/components/architecture/architecture-violations";
import { ArchitectureHealth } from "@/components/architecture/architecture-health";
import { ArchitectureHistory } from "@/components/architecture/architecture-history";
import { ArchitectureRisks } from "@/components/architecture/architecture-risks";
import { ArchitectureComponentDetails } from "@/components/architecture/architecture-component-details";
import { ArchitectureViolationDetails } from "@/components/architecture/architecture-violation-details";
import { ArchitectureMap } from "@/components/architecture/architecture-map";

import { MOCK_ARCHITECTURE_DATA } from "@/lib/mock-data/architecture";

describe("Architecture Components", () => {
  it("renders ArchitectureHeader and handles analysis click", () => {
    const onRunAnalysis = vi.fn();
    render(
      <ArchitectureHeader 
        overview={MOCK_ARCHITECTURE_DATA.overview}
        isAnalyzing={false}
        onRunAnalysis={onRunAnalysis}
      />
    );
    expect(screen.getByText("Architecture")).toBeInTheDocument();
    expect(screen.getByText("84")).toBeInTheDocument(); // health score
    
    fireEvent.click(screen.getByText("Run Analysis"));
    expect(onRunAnalysis).toHaveBeenCalled();
  });

  it("renders ArchitectureOverviewMetrics", () => {
    render(
      <ArchitectureOverviewMetrics 
        stats={MOCK_ARCHITECTURE_DATA.stats}
        criticalViolations={2}
      />
    );
    expect(screen.getByText("Components")).toBeInTheDocument();
    expect(screen.getByText("84")).toBeInTheDocument();
    expect(screen.getByText("Critical")).toBeInTheDocument();
  });

  it("renders ArchitectureToolbar", () => {
    const onSearch = vi.fn();
    const onViewChange = vi.fn();
    render(
      <ArchitectureToolbar 
        searchQuery=""
        onSearchChange={onSearch}
        viewMode="overview"
        onViewModeChange={onViewChange}
      />
    );
    
    fireEvent.change(screen.getByPlaceholderText("Search components..."), { target: { value: "Controller" } });
    expect(onSearch).toHaveBeenCalledWith("Controller");
    
    fireEvent.click(screen.getByText("Violations"));
    expect(onViewChange).toHaveBeenCalledWith("violations");
  });

  it("renders ArchitectureBoundaries", () => {
    render(<ArchitectureBoundaries boundaries={MOCK_ARCHITECTURE_DATA.boundaries} />);
    expect(screen.getByText("Architecture Boundaries")).toBeInTheDocument();
    expect(screen.getAllByText("Presentation").length).toBeGreaterThan(0);
  });

  it("renders ArchitectureViolations", () => {
    const onSelect = vi.fn();
    render(
      <ArchitectureViolations 
        violations={MOCK_ARCHITECTURE_DATA.violations}
        onSelect={onSelect}
        selectedId={null}
      />
    );
    expect(screen.getByText("Architecture Violations")).toBeInTheDocument();
    
    fireEvent.click(screen.getByText("Domain layer directly accesses infrastructure"));
    expect(onSelect).toHaveBeenCalled();
  });

  it("renders ArchitectureHealth", () => {
    render(
      <ArchitectureHealth 
        breakdown={MOCK_ARCHITECTURE_DATA.healthBreakdown}
        overview={MOCK_ARCHITECTURE_DATA.overview}
      />
    );
    expect(screen.getByText("Health Breakdown")).toBeInTheDocument();
    expect(screen.getByText("Boundary Compliance")).toBeInTheDocument();
  });

  it("renders ArchitectureHistory", () => {
    render(<ArchitectureHistory history={MOCK_ARCHITECTURE_DATA.history} />);
    expect(screen.getByText("Architecture Evolution")).toBeInTheDocument();
    expect(screen.getByText("Oct 01")).toBeInTheDocument();
  });

  it("renders ArchitectureRisks", () => {
    render(<ArchitectureRisks risks={MOCK_ARCHITECTURE_DATA.risks} />);
    expect(screen.getByText("Architecture Risks")).toBeInTheDocument();
    expect(screen.getByText("High Coupling")).toBeInTheDocument();
  });

  it("renders ArchitectureComponentDetails", () => {
    const onClose = vi.fn();
    render(
      <ArchitectureComponentDetails 
        componentId="ProjectService"
        data={MOCK_ARCHITECTURE_DATA}
        onClose={onClose}
      />
    );
    expect(screen.getByText("Component Details")).toBeInTheDocument();
    expect(screen.getByText("ProjectService")).toBeInTheDocument();
  });

  it("renders ArchitectureViolationDetails", () => {
    const onClose = vi.fn();
    render(
      <ArchitectureViolationDetails 
        violationId="v1"
        violations={MOCK_ARCHITECTURE_DATA.violations}
        onClose={onClose}
      />
    );
    expect(screen.getByText("Violation Details")).toBeInTheDocument();
    expect(screen.getByText("ARCH-001")).toBeInTheDocument();
  });

  it("renders ArchitectureMap", () => {
    render(
      <ArchitectureMap 
        data={MOCK_ARCHITECTURE_DATA}
        searchQuery=""
        selectedComponentId={null}
        onComponentSelect={() => {}}
        selectedLayerId={null}
        onLayerSelect={() => {}}
      />
    );
    const flowContainers = document.getElementsByClassName("react-flow");
    expect(flowContainers.length).toBeGreaterThan(0);
  });
});
