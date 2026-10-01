"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { ProjectsHeader } from "@/components/projects/projects-header";
import { ProjectsToolbar } from "@/components/projects/projects-toolbar";
import { ProjectList } from "@/components/projects/project-list";
import { ProjectsEmpty, ProjectsNoResults } from "@/components/projects/projects-empty";
import { ProjectsError } from "@/components/projects/projects-error";
import { ProjectsSkeleton } from "@/components/projects/projects-skeleton";
import { ProjectCreateDialog } from "@/components/projects/project-create-dialog";
import { ProjectEditDialog } from "@/components/projects/project-edit-dialog";
import { ProjectDeleteDialog } from "@/components/projects/project-delete-dialog";
import { useProjects } from "@/lib/query/use-projects";
import { ProjectResponse } from "@/types/project";

export default function ProjectsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [visibility, setVisibility] = useState("");
  const [sortBy, setSortBy] = useState("updated_at");
  const [order, setOrder] = useState<"asc" | "desc">("desc");

  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<ProjectResponse | null>(null);
  const [deletingProject, setDeletingProject] = useState<ProjectResponse | null>(null);

  const { data, isLoading, isError, error, refetch } = useProjects({
    page,
    size: 12,
    search: search || undefined,
    visibility: visibility || undefined,
    sort_by: sortBy as "created_at" | "updated_at" | "name",
    order,
  });

  const handleSearchChange = (newSearch: string) => {
    setSearch(newSearch);
    setPage(1); // reset to page 1 on search
  };

  const handleVisibilityChange = (newVisibility: string) => {
    setVisibility(newVisibility);
    setPage(1);
  };

  const handleSortByChange = (newSortBy: string) => {
    setSortBy(newSortBy);
    setPage(1);
  };

  const handleOrderChange = (newOrder: "asc" | "desc") => {
    setOrder(newOrder);
    setPage(1);
  };

  const handleClearFilters = () => {
    setSearch("");
    setVisibility("");
    setSortBy("updated_at");
    setOrder("desc");
    setPage(1);
  };

  let content;

  if (isLoading) {
    content = <ProjectsSkeleton />;
  } else if (isError) {
    content = (
      <ProjectsError
        message={error instanceof Error ? error.message : undefined}
        onRetry={() => refetch()}
      />
    );
  } else if (!data || data.items.length === 0) {
    if (search || visibility) {
      content = <ProjectsNoResults onClearFilters={handleClearFilters} />;
    } else {
      content = <ProjectsEmpty onCreateProject={() => setCreateDialogOpen(true)} />;
    }
  } else {
    content = (
      <ProjectList
        projects={data.items}
        onEdit={(p) => setEditingProject(p)}
        onDelete={(p) => setDeletingProject(p)}
        page={data.page}
        totalPages={data.pages}
        hasNext={data.has_next}
        hasPrevious={data.has_previous}
        onPageChange={setPage}
      />
    );
  }

  return (
    <AppShell breadcrumb="Projects">
      <div className="flex flex-col h-full space-y-6">
        <ProjectsHeader onCreateProject={() => setCreateDialogOpen(true)} />
        
        {/* Only show toolbar if not loading, no error, and (there are items OR user is searching/filtering) */}
        {!isLoading && !isError && ((data && data.items.length > 0) || search || visibility) && (
          <ProjectsToolbar
            search={search}
            onSearchChange={handleSearchChange}
            visibility={visibility}
            onVisibilityChange={handleVisibilityChange}
            sortBy={sortBy}
            onSortByChange={handleSortByChange}
            order={order}
            onOrderChange={handleOrderChange}
          />
        )}
        
        <div className="flex-1 pb-10">
          {content}
        </div>
      </div>

      {createDialogOpen && (
        <ProjectCreateDialog onClose={() => setCreateDialogOpen(false)} />
      )}
      {editingProject && (
        <ProjectEditDialog
          project={editingProject}
          onClose={() => setEditingProject(null)}
        />
      )}
      {deletingProject && (
        <ProjectDeleteDialog
          project={deletingProject}
          onClose={() => setDeletingProject(null)}
        />
      )}
    </AppShell>
  );
}
