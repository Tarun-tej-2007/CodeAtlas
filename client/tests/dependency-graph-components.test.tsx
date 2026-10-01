import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeAll } from "vitest";

// Mock ResizeObserver for React Flow
beforeAll(() => {
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
});

import { DependencyGraphHeader } from "@/components/dependency-graph/dependency-graph-header";
import { DependencyGraphToolbar } from "@/components/dependency-graph/dependency-graph-toolbar";
import { DependencyFilterPanel } from "@/components/dependency-graph/dependency-filter-panel";
import { DependencyNodeDetails } from "@/components/dependency-graph/dependency-node-details";
import { DependencyIssuesPanel } from "@/components/dependency-graph/dependency-issues-panel";
import { DependencyGraphSkeleton } from "@/components/dependency-graph/dependency-graph-skeleton";
import { DependencyGraphLegend } from "@/components/dependency-graph/dependency-graph-legend";
import { DependencyGraphCanvas } from "@/components/dependency-graph/dependency-graph-canvas";

import { MOCK_GRAPH_STATS, MOCK_GRAPH_ISSUES, MOCK_GRAPH_DATA } from "@/lib/mock-data/dependency-graph";

describe("Dependency Graph Components", () => {
  it("renders DependencyGraphHeader correctly", () => {
    render(<DependencyGraphHeader stats={MOCK_GRAPH_STATS} />);
    expect(screen.getByText("Dependency Graph")).toBeInTheDocument();
    expect(screen.getByText(MOCK_GRAPH_STATS.totalNodes.toString())).toBeInTheDocument();
    expect(screen.getByText(MOCK_GRAPH_STATS.totalEdges.toString())).toBeInTheDocument();
  });

  it("renders DependencyGraphToolbar and supports interaction", () => {
    const onSearch = vi.fn();
    const onLayout = vi.fn();
    const onZoomIn = vi.fn();
    
    render(
      <DependencyGraphToolbar 
        searchQuery="" 
        onSearchChange={onSearch} 
        layout="hierarchical" 
        onLayoutChange={onLayout}
        onZoomIn={onZoomIn}
        onZoomOut={() => {}}
        onFitView={() => {}}
        onReset={() => {}}
      />
    );
    
    expect(screen.getByPlaceholderText("Search components...")).toBeInTheDocument();
    
    fireEvent.change(screen.getByPlaceholderText("Search components..."), { target: { value: "Service" } });
    expect(onSearch).toHaveBeenCalledWith("Service");
    
    fireEvent.click(screen.getByText("force"));
    expect(onLayout).toHaveBeenCalledWith("force");
    
    // Zoom In title is "Zoom In"
    fireEvent.click(screen.getByTitle("Zoom In"));
    expect(onZoomIn).toHaveBeenCalled();
  });

  it("renders DependencyFilterPanel correctly", () => {
    const onChange = vi.fn();
    const onClear = vi.fn();
    
    render(
      <DependencyFilterPanel 
        filters={{ layer: "All", relationship: "All", risk: "All", issues: "All" }}
        onFilterChange={onChange}
        onClear={onClear}
      />
    );
    
    expect(screen.getByText("Filters")).toBeInTheDocument();
    
    fireEvent.click(screen.getByText("Clear"));
    expect(onClear).toHaveBeenCalled();
  });

  it("renders DependencyNodeDetails correctly", () => {
    const onClose = vi.fn();
    render(
      <DependencyNodeDetails 
        nodeId="ProjectService"
        data={MOCK_GRAPH_DATA}
        onClose={onClose}
      />
    );
    
    expect(screen.getByText("Node Details")).toBeInTheDocument();
    expect(screen.getByText("ProjectService")).toBeInTheDocument();
    
    // Check if relationships are displayed
    expect(screen.getByText("AnalysisService")).toBeInTheDocument();
    
    fireEvent.click(screen.getByRole("button")); // Assuming X icon is the only button
    expect(onClose).toHaveBeenCalled();
  });

  it("renders DependencyIssuesPanel correctly", () => {
    const onSelect = vi.fn();
    render(<DependencyIssuesPanel issues={MOCK_GRAPH_ISSUES} onIssueSelect={onSelect} />);
    
    expect(screen.getByText("Architecture Issues")).toBeInTheDocument();
    expect(screen.getByText("Circular dependency detected")).toBeInTheDocument();
    
    // Click the first issue
    fireEvent.click(screen.getByText("Circular dependency detected"));
    expect(onSelect).toHaveBeenCalled();
  });

  it("renders DependencyGraphLegend", () => {
    render(<DependencyGraphLegend />);
    expect(screen.getByText("Application")).toBeInTheDocument();
  });

  it("renders DependencyGraphSkeleton", () => {
    render(<DependencyGraphSkeleton />);
    expect(screen.getByTestId("dependency-graph-skeleton")).toBeInTheDocument();
  });

  it("renders DependencyGraphCanvas without crashing", () => {
    const onNodeSelect = vi.fn();
    
    render(
      <DependencyGraphCanvas 
        data={MOCK_GRAPH_DATA}
        layout="hierarchical"
        selectedNodeId={null}
        onNodeSelect={onNodeSelect}
        searchQuery=""
      />
    );
    
    // React Flow creates a div with class 'react-flow'
    const flowContainers = document.getElementsByClassName("react-flow");
    expect(flowContainers.length).toBeGreaterThan(0);
  });
});
