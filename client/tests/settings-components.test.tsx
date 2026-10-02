import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import SettingsPage from "@/app/settings/page";

describe("Settings Page", () => {
  it("renders header and summary", () => {
    render(<SettingsPage />);
    expect(screen.getAllByText("Settings").length).toBeGreaterThan(0);
    expect(screen.getByText("Configured")).toBeInTheDocument();
    expect(screen.getByText("Settings Summary")).toBeInTheDocument();
  });

  it("navigates between sections", () => {
    render(<SettingsPage />);
    
    // Default is General
    expect(screen.getByText("Workspace Information")).toBeInTheDocument();
    
    // Click Analysis
    const analysisTab = screen.getAllByText("Analysis")[0];
    fireEvent.click(analysisTab);
    
    expect(screen.getByText("Analysis Depth")).toBeInTheDocument();
    expect(screen.queryByText("Workspace Information")).not.toBeInTheDocument();
  });

  it("marks page as dirty when a setting is changed", () => {
    render(<SettingsPage />);
    
    // Should be configured initially
    expect(screen.getByText("Configured")).toBeInTheDocument();
    
    // Change workspace name
    const input = screen.getByDisplayValue("CodeAtlas Workspace");
    fireEvent.change(input, { target: { value: "New Workspace Name" } });
    
    // Should now be dirty
    expect(screen.getByText("Unsaved changes")).toBeInTheDocument();
    expect(screen.getByText("Unsaved changes exist")).toBeInTheDocument();
    
    // Save
    const saveBtn = screen.getByText("Save Changes");
    fireEvent.click(saveBtn);
    
    // Should be clean again
    expect(screen.getByText("Configured")).toBeInTheDocument();
    expect(screen.getByText("All changes saved")).toBeInTheDocument();
  });

  it("handles resetting to defaults", () => {
    render(<SettingsPage />);
    
    // Change workspace name
    const input = screen.getByDisplayValue("CodeAtlas Workspace");
    fireEvent.change(input, { target: { value: "Changed Name" } });
    expect(screen.getByText("Unsaved changes")).toBeInTheDocument();
    
    // Click reset defaults
    const resetBtn = screen.getByText("Reset Defaults");
    fireEvent.click(resetBtn);
    
    // Verify dialog appears
    expect(screen.getByText("Reset Settings")).toBeInTheDocument();
    
    // Confirm reset
    const confirmBtn = screen.getAllByText("Reset Defaults")[1];
    fireEvent.click(confirmBtn);
    
    // Should be clean
    expect(screen.getByText("Configured")).toBeInTheDocument();
    
    // Input should be back to default
    expect(screen.getByDisplayValue("CodeAtlas Workspace")).toBeInTheDocument();
  });
  
  it("shows empty state when search finds no matches", () => {
    render(<SettingsPage />);
    
    // Search for something obscure
    const searchInput = screen.getByPlaceholderText("Search settings...");
    fireEvent.change(searchInput, { target: { value: "xxyyzz123" } });
    
    expect(screen.getByText("No settings found")).toBeInTheDocument();
  });
});
