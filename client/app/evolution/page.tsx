"use client";

import { useState, useMemo } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { MOCK_EVOLUTION_DATA } from "@/lib/mock-data/architecture-evolution";

import { ArchitectureEvolutionHeader } from "@/components/architecture-evolution/architecture-evolution-header";
import { EvolutionOverview } from "@/components/architecture-evolution/evolution-overview";
import { EvolutionTrend } from "@/components/architecture-evolution/evolution-trend";
import { EvolutionChangeSummary } from "@/components/architecture-evolution/evolution-change-summary";
import { EvolutionTimeline } from "@/components/architecture-evolution/evolution-timeline";
import { EvolutionComparison } from "@/components/architecture-evolution/evolution-comparison";
import { EvolutionDrift } from "@/components/architecture-evolution/evolution-drift";
import { EvolutionRiskTrend } from "@/components/architecture-evolution/evolution-risk-trend";
import { EvolutionFilters } from "@/components/architecture-evolution/evolution-filters";
import { EvolutionSnapshotSelector } from "@/components/architecture-evolution/evolution-snapshot-selector";
import { EvolutionChangeDetails } from "@/components/architecture-evolution/evolution-change-details";

export default function EvolutionPage() {
  const data = MOCK_EVOLUTION_DATA;
  const latestSnapshot = data.snapshots[data.snapshots.length - 1];
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // Snapshot selection for comparison
  const [baselineId, setBaselineId] = useState<string>(data.snapshots[data.snapshots.length - 5]?.id || data.snapshots[0].id);
  const [currentId, setCurrentId] = useState<string>(latestSnapshot.id);
  
  // Event selection
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  // Filters
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [severityFilter, setSeverityFilter] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");

  const handleRunAnalysis = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 2000);
  };

  const baselineSnapshot = useMemo(() => data.snapshots.find(s => s.id === baselineId) || data.snapshots[0], [baselineId, data]);
  const currentSnapshot = useMemo(() => data.snapshots.find(s => s.id === currentId) || latestSnapshot, [currentId, latestSnapshot, data]);

  const filteredEvents = useMemo(() => {
    return data.events.filter(event => {
      if (categoryFilter !== "All" && event.category.toLowerCase() !== categoryFilter.toLowerCase()) return false;
      if (severityFilter !== "All" && event.severity !== severityFilter) return false;
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (!event.title.toLowerCase().includes(query) && !event.description.toLowerCase().includes(query)) return false;
      }
      return true;
    });
  }, [data.events, categoryFilter, severityFilter, searchQuery]);

  const selectedEvent = selectedEventId ? data.events.find(e => e.id === selectedEventId) : null;

  return (
    <AppShell breadcrumb="Architecture Evolution">
      <div className="flex flex-col bg-[#080D18] pb-6 relative">
        <ArchitectureEvolutionHeader 
          healthScore={latestSnapshot.healthScore}
          driftScore={latestSnapshot.driftScore}
          isAnalyzing={isAnalyzing}
          onRunAnalysis={handleRunAnalysis}
        />

        <EvolutionOverview stats={data.stats} />

        <div className="mb-6">
          <EvolutionTrend snapshots={data.snapshots} />
        </div>

        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
          <EvolutionSnapshotSelector 
            snapshots={data.snapshots}
            selectedBaselineId={baselineId}
            onBaselineChange={setBaselineId}
            selectedCurrentId={currentId}
            onCurrentChange={setCurrentId}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-1 h-[400px]">
            <EvolutionChangeSummary stats={data.stats} />
          </div>
          <div className="lg:col-span-1 h-[400px]">
            <EvolutionComparison baselineSnapshot={baselineSnapshot} currentSnapshot={currentSnapshot} />
          </div>
          <div className="lg:col-span-1 h-[400px]">
            <EvolutionDrift currentDrift={latestSnapshot.driftScore} breakdown={data.driftBreakdown} />
          </div>
        </div>

        <EvolutionFilters 
          categoryFilter={categoryFilter}
          onCategoryFilterChange={setCategoryFilter}
          severityFilter={severityFilter}
          onSeverityFilterChange={setSeverityFilter}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <EvolutionTimeline 
              events={filteredEvents}
              onSelectEvent={(e) => setSelectedEventId(e.id)}
              selectedEventId={selectedEventId}
            />
          </div>
          <div className="lg:col-span-1">
            <EvolutionRiskTrend baselineSnapshot={baselineSnapshot} currentSnapshot={currentSnapshot} />
          </div>
        </div>

        {/* Overlay Drawer for Event Details */}
        {selectedEvent && (
          <div className="fixed inset-y-0 right-0 z-50 shadow-2xl flex border-l border-[#1E293B]">
            <EvolutionChangeDetails 
              event={selectedEvent}
              onClose={() => setSelectedEventId(null)}
            />
          </div>
        )}
      </div>
    </AppShell>
  );
}
