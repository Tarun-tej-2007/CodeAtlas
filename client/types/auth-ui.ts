export type SignupSubmissionState = "IDLE" | "SUBMITTING" | "SUCCESS" | "ERROR";

export type PasswordStrength = "WEAK" | "FAIR" | "STRONG";

export interface PasswordRequirement {
  id: string;
  label: string;
  test: (password: string) => boolean;
}

export interface SignupFormData {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
  termsAccepted: boolean;
}

export interface SignupValidationState {
  fullNameError: string | null;
  emailError: string | null;
  passwordError: string | null;
  confirmPasswordError: string | null;
}
