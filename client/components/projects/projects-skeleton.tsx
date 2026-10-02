export function ProjectsSkeleton() {
  return (
    <div className="space-y-6 animate-pulse" data-testid="projects-skeleton">
      {/* Header Skeleton */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between pb-4.5 border-b border-[#1E293B]">
        <div className="space-y-1.5">
          <div className="h-6 w-36 rounded bg-[#141E2E]" />
          <div className="h-4 w-64 rounded bg-[#0F1726]" />
        </div>
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-28 rounded bg-[#141E2E]" />
        </div>
      </div>

      {/* Toolbar Skeleton */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between py-4">
        <div className="h-8 w-full sm:w-64 rounded bg-[#0F1726] border border-[#1E293B]" />
        <div className="flex items-center gap-2">
          <div className="h-8 w-32 rounded bg-[#0F1726] border border-[#1E293B]" />
          <div className="h-8 w-32 rounded bg-[#0F1726] border border-[#1E293B]" />
          <div className="h-8 w-8 rounded bg-[#0F1726] border border-[#1E293B]" />
        </div>
      </div>

      {/* Grid Skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4.5">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="flex flex-col justify-between rounded-lg border border-[#1E293B] bg-[#0F1726] p-4.5 shadow-xs h-[180px]">
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="h-5 w-5 rounded bg-[#141E2E]" />
                  <div className="h-4 w-32 rounded bg-[#141E2E]" />
                </div>
                <div className="h-4 w-4 rounded bg-[#141E2E]" />
              </div>
              <div className="space-y-2 mb-4">
                <div className="h-3 w-full rounded bg-[#141E2E]" />
                <div className="h-3 w-4/5 rounded bg-[#141E2E]" />
              </div>
            </div>
            
            <div className="mt-auto flex flex-col gap-3">
              <div className="flex items-center gap-3">
                <div className="h-4 w-16 rounded-full bg-[#141E2E]" />
                <div className="h-3 w-24 rounded bg-[#141E2E]" />
              </div>
              <div className="h-8 w-full rounded bg-[#141E2E]" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
