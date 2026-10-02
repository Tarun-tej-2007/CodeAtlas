export function AnalysisSkeleton() {
  return (
    <div className="flex flex-col h-full space-y-6 animate-pulse" data-testid="analysis-skeleton">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <div className="h-8 w-48 bg-[#1E293B] rounded-md mb-2"></div>
          <div className="h-4 w-64 bg-[#1E293B] rounded-md"></div>
        </div>
        <div className="h-10 w-32 bg-[#1E293B] rounded-md"></div>
      </div>
      
      {/* Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-24 bg-[#0F1726] border border-[#1E293B] rounded-lg"></div>
        ))}
      </div>

      {/* Workspace Split */}
      <div className="flex-1 flex gap-4 min-h-0">
        <div className="w-64 shrink-0 border border-[#1E293B] rounded-lg bg-[#0F1726] h-full hidden md:block"></div>
        <div className="flex-1 border border-[#1E293B] rounded-lg bg-[#0F1726] h-full"></div>
      </div>
    </div>
  );
}
