import { listProjects } from "./projects";
import { adaptDashboardData } from "./adapters/dashboard-adapter";
import { DashboardData } from "@/types/dashboard";

export async function getDashboardData(): Promise<DashboardData> {
  try {
    const projectsResponse = await listProjects({ page: 1, size: 10, sort_by: "updated_at", order: "desc" });
    return adaptDashboardData(projectsResponse.items);
  } catch {
    // If backend server is currently starting up or offline, return clean baseline structure with empty projects
    return adaptDashboardData([]);
  }
}
