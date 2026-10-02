export function DependencyGraphSkeleton() {
  return (
    <div className="flex flex-col h-full space-y-4 animate-pulse" data-testid="dependency-graph-skeleton">
      <div className="flex justify-between items-center mb-4">
        <div>
          <div className="h-8 w-48 bg-[#1E293B] rounded-md mb-2"></div>
          <div className="h-4 w-64 bg-[#1E293B] rounded-md"></div>
        </div>
        <div className="h-10 w-48 bg-[#1E293B] rounded-md"></div>
      </div>

      <div className="flex-1 flex border border-[#1E293B] rounded-lg bg-[#0F1726] overflow-hidden">
        <div className="w-56 border-r border-[#1E293B] bg-[#0F1726] hidden sm:block"></div>
        <div className="flex-1 bg-[#080D18] relative">
          <div className="absolute top-4 left-4 right-4 h-12 bg-[#1E293B] rounded-md"></div>
        </div>
      </div>
    </div>
  );
}
