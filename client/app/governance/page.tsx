"use client";

import { useState, useMemo } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { MOCK_GOVERNANCE_DATA } from "@/lib/mock-data/governance";
import { PolicyCategory } from "@/types/governance-ui";

import { GovernanceHeader } from "@/components/governance/governance-header";
import { GovernanceHealthOverview } from "@/components/governance/governance-health-overview";
import { GovernanceCategoryCompliance } from "@/components/governance/governance-category-compliance";
import { GovernanceComplianceTrend } from "@/components/governance/governance-compliance-trend";
import { GovernancePolicyList } from "@/components/governance/governance-policy-list";
import { GovernancePolicyDetails } from "@/components/governance/governance-policy-details";
import { GovernanceViolationFilters } from "@/components/governance/governance-violation-filters";
import { GovernanceViolations } from "@/components/governance/governance-violations";
import { GovernanceViolationDetails } from "@/components/governance/governance-violation-details";
import { GovernanceExceptions } from "@/components/governance/governance-exceptions";
import { GovernanceActivityTimeline } from "@/components/governance/governance-activity-timeline";
import { GovernanceSummary } from "@/components/governance/governance-summary";
import { GovernanceSettings } from "@/components/governance/governance-settings";
import { GovernanceRequestException } from "@/components/governance/governance-request-exception";

export default function GovernancePage() {
  // Local state to simulate interactions
  const [data, setData] = useState(MOCK_GOVERNANCE_DATA);
  
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [requestExceptionId, setRequestExceptionId] = useState<string | null>(null);

  // Policy List State
  const [selectedPolicyId, setSelectedPolicyId] = useState<string | null>(null);
  const [policySearch, setPolicySearch] = useState("");
  const [policyCategory, setPolicyCategory] = useState("All");
  const [policyStatus, setPolicyStatus] = useState("All");

  // Violation List State
  const [selectedViolationId, setSelectedViolationId] = useState<string | null>(null);
  const [violationSearch, setViolationSearch] = useState("");
  const [violationCategory, setViolationCategory] = useState("All");
  const [violationSeverity, setViolationSeverity] = useState("All");
  const [violationStatus, setViolationStatus] = useState("Open"); // Default to Open
  const [violationPolicy, setViolationPolicy] = useState("All Policies");

  const handleRunCheck = () => {
    setIsEvaluating(true);
    setTimeout(() => {
      setIsEvaluating(false);
      setData(prev => {
        // Minor mock update: update the last evaluated timestamp
        const newPolicies = prev.policies.map(p => ({ ...p, lastEvaluated: "Just now" }));
        const newActivities = [
          { id: `act-${Date.now()}`, type: "evaluation", date: "Just now", message: `Governance check completed (Compliance: ${prev.stats.health.compliance}%)`, actor: "System", category: "Architecture" as PolicyCategory },
          ...prev.activities
        ];
        return { ...prev, policies: newPolicies, activities: newActivities };
      });
    }, 2000);
  };

  const handleMarkResolved = (violationId: string) => {
    setData(prev => {
      const vIndex = prev.violations.findIndex(v => v.id === violationId);
      if (vIndex === -1) return prev;
      
      const newViolations = [...prev.violations];
      newViolations[vIndex] = { ...newViolations[vIndex], status: "Resolved" };

      const v = newViolations[vIndex];
      const newHealth = { ...prev.stats.health };
      newHealth.openViolations -= 1;
      newHealth.resolvedViolations += 1;
      if (v.severity === "Critical") newHealth.criticalViolations -= 1;

      return {
        ...prev,
        violations: newViolations,
        stats: { ...prev.stats, health: newHealth }
      };
    });
    setSelectedViolationId(null);
  };

  const handleSubmitException = (violationId: string, reason: string, expiry: string) => {
    setData(prev => {
      const v = prev.violations.find(vx => vx.id === violationId);
      if (!v) return prev;
      
      const newException = {
        id: `exc-${Date.now()}`,
        policyId: v.policyId,
        component: v.component,
        reason,
        expiry,
        approvedBy: "Current User",
        status: "Active" as const,
        scope: "Component"
      };

      const newHealth = { ...prev.stats.health };
      newHealth.activeExceptions += 1;

      return {
        ...prev,
        exceptions: [newException, ...prev.exceptions],
        stats: { ...prev.stats, health: newHealth }
      };
    });
    setRequestExceptionId(null);
    setSelectedViolationId(null); // Close the violation drawer
  };

  // Derived Data (Filtering)
  const filteredPolicies = useMemo(() => {
    return data.policies.filter(p => {
      if (policyCategory !== "All" && p.category !== policyCategory) return false;
      if (policyStatus !== "All" && p.status !== policyStatus) return false;
      if (policySearch) {
        const q = policySearch.toLowerCase();
        if (!p.name.toLowerCase().includes(q) && !p.description.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [data.policies, policyCategory, policyStatus, policySearch]);

  const filteredViolations = useMemo(() => {
    return data.violations.filter(v => {
      if (violationStatus !== "All" && v.status !== violationStatus) return false;
      if (violationSeverity !== "All" && v.severity !== violationSeverity) return false;
      if (violationPolicy !== "All Policies" && v.policyId !== violationPolicy) return false;
      
      const policy = data.policies.find(p => p.id === v.policyId);
      if (violationCategory !== "All" && policy?.category !== violationCategory) return false;
      
      if (violationSearch) {
        const q = violationSearch.toLowerCase();
        if (!v.message.toLowerCase().includes(q) && !v.component.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [data.violations, data.policies, violationStatus, violationSeverity, violationPolicy, violationCategory, violationSearch]);

  const selectedPolicy = selectedPolicyId ? data.policies.find(p => p.id === selectedPolicyId) : null;
  const selectedViolation = selectedViolationId ? data.violations.find(v => v.id === selectedViolationId) : null;
  const selectedViolationPolicy = selectedViolation ? data.policies.find(p => p.id === selectedViolation.policyId) : undefined;
  const requestExceptionPolicy = requestExceptionId ? data.policies.find(p => p.id === data.violations.find(v => v.id === requestExceptionId)?.policyId) : undefined;

  return (
    <AppShell breadcrumb="Governance">
      <div className="flex flex-col bg-[#080D18] pb-6 relative">
        <GovernanceHeader 
          healthScore={data.stats.health.score}
          lastEvaluated="12 mins ago" // In a real app derived from data
          isEvaluating={isEvaluating}
          onRunCheck={handleRunCheck}
          onOpenSettings={() => setIsSettingsOpen(true)}
        />

        <GovernanceHealthOverview health={data.stats.health} />

        <div className="mb-8">
          <GovernancePolicyList 
            policies={filteredPolicies}
            searchQuery={policySearch}
            onSearchChange={setPolicySearch}
            statusFilter={policyStatus}
            onStatusFilterChange={setPolicyStatus}
            categoryFilter={policyCategory}
            onCategoryFilterChange={setPolicyCategory}
            onSelectPolicy={(p) => setSelectedPolicyId(p.id)}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <GovernanceComplianceTrend data={data.stats.trend} />
          </div>
          <div className="lg:col-span-1">
            <GovernanceCategoryCompliance 
              categories={data.stats.categories} 
              onCategoryClick={(cat) => {
                setPolicyCategory(cat);
                // Scroll to top or just let them see the filtered policies above
              }} 
            />
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-semibold text-[#F8FAFC] mb-4">Governance Violations</h2>
          <GovernanceViolationFilters 
            searchQuery={violationSearch}
            onSearchChange={setViolationSearch}
            categoryFilter={violationCategory}
            onCategoryFilterChange={setViolationCategory}
            severityFilter={violationSeverity}
            onSeverityFilterChange={setViolationSeverity}
            statusFilter={violationStatus}
            onStatusFilterChange={setViolationStatus}
            policyFilter={violationPolicy}
            onPolicyFilterChange={setViolationPolicy}
            availablePolicies={data.policies}
          />
          <GovernanceViolations 
            violations={filteredViolations}
            onSelectViolation={(v) => setSelectedViolationId(v.id)}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="h-96">
            <GovernanceExceptions exceptions={data.exceptions} />
          </div>
          <div className="h-96">
            <GovernanceActivityTimeline activities={data.activities} />
          </div>
        </div>

        <GovernanceSummary stats={data.stats} />

        {/* Drawers and Modals */}
        {selectedPolicy && (
          <div className="fixed inset-y-0 right-0 z-50 shadow-2xl flex border-l border-[#1E293B]">
            <GovernancePolicyDetails 
              policy={selectedPolicy} 
              onClose={() => setSelectedPolicyId(null)} 
            />
          </div>
        )}

        {selectedViolation && (
          <div className="fixed inset-y-0 right-0 z-50 shadow-2xl flex border-l border-[#1E293B]">
            <GovernanceViolationDetails 
              violation={selectedViolation} 
              policy={selectedViolationPolicy}
              onClose={() => setSelectedViolationId(null)} 
              onMarkResolved={handleMarkResolved}
              onRequestException={setRequestExceptionId}
            />
          </div>
        )}

        {requestExceptionId && (
          <GovernanceRequestException
            violationId={requestExceptionId}
            policyId={requestExceptionPolicy?.name || requestExceptionPolicy?.id || "Unknown Policy"}
            onClose={() => setRequestExceptionId(null)}
            onSubmit={handleSubmitException}
          />
        )}

        {isSettingsOpen && (
          <GovernanceSettings onClose={() => setIsSettingsOpen(false)} />
        )}
      </div>
    </AppShell>
  );
}
