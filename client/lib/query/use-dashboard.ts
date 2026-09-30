"use client";

import { useQuery } from "@tanstack/react-query";
import { getDashboardData } from "@/lib/api/dashboard";

export function useDashboardData() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: getDashboardData,
  });
}
