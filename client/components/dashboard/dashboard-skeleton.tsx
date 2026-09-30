export function DashboardSkeleton() {
  return (
    <div className="space-y-4.5 animate-pulse" data-testid="dashboard-skeleton">
      {/* Header Skeleton */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between pb-4.5 border-b border-[#1E293B]">
        <div className="space-y-1.5">
          <div className="h-6 w-36 rounded bg-[#141E2E]" />
          <div className="h-4 w-64 rounded bg-[#0F1726]" />
        </div>
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-32 rounded bg-[#0F1726]" />
          <div className="h-8 w-28 rounded bg-[#141E2E]" />
        </div>
      </div>

      {/* Unified Architecture Overview Surface Skeleton */}
      <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] shadow-xs overflow-hidden">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 divide-y sm:divide-y-0 divide-[#1E293B] sm:divide-x">
          <div className="p-4 sm:p-5 lg:col-span-4 h-32 flex flex-col justify-between">
            <div className="h-3 w-28 rounded bg-[#141E2E]" />
            <div className="h-8 w-24 rounded bg-[#141E2E]" />
            <div className="h-3 w-36 rounded bg-[#141E2E]" />
          </div>
          <div className="p-4 sm:p-5 lg:col-span-3 h-32 flex flex-col justify-between">
            <div className="h-3 w-24 rounded bg-[#141E2E]" />
            <div className="h-7 w-20 rounded bg-[#141E2E]" />
            <div className="h-3 w-32 rounded bg-[#141E2E]" />
          </div>
          <div className="p-4 sm:p-5 lg:col-span-3 h-32 flex flex-col justify-between">
            <div className="h-3 w-24 rounded bg-[#141E2E]" />
            <div className="h-7 w-20 rounded bg-[#141E2E]" />
            <div className="h-3 w-32 rounded bg-[#141E2E]" />
          </div>
          <div className="p-4 sm:p-5 lg:col-span-2 h-32 flex flex-col justify-between">
            <div className="h-3 w-24 rounded bg-[#141E2E]" />
            <div className="h-7 w-16 rounded bg-[#141E2E]" />
            <div className="h-3 w-24 rounded bg-[#141E2E]" />
          </div>
        </div>
      </div>

      {/* Health Chart + Status Row Skeleton */}
      <div className="grid grid-cols-1 gap-4.5 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-lg border border-[#1E293B] bg-[#0F1726] p-4.5 h-84 flex flex-col justify-between">
          <div className="h-5 w-40 rounded bg-[#141E2E]" />
          <div className="h-48 w-full rounded bg-[#0B1220]" />
        </div>
        <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4.5 h-84 flex flex-col justify-between">
          <div className="h-5 w-36 rounded bg-[#141E2E]" />
          <div className="grid grid-cols-2 gap-2.5">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 rounded bg-[#0B1220]" />
            ))}
          </div>
          <div className="h-12 w-full rounded bg-[#0B1220]" />
        </div>
      </div>

      {/* Issues & Changes Row Skeleton */}
      <div className="grid grid-cols-1 gap-4.5 lg:grid-cols-2">
        <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4.5 h-60">
          <div className="h-4 w-32 rounded bg-[#141E2E] mb-3" />
          <div className="space-y-2.5">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 rounded bg-[#0B1220]" />
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4.5 h-60">
          <div className="h-4 w-44 rounded bg-[#141E2E] mb-3" />
          <div className="space-y-2.5">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 rounded bg-[#0B1220]" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
