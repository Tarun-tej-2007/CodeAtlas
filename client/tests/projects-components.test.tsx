import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ProjectsHeader } from "@/components/projects/projects-header";
import { ProjectsToolbar } from "@/components/projects/projects-toolbar";
import { ProjectCard } from "@/components/projects/project-card";
import { ProjectList } from "@/components/projects/project-list";
import { ProjectsEmpty, ProjectsNoResults } from "@/components/projects/projects-empty";
import { ProjectsError } from "@/components/projects/projects-error";
import { ProjectsSkeleton } from "@/components/projects/projects-skeleton";
import { ProjectCreateDialog } from "@/components/projects/project-create-dialog";
import { ProjectEditDialog } from "@/components/projects/project-edit-dialog";
import { ProjectDeleteDialog } from "@/components/projects/project-delete-dialog";
import { ProjectResponse } from "@/types/project";
import { AppQueryProvider } from "@/lib/query/providers";

const mockProject: ProjectResponse = {
  id: "proj-123",
  owner_id: "user-456",
  name: "Frontend Service",
  slug: "frontend-service",
  description: "Main web interface",
  visibility: "private",
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

describe("Projects Components", () => {
  it("renders ProjectsHeader correctly", () => {
    const onCreateProject = vi.fn();
    render(<ProjectsHeader onCreateProject={onCreateProject} />);
    
    expect(screen.getByText("Projects")).toBeInTheDocument();
    expect(screen.getByText("Manage your software projects and architecture analysis.")).toBeInTheDocument();
    
    const newBtn = screen.getByText("New Project");
    fireEvent.click(newBtn);
    expect(onCreateProject).toHaveBeenCalled();
  });

  it("renders ProjectsToolbar correctly", () => {
    const onSearchChange = vi.fn();
    const onVisibilityChange = vi.fn();
    const onSortByChange = vi.fn();
    const onOrderChange = vi.fn();

    render(
      <ProjectsToolbar 
        search="foo"
        onSearchChange={onSearchChange}
        visibility="public"
        onVisibilityChange={onVisibilityChange}
        sortBy="name"
        onSortByChange={onSortByChange}
        order="asc"
        onOrderChange={onOrderChange}
      />
    );

    expect(screen.getByDisplayValue("foo")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Public")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Sort: Name")).toBeInTheDocument();
  });

  it("renders ProjectCard correctly", () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    
    render(
      <AppQueryProvider>
        <ProjectCard project={mockProject} onEdit={onEdit} onDelete={onDelete} />
      </AppQueryProvider>
    );

    expect(screen.getByText("Frontend Service")).toBeInTheDocument();
    expect(screen.getByText("Main web interface")).toBeInTheDocument();
    expect(screen.getByText("private")).toBeInTheDocument();
    expect(screen.getByText("Open Project")).toBeInTheDocument();
  });

  it("renders ProjectList with pagination", () => {
    const onPageChange = vi.fn();
    render(
      <AppQueryProvider>
        <ProjectList 
          projects={[mockProject]} 
          onEdit={() => {}} 
          onDelete={() => {}} 
          page={2}
          totalPages={5}
          hasNext={true}
          hasPrevious={true}
          onPageChange={onPageChange}
        />
      </AppQueryProvider>
    );

    expect(screen.getByText("Frontend Service")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    
    const prevBtn = screen.getByText("Previous");
    fireEvent.click(prevBtn);
    expect(onPageChange).toHaveBeenCalledWith(1);
    
    const nextBtn = screen.getByText("Next");
    fireEvent.click(nextBtn);
    expect(onPageChange).toHaveBeenCalledWith(3);
  });

  it("renders ProjectsEmpty and ProjectsNoResults", () => {
    const onCreateProject = vi.fn();
    const onClearFilters = vi.fn();

    const { unmount } = render(<ProjectsEmpty onCreateProject={onCreateProject} />);
    expect(screen.getByText("No projects yet")).toBeInTheDocument();
    expect(screen.getByText("Create Project")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Create Project"));
    expect(onCreateProject).toHaveBeenCalled();
    unmount();

    render(<ProjectsNoResults onClearFilters={onClearFilters} />);
    expect(screen.getByText("No matching projects")).toBeInTheDocument();
    expect(screen.getByText("Clear filters")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Clear filters"));
    expect(onClearFilters).toHaveBeenCalled();
  });

  it("renders ProjectsError correctly", () => {
    const onRetry = vi.fn();
    render(<ProjectsError message="Failed to load" onRetry={onRetry} />);
    
    expect(screen.getByTestId("projects-error")).toBeInTheDocument();
    expect(screen.getByText("Failed to load")).toBeInTheDocument();
    expect(screen.getByText("Retry connection")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Retry connection"));
    expect(onRetry).toHaveBeenCalled();
  });

  it("renders ProjectsSkeleton", () => {
    render(<ProjectsSkeleton />);
    expect(screen.getByTestId("projects-skeleton")).toBeInTheDocument();
  });

  it("renders ProjectCreateDialog", () => {
    const onClose = vi.fn();
    render(
      <AppQueryProvider>
        <ProjectCreateDialog onClose={onClose} />
      </AppQueryProvider>
    );
    expect(screen.getByText("Create Project", { selector: 'h2' })).toBeInTheDocument();
  });

  it("renders ProjectEditDialog", () => {
    const onClose = vi.fn();
    render(
      <AppQueryProvider>
        <ProjectEditDialog project={mockProject} onClose={onClose} />
      </AppQueryProvider>
    );
    expect(screen.getByText("Edit Project", { selector: 'h2' })).toBeInTheDocument();
    expect(screen.getByDisplayValue("Frontend Service")).toBeInTheDocument();
  });

  it("renders ProjectDeleteDialog", () => {
    const onClose = vi.fn();
    render(
      <AppQueryProvider>
        <ProjectDeleteDialog project={mockProject} onClose={onClose} />
      </AppQueryProvider>
    );
    expect(screen.getByText("Delete Project?")).toBeInTheDocument();
    expect(screen.getByText("Frontend Service")).toBeInTheDocument();
  });
});
