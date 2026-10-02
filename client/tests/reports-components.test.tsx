import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import ReportsPage from "@/app/reports/page";

describe("Reports Page", () => {
  it("renders header and overview metrics", () => {
    render(<ReportsPage />);
    expect(screen.getAllByText("Reports").length).toBeGreaterThan(0);
    
    // Overview metrics
    expect(screen.getByText("12")).toBeInTheDocument(); // Total Reports
    expect(screen.getByText("10")).toBeInTheDocument(); // Completed
    expect(screen.getByText("1")).toBeInTheDocument(); // In Progress
    expect(screen.getByText("86 / 100")).toBeInTheDocument(); // Latest Score
    expect(screen.getAllByText("94%").length).toBeGreaterThan(0); // Coverage
  });

  it("renders report list and handles filtering", () => {
    render(<ReportsPage />);
    
    // Should see initial reports
    expect(screen.getAllByText("Comprehensive Architecture Review").length).toBeGreaterThan(0);
    expect(screen.getByText("Dependency Analysis Report")).toBeInTheDocument();
    
    // Filter by type
    const typeSelect = screen.getAllByRole("combobox")[0]; // First is type filter
    fireEvent.change(typeSelect, { target: { value: "DEPENDENCY" } });
    
    // Comprehensive should disappear
    expect(screen.queryByText("Comprehensive Architecture Review")).not.toBeInTheDocument();
    
    // Dependency should stay
    expect(screen.getByText("Dependency Analysis Report")).toBeInTheDocument();
  });

  it("handles empty state when no reports match", () => {
    render(<ReportsPage />);
    
    const typeSelect = screen.getAllByRole("combobox")[0];
    fireEvent.change(typeSelect, { target: { value: "DECISION" } });
    
    const formatSelect = screen.getAllByRole("combobox")[2];
    fireEvent.change(formatSelect, { target: { value: "JSON" } });
    
    // No Decision report with JSON format
    expect(screen.getByText("No reports found")).toBeInTheDocument();
  });

  it("opens report detail drawer", () => {
    render(<ReportsPage />);
    
    // Find title and click it (we use getAllByText because it's also in summary)
    const titles = screen.getAllByText("Comprehensive Architecture Review");
    fireEvent.click(titles[titles.length - 1]); // the one in the list
    
    // Wait for drawer (it should show "Summary" and "Key Recommendations" which are in the drawer)
    expect(screen.getAllByText("Summary").length).toBeGreaterThan(0);
    expect(screen.getByText("Key Recommendations")).toBeInTheDocument();
    
    // Close via Esc
    fireEvent.keyDown(window, { key: "Escape" });
  });

  it("opens report preview modal", () => {
    render(<ReportsPage />);
    
    const titles = screen.getAllByText("Comprehensive Architecture Review");
    fireEvent.click(titles[titles.length - 1]); 
    
    const previewBtn = screen.getByText("Preview");
    fireEvent.click(previewBtn);
    
    expect(screen.getByText("PREVIEW")).toBeInTheDocument();
    expect(screen.getByText("Executive Summary")).toBeInTheDocument();
    expect(screen.getByText("Action Plan")).toBeInTheDocument();
    
    fireEvent.keyDown(window, { key: "Escape" });
  });

  it("opens generator modal and starts generation", () => {
    render(<ReportsPage />);
    
    const generateBtn = screen.getByText("Generate Report");
    fireEvent.click(generateBtn);
    
    expect(screen.getByText("Configure and run a new CodeAtlas analysis report.")).toBeInTheDocument();
    
    const startBtn = screen.getByText("Generate");
    fireEvent.click(startBtn);
    
    // Should show generating modal
    expect(screen.getByText("Generating Report")).toBeInTheDocument();
  });

  it("opens settings modal", () => {
    render(<ReportsPage />);
    
    const settingsBtn = screen.getByLabelText("Report Settings");
    fireEvent.click(settingsBtn);
    
    expect(screen.getByText("Report Retention")).toBeInTheDocument();
    expect(screen.getByText("Save Settings")).toBeInTheDocument();
    
    fireEvent.keyDown(window, { key: "Escape" });
  });
});
