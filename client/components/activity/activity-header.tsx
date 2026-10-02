import { Activity, Download, RefreshCw } from "lucide-react";

interface Props {
  totalEvents: number;
  latestActivity: string;
  onRefresh: () => void;
  onExport: () => void;
  isRefreshing: boolean;
}

export function ActivityHeader({ totalEvents, latestActivity, onRefresh, onExport, isRefreshing }: Props) {
  return (
    <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6 pb-6 border-b border-[#1E293B]">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Activity className="h-5 w-5 text-[#3B82F6]" />
          <h1 className="text-2xl font-bold tracking-tight text-[#F8FAFC]">Activity & Audit Log</h1>
        </div>
        <p className="text-sm text-[#94A3B8]">
          Track engineering activity, analysis runs, architectural changes, and workspace events.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="flex flex-col items-start sm:items-end mr-4 hidden sm:flex">
          <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">
            Latest Activity
          </span>
          <div className="text-sm font-bold text-[#F8FAFC]">
            {totalEvents} Events
          </div>
          <div className="text-[10px] text-[#94A3B8]">
            {latestActivity}
          </div>
        </div>
        
        <button 
          onClick={onRefresh}
          disabled={isRefreshing}
          className="px-3 py-2 bg-[#0F1726] border border-[#1E293B] text-[#CBD5E1] rounded-md hover:bg-[#1E293B] hover:text-[#F8FAFC] transition-colors flex items-center gap-2 text-sm font-medium disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
          <span className="hidden sm:inline">Refresh</span>
        </button>
        
        <button
          onClick={onExport}
          className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-md text-sm font-medium transition-colors shadow focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#3B82F6]"
        >
          <Download className="h-4 w-4" />
          Export Activity
        </button>
      </div>
    </div>
  );
}

