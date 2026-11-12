"use client";

import { useState, useMemo } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { ActivityEvent, ActivityFilterState, ActivityStats, ActivitySummary as ActivitySummaryType, ActivityTimelineGroup } from "@/types/activity-ui";
import { MOCK_ACTIVITY_EVENTS } from "@/lib/mock-data/activity";
import { ActivityHeader } from "@/components/activity/activity-header";
import { ActivityOverview } from "@/components/activity/activity-overview";
import { ActivityFilters } from "@/components/activity/activity-filters";
import { ActivityTimeline } from "@/components/activity/activity-timeline";
import { ActivityDetails } from "@/components/activity/activity-details";
import { ActivityStatistics } from "@/components/activity/activity-statistics";
import { ActivitySummary } from "@/components/activity/activity-summary";
import { ActivityExport } from "@/components/activity/activity-export";
import { ActivitySkeleton } from "@/components/activity/activity-skeleton";
import { CheckCircle2 } from "lucide-react";

export default function ActivityPage() {
  const [events, setEvents] = useState<ActivityEvent[]>(MOCK_ACTIVITY_EVENTS);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  
  const [filters, setFilters] = useState<ActivityFilterState>({
    search: "",
    type: "ALL",
    severity: "ALL",
    status: "ALL",
    actorType: "ALL",
    date: "ALL"
  });

  // Calculate overall stats from all events (not filtered)
  const stats = useMemo<ActivityStats>(() => {
    let today = 0;
    let warnings = 0;
    let critical = 0;
    let resolved = 0;
    let automated = 0;

    events.forEach(e => {
      if (e.dateLabel === "Today") today++;
      if (e.severity === "WARNING") warnings++;
      if (e.severity === "CRITICAL") critical++;
      if (e.status === "RESOLVED") resolved++;
      if (e.actor.type === "AUTOMATION" || e.actor.type === "AI") automated++;
    });

    return {
      total: events.length,
      today,
      warnings,
      critical,
      resolved,
      automated
    };
  }, [events]);

  // Derived summary
  const summary = useMemo<ActivitySummaryType>(() => {
    const aiReviewCompleted = events.find(e => e.type === "AI_REVIEW" && e.status === "COMPLETED");
    const govCompleted = events.find(e => e.type === "GOVERNANCE" && e.status === "COMPLETED");
    const reportsGen = events.filter(e => e.type === "REPORT").length;
    
    return {
      description: `${stats.total} engineering events were recorded during the current monitoring period. Automated analysis represents the largest source of activity, while architecture and governance events account for the majority of recent engineering changes.`,
      highlights: [
        aiReviewCompleted ? "Architecture review completed" : "Architecture checks in progress",
        govCompleted ? "Governance evaluation completed" : "Pending governance checks",
        `${stats.critical} critical finding${stats.critical === 1 ? "" : "s"} detected`,
        `${stats.resolved} issue${stats.resolved === 1 ? "" : "s"} resolved`,
        `${reportsGen} report${reportsGen === 1 ? "" : "s"} generated`
      ]
    };
  }, [stats, events]);

  // Apply filters
  const filteredEvents = useMemo(() => {
    return events.filter(e => {
      // Date filter (mock logic)
      if (filters.date === "TODAY" && e.dateLabel !== "Today") return false;
      if (filters.date === "YESTERDAY" && e.dateLabel !== "Yesterday") return false;
      
      if (filters.type !== "ALL" && e.type !== filters.type) return false;
      if (filters.severity !== "ALL" && e.severity !== filters.severity) return false;
      if (filters.status !== "ALL" && e.status !== filters.status) return false;
      if (filters.actorType !== "ALL" && e.actor.type !== filters.actorType) return false;
      
      if (filters.search) {
        const query = filters.search.toLowerCase();
        return (
          e.title.toLowerCase().includes(query) ||
          e.description.toLowerCase().includes(query) ||
          e.actor.name.toLowerCase().includes(query) ||
          e.type.toLowerCase().includes(query) ||
          (e.relatedProject && e.relatedProject.toLowerCase().includes(query)) ||
          (e.relatedComponent && e.relatedComponent.toLowerCase().includes(query))
        );
      }
      
      return true;
    });
  }, [events, filters]);

  // Group by dateLabel
  const groupedEvents = useMemo(() => {
    const map = new Map<string, ActivityEvent[]>();
    filteredEvents.forEach(e => {
      const g = map.get(e.dateLabel) || [];
      g.push(e);
      map.set(e.dateLabel, g);
    });
    
    const groups: ActivityTimelineGroup[] = [];
    map.forEach((evts, dateLabel) => {
      groups.push({ dateLabel, events: evts });
    });
    
    // Sort logic relies on mock data order roughly, since dateLabel sorting is complex 
    // without real dates. Mock data is already sorted.
    return groups;
  }, [filteredEvents]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    // Simulate network delay
    setTimeout(() => {
      setEvents([...MOCK_ACTIVITY_EVENTS]);
      setIsRefreshing(false);
    }, 1200);
  };

  const handleExport = () => {
    setExportSuccess(true);
    setTimeout(() => setExportSuccess(false), 3000);
  };

  const selectedEvent = events.find(e => e.id === selectedEventId) || null;

  return (
    <AppShell breadcrumb="Activity">
      <div className="max-w-7xl mx-auto space-y-6">
        <ActivityHeader 
          totalEvents={stats.total}
          latestActivity={events.length > 0 ? events[0].timestamp : "No activity"}
          onRefresh={handleRefresh}
          onExport={() => setShowExport(true)}
          isRefreshing={isRefreshing}
        />
        
        {exportSuccess && (
          <div className="bg-[#10B981]/10 border border-[#10B981]/30 rounded-lg p-4 flex items-center gap-3 text-[#10B981]">
            <CheckCircle2 className="h-5 w-5" />
            <span className="font-medium">Export prepared successfully</span>
          </div>
        )}

        <ActivityOverview stats={stats} />

        <div className="flex flex-col lg:flex-row gap-6">
          <div className="lg:w-[70%]">
            <ActivityFilters 
              filters={filters}
              onChange={(updates) => setFilters(prev => ({ ...prev, ...updates }))}
              onClear={() => setFilters({
                search: "", type: "ALL", severity: "ALL", status: "ALL", actorType: "ALL", date: "ALL"
              })}
              resultCount={filteredEvents.length}
            />
            
            {isRefreshing ? (
              <ActivitySkeleton />
            ) : (
              <ActivityTimeline 
                groups={groupedEvents}
                selectedEventId={selectedEventId}
                onSelect={(e) => setSelectedEventId(e.id)}
              />
            )}
          </div>
          
          <div className="lg:w-[30%] space-y-6">
            <ActivitySummary summary={summary} />
            <ActivityStatistics events={events} />
          </div>
        </div>
      </div>

      <ActivityDetails 
        event={selectedEvent} 
        onClose={() => setSelectedEventId(null)} 
      />

      {showExport && (
        <ActivityExport 
          onClose={() => setShowExport(false)} 
          onExport={handleExport}
        />
      )}
    </AppShell>
  );
}
