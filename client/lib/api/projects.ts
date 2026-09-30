import { apiClient } from "./client";
import {
  ProjectResponse,
  PaginatedProjectResponse,
  ProjectCreate,
  ProjectUpdate,
} from "@/types/project";
import { AnalysisResponse } from "@/types/analysis";

export interface ListProjectsParams {
  page?: number;
  size?: number;
  sort_by?: "created_at" | "updated_at" | "name";
  order?: "asc" | "desc";
  search?: string;
  visibility?: string;
}

export async function listProjects(
  params: ListProjectsParams = {}
): Promise<PaginatedProjectResponse> {
  const query = new URLSearchParams();
  if (params.page) query.set("page", params.page.toString());
  if (params.size) query.set("size", params.size.toString());
  if (params.sort_by) query.set("sort_by", params.sort_by);
  if (params.order) query.set("order", params.order);
  if (params.search) query.set("search", params.search);
  if (params.visibility) query.set("visibility", params.visibility);

  const qs = query.toString();
  const endpoint = `/api/v1/projects${qs ? `?${qs}` : ""}`;
  return apiClient<PaginatedProjectResponse>(endpoint);
}

export async function getProject(projectId: string): Promise<ProjectResponse> {
  return apiClient<ProjectResponse>(`/api/v1/projects/${projectId}`);
}

export async function createProject(data: ProjectCreate): Promise<ProjectResponse> {
  return apiClient<ProjectResponse>("/api/v1/projects", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateProject(
  projectId: string,
  data: ProjectUpdate
): Promise<ProjectResponse> {
  return apiClient<ProjectResponse>(`/api/v1/projects/${projectId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteProject(projectId: string): Promise<void> {
  return apiClient<void>(`/api/v1/projects/${projectId}`, {
    method: "DELETE",
  });
}

export async function triggerProjectAnalysis(
  projectId: string,
  requestId?: string
): Promise<AnalysisResponse> {
  const headers: Record<string, string> = {};
  if (requestId) {
    headers["X-Request-ID"] = requestId;
  }
  return apiClient<AnalysisResponse>(`/api/v1/projects/${projectId}/analyze`, {
    method: "POST",
    headers,
  });
}
