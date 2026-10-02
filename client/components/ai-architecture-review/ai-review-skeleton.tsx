export function AIReviewSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-20 bg-[#0F1726] rounded-lg border border-[#1E293B]"></div>
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-24 bg-[#0F1726] rounded-lg border border-[#1E293B]"></div>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 h-96 bg-[#0F1726] rounded-lg border border-[#1E293B]"></div>
        <div className="h-96 bg-[#0F1726] rounded-lg border border-[#1E293B]"></div>
      </div>
    </div>
  );
}
