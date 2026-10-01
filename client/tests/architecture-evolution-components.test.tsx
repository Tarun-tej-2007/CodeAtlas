import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import EvolutionPage from "@/app/evolution/page";
import { MOCK_EVOLUTION_DATA } from "@/lib/mock-data/architecture-evolution";

// Mock Recharts
vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  LineChart: ({ children }: { children: React.ReactNode }) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />
}));

describe("Architecture Evolution Page", () => {
  it("renders the page and header correctly", () => {
    render(<EvolutionPage />);
    expect(screen.getAllByText("Architecture Evolution").length).toBeGreaterThan(0);
    expect(screen.getByText("Track structural changes, architectural drift, and system health across analysis history.")).toBeInTheDocument();
  });

  it("renders overview metrics with correct latest snapshot data", () => {
    render(<EvolutionPage />);
    expect(screen.getByText("84 / 100")).toBeInTheDocument(); // Current Health
    expect(screen.getAllByText("Low").length).toBeGreaterThan(0); // Current Drift label in header
  });

  it("renders trend chart and time range selector", () => {
    render(<EvolutionPage />);
    expect(screen.getByText("Architecture Trend")).toBeInTheDocument();
    expect(screen.getByTestId("line-chart")).toBeInTheDocument();
    
    // Time range buttons
    expect(screen.getByText("7D")).toBeInTheDocument();
    expect(screen.getByText("30D")).toBeInTheDocument();
    expect(screen.getByText("90D")).toBeInTheDocument();
    expect(screen.getByText("1Y")).toBeInTheDocument();
    
    // Metric toggles
    expect(screen.getByLabelText("Health")).toBeInTheDocument();
    expect(screen.getByLabelText("Drift")).toBeInTheDocument();
    expect(screen.getByLabelText("Violations")).toBeInTheDocument();
  });

  it("filters update appropriately", () => {
    render(<EvolutionPage />);
    // There are 6 events in mock data
    const timelineEventsBeforeFilter = screen.getAllByRole("button", { name: /ProjectService refactored|New ArchitectureService introduced|Circular dependency detected|Boundary violation resolved|RepositoryScanner added/i });
    
    const categorySelect = screen.getAllByRole("combobox")[2]; // Assuming first two are snapshot selectors
    fireEvent.change(categorySelect, { target: { value: "Structure" } });
    
    // Now only structure events should be shown. "ProjectService refactored", "New ArchitectureService introduced", "RepositoryScanner added"
    expect(screen.getByText("ProjectService refactored")).toBeInTheDocument();
    expect(screen.queryByText("Circular dependency detected")).not.toBeInTheDocument();
  });

  it("opens change detail drawer when timeline event is clicked", () => {
    render(<EvolutionPage />);
    
    // Ensure drawer is not open
    expect(screen.queryByText("Event Details")).not.toBeInTheDocument();
    
    // Click an event
    const eventElement = screen.getByText("ProjectService refactored");
    fireEvent.click(eventElement);
    
    expect(screen.getByText("Event Details")).toBeInTheDocument();
  });

  it("renders comparison section", () => {
    render(<EvolutionPage />);
    expect(screen.getByText("Before / After Comparison")).toBeInTheDocument();
    expect(screen.getByText("Added Components")).toBeInTheDocument();
    expect(screen.getByText("Removed Components")).toBeInTheDocument();
    expect(screen.getByText("Resolved Violations")).toBeInTheDocument();
    expect(screen.getByText("New Violations")).toBeInTheDocument();
  });

  it("renders drift breakdown section", () => {
    render(<EvolutionPage />);
    expect(screen.getAllByText("Architecture Drift").length).toBeGreaterThan(0);
    expect(screen.getByText("Boundary Drift")).toBeInTheDocument();
    expect(screen.getByText("Dependency Drift")).toBeInTheDocument();
    expect(screen.getByText("Structural Drift")).toBeInTheDocument();
    expect(screen.getByText("Coupling Drift")).toBeInTheDocument();
  });

  it("renders risk trend section", () => {
    render(<EvolutionPage />);
    expect(screen.getByText("Risk Trend")).toBeInTheDocument();
    expect(screen.getAllByText("Critical").length).toBeGreaterThan(0);
    expect(screen.getAllByText("High").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Medium").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Low").length).toBeGreaterThan(0);
  });

  it("handles run analysis mock state", async () => {
    render(<EvolutionPage />);
    const runBtn = screen.getByText("Run Analysis");
    fireEvent.click(runBtn);
    
    expect(screen.getByText("Analyzing...")).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText("Run Analysis")).toBeInTheDocument();
    }, { timeout: 2500 });
  });
});
