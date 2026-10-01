export function ArchitectureSkeleton() {
  return (
    <div className="flex flex-col h-full animate-pulse" data-testid="architecture-skeleton">
      <div className="flex justify-between items-center mb-6">
        <div>
          <div className="h-8 w-40 bg-[#1E293B] rounded mb-2"></div>
          <div className="h-4 w-64 bg-[#1E293B] rounded"></div>
        </div>
        <div className="flex gap-4">
          <div className="h-10 w-24 bg-[#1E293B] rounded"></div>
          <div className="h-10 w-32 bg-[#1E293B] rounded"></div>
        </div>
      </div>
      
      <div className="grid grid-cols-6 gap-3 mb-6">
        {[1, 2, 3, 4, 5, 6].map(i => (
          <div key={i} className="h-20 bg-[#1E293B] rounded-lg"></div>
        ))}
      </div>
      
      <div className="flex-1 flex gap-4 overflow-hidden">
        <div className="flex-1 bg-[#1E293B] rounded-lg"></div>
        <div className="w-80 flex flex-col gap-4">
          <div className="h-1/3 bg-[#1E293B] rounded-lg"></div>
          <div className="h-1/3 bg-[#1E293B] rounded-lg"></div>
          <div className="h-1/3 bg-[#1E293B] rounded-lg"></div>
        </div>
      </div>
    </div>
  );
}
