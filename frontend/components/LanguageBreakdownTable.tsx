import React from "react";
import { LanguageMetric } from "@/types";

interface LanguageBreakdownTableProps {
  data: Record<string, LanguageMetric>;
}

export default function LanguageBreakdownTable({ data }: LanguageBreakdownTableProps) {
  const langNames: Record<string, { name: string; flag: string }> = {
    en: { name: "English", flag: "EN" },
    kn: { name: "Kannada (ಕನ್ನಡ)", flag: "KN" },
    hi: { name: "Hindi (हिन्दी)", flag: "HI" },
    te: { name: "Telugu (తెలుగు)", flag: "TE" },
  };

  const getPillColor = (score: number) => {
    const pct = Math.round(score * 100);
    if (pct >= 85) return "bg-emerald-950/60 text-emerald-400 border border-emerald-800/40";
    if (pct >= 70) return "bg-amber-950/60 text-amber-400 border border-amber-800/40";
    return "bg-rose-950/60 text-rose-400 border border-rose-800/40";
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
      <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
            Multilingual Reliability Breakdown
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Observing performance, grounding, and cross-lingual drift across target languages
          </p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/50 text-slate-400 uppercase font-semibold text-[11px] border-b border-slate-800">
            <tr>
              <th className="px-6 py-3.5">Language</th>
              <th className="px-4 py-3.5">Tests</th>
              <th className="px-4 py-3.5">Composite Score</th>
              <th className="px-4 py-3.5">Correctness</th>
              <th className="px-4 py-3.5">Grounding</th>
              <th className="px-4 py-3.5">Citations</th>
              <th className="px-4 py-3.5">Translation Fidelity</th>
              <th className="px-4 py-3.5">Trajectory</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {Object.entries(data).map(([langKey, metrics]) => {
              const meta = langNames[langKey] || { name: langKey.toUpperCase(), flag: langKey.toUpperCase() };
              return (
                <tr key={langKey} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4 font-medium text-slate-100 flex items-center space-x-2.5">
                    <span className="font-mono text-[10px] bg-slate-800 text-sky-400 px-1.5 py-0.5 rounded border border-slate-700">
                      {meta.flag}
                    </span>
                    <span>{meta.name}</span>
                  </td>
                  <td className="px-4 py-4 font-mono text-slate-400">
                    {metrics.passed_tests}/{metrics.total_tests} ({Math.round(metrics.pass_rate * 100)}%)
                  </td>
                  <td className="px-4 py-4">
                    <span className={`inline-block px-2.5 py-0.5 rounded-full font-semibold ${getPillColor(metrics.composite_score)}`}>
                      {Math.round(metrics.composite_score * 100)}%
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="font-semibold text-slate-200">
                      {Math.round(metrics.correctness_score * 100)}%
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="font-semibold text-slate-200">
                      {Math.round(metrics.grounding_score * 100)}%
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="font-semibold text-slate-200">
                      {Math.round(metrics.citation_score * 100)}%
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    {langKey === "en" ? (
                      <span className="text-slate-500 font-mono text-[11px]">N/A (Source)</span>
                    ) : (
                      <span className={`inline-block px-2 py-0.5 rounded font-semibold ${getPillColor(metrics.translation_score)}`}>
                        {Math.round(metrics.translation_score * 100)}%
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-4">
                    <span className="font-semibold text-slate-200">
                      {Math.round(metrics.trajectory_score * 100)}%
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
