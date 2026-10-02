export function ActivitySkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      {[1, 2].map((group) => (
        <div key={group}>
          <div className="h-4 w-24 bg-[#1E293B] rounded mb-4"></div>
          
          <div className="space-y-3 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-[#1E293B] before:to-transparent">
            {[1, 2, 3].map((item) => (
              <div key={item} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse">
                <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-[#080D18] bg-[#1E293B] shrink-0 md:order-1 md:odd:-translate-x-1/2 md:even:translate-x-1/2 z-10 mx-auto absolute left-0 md:left-1/2 -translate-x-0" />
                
                <div className="w-[calc(100%-3rem)] md:w-[calc(50%-2rem)] p-4 rounded-xl border border-[#1E293B] bg-[#0F1726]">
                  <div className="flex justify-between mb-3">
                    <div className="h-3 w-16 bg-[#1E293B] rounded"></div>
                    <div className="h-3 w-12 bg-[#1E293B] rounded"></div>
                  </div>
                  <div className="h-4 w-3/4 bg-[#1E293B] rounded mb-2"></div>
                  <div className="h-3 w-full bg-[#1E293B] rounded mb-1"></div>
                  <div className="h-3 w-2/3 bg-[#1E293B] rounded"></div>
                  
                  <div className="flex items-center gap-4 mt-4 pt-3 border-t border-[#1E293B]/50">
                    <div className="h-4 w-20 bg-[#1E293B] rounded"></div>
                    <div className="h-4 w-16 bg-[#1E293B] rounded"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
