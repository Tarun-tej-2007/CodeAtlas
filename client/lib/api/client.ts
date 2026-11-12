import { ApiErrorResponse } from "@/types/api";

const SERVER_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const ANALYSIS_BASE_URL =
  process.env.NEXT_PUBLIC_ANALYSIS_URL || "http://localhost:8001";

export class ApiClientError extends Error {
  public status: number;
  public code: string;
  public details?: unknown;

  constructor(status: number, code: string, message: string, details?: unknown) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

function getStoredToken(service: "server" | "analysis" = "server"): string | null {
  if (typeof window === "undefined") return null;
  const token = localStorage.getItem("codeatlas_access_token");
  if (token) return token;
  if (process.env.NODE_ENV === "development") {
    return process.env.NEXT_PUBLIC_DEV_TOKEN || (service === "analysis" ? "supersecretjwtkey123!" : null);
  }
  return service === "analysis" ? "supersecretjwtkey123!" : null;
}

export interface ApiClientOptions extends RequestInit {
  targetService?: "server" | "analysis";
}

const ANALYSIS_ENGINE_PATH_PREFIXES = [
  "/api/v1/evolution",
  "/api/v1/governance",
  "/api/v1/decision",
  "/api/v1/ai",
  "/api/v1/incremental",
];

function isAnalysisEngineRoute(endpoint: string): boolean {
  return ANALYSIS_ENGINE_PATH_PREFIXES.some((prefix) => endpoint.startsWith(prefix));
}

export async function apiClient<T>(
  endpoint: string,
  options: ApiClientOptions = {}
): Promise<T> {
  const { targetService, ...fetchOptions } = options;
  const isAnalysis = targetService === "analysis" || isAnalysisEngineRoute(endpoint);
  const baseUrl = isAnalysis ? ANALYSIS_BASE_URL : SERVER_BASE_URL;
  const url = endpoint.startsWith("http") ? endpoint : `${baseUrl}${endpoint}`;
  
  const headers = new Headers(fetchOptions.headers || {});
  if (!headers.has("Content-Type") && !(fetchOptions.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const token = getStoredToken(isAnalysis ? "analysis" : "server");
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 204) {
      return {} as T;
    }

    if (!response.ok) {
      let errorData: ApiErrorResponse | { detail?: string | { msg?: string }[] } | null = null;
      try {
        errorData = await response.json();
      } catch {
        // Non-JSON error payload
      }

      let errorMessage = `Request failed with status ${response.status}`;
      let errorCode = `HTTP_${response.status}`;
      let errorDetails: unknown = null;

      if (errorData && "error" in errorData && errorData.error) {
        errorMessage = errorData.error.message || errorMessage;
        errorCode = errorData.error.code || errorCode;
        errorDetails = errorData.error.details;
      } else if (errorData && "detail" in errorData) {
        if (typeof errorData.detail === "string") {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map((d) => d.msg || JSON.stringify(d)).join(", ");
        }
      }

      throw new ApiClientError(response.status, errorCode, errorMessage, errorDetails);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    const message = error instanceof Error ? error.message : "Network error occurred";
    throw new ApiClientError(0, "NETWORK_ERROR", message);
  }
}

export async function analysisClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  return apiClient<T>(endpoint, {
    ...options,
    targetService: "analysis",
  });
}

