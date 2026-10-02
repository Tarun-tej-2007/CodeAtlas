import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import LoginPage from "@/app/login/page";
import { MOCK_AUTH_CONFIG } from "@/lib/mock-data/auth";

// Mock setTimeout
vi.useFakeTimers();

// Mock useRouter
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe("Login Page", () => {
  it("renders branding and form fields", () => {
    render(<LoginPage />);
    
    // Branding
    expect(screen.getByText("Architecture intelligence for modern engineering.")).toBeInTheDocument();
    
    // Fields
    expect(screen.getByText("Welcome back")).toBeInTheDocument();
    expect(screen.getByLabelText("Email address")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByLabelText("Remember me")).toBeInTheDocument();
    expect(screen.getByText("Forgot password?")).toBeInTheDocument();
    expect(screen.getByText(/Don't have an account\?/)).toBeInTheDocument();
  });

  it("validates required fields", () => {
    render(<LoginPage />);
    
    const emailInput = screen.getByLabelText("Email address");
    const passwordInput = screen.getByLabelText("Password");
    
    fireEvent.focus(emailInput);
    fireEvent.blur(emailInput);
    
    fireEvent.focus(passwordInput);
    fireEvent.blur(passwordInput);
    
    expect(screen.getByText("Please enter your email address.")).toBeInTheDocument();
    expect(screen.getByText("Please enter your password.")).toBeInTheDocument();
  });

  it("validates invalid email format", () => {
    render(<LoginPage />);
    
    const emailInput = screen.getByLabelText("Email address");
    
    fireEvent.change(emailInput, { target: { value: "invalid-email" } });
    fireEvent.blur(emailInput);
    
    expect(screen.getByText("Please enter a valid email address.")).toBeInTheDocument();
  });

  it("disables submit button when invalid", () => {
    render(<LoginPage />);
    
    const button = screen.getByRole("button", { name: "Sign In" });
    expect(button).toBeDisabled();
  });

  it("enables button and submits successfully with valid credentials", async () => {
    render(<LoginPage />);
    
    fireEvent.change(screen.getByLabelText("Email address"), { target: { value: MOCK_AUTH_CONFIG.validLoginEmail } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: MOCK_AUTH_CONFIG.validLoginPassword } });
    
    const button = screen.getByRole("button", { name: "Sign In" });
    expect(button).toBeEnabled();
    
    fireEvent.click(button);
    
    expect(button).toBeDisabled();
    expect(screen.getByText("Signing In...")).toBeInTheDocument();
    
    act(() => {
      vi.advanceTimersByTime(MOCK_AUTH_CONFIG.simulatedDelayMs);
    });
    
    expect(screen.getByText("Signed in successfully")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Continue to Dashboard" })).toBeInTheDocument();
  });

  it("shows error for invalid credentials", () => {
    render(<LoginPage />);
    
    const passwordInput = screen.getByLabelText("Password");
    
    fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "wrong@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "wrongpassword" } });
    
    fireEvent.click(screen.getByRole("button", { name: "Sign In" }));
    
    act(() => {
      vi.advanceTimersByTime(MOCK_AUTH_CONFIG.simulatedDelayMs);
    });
    
    expect(screen.getByText("Invalid email or password.")).toBeInTheDocument();
    // Password field should be cleared on error
    expect(passwordInput).toHaveValue("");
  });

  it("toggles password visibility", () => {
    render(<LoginPage />);
    
    const passwordInput = screen.getByLabelText("Password");
    expect(passwordInput).toHaveAttribute("type", "password");
    
    const toggleButton = screen.getByLabelText("Show password", { selector: "button" });
    fireEvent.click(toggleButton);
    
    expect(passwordInput).toHaveAttribute("type", "text");
    
    fireEvent.click(screen.getByLabelText("Hide password", { selector: "button" }));
    
    expect(passwordInput).toHaveAttribute("type", "password");
  });
});
