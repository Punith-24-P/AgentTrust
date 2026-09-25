"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Play,
  Layers,
  GitCompare,
  ArrowRight,
  CheckCircle2,
  FileCheck2,
  Languages,
  Activity,
  Quote,
  Sparkles,
  ExternalLink,
} from "lucide-react";
import { fetchRuns, triggerOneClickDemo } from "@/lib/api";
import { RunItem } from "@/types";

export default function HomePage() {
  const [runs, setRuns] = useState<RunItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [startingDemo, setStartingDemo] = useState(false);

  useEffect(() => {
    fetchRuns()
      .then((data) => setRuns(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleStartDemo = async () => {
    try {
      setStartingDemo(true);
      const res = await triggerOneClickDemo();
      window.location.href = `/runs/${res.baseline_run_id}`;
    } catch (err: any) {
      alert("Failed to run demo: " + err.message);
      setStartingDemo(false);
    }
  };

  const latestRun = runs.length > 0 ? runs[0] : null;

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800 p-8 sm:p-12 shadow-lg">
        <div className="max-w-3xl space-y-5">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Independent Evaluation Layer for AI Agents</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Evidence-backed reliability reports for AI agents.
          </h1>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed">
            Test observable agent execution automatically. Uncover contradicted evidence,
            mismatched citations, and multilingual translation drift across English, Kannada, Hindi, and Telugu.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-4">
            <button
              onClick={handleStartDemo}
              disabled={startingDemo}
              className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-sm transition-all shadow-md hover:shadow-sky-500/20 disabled:opacity-50"
            >
              <Play className={`w-4 h-4 fill-current ${startingDemo ? "animate-spin" : ""}`} />
              <span>{startingDemo ? "Running Demo Suite..." : "Start Demo Evaluation"}</span>
            </button>

            {latestRun && (
              <Link
                href={`/runs/${latestRun.id}`}
                className="flex items-center space-x-2 px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm transition-colors border border-slate-700"
              >
                <span>View Latest Run ({latestRun.agent_version})</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* 5 Evaluator Principles */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 uppercase tracking-wider">
            Diagnostic Evaluation Pillars
          </h2>
          <p className="text-xs text-slate-400">
            Every failure is grounded with specific evidence snippets, line numbers, and explainable reasons.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-slate-100 text-sm">Correctness</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Hybrid Layer: Deterministic extraction of statutory sections, dates, and authorities + semantic meaning check.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
              <FileCheck2 className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-slate-100 text-sm">Grounding</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Verifies whether claims are SUPPORTED, UNSUPPORTED, or CONTRADICTED by retrieved documents.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Quote className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-slate-100 text-sm">Citations</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Validates that cited sources and sections exist in active law repositories and match retrieved evidence.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <Languages className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-slate-100 text-sm">Translation</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Cross-lingual back-translation fidelity testing across Kannada, Hindi, and Telugu to detect semantic drift.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Activity className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-slate-100 text-sm">Trajectory</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Validates observable tool sequences, detects redundant loops, and verifies required retrieval.
            </p>
          </div>
        </div>
      </section>

      {/* Recent Evaluation Runs */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-100 uppercase tracking-wider">
              Recent Evaluation Runs
            </h2>
            <p className="text-xs text-slate-400">
              Track regression testing and compare versions across reproducible benchmarks
            </p>
          </div>

          <Link href="/runs" className="text-xs font-semibold text-sky-400 hover:text-sky-300 flex items-center space-x-1">
            <span>View All Runs</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          {loading ? (
            <div className="p-8 text-center text-xs text-slate-500">Loading runs...</div>
          ) : runs.length === 0 ? (
            <div className="p-8 text-center space-y-3">
              <p className="text-sm text-slate-400">No evaluation runs recorded yet.</p>
              <button
                onClick={handleStartDemo}
                className="px-4 py-2 rounded-lg bg-sky-500 text-slate-950 text-xs font-bold"
              >
                Launch First Demo Evaluation
              </button>
            </div>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 uppercase font-semibold text-[11px] border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3.5">Run ID</th>
                  <th className="px-4 py-3.5">Agent</th>
                  <th className="px-4 py-3.5">Version</th>
                  <th className="px-4 py-3.5">Dataset</th>
                  <th className="px-4 py-3.5">Tests</th>
                  <th className="px-4 py-3.5">Reliability Score</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-6 py-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {runs.slice(0, 5).map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 font-mono font-bold text-sky-400">
                      {r.id.slice(0, 8)}
                    </td>
                    <td className="px-4 py-4 font-semibold text-slate-100">{r.agent_name}</td>
                    <td className="px-4 py-4 font-mono text-slate-400">{r.agent_version}</td>
                    <td className="px-4 py-4 text-slate-300">{r.dataset_name}</td>
                    <td className="px-4 py-4 font-mono">{r.completed_tests}/{r.total_tests}</td>
                    <td className="px-4 py-4">
                      {r.composite_score !== null && r.composite_score !== undefined ? (
                        <span className="font-bold text-slate-100">
                          {Math.round(r.composite_score * 100)}%
                        </span>
                      ) : (
                        <span className="text-slate-500">In Progress</span>
                      )}
                    </td>
                    <td className="px-4 py-4">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                          r.status === "COMPLETED"
                            ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                            : r.status === "RUNNING"
                            ? "bg-sky-950 text-sky-400 border border-sky-800 animate-pulse"
                            : "bg-slate-800 text-slate-400 border border-slate-700"
                        }`}
                      >
                        {r.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link
                        href={`/runs/${r.id}`}
                        className="text-xs font-semibold text-sky-400 hover:text-sky-300 inline-flex items-center space-x-1"
                      >
                        <span>Dashboard</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  );
}
