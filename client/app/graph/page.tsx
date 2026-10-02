"use client";

import { useState, useMemo, useRef, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { DependencyGraphHeader } from "@/components/dependency-graph/dependency-graph-header";
import { DependencyGraphToolbar } from "@/components/dependency-graph/dependency-graph-toolbar";
import { DependencyGraphCanvas } from "@/components/dependency-graph/dependency-graph-canvas";
import { DependencyFilterPanel, GraphFilters } from "@/components/dependency-graph/dependency-filter-panel";
import { DependencyNodeDetails } from "@/components/dependency-graph/dependency-node-details";
import { DependencyIssuesPanel } from "@/components/dependency-graph/dependency-issues-panel";
import { DependencyGraphLegend } from "@/components/dependency-graph/dependency-graph-legend";

import { MOCK_GRAPH_DATA, MOCK_GRAPH_STATS, MOCK_GRAPH_ISSUES } from "@/lib/mock-data/dependency-graph";

export default function DependencyGraphPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [layout, setLayout] = useState<"hierarchical" | "force" | "circular">("hierarchical");
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  
  const [filters, setFilters] = useState<GraphFilters>({
    layer: "All",
    relationship: "All",
    risk: "All",
    issues: "All",
  });

  const handleClearFilters = useCallback(() => {
    setFilters({ layer: "All", relationship: "All", risk: "All", issues: "All" });
    setSearchQuery("");
  }, []);

  // Filter Data
  const filteredData = useMemo(() => {
    let nodes = MOCK_GRAPH_DATA.nodes;
    let edges = MOCK_GRAPH_DATA.edges;

    if (filters.layer !== "All") nodes = nodes.filter(n => n.layer === filters.layer);
    if (filters.risk !== "All") nodes = nodes.filter(n => n.risk === filters.risk);
    if (filters.issues === "Has Issues") nodes = nodes.filter(n => n.issueCount > 0);
    if (filters.issues === "No Issues") nodes = nodes.filter(n => n.issueCount === 0);

    const validNodeIds = new Set(nodes.map(n => n.id));
    edges = edges.filter(e => validNodeIds.has(e.source) && validNodeIds.has(e.target));
    
    if (filters.relationship !== "All") edges = edges.filter(e => e.relationship === filters.relationship);

    return { nodes, edges };
  }, [filters]);

  // Zoom/Pan controllers using window events or React Flow instance if we had access to it easily here.
  // We passed these down, but actually XYFlow uses useReactFlow hook which is inside the provider.
  // For simplicity, we just pass down state triggers if needed, or we omit external zoom/pan if not strictly requested to be external.
  // The toolbar buttons just need to trigger it. We can do that by creating an event bus or moving toolbar inside provider.
  // Since we already built Toolbar outside, we'll use a hack to dispatch a custom event.
  const handleZoomIn = () => document.dispatchEvent(new CustomEvent("xyflow-zoom-in"));
  const handleZoomOut = () => document.dispatchEvent(new CustomEvent("xyflow-zoom-out"));
  const handleFitView = () => document.dispatchEvent(new CustomEvent("xyflow-fit-view"));
  const handleReset = () => document.dispatchEvent(new CustomEvent("xyflow-reset"));

  return (
    <AppShell breadcrumb="Dependency Graph">
      <div className="flex flex-col h-[calc(100vh-theme(spacing.14)-theme(spacing.8))] overflow-hidden">
        
        <DependencyGraphHeader stats={MOCK_GRAPH_STATS} />

        <div className="flex flex-col flex-1 border border-[#1E293B] bg-[#0F1726] rounded-lg shadow-xs overflow-hidden">
          <DependencyGraphToolbar 
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            layout={layout}
            onLayoutChange={setLayout}
            onZoomIn={handleZoomIn}
            onZoomOut={handleZoomOut}
            onFitView={handleFitView}
            onReset={handleReset}
          />

          <div className="flex flex-1 overflow-hidden relative">
            <div className="flex flex-col shrink-0 w-full sm:w-72 bg-[#0F1726] border-r border-[#1E293B] h-full overflow-hidden">
              <div className="flex-1 overflow-hidden flex flex-col">
                <DependencyFilterPanel 
                  filters={filters}
                  onFilterChange={setFilters}
                  onClear={handleClearFilters}
                />
              </div>
              <div className="h-2/5 shrink-0 border-t border-[#1E293B] overflow-hidden flex flex-col">
                <DependencyIssuesPanel 
                  issues={MOCK_GRAPH_ISSUES} 
                  onIssueSelect={(nodeId) => {
                    setSelectedNodeId(nodeId);
                    document.dispatchEvent(new CustomEvent("xyflow-fit-view"));
                  }}
                />
              </div>
            </div>

            <div className="flex-1 relative bg-[#080D18]">
              {filteredData.nodes.length > 0 ? (
                <DependencyGraphCanvas 
                  data={filteredData}
                  layout={layout}
                  selectedNodeId={selectedNodeId}
                  onNodeSelect={setSelectedNodeId}
                  searchQuery={searchQuery}
                />
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-[#94A3B8]">
                  <p className="text-sm font-medium">No matching components</p>
                  <button onClick={handleClearFilters} className="mt-2 text-xs text-[#3B82F6] hover:underline">
                    Clear Filters
                  </button>
                </div>
              )}

              {/* Legend */}
              <div className="absolute bottom-4 right-4 z-30 bg-[#0F1726]/90 backdrop-blur-sm border border-[#1E293B] rounded-lg p-3 hidden sm:block shadow-xs">
                <DependencyGraphLegend />
              </div>
            </div>

            {/* Right Drawer for Node Details */}
            {selectedNodeId && (
              <div className="absolute top-0 right-0 h-full bottom-0 z-30 shadow-[-4px_0_15px_rgba(0,0,0,0.5)]">
                <DependencyNodeDetails 
                  nodeId={selectedNodeId}
                  data={MOCK_GRAPH_DATA}
                  onClose={() => setSelectedNodeId(null)}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
