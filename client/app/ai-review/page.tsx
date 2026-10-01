"use client";

import { useState, useMemo } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { MOCK_AI_REVIEW_DATA } from "@/lib/mock-data/ai-architecture-review";
import { FindingStatus } from "@/types/ai-architecture-review-ui";

import { AIReviewHeader } from "@/components/ai-architecture-review/ai-review-header";
import { AIReviewOverview } from "@/components/ai-architecture-review/ai-review-overview";
import { ArchitectureScoreBreakdown } from "@/components/ai-architecture-review/architecture-score-breakdown";
import { AIReviewSummary } from "@/components/ai-architecture-review/ai-review-summary";
import { ReviewFindingFilters } from "@/components/ai-architecture-review/review-finding-filters";
import { ReviewFindings } from "@/components/ai-architecture-review/review-findings";
import { FindingDetails } from "@/components/ai-architecture-review/finding-details";
import { ReviewRecommendations } from "@/components/ai-architecture-review/review-recommendations";
import { RecommendationDetails } from "@/components/ai-architecture-review/recommendation-details";
import { ArchitectureStrengths } from "@/components/ai-architecture-review/architecture-strengths";
import { ReviewEvidence } from "@/components/ai-architecture-review/review-evidence";
import { ReviewHistory } from "@/components/ai-architecture-review/review-history";
import { ReviewRunner } from "@/components/ai-architecture-review/review-runner";

export default function AIReviewPage() {
  const [data, setData] = useState(MOCK_AI_REVIEW_DATA);
  const [isRunning, setIsRunning] = useState(false);
  
  // Local state for filters
  const [searchQuery, setSearchQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [confidenceFilter, setConfidenceFilter] = useState("ALL");

  // Selection state
  const [selectedFindingId, setSelectedFindingId] = useState<string | null>(null);
  const [selectedRecId, setSelectedRecId] = useState<string | null>(null);

  // Derived filtered data
  const filteredFindings = useMemo(() => {
    return data.findings.filter(f => {
      // Search
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        if (!f.title.toLowerCase().includes(q) && 
            !f.description.toLowerCase().includes(q) &&
            !f.category.toLowerCase().includes(q) &&
            !f.evidence.toLowerCase().includes(q) &&
            !f.affectedComponents.some(c => c.toLowerCase().includes(q))) {
          return false;
        }
      }
      
      // Selects
      if (severityFilter !== "ALL" && f.severity !== severityFilter) return false;
      if (categoryFilter !== "ALL" && f.category !== categoryFilter) return false;
      if (statusFilter !== "ALL" && f.status !== statusFilter) return false;
      
      if (confidenceFilter !== "ALL") {
        const confReq = parseInt(confidenceFilter, 10);
        if (f.confidence < confReq) return false;
      }
      
      return true;
    });
  }, [data.findings, searchQuery, severityFilter, categoryFilter, statusFilter, confidenceFilter]);

  const handleFindingStatusChange = (id: string, newStatus: FindingStatus) => {
    setData(prev => ({
      ...prev,
      findings: prev.findings.map(f => f.id === id ? { ...f, status: newStatus } : f)
    }));
  };

  const handleRecStatusChange = (id: string, newStatus: FindingStatus) => {
    setData(prev => ({
      ...prev,
      recommendations: prev.recommendations.map(r => r.id === id ? { ...r, status: newStatus } : r)
    }));
  };

  const selectedFinding = useMemo(() => 
    data.findings.find(f => f.id === selectedFindingId) || null
  , [data.findings, selectedFindingId]);

  const selectedRec = useMemo(() => 
    data.recommendations.find(r => r.id === selectedRecId) || null
  , [data.recommendations, selectedRecId]);

  return (
    <AppShell breadcrumb="AI Architecture Review">
      <div className="p-6 max-w-[1600px] mx-auto min-h-full">
        <AIReviewHeader 
          score={data.stats.score} 
          lastReviewTime="18 mins ago" 
          onRunReview={() => setIsRunning(true)} 
          isRunning={isRunning} 
        />
        
        <AIReviewOverview stats={data.stats} />
        
        <div className="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-6">
          <div className="lg:col-span-2 xl:col-span-3">
            <AIReviewSummary summary={data.summary} />
          </div>
          <div className="lg:col-span-1 xl:col-span-1">
            <ArchitectureScoreBreakdown categories={data.categories} />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-6">
            <div>
              <h2 className="text-lg font-bold text-[#F8FAFC] mb-4">Architecture Findings</h2>
              <ReviewFindingFilters 
                searchQuery={searchQuery} setSearchQuery={setSearchQuery}
                severityFilter={severityFilter} setSeverityFilter={setSeverityFilter}
                categoryFilter={categoryFilter} setCategoryFilter={setCategoryFilter}
                statusFilter={statusFilter} setStatusFilter={setStatusFilter}
                confidenceFilter={confidenceFilter} setConfidenceFilter={setConfidenceFilter}
              />
              <ReviewFindings 
                findings={filteredFindings} 
                onSelect={setSelectedFindingId} 
                selectedId={selectedFindingId} 
              />
            </div>
          </div>
          
          {/* Right Sidebar Area */}
          <div className="space-y-6">
            <ReviewRecommendations 
              recommendations={data.recommendations} 
              onSelect={setSelectedRecId} 
              selectedId={selectedRecId} 
            />
            <ArchitectureStrengths strengths={data.strengths} />
            <ReviewEvidence evidence={data.evidence} />
            <ReviewHistory history={data.history} />
          </div>
        </div>
      </div>
      
      {/* Modals and Drawers */}
      <ReviewRunner 
        isRunning={isRunning} 
        onComplete={() => setIsRunning(false)} 
      />
      
      <FindingDetails 
        finding={selectedFinding} 
        onClose={() => setSelectedFindingId(null)} 
        onStatusChange={handleFindingStatusChange} 
      />
      
      <RecommendationDetails 
        recommendation={selectedRec} 
        onClose={() => setSelectedRecId(null)} 
        onStatusChange={handleRecStatusChange} 
      />
    </AppShell>
  );
}
