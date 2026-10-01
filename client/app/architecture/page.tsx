"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { ArchitectureHeader } from "@/components/architecture/architecture-header";
import { ArchitectureOverviewMetrics } from "@/components/architecture/architecture-overview";
import { ArchitectureToolbar, ViewMode } from "@/components/architecture/architecture-toolbar";
import { ArchitectureMap } from "@/components/architecture/architecture-map";
import { ArchitectureComponentDetails } from "@/components/architecture/architecture-component-details";
import { ArchitectureViolationDetails } from "@/components/architecture/architecture-violation-details";
import { ArchitectureHealth } from "@/components/architecture/architecture-health";
import { ArchitectureBoundaries } from "@/components/architecture/architecture-boundaries";
import { ArchitectureViolations } from "@/components/architecture/architecture-violations";
import { ArchitectureHistory } from "@/components/architecture/architecture-history";
import { ArchitectureRisks } from "@/components/architecture/architecture-risks";

import { MOCK_ARCHITECTURE_DATA } from "@/lib/mock-data/architecture";

export default function ArchitecturePage() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<ViewMode>("overview");
  const [selectedComponentId, setSelectedComponentId] = useState<string | null>(null);
  const [selectedLayerId, setSelectedLayerId] = useState<string | null>(null);
  const [selectedViolationId, setSelectedViolationId] = useState<string | null>(null);

  const handleRunAnalysis = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 2000);
  };

  return (
    <AppShell breadcrumb="Architecture">
      <div className="flex flex-col bg-[#080D18] pb-6">
        <ArchitectureHeader 
          overview={MOCK_ARCHITECTURE_DATA.overview} 
          isAnalyzing={isAnalyzing}
          onRunAnalysis={handleRunAnalysis}
        />
        
        <ArchitectureOverviewMetrics 
          stats={MOCK_ARCHITECTURE_DATA.stats} 
          criticalViolations={MOCK_ARCHITECTURE_DATA.overview.criticalViolationCount}
        />
        
        <ArchitectureToolbar 
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
        />

        <div className="flex flex-col lg:flex-row gap-4 min-h-[600px] h-[calc(100vh-320px)]">
          {/* Main Map Area */}
          <div className="flex-1 border border-[#1E293B] rounded-lg overflow-hidden flex relative bg-[#080D18]">
            <ArchitectureMap 
              data={MOCK_ARCHITECTURE_DATA}
              searchQuery={searchQuery}
              selectedComponentId={selectedComponentId}
              onComponentSelect={setSelectedComponentId}
              selectedLayerId={selectedLayerId}
              onLayerSelect={setSelectedLayerId}
            />
            
            {/* Drawers over the map */}
            {selectedComponentId && (
              <div className="absolute right-0 top-0 bottom-0 shadow-[-10px_0_30px_rgba(0,0,0,0.5)]">
                <ArchitectureComponentDetails 
                  componentId={selectedComponentId}
                  data={MOCK_ARCHITECTURE_DATA}
                  onClose={() => setSelectedComponentId(null)}
                />
              </div>
            )}
            
            {selectedViolationId && (
              <div className="absolute right-0 top-0 bottom-0 shadow-[-10px_0_30px_rgba(0,0,0,0.5)]">
                <ArchitectureViolationDetails 
                  violationId={selectedViolationId}
                  violations={MOCK_ARCHITECTURE_DATA.violations}
                  onClose={() => setSelectedViolationId(null)}
                />
              </div>
            )}
          </div>

          {/* Right Sidebar Panels */}
          <div className="w-full lg:w-80 shrink-0 flex flex-col gap-4 h-full">
            {viewMode === "overview" && (
              <>
                <div className="flex-[0.8] min-h-0"><ArchitectureHealth breakdown={MOCK_ARCHITECTURE_DATA.healthBreakdown} overview={MOCK_ARCHITECTURE_DATA.overview} /></div>
                <div className="flex-1 min-h-0"><ArchitectureBoundaries boundaries={MOCK_ARCHITECTURE_DATA.boundaries} /></div>
                <div className="flex-1 min-h-0"><ArchitectureRisks risks={MOCK_ARCHITECTURE_DATA.risks} /></div>
              </>
            )}
            
            {viewMode === "layers" && (
              <>
                <div className="flex-1 min-h-0"><ArchitectureBoundaries boundaries={MOCK_ARCHITECTURE_DATA.boundaries} /></div>
                <div className="flex-[0.8] min-h-0"><ArchitectureHistory history={MOCK_ARCHITECTURE_DATA.history} /></div>
              </>
            )}
            
            {viewMode === "boundaries" && (
              <>
                <div className="flex-1 min-h-0"><ArchitectureBoundaries boundaries={MOCK_ARCHITECTURE_DATA.boundaries} /></div>
              </>
            )}
            
            {viewMode === "violations" && (
              <>
                <div className="flex-1 min-h-0">
                  <ArchitectureViolations 
                    violations={MOCK_ARCHITECTURE_DATA.violations}
                    onSelect={(id) => setSelectedViolationId(id)}
                    selectedId={selectedViolationId}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
