"use client";

import { useState, useMemo, useEffect } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { MOCK_DECISION_DATA } from "@/lib/mock-data/decision-intelligence";
import { DecisionHeader } from "@/components/decision-intelligence/decision-header";
import { DecisionHealthOverview } from "@/components/decision-intelligence/decision-health-overview";
import { RecommendationFilters } from "@/components/decision-intelligence/recommendation-filters";
import { RecommendationList } from "@/components/decision-intelligence/recommendation-list";
import { RecommendationDetails } from "@/components/decision-intelligence/recommendation-details";
import { DecisionCategoryBreakdown } from "@/components/decision-intelligence/decision-category-breakdown";
import { ImpactEffortMatrix } from "@/components/decision-intelligence/impact-effort-matrix";
import { TechnicalDebtAnalysis } from "@/components/decision-intelligence/technical-debt-analysis";
import { DecisionHistory } from "@/components/decision-intelligence/decision-history";
import { DecisionSummary } from "@/components/decision-intelligence/decision-summary";
import { DecisionAnalysisRunner } from "@/components/decision-intelligence/decision-analysis-runner";
import { DecisionCategory, DecisionRecommendation, EffortLevel, ImpactLevel, RecommendationPriority, RecommendationStatus, DecisionAnalysisState } from "@/types/decision-intelligence-ui";

export default function DecisionIntelligencePage() {
  const [data, setData] = useState(MOCK_DECISION_DATA);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<DecisionCategory | "ALL">("ALL");
  const [priorityFilter, setPriorityFilter] = useState<RecommendationPriority | "ALL">("ALL");
  const [statusFilter, setStatusFilter] = useState<RecommendationStatus | "ALL">("ALL");
  const [impactFilter, setImpactFilter] = useState<ImpactLevel | "ALL">("ALL");
  const [effortFilter, setEffortFilter] = useState<EffortLevel | "ALL">("ALL");
  
  const [selectedRecId, setSelectedRecId] = useState<string | null>(null);
  const [lastAnalysis, setLastAnalysis] = useState("12 mins ago");
  
  // Analysis Runner State
  const [analysisState, setAnalysisState] = useState<DecisionAnalysisState>("Ready");
  const [showRunner, setShowRunner] = useState(false);

  // Keyboard shortcut to close drawer
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSelectedRecId(null);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleStatusChange = (id: string, newStatus: RecommendationStatus) => {
    setData((prev) => ({
      ...prev,
      recommendations: prev.recommendations.map((r) => 
        r.id === id ? { ...r, status: newStatus } : r
      )
    }));
  };

  const runAnalysis = () => {
    setShowRunner(true);
    setAnalysisState("Analyzing Architecture");
    
    const steps: DecisionAnalysisState[] = [
      "Analyzing Dependencies",
      "Analyzing Governance",
      "Analyzing Technical Debt",
      "Calculating Impact",
      "Generating Recommendations",
      "Complete"
    ];
    
    const delay = 600;
    steps.forEach((step, index) => {
      setTimeout(() => {
        setAnalysisState(step);
        if (step === "Complete") {
          setTimeout(() => {
            setShowRunner(false);
            setAnalysisState("Ready");
            setLastAnalysis("Just now");
          }, 1000);
        }
      }, delay * (index + 1));
    });
  };

  const filteredRecommendations = useMemo(() => {
    return data.recommendations.filter((rec) => {
      if (categoryFilter !== "ALL" && rec.category !== categoryFilter) return false;
      if (priorityFilter !== "ALL" && rec.priority !== priorityFilter) return false;
      if (statusFilter !== "ALL" && rec.status !== statusFilter) return false;
      if (impactFilter !== "ALL" && rec.impact !== impactFilter) return false;
      if (effortFilter !== "ALL" && rec.effort !== effortFilter) return false;
      
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          rec.title.toLowerCase().includes(query) ||
          rec.problem.toLowerCase().includes(query) ||
          rec.evidence.toLowerCase().includes(query) ||
          rec.affectedComponents.some(c => c.toLowerCase().includes(query)) ||
          rec.category.toLowerCase().includes(query)
        );
      }
      return true;
    });
  }, [data.recommendations, categoryFilter, priorityFilter, statusFilter, impactFilter, effortFilter, searchQuery]);

  // Derived stats
  const derivedHealth = useMemo(() => {
    const active = data.recommendations.filter(r => r.status !== "DISMISSED");
    const highPriority = active.filter(r => r.priority === "CRITICAL" || r.priority === "HIGH").length;
    const archRisks = active.filter(r => r.category === "ARCHITECTURE").length;
    return {
      ...data.stats.health,
      recommendations: data.recommendations.length,
      highPriority,
      architectureRisks: archRisks,
    };
  }, [data]);

  const categoryStats = useMemo(() => {
    const cats: DecisionCategory[] = ["ARCHITECTURE", "DEPENDENCIES", "SECURITY", "CODE_QUALITY", "PERFORMANCE", "MAINTAINABILITY"];
    return cats.map(cat => {
      const recs = data.recommendations.filter(r => r.category === cat);
      const activeRecs = recs.filter(r => r.status !== "DISMISSED");
      const highPri = activeRecs.filter(r => r.priority === "CRITICAL" || r.priority === "HIGH").length;
      return {
        category: cat,
        recommendations: recs.length,
        highPriority: highPri,
        riskCount: recs.length,
        averageConfidence: recs.length ? Math.round(recs.reduce((acc, r) => acc + r.confidence, 0) / recs.length) : 0,
      };
    }).sort((a, b) => b.recommendations - a.recommendations);
  }, [data]);

  const selectedRec = data.recommendations.find(r => r.id === selectedRecId) || null;
  const topCategory = categoryStats.length > 0 ? categoryStats[0].category.replace("_", " ") : "Architecture";

  return (
    <AppShell breadcrumb="Workspace > Decision Intelligence">
      <div className="p-6">
        <DecisionHeader 
          health={derivedHealth} 
          lastAnalysis={lastAnalysis} 
          onRunAnalysis={runAnalysis}
          isRunning={showRunner}
        />
        
        <DecisionHealthOverview health={derivedHealth} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2 space-y-6">
            <ImpactEffortMatrix 
              points={data.matrixPoints} 
              onSelect={setSelectedRecId} 
            />
            
            <div id="recommendations-list">
              <h3 className="text-lg font-bold text-[#F8FAFC] mb-4">Priority Recommendations</h3>
              <RecommendationFilters 
                searchQuery={searchQuery} setSearchQuery={setSearchQuery}
                categoryFilter={categoryFilter} setCategoryFilter={setCategoryFilter}
                priorityFilter={priorityFilter} setPriorityFilter={setPriorityFilter}
                statusFilter={statusFilter} setStatusFilter={setStatusFilter}
                impactFilter={impactFilter} setImpactFilter={setImpactFilter}
                effortFilter={effortFilter} setEffortFilter={setEffortFilter}
              />
              <RecommendationList 
                recommendations={filteredRecommendations}
                selectedId={selectedRecId}
                onSelect={setSelectedRecId}
              />
            </div>
          </div>
          
          <div className="space-y-6">
            <DecisionSummary health={derivedHealth} topCategory={topCategory} />
            <DecisionCategoryBreakdown stats={categoryStats} />
            <TechnicalDebtAnalysis debt={data.stats.debt} />
            <DecisionHistory history={data.history} />
          </div>
        </div>
      </div>

      <RecommendationDetails 
        recommendation={selectedRec} 
        onClose={() => setSelectedRecId(null)}
        onStatusChange={handleStatusChange}
      />
      
      <DecisionAnalysisRunner 
        state={analysisState}
        isVisible={showRunner}
      />
    </AppShell>
  );
}
