import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat("en-US").format(num);
}

export function formatPercentage(val: number): string {
  const prefix = val > 0 ? "+" : "";
  return `${prefix}${val.toFixed(1)}%`;
}

export function getHealthStatus(score: number): {
  label: "Healthy" | "Warning" | "Critical";
  colorClass: string;
  bgClass: string;
  borderClass: string;
} {
  if (score >= 80) {
    return {
      label: "Healthy",
      colorClass: "text-[#22C55E]",
      bgClass: "bg-[#22C55E]/10",
      borderClass: "border-[#22C55E]/20",
    };
  }
  if (score >= 60) {
    return {
      label: "Warning",
      colorClass: "text-[#F59E0B]",
      bgClass: "bg-[#F59E0B]/10",
      borderClass: "border-[#F59E0B]/20",
    };
  }
  return {
    label: "Critical",
    colorClass: "text-[#EF4444]",
    bgClass: "bg-[#EF4444]/10",
    borderClass: "border-[#EF4444]/20",
  };
}
