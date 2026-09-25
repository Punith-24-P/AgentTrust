"use client";

import React from "react";
import { ArrowUpRight, ArrowDownRight, Minus, GitCompare } from "lucide-react";
import { RunComparison } from "@/types";

interface RunComparisonViewProps {
  comparison: RunComparison;
}

export default function RunComparisonView({ comparison }: RunComparisonViewProps) {
  const metricLabels: Record<string, string> = {
    composite_score: "Composite Reliability",
    overall_pass_rate: "Overall Pass Rate",
    correctness_score: "Correctness Rate",
    grounding_score: "Grounding Score",
    citation_score: "Citation Accuracy",
    translation_score: "Translation Fidelity",
    trajectory_score: "Trajectory Integrity",
  };

  const renderDeltaBadge = (delta: number) => {
    const pct = Math.round(delta * 1000) / 10;
    if (delta > 0) {
      return (
        <span className="flex items-center text-xs font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 rounded-full">
          <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
          +{pct}%
        </span>
      );
    } else if (delta < 0) {
      return (
        <span className="flex items-center text-xs font-bold text-rose-400 bg-rose-950/60 border border-rose-800/60 px-2 py-0.5 rounded-full">
          <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
          {pct}%
        </span>
      );
    }
    return (
      <span className="flex items-center text-xs font-medium text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full">
        <Minus className="w-3.5 h-3.5 mr-0.5" />
        0.0%
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Run Header Comparison Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-center space-x-2 text-slate-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <GitCompare className="w-4 h-4 text-sky-400" />
          <span>Before / After Experiment Comparison</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
            <span className="text-[11px] font-mono text-slate-400 block mb-1">
              BASELINE RUN ({comparison.before_run_id.slice(0, 8)})
            </span>
            <div className="text-base font-bold text-slate-100">{comparison.before_agent_name}</div>
            <div className="text-xs text-slate-400 mt-1">Version: {comparison.before_version}</div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
            <span className="text-[11px] font-mono text-sky-400 block mb-1">
              AFTER RUN ({comparison.after_run_id.slice(0, 8)})
            </span>
            <div className="text-base font-bold text-slate-100">{comparison.after_agent_name}</div>
            <div className="text-xs text-slate-400 mt-1">Version: {comparison.after_version}</div>
          </div>
        </div>
      </div>

      {/* Metrics Delta Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/40">
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
            Evaluation Property Deltas
          </h3>
        </div>

        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/60 text-slate-400 uppercase font-semibold text-[11px] border-b border-slate-800">
            <tr>
              <th className="px-6 py-3.5">Evaluator Property</th>
              <th className="px-4 py-3.5">Before (Baseline)</th>
              <th className="px-4 py-3.5">After (New Version)</th>
              <th className="px-6 py-3.5 text-right">Net Change</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {Object.entries(comparison.metrics).map(([key, item]) => {
              const label = metricLabels[key] || key.replace("_", " ").toUpperCase();
              return (
                <tr key={key} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4 font-semibold text-slate-100">{label}</td>
                  <td className="px-4 py-4 font-mono text-slate-400">
                    {Math.round(item.before * 1000) / 10}%
                  </td>
                  <td className="px-4 py-4 font-mono font-bold text-slate-200">
                    {Math.round(item.after * 1000) / 10}%
                  </td>
                  <td className="px-6 py-4 text-right flex justify-end">
                    {renderDeltaBadge(item.delta)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Multilingual Deltas */}
      {comparison.language_deltas && Object.keys(comparison.language_deltas).length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/40">
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Multilingual Composite Score Shifts
            </h3>
          </div>

          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase font-semibold text-[11px] border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">Language</th>
                <th className="px-4 py-3.5">Before Score</th>
                <th className="px-4 py-3.5">After Score</th>
                <th className="px-6 py-3.5 text-right">Language Delta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {Object.entries(comparison.language_deltas).map(([langKey, data]) => {
                const compItem = data.composite_score;
                return (
                  <tr key={langKey} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 font-mono font-bold uppercase text-sky-400">
                      {langKey}
                    </td>
                    <td className="px-4 py-4 font-mono text-slate-400">
                      {Math.round(compItem.before * 1000) / 10}%
                    </td>
                    <td className="px-4 py-4 font-mono font-bold text-slate-200">
                      {Math.round(compItem.after * 1000) / 10}%
                    </td>
                    <td className="px-6 py-4 text-right flex justify-end">
                      {renderDeltaBadge(compItem.delta)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
