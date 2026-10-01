import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import AIReviewPage from "@/app/ai-review/page";

// Mock matchMedia for Recharts (if used inside dependencies)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

describe("AI Architecture Review Page", () => {
  it("renders header and top-level metrics", () => {
    render(<AIReviewPage />);
    expect(screen.getAllByText("AI Architecture Review").length).toBeGreaterThan(0);
    
    // Overview metrics
    expect(screen.getAllByText("86 / 100").length).toBeGreaterThan(0); // Score
    expect(screen.getByText("93%")).toBeInTheDocument(); // Confidence
    expect(screen.getByText("14")).toBeInTheDocument(); // Findings
    expect(screen.getAllByText("1").length).toBeGreaterThan(0); // Critical
    expect(screen.getAllByText("3").length).toBeGreaterThan(0); // High
    expect(screen.getByText("9")).toBeInTheDocument(); // Recommendations
  });

  it("renders architecture score breakdown", () => {
    render(<AIReviewPage />);
    expect(screen.getByText("Score Breakdown")).toBeInTheDocument();
    expect(screen.getAllByText("Architecture").length).toBeGreaterThan(0);
    expect(screen.getAllByText("91%").length).toBeGreaterThan(0);
  });

  it("renders AI review summary", () => {
    render(<AIReviewPage />);
    expect(screen.getByText("AI Review Summary")).toBeInTheDocument();
    expect(screen.getByText("Strengths")).toBeInTheDocument();
    expect(screen.getByText("Concerns")).toBeInTheDocument();
  });

  it("renders findings list and handles filter", () => {
    render(<AIReviewPage />);
    
    // Should see findings
    expect(screen.getByText("Cross-Layer Dependency Detected")).toBeInTheDocument();
    
    // Filter to critical
    const severitySelect = screen.getAllByRole("combobox")[0]; // first is severity
    fireEvent.change(severitySelect, { target: { value: "CRITICAL" } });
    
    // Cross-Layer is HIGH, so it should disappear
    expect(screen.queryByText("Cross-Layer Dependency Detected")).not.toBeInTheDocument();
    
    // Circular Dependency is CRITICAL, so it should stay
    expect(screen.getByText("Circular Dependency Cluster")).toBeInTheDocument();
  });

  it("renders empty state when filters match nothing", () => {
    render(<AIReviewPage />);
    
    // Status filter
    const statusSelect = screen.getAllByRole("combobox")[2];
    fireEvent.change(statusSelect, { target: { value: "DISMISSED" } });
    
    expect(screen.getByText("No findings match the current filters.")).toBeInTheDocument();
  });

  it("opens finding drawer and handles status mutation", () => {
    render(<AIReviewPage />);
    
    // Click finding
    fireEvent.click(screen.getByText("Cross-Layer Dependency Detected"));
    
    // Drawer should open
    expect(screen.getByText("Why This Matters")).toBeInTheDocument();
    
    // Change status
    const ackBtn = screen.getByText("Acknowledge");
    fireEvent.click(ackBtn);
    
    // Should update status to ACKNOWLEDGED
    expect(screen.getAllByText("ACKNOWLEDGED").length).toBeGreaterThan(0);
    
    // Close via Esc
    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.queryByText("Why This Matters")).not.toBeInTheDocument();
  });

  it("opens recommendation drawer", () => {
    render(<AIReviewPage />);
    
    fireEvent.click(screen.getByText("Introduce Repository Abstraction"));
    
    expect(screen.getByText("Architecture Recommendation")).toBeInTheDocument();
    expect(screen.getByText("The Problem")).toBeInTheDocument();
    
    fireEvent.keyDown(window, { key: "Escape" });
  });

  it("renders strengths, evidence, and history", () => {
    render(<AIReviewPage />);
    
    expect(screen.getByText("Architecture Strengths")).toBeInTheDocument();
    expect(screen.getByText("Strong Layer Separation")).toBeInTheDocument();
    
    expect(screen.getByText("Supporting Evidence")).toBeInTheDocument();
    
    expect(screen.getAllByText("Review History").length).toBeGreaterThan(0);
  });

  it("handles AI review runner flow", async () => {
    render(<AIReviewPage />);
    
    const runBtn = screen.getByText("Run Architecture Review");
    fireEvent.click(runBtn);
    
    // Should show modal
    expect(screen.getAllByText("Loading Architecture Snapshot").length).toBeGreaterThan(0);
    
    // Let's just wait for a short bit. We won't wait for all 8 seconds to save test time.
    await waitFor(() => {
      expect(screen.getByText("Analyzing Components")).toBeInTheDocument();
    }, { timeout: 1500 });
  });
});
