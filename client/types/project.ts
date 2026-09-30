export type ProjectVisibility = "public" | "private" | "internal";

export interface ProjectResponse {
  id: string;
  owner_id: string;
  name: string;
  slug: string;
  description: string | null;
  visibility: ProjectVisibility;
  created_at: string;
  updated_at: string;
}

export interface PaginatedProjectResponse {
  items: ProjectResponse[];
  count: number;
  total: number;
  page: number;
  size: number;
  pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface ProjectCreate {
  name: string;
  description?: string | null;
  visibility?: ProjectVisibility;
}

export interface ProjectUpdate {
  name?: string | null;
  description?: string | null;
  visibility?: ProjectVisibility | null;
}
