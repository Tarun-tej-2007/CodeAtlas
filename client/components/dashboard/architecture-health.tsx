"use client";

import { useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { HealthTrendPoint } from "@/types/dashboard";
import { formatPercentage } from "@/lib/utils";

interface ArchitectureHealthProps {
  trendData: HealthTrendPoint[];
  stats: {
    current: number;
    previous: number;
    trend: number;
  };
}

type TimeframeOption = "7a" | "30d" | "90d" | "1y";

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    value: number;
    payload: HealthTrendPoint;
  }>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="rounded-md border border-[#1E293B] bg-[#0B1220] p-2.5 shadow-lg">
        <div className="flex items-center justify-between gap-4">
          <span className="text-xs font-mono text-[#94A3B8]">{data.name}</span>
          <span className="text-[10px] font-mono text-[#64748B]">{data.date}</span>
        </div>
        <div className="mt-1 flex items-baseline gap-1">
          <span className="text-sm font-bold font-mono text-[#F8FAFC]">
            {payload[0].value}
          </span>
          <span className="text-[10px] text-[#64748B]">score</span>
        </div>
        {data.commitHash && (
          <div className="mt-1 text-[10px] font-mono text-[#3B82F6]">
            commit: {data.commitHash}
          </div>
        )}
      </div>
    );
  }
  return null;
}

export function ArchitectureHealth({ trendData, stats }: ArchitectureHealthProps) {
  const [timeframe, setTimeframe] = useState<TimeframeOption>("7a");

  const timeframeButtons: { id: TimeframeOption; label: string }[] = [
    { id: "7a", label: "Last 7 analyses" },
    { id: "30d", label: "30D" },
    { id: "90d", label: "90D" },
    { id: "1y", label: "1Y" },
  ];

  return (
    <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4.5 shadow-xs flex flex-col justify-between h-full">
      {/* Header & Controls */}
      <div>
        <div className="flex flex-col gap-2.5 sm:flex-row sm:items-center sm:justify-between pb-2 border-b border-[#1E293B]">
          <div>
            <h2 className="text-sm font-semibold tracking-tight text-[#F8FAFC]">
              Architecture Health
            </h2>
            <p className="text-xs text-[#94A3B8] mt-0.5">
              Health score over last 7 analyses
            </p>
          </div>

          {/* Timeframe selector pill */}
          <div className="flex items-center rounded-md border border-[#1E293B] bg-[#0B1220] p-0.5">
            {timeframeButtons.map((btn) => (
              <button
                key={btn.id}
                type="button"
                onClick={() => setTimeframe(btn.id)}
                className={`rounded px-2.5 py-1 text-[11px] font-medium transition-colors ${
                  timeframe === btn.id
                    ? "bg-[#141E2E] text-[#F8FAFC] border border-[#334155]/60"
                    : "text-[#94A3B8] hover:text-[#CBD5E1]"
                }`}
              >
                {btn.label}
              </button>
            ))}
          </div>
        </div>

        {/* Numerical Stats Row */}
        <div className="mt-3 flex flex-wrap items-center gap-6 border-b border-[#1E293B] pb-3">
          <div>
            <span className="text-[11px] text-[#64748B]">Current</span>
            <div className="text-xl font-bold font-mono text-[#F8FAFC] leading-tight">
              {stats.current}
            </div>
          </div>

          <div className="h-7 w-px bg-[#1E293B]" />

          <div>
            <span className="text-[11px] text-[#64748B]">Previous</span>
            <div className="text-xl font-bold font-mono text-[#94A3B8] leading-tight">
              {stats.previous}
            </div>
          </div>

          <div className="h-7 w-px bg-[#1E293B]" />

          <div>
            <span className="text-[11px] text-[#64748B]">Trend</span>
            <div className="text-xl font-bold font-mono text-[#22C55E] leading-tight">
              {formatPercentage(stats.trend)}
            </div>
          </div>
        </div>
      </div>

      {/* Chart Visualization */}
      <div className="mt-3.5 h-52 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={trendData}
            margin={{ top: 10, right: 10, left: -25, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              domain={[60, 100]}
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              ticks={[60, 70, 80, 90, 100]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="score"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={{ fill: "#3B82F6", stroke: "#0B1220", strokeWidth: 2, r: 4 }}
              activeDot={{ fill: "#60A5FA", stroke: "#3B82F6", strokeWidth: 2, r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
