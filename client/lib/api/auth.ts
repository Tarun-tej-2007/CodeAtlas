import { apiClient } from "./client";
import { AuthResponse, CurrentUserResponse } from "@/types/auth";

export async function loginUser(identifier: string, password: string): Promise<AuthResponse> {
  const response = await apiClient<AuthResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ identifier, password }),
  });
  if (typeof window !== "undefined" && response.tokens?.access_token) {
    localStorage.setItem("codeatlas_access_token", response.tokens.access_token);
    localStorage.setItem("codeatlas_refresh_token", response.tokens.refresh_token);
  }
  return response;
}

export async function getCurrentUser(): Promise<CurrentUserResponse> {
  return apiClient<CurrentUserResponse>("/api/v1/auth/me");
}

export async function logoutUser(): Promise<void> {
  const refreshToken =
    typeof window !== "undefined"
      ? localStorage.getItem("codeatlas_refresh_token")
      : null;

  if (refreshToken) {
    try {
      await apiClient("/api/v1/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } catch {
      // Best-effort logout
    }
  }

  if (typeof window !== "undefined") {
    localStorage.removeItem("codeatlas_access_token");
    localStorage.removeItem("codeatlas_refresh_token");
  }
}
