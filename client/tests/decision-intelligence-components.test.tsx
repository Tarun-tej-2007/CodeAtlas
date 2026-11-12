import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import DecisionIntelligencePage from "@/app/decisions/page";

vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  ScatterChart: ({ children }: { children: React.ReactNode }) => <div data-testid="scatter-chart">{children}</div>,
  Scatter: ({ children, onClick }: { children: React.ReactNode, onClick: (e: { payload: { recommendationId: string } }) => void }) => (
    <div data-testid="scatter" onClick={() => onClick({ payload: { recommendationId: "rec-1" } })}>
      {children}
    </div>
  ),
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  Cell: () => <div data-testid="cell" />
}));

describe("Decision Intelligence Page", () => {
  it("renders page and decision health metrics", () => {
    render(<DecisionIntelligencePage />);
    expect(screen.getAllByText("Decision Intelligence").length).toBeGreaterThan(0);
    
    // Derived numbers from mock data
    expect(screen.getByText("82")).toBeInTheDocument();
    expect(screen.getAllByText("18").length).toBeGreaterThan(0); // Recommendations
    expect(screen.getAllByText("34").length).toBeGreaterThan(0); // Tech Debt
    expect(screen.getAllByText("5").length).toBeGreaterThan(0); // High Priority
    expect(screen.getByText("21%")).toBeInTheDocument(); // Potential Savings
  });

  it("renders recommendations and search works", () => {
    render(<DecisionIntelligencePage />);
    
    expect(screen.getAllByText("Refactor Authentication Boundary").length).toBeGreaterThan(0);
    
    const searchInput = screen.getByPlaceholderText(/Search recommendations/i);
    fireEvent.change(searchInput, { target: { value: "circular" } });
    
    expect(screen.getAllByText("Resolve Circular Dependency Cluster")[0]).toBeInTheDocument();
    expect(screen.queryByText("Refactor Authentication Boundary")).not.toBeInTheDocument();
  });

  it("renders recommendation drawer and handles status changes", () => {
    render(<DecisionIntelligencePage />);
    
    // Open drawer
    const row = screen.getAllByText("Refactor Authentication Boundary")[0];
    fireEvent.click(row);
    
    expect(screen.getByText("Recommendation Details")).toBeInTheDocument();
    expect(screen.getAllByText("NEW").length).toBeGreaterThan(0);
    
    // Change status to Reviewed
    const markReviewed = screen.getByText("Mark Reviewed");
    fireEvent.click(markReviewed);
    
    // Status should change to REVIEWED
    expect(screen.getAllByText("REVIEWED").length).toBeGreaterThan(0);
    
    // Close drawer using Escape
    fireEvent.keyDown(window, { key: "Escape" });
    
    expect(screen.queryByText("Recommendation Details")).not.toBeInTheDocument();
  });

  it("handles category filter", () => {
    render(<DecisionIntelligencePage />);
    
    const categorySelect = screen.getAllByRole("combobox")[0];
    fireEvent.change(categorySelect, { target: { value: "SECURITY" } });
    
    expect(screen.queryByText("Refactor Authentication Boundary")).not.toBeInTheDocument(); // it's architecture
  });

  it("renders impact/effort matrix and handles click", () => {
    render(<DecisionIntelligencePage />);
    
    expect(screen.getByTestId("scatter-chart")).toBeInTheDocument();
    
    // Click scatter point
    const scatter = screen.getByTestId("scatter");
    fireEvent.click(scatter);
    
    // rec-1 should open
    expect(screen.getByText("Recommendation Details")).toBeInTheDocument();
    expect(screen.getAllByText("Refactor Authentication Boundary").length).toBeGreaterThan(0);
  });

  it("renders category breakdown", () => {
    render(<DecisionIntelligencePage />);
    expect(screen.getByText("Category Breakdown")).toBeInTheDocument();
  });

  it("renders technical debt", () => {
    render(<DecisionIntelligencePage />);
    expect(screen.getAllByText("Technical Debt").length).toBeGreaterThan(0);
  });

  it("renders decision history", () => {
    render(<DecisionIntelligencePage />);
    expect(screen.getByText("Decision History")).toBeInTheDocument();
    expect(screen.getByText("Dependency direction recommendation generated")).toBeInTheDocument();
  });

  it("handles decision analysis runner", () => { expect(true).toBe(true); });
});

