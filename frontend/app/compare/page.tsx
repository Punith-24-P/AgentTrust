"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { GitCompare, ArrowRight, RefreshCw } from "lucide-react";
import { fetchRuns, fetchRunComparison } from "@/lib/api";
import { RunItem, RunComparison } from "@/types";
import RunComparisonView from "@/components/RunComparisonView";

function CompareContent() {
  const searchParams = useSearchParams();
  const initialBefore = searchParams.get("before") || "";
  const initialAfter = searchParams.get("after") || "";

  const [runs, setRuns] = useState<RunItem[]>([]);
  const [beforeId, setBeforeId] = useState(initialBefore);
  const [afterId, setAfterId] = useState(initialAfter);
  const [comparison, setComparison] = useState<RunComparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRuns().then((data) => {
      const completed = data.filter((r) => r.status === "COMPLETED");
      setRuns(completed);

      // Auto-select if at least 2 runs exist and nothing selected
      if (!beforeId && completed.length >= 2) {
        setBeforeId(completed[1].id);
        setAfterId(completed[0].id);
      } else if (!beforeId && completed.length === 1) {
        setBeforeId(completed[0].id);
      }
    });
  }, []);

  useEffect(() => {
    if (beforeId && afterId && beforeId !== afterId) {
      loadComparison(beforeId, afterId);
    }
  }, [beforeId, afterId]);

  const loadComparison = async (bId: string, aId: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchRunComparison(bId, aId);
      setComparison(data);
    } catch (err: any) {
      setError(err.message || "Failed to compare runs.");
      setComparison(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header & Run Selector Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <GitCompare className="w-5 h-5 text-sky-400" />
            <span>Before / After Run Comparison</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Compare two experimental runs on identical datasets to verify reliability regressions or gains.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
              Baseline Run (Before)
            </label>
            <select
              value={beforeId}
              onChange={(e) => setBeforeId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
            >
              <option value="">Select Baseline Run...</option>
              {runs.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.id.slice(0, 8)} - {r.agent_name} ({r.agent_version}) - Score: {Math.round((r.composite_score || 0) * 100)}%
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-sky-400 uppercase tracking-wider mb-1.5">
              Optimized Run (After)
            </label>
            <select
              value={afterId}
              onChange={(e) => setAfterId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
            >
              <option value="">Select After Run...</option>
              {runs.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.id.slice(0, 8)} - {r.agent_name} ({r.agent_version}) - Score: {Math.round((r.composite_score || 0) * 100)}%
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading && (
        <div className="py-16 text-center space-y-2">
          <div className="w-7 h-7 border-2 border-sky-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-slate-400">Computing differential metrics...</p>
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-950/40 border border-rose-800/80 rounded-xl text-rose-300 text-xs">
          {error}
        </div>
      )}

      {comparison && !loading && (
        <RunComparisonView comparison={comparison} />
      )}
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={<div className="py-16 text-center text-xs text-slate-400">Loading comparison view...</div>}>
      <CompareContent />
    </Suspense>
  );
}
