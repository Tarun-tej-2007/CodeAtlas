import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import ActivityPage from "@/app/activity/page";

describe("Activity & Audit Log Page", () => {
  it("renders header and overview metrics", () => {
    render(<ActivityPage />);
    
    // Header
    expect(screen.getAllByText("Activity & Audit Log").length).toBeGreaterThan(0);
    expect(screen.getByText("Export Activity")).toBeInTheDocument();
    
    // Overview derived from mock data (Total events: 8 + 10 + 24 = 42)
    expect(screen.getAllByText("42").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Today").length).toBeGreaterThan(0);
  });

  it("handles filtering by type", () => {
    render(<ActivityPage />);
    
    // Default search shows the review
    expect(screen.getAllByText("Comprehensive Architecture Review completed").length).toBeGreaterThan(0);
    
    // Filter by type GOVERNANCE
    const selects = screen.getAllByRole("combobox");
    const typeSelect = selects[0]; // Assuming type is first
    fireEvent.change(typeSelect, { target: { value: "GOVERNANCE" } });
    
    // The previous item should disappear
    expect(screen.queryByText("Comprehensive Architecture Review completed")).not.toBeInTheDocument();
    // Governance item should remain
    expect(screen.getAllByText("Governance compliance evaluation completed").length).toBeGreaterThan(0);
  });

  it("handles filtering by search", () => {
    render(<ActivityPage />);
    
    const searchInput = screen.getByPlaceholderText("Search events, components, projects...");
    fireEvent.change(searchInput, { target: { value: "left-pad" } });
    
    expect(screen.queryByText("Comprehensive Architecture Review completed")).not.toBeInTheDocument();
    expect(screen.getAllByText("Dependency Security check failed").length).toBeGreaterThan(0);
  });

  it("handles empty state when no results", () => {
    render(<ActivityPage />);
    
    const searchInput = screen.getByPlaceholderText("Search events, components, projects...");
    fireEvent.change(searchInput, { target: { value: "NO_MATCHING_TEXT_HERE" } });
    
    expect(screen.getByText("No activity matches the current filters.")).toBeInTheDocument();
  });

  it("opens event detail drawer on click", () => {
    render(<ActivityPage />);
    
    const firstEvent = screen.getByText("Comprehensive Architecture Review completed");
    fireEvent.click(firstEvent);
    
    // Drawer content
    expect(screen.getByText("Event Details")).toBeInTheDocument();
    
    // Metadata
    expect(screen.getByText("86")).toBeInTheDocument(); // architectureScore
    expect(screen.getAllByText("14").length).toBeGreaterThan(0); // findingsCount
    
    // Close using esc
    fireEvent.keyDown(window, { key: "Escape" });
  });

  it("opens export modal", () => {
    render(<ActivityPage />);
    
    const exportBtn = screen.getByText("Export Activity");
    fireEvent.click(exportBtn);
    
    expect(screen.getByText("Export Activity Log")).toBeInTheDocument();
    
    // Select CSV
    const csvBtn = screen.getByText("CSV");
    fireEvent.click(csvBtn);
    
    // Click Export
    const downloadBtn = screen.getByText("Download File");
    fireEvent.click(downloadBtn);
    
    expect(screen.getByText("Preparing...")).toBeInTheDocument();
  });
  
  it("renders statistics and summary correctly", () => {
    render(<ActivityPage />);
    
    expect(screen.getByText("Event Statistics")).toBeInTheDocument();
    expect(screen.getByText("AI Summary")).toBeInTheDocument();
  });
});

