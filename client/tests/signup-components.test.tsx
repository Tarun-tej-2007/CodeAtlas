import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import SignupPage from "@/app/signup/page";
import { MOCK_AUTH_CONFIG } from "@/lib/mock-data/auth";

// Mock setTimeout
vi.useFakeTimers();

describe("Signup Page", () => {
  it("renders branding and form fields", () => {
    render(<SignupPage />);
    
    // Branding
    expect(screen.getByText("Architecture intelligence for modern engineering.")).toBeInTheDocument();
    
    // Fields
    expect(screen.getByLabelText("Full name")).toBeInTheDocument();
    expect(screen.getByLabelText("Email address")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByLabelText("Confirm password")).toBeInTheDocument();
    expect(screen.getByText(/I agree to the/)).toBeInTheDocument();
  });

  it("validates full name", () => {
    render(<SignupPage />);
    
    const nameInput = screen.getByLabelText("Full name");
    
    // Focus and blur to trigger touched state
    fireEvent.focus(nameInput);
    fireEvent.blur(nameInput);
    
    expect(screen.getByText("Please enter your full name.")).toBeInTheDocument();
    
    fireEvent.change(nameInput, { target: { value: "A" } });
    fireEvent.blur(nameInput);
    
    expect(screen.getByText("Name must be at least 2 characters.")).toBeInTheDocument();
  });

  it("validates email", () => {
    render(<SignupPage />);
    
    const emailInput = screen.getByLabelText("Email address");
    
    fireEvent.change(emailInput, { target: { value: "invalid-email" } });
    fireEvent.blur(emailInput);
    
    expect(screen.getByText("Enter a valid email address.")).toBeInTheDocument();
  });

  it("updates password requirements and strength", () => {
    render(<SignupPage />);
    
    const passwordInput = screen.getByLabelText("Password");
    
    fireEvent.change(passwordInput, { target: { value: "codeatlas" } });
    
    expect(screen.getByText("Weak")).toBeInTheDocument();
    
    fireEvent.change(passwordInput, { target: { value: "CodeAtlas@2026" } });
    
    expect(screen.getByText("Strong")).toBeInTheDocument();
  });

  it("validates confirm password", () => {
    render(<SignupPage />);
    
    const passwordInput = screen.getByLabelText("Password");
    const confirmInput = screen.getByLabelText("Confirm password");
    
    fireEvent.change(passwordInput, { target: { value: "CodeAtlas@2026" } });
    fireEvent.change(confirmInput, { target: { value: "CodeAtlas@2025" } });
    fireEvent.blur(confirmInput);
    
    expect(screen.getByText("Passwords do not match.")).toBeInTheDocument();
  });

  it("disables button when invalid", () => {
    render(<SignupPage />);
    
    const button = screen.getByRole("button", { name: "Create Account" });
    expect(button).toBeDisabled();
  });

  it("enables button and submits successfully", async () => {
    render(<SignupPage />);
    
    fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "Test User" } });
    fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "test@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "CodeAtlas@2026" } });
    fireEvent.change(screen.getByLabelText("Confirm password"), { target: { value: "CodeAtlas@2026" } });
    
    const checkbox = screen.getByRole("checkbox");
    fireEvent.click(checkbox);
    
    const button = screen.getByRole("button", { name: "Create Account" });
    expect(button).toBeEnabled();
    
    fireEvent.click(button);
    
    expect(button).toBeDisabled();
    expect(screen.getByText("Creating Account...")).toBeInTheDocument();
    
    act(() => {
      vi.advanceTimersByTime(MOCK_AUTH_CONFIG.simulatedDelayMs);
    });
    
    expect(screen.getByText("Account Created")).toBeInTheDocument();
  });

  it("shows error for existing email", () => {
    render(<SignupPage />);
    
    fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "Test User" } });
    fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "existing@codeatlas.local" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "CodeAtlas@2026" } });
    fireEvent.change(screen.getByLabelText("Confirm password"), { target: { value: "CodeAtlas@2026" } });
    fireEvent.click(screen.getByRole("checkbox"));
    
    fireEvent.click(screen.getByRole("button", { name: "Create Account" }));
    
    act(() => {
      vi.advanceTimersByTime(MOCK_AUTH_CONFIG.simulatedDelayMs);
    });
    
    expect(screen.getByText("An account with this email already exists.")).toBeInTheDocument();
  });

  it("toggles password visibility", () => {
    render(<SignupPage />);
    
    const passwordInput = screen.getByLabelText("Password");
    expect(passwordInput).toHaveAttribute("type", "password");
    
    const toggleButton = screen.getAllByLabelText("Show password", { selector: "button" })[0];
    fireEvent.click(toggleButton);
    
    expect(passwordInput).toHaveAttribute("type", "text");
  });
});

