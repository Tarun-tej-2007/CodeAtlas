import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import GovernancePage from "@/app/governance/page";

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

describe("Governance Page", () => {
  it("renders the governance page header and overview", () => {
    render(<GovernancePage />);
    expect(screen.getAllByText("Governance").length).toBeGreaterThan(0);
    expect(screen.getByText("Monitor architectural policies, engineering standards, and compliance across your codebase.")).toBeInTheDocument();
    
    // Overview metrics
    expect(screen.getAllByText("87")[0]).toBeInTheDocument(); // Health Score
    expect(screen.getAllByText("91%")[0]).toBeInTheDocument(); // Compliance
    expect(screen.getAllByText("12")[0]).toBeInTheDocument(); // Policies
    expect(screen.getAllByText("23").length).toBeGreaterThan(0); // Open Violations
    expect(screen.getAllByText("2").length).toBeGreaterThan(0); // Critical
  });

  it("renders the policy list and filters work", () => {
    render(<GovernancePage />);
    
    // Initial render shows policies
    expect(screen.getAllByText("Architecture Layering")[0]).toBeInTheDocument();
    expect(screen.getAllByText("Domain Isolation")[0]).toBeInTheDocument();

    // Change category filter
    const categorySelect = screen.getAllByRole("combobox")[0]; // the first select is for policy categories
    fireEvent.change(categorySelect, { target: { value: "Security" } });

    // Should show only security
    expect(screen.getAllByText("Security Baseline")[0]).toBeInTheDocument();
    // The text 'Architecture Layering' is still in the violation filters select option
    expect(screen.getAllByText("Architecture Layering").length).toBe(1);

    // Clear filters
    const clearBtn = screen.getAllByText("Clear")[0];
    fireEvent.click(clearBtn);
    expect(screen.getAllByText("Architecture Layering")[0]).toBeInTheDocument();
  });

  it("opens policy details drawer", () => {
    render(<GovernancePage />);
    expect(screen.queryByText("Policy Details")).not.toBeInTheDocument();
    
    const policyRow = screen.getAllByText("Architecture Layering")[0];
    fireEvent.click(policyRow);
    
    expect(screen.getByText("Policy Details")).toBeInTheDocument();
    expect(screen.getByText("Enforce correct boundaries between Domain, Application, and Infrastructure layers.")).toBeInTheDocument();
  });

  it("renders violations and status filter works", () => {
    render(<GovernancePage />);
    expect(screen.getByText("Domain directly accesses PostgreSQLRepository")).toBeInTheDocument();

    // Change status filter to Resolved
    // violation status is the 4th select on the page (index 4)
    const statusSelect = screen.getAllByRole("combobox")[4]; 
    fireEvent.change(statusSelect, { target: { value: "Resolved" } });
    
    // The open violation should be gone
    expect(screen.queryByText("Domain directly accesses PostgreSQLRepository")).not.toBeInTheDocument();
    expect(screen.getAllByText("Resolved security violation").length).toBeGreaterThan(0);
  });

  it("opens violation details drawer and mark resolved works", () => {
    render(<GovernancePage />);
    
    // Click violation
    const violationRow = screen.getAllByText("Controller bypasses application service")[0];
    fireEvent.click(violationRow);
    
    expect(screen.getByText("Violation Details")).toBeInTheDocument();
    
    // Mark Resolved
    const resolveBtn = screen.getByText("Mark Resolved");
    fireEvent.click(resolveBtn);
    
    // Drawer should close and open violations should decrease
    expect(screen.queryByText("Violation Details")).not.toBeInTheDocument();
    
    // By default violations filter is "Open", so the resolved one should no longer be in the list
    expect(screen.queryByText("Controller bypasses application service")).not.toBeInTheDocument();
  });

  it("opens request exception modal", () => {
    render(<GovernancePage />);
    
    const violationRow = screen.getByText("Circular dependency detected");
    fireEvent.click(violationRow);
    
    const requestBtn = screen.getByText("Request Exception");
    fireEvent.click(requestBtn);
    
    expect(screen.getByText("Request Governance Exception")).toBeInTheDocument();
    expect(screen.getByText("Submit Request")).toBeInTheDocument();
  });

  it("submits request exception correctly", () => {
    render(<GovernancePage />);
    const violationRow = screen.getByText("Service exceeds dependency threshold");
    fireEvent.click(violationRow);
    fireEvent.click(screen.getByText("Request Exception"));
    
    const reasonInput = screen.getByPlaceholderText(/Explain why this exception is needed/i);
    fireEvent.change(reasonInput, { target: { value: "Test exception reason" } });
    
    const submitBtn = screen.getByText("Submit Request");
    fireEvent.click(submitBtn);
    
    // Modal and Drawer close
    expect(screen.queryByText("Request Governance Exception")).not.toBeInTheDocument();
    expect(screen.queryByText("Violation Details")).not.toBeInTheDocument();
    
    // Exception appears in active exceptions
    expect(screen.getByText("Test exception reason")).toBeInTheDocument();
  });

  it("renders category compliance progress bars", () => {
    render(<GovernancePage />);
    expect(screen.getByText("Category Compliance")).toBeInTheDocument();
    expect(screen.getAllByText("88%")[0]).toBeInTheDocument(); // Architecture
    expect(screen.getAllByText("96%")[0]).toBeInTheDocument(); // Security
  });

  it("renders trend chart", () => {
    render(<GovernancePage />);
    expect(screen.getByText("Compliance Trend")).toBeInTheDocument();
    expect(screen.getByTestId("line-chart")).toBeInTheDocument();
  });

  it("renders activity timeline", () => {
    render(<GovernancePage />);
    expect(screen.getByText("Governance Activity")).toBeInTheDocument();
    expect(screen.getByText("Dependency Direction policy updated")).toBeInTheDocument();
  });

  it("renders governance summary", () => {
    render(<GovernancePage />);
    expect(screen.getByText("Governance Summary")).toBeInTheDocument();
    expect(screen.getAllByText("91%").length).toBeGreaterThan(0);
    expect(screen.getAllByText("2").length).toBeGreaterThan(0);
  });

  it("handles settings modal", () => {
    render(<GovernancePage />);
    // There isn't text on the button, but there's a settings icon. We can click the second button in the header.
    const buttons = screen.getAllByRole("button");
    const settingsBtn = buttons.find(b => b.innerHTML.includes("lucide-settings"));
    if (settingsBtn) {
      fireEvent.click(settingsBtn);
      expect(screen.getByText("Governance Settings")).toBeInTheDocument();
      expect(screen.getByText("Evaluation Frequency")).toBeInTheDocument();
      
      fireEvent.click(screen.getByText("Cancel"));
      expect(screen.queryByText("Governance Settings")).not.toBeInTheDocument();
    }
  });

  it("handles run compliance check mock state", async () => {
    render(<GovernancePage />);
    const runBtn = screen.getByText("Run Compliance Check");
    fireEvent.click(runBtn);
    
    expect(screen.getByText("Running Check...")).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText("Run Compliance Check")).toBeInTheDocument();
      expect(screen.getAllByText("Governance check completed (Compliance: 91%)")[0]).toBeInTheDocument(); // Appears in activity timeline
    }, { timeout: 3500 });
  });
});
