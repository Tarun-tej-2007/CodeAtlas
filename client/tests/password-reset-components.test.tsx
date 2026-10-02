import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import ForgotPasswordPage from "@/app/forgot-password/page";
import ResetPasswordPage from "@/app/reset-password/page";
import { MOCK_AUTH_CONFIG } from "@/lib/mock-data/auth";

vi.useFakeTimers();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe("Forgot Password Flow", () => {
  it("renders forgot password page", () => {
    render(<ForgotPasswordPage />);
    expect(screen.getByText("Forgot your password?")).toBeInTheDocument();
    expect(screen.getByLabelText("Email address")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Send Reset Link" })).toBeInTheDocument();
    expect(screen.getByText(/Remember your password\?/)).toBeInTheDocument();
  });

  it("validates required email field", () => {
    render(<ForgotPasswordPage />);
    const emailInput = screen.getByLabelText("Email address");
    fireEvent.focus(emailInput);
    fireEvent.blur(emailInput);
    expect(screen.getByText("Please enter your email address.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Send Reset Link" })).toBeDisabled();
  });

  it("validates invalid email format", () => {
    render(<ForgotPasswordPage />);
    const emailInput = screen.getByLabelText("Email address");
    fireEvent.change(emailInput, { target: { value: "invalid-email" } });
    fireEvent.blur(emailInput);
    expect(screen.getByText("Please enter a valid email address.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Send Reset Link" })).toBeDisabled();
  });

  it("handles valid submission successfully", () => {
    render(<ForgotPasswordPage />);
    const emailInput = screen.getByLabelText("Email address");
    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    
    const button = screen.getByRole("button", { name: "Send Reset Link" });
    expect(button).toBeEnabled();
    fireEvent.click(button);
    
    expect(screen.getByText("Sending...")).toBeInTheDocument();
    
    act(() => {
      vi.advanceTimersByTime(MOCK_AUTH_CONFIG.simulatedDelayMs);
    });
    
    expect(screen.getByText("Check your email")).toBeInTheDocument();
    expect(screen.getByText("Reset link request submitted. If this were production, a reset link would be sent to your email.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Continue to Reset Password" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Back to Login" })).toBeInTheDocument();
  });
});

describe("Reset Password Flow", () => {
  it("renders reset password page", () => {
    render(<ResetPasswordPage />);
    expect(screen.getByText("Reset your password")).toBeInTheDocument();
    expect(screen.getByLabelText("New password")).toBeInTheDocument();
    expect(screen.getByLabelText("Confirm password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Reset Password" })).toBeInTheDocument();
    expect(screen.getByText("Back to Login")).toBeInTheDocument();
  });

  it("validates password strength and requirements", () => {
    render(<ResetPasswordPage />);
    const passwordInput = screen.getByLabelText("New password");
    
    fireEvent.change(passwordInput, { target: { value: "weak" } });
    expect(screen.getByText("Weak")).toBeInTheDocument();
    
    fireEvent.change(passwordInput, { target: { value: "Strong123!" } });
    expect(screen.getByText("Strong")).toBeInTheDocument();
  });

  it("validates mismatched passwords", () => {
    render(<ResetPasswordPage />);
    const passwordInput = screen.getByLabelText("New password");
    const confirmInput = screen.getByLabelText("Confirm password");
    
    fireEvent.change(passwordInput, { target: { value: "CodeAtlas123!" } });
    fireEvent.change(confirmInput, { target: { value: "Different123!" } });
    
    fireEvent.focus(confirmInput);
    fireEvent.blur(confirmInput);
    
    expect(screen.getByText("Passwords do not match.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Reset Password" })).toBeDisabled();
  });

  it("handles valid password reset submission successfully", () => {
    render(<ResetPasswordPage />);
    const passwordInput = screen.getByLabelText("New password");
    const confirmInput = screen.getByLabelText("Confirm password");
    
    fireEvent.change(passwordInput, { target: { value: "CodeAtlas123!" } });
    fireEvent.change(confirmInput, { target: { value: "CodeAtlas123!" } });
    
    const button = screen.getByRole("button", { name: "Reset Password" });
    expect(button).toBeEnabled();
    fireEvent.click(button);
    
    expect(screen.getByText("Resetting Password...")).toBeInTheDocument();
    
    act(() => {
      vi.advanceTimersByTime(MOCK_AUTH_CONFIG.simulatedDelayMs);
    });
    
    expect(screen.getByText("Password reset successfully")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Continue to Login" })).toBeInTheDocument();
  });
  
  it("toggles password visibility", () => {
    render(<ResetPasswordPage />);
    const passwordInput = screen.getByLabelText("New password");
    const confirmInput = screen.getByLabelText("Confirm password");
    
    expect(passwordInput).toHaveAttribute("type", "password");
    expect(confirmInput).toHaveAttribute("type", "password");
    
    const toggleButtons = screen.getAllByLabelText("Show password", { selector: "button" });
    fireEvent.click(toggleButtons[0]);
    fireEvent.click(toggleButtons[1]);
    
    expect(passwordInput).toHaveAttribute("type", "text");
    expect(confirmInput).toHaveAttribute("type", "text");
  });
});
