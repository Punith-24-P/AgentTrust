"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Play,
  Layers,
  ArrowRight,
  CheckCircle2,
  FileCheck2,
  Languages,
  Activity,
  Quote,
  AlertTriangle,
  Bot,
  Database,
  Plus,
  RefreshCw,
  FolderGit2,
} from "lucide-react";
import {
  fetchRuns,
  fetchProjects,
  fetchAgents,
  fetchDatasets,
  triggerOneClickDemo,
} from "@/lib/api";
import { RunItem, Project, Agent, Dataset } from "@/types";

export default function HomePage() {
  const [runs, setRuns] = useState<RunItem[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [startingDemo, setStartingDemo] = useState(false);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        const [rData, pData, aData, dData] = await Promise.all([
          fetchRuns(),
          fetchProjects(),
          fetchAgents(),
          fetchDatasets(),
        ]);
        setRuns(rData);
        setProjects(pData);
        setAgents(aData);
        setDatasets(dData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
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
    <div className="space-y-10">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-[#111827] via-[#0f172a] to-[#0b0f19] border border-[#1e293b] p-8 sm:p-10 shadow-xl">
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
            <span>Independent AI Reliability Layer</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
            Evidence-backed reliability reports for AI agents.
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            Evaluate correctness, grounding, citations, multilingual fidelity, and observable agent behavior with reproducible test runs. Turn complex agent execution into actionable reliability diagnostics.
          </p>

          <div className="pt-3 flex flex-wrap items-center gap-3">
            <Link
              href="/runs"
              className="flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-xs transition shadow-sm"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Run Evaluation</span>
            </Link>

            <Link
              href="/agents"
              className="flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition border border-slate-700"
            >
              <Bot className="w-3.5 h-3.5 text-sky-400" />
              <span>Connect Agent</span>
            </Link>

            <button
              onClick={handleStartDemo}
              disabled={startingDemo}
              className="flex items-center space-x-2 px-4 py-2.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 font-medium text-xs transition border border-amber-500/30 disabled:opacity-50"
            >
              <span>{startingDemo ? "Simulating..." : "Run Showcase Demo"}</span>
            </button>
          </div>
        </div>
      </section>

      {/* Summary KPI Cards */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#111827] border border-[#1e293b] rounded-xl p-5 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs uppercase tracking-wider font-semibold">Projects</span>
            <FolderGit2 className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{projects.length}</div>
          <div className="text-[11px] text-slate-400">Workspace active environments</div>
        </div>

        <div className="bg-[#111827] border border-[#1e293b] rounded-xl p-5 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs uppercase tracking-wider font-semibold">Agents</span>
            <Bot className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{agents.length}</div>
          <div className="text-[11px] text-slate-400">Connected models & endpoints</div>
        </div>

        <div className="bg-[#111827] border border-[#1e293b] rounded-xl p-5 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs uppercase tracking-wider font-semibold">Datasets</span>
            <Database className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{datasets.length}</div>
          <div className="text-[11px] text-slate-400">Versioned test benchmarks</div>
        </div>

        <div className="bg-[#111827] border border-[#1e293b] rounded-xl p-5 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs uppercase tracking-wider font-semibold">Evaluations</span>
            <Layers className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{runs.length}</div>
          <div className="text-[11px] text-slate-400">Historical benchmark runs</div>
        </div>
      </section>

      {/* Latest Evaluation Scorecard */}
      {latestRun && (
        <section className="bg-[#111827] border border-[#1e293b] rounded-2xl p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">Latest Evaluation Diagnostic</h2>
                {latestRun.is_demo && (
                  <span className="text-[10px] font-mono uppercase bg-amber-500/10 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded font-bold">
                    DEMO / SIMULATION
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Agent <strong className="text-slate-200">{latestRun.agent_name}</strong> v{latestRun.agent_version} evaluated against {latestRun.dataset_name} v{latestRun.dataset_version}
              </p>
            </div>

            <Link
              href={`/runs/${latestRun.id}`}
              className="inline-flex items-center gap-1.5 text-xs text-sky-400 hover:text-sky-300 font-semibold"
            >
              <span>Inspect Full Run</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b] text-center space-y-1">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                Composite
              </span>
              <div className="text-2xl font-bold font-mono text-sky-400">
                {latestRun.composite_score !== null && latestRun.composite_score !== undefined
                  ? `${Math.round(latestRun.composite_score * 100)}%`
                  : "--"}
              </div>
              <span className="text-[10px] text-slate-500">Documented formula</span>
            </div>

            <div className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b] text-center space-y-1">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                Status
              </span>
              <div
                className={`text-sm font-bold font-mono uppercase py-1 ${
                  latestRun.status === "COMPLETED"
                    ? "text-emerald-400"
                    : latestRun.status === "RUNNING"
                    ? "text-sky-400 animate-pulse"
                    : "text-slate-300"
                }`}
              >
                {latestRun.status}
              </div>
              <span className="text-[10px] text-slate-500">
                {latestRun.completed_tests}/{latestRun.total_tests} tests
              </span>
            </div>

            <div className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b] text-center space-y-1">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                Duration
              </span>
              <div className="text-xl font-bold font-mono text-white">
                {latestRun.duration_seconds ? `${latestRun.duration_seconds}s` : "--"}
              </div>
              <span className="text-[10px] text-slate-500">Total runtime</span>
            </div>

            <div className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b] text-center space-y-1">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                Grounding
              </span>
              <div className="text-xl font-bold font-mono text-emerald-400">Verified</div>
              <span className="text-[10px] text-slate-500">Claim-level check</span>
            </div>

            <div className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b] text-center space-y-1">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                Citations
              </span>
              <div className="text-xl font-bold font-mono text-indigo-400">Validated</div>
              <span className="text-[10px] text-slate-500">Statutory sources</span>
            </div>

            <div className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b] text-center space-y-1">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                Multilingual
              </span>
              <div className="text-xl font-bold font-mono text-purple-400">Audited</div>
              <span className="text-[10px] text-slate-500">EN, KN, HI, TE</span>
            </div>
          </div>
        </section>
      )}

      {/* 5 Evaluator Principles */}
      <section className="space-y-4">
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            Evidence-Backed Evaluation Pillars
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Every failure is grounded with specific evidence snippets, line numbers, and explainable reasons.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <div className="bg-[#111827] border border-[#1e293b] rounded-xl p-4 space-y-2">
            <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-white text-xs">Correctness</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Hybrid Layer: Deterministic extraction of statutory sections, dates, numbers + semantic check.
            </p>
          </div>

          <div className="bg-[#111827] border border-[#1e293b] rounded-xl p-4 space-y-2">
            <div className="w-7 h-7 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
              <FileCheck2 className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-white text-xs">Grounding</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Verifies whether claims are SUPPORTED, UNSUPPORTED, or CONTRADICTED by retrieved documents.
            </p>
          </div>

          <div className="bg-[#111827] border border-[#1e293b] rounded-xl p-4 space-y-2">
            <div className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Quote className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-white text-xs">Citations</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Validates that cited sources and sections exist in active law repositories and match retrieved evidence.
            </p>
          </div>

          <div className="bg-[#111827] border border-[#1e293b] rounded-xl p-4 space-y-2">
            <div className="w-7 h-7 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <Languages className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-white text-xs">Translation</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Cross-lingual back-translation fidelity testing across Kannada, Hindi, and Telugu to detect semantic drift.
            </p>
          </div>

          <div className="bg-[#111827] border border-[#1e293b] rounded-xl p-4 space-y-2">
            <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Activity className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-white text-xs">Trajectory</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Validates observable tool sequences, detects redundant loops, and verifies required retrieval.
            </p>
          </div>
        </div>
      </section>

      {/* Recent Evaluation Runs Table */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              Recent Evaluation Runs
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Empirical execution records calculated dynamically from actual test outputs.
            </p>
          </div>

          <Link
            href="/runs"
            className="text-xs font-semibold text-sky-400 hover:text-sky-300 flex items-center space-x-1"
          >
            <span>View All Runs</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="bg-[#111827] border border-[#1e293b] rounded-xl overflow-hidden shadow-sm">
          {loading ? (
            <div className="p-8 text-center text-xs text-slate-500">Loading runs...</div>
          ) : runs.length === 0 ? (
            <div className="p-10 text-center space-y-3">
              <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 mx-auto flex items-center justify-center text-slate-400">
                <Layers className="w-5 h-5" />
              </div>
              <p className="text-sm font-semibold text-white">No evaluation runs yet</p>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Connect your AI agent and launch your first evaluation run to see evidence-backed reliability scores.
              </p>
              <div className="pt-2">
                <Link
                  href="/runs"
                  className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-semibold inline-block"
                >
                  Run your first evaluation
                </Link>
              </div>
            </div>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0b0f19] text-slate-400 uppercase font-semibold text-[10px] border-b border-[#1e293b]">
                <tr>
                  <th className="px-6 py-3">Run ID</th>
                  <th className="px-4 py-3">Agent</th>
                  <th className="px-4 py-3">Version</th>
                  <th className="px-4 py-3">Dataset</th>
                  <th className="px-4 py-3">Tests</th>
                  <th className="px-4 py-3">Composite Score</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-6 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1e293b]/60 text-slate-300">
                {runs.slice(0, 5).map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-3.5 font-mono font-bold text-sky-400">
                      {r.id.slice(0, 8)}
                    </td>
                    <td className="px-4 py-3.5 font-semibold text-white">{r.agent_name}</td>
                    <td className="px-4 py-3.5 font-mono text-slate-400">{r.agent_version}</td>
                    <td className="px-4 py-3.5 text-slate-300">{r.dataset_name}</td>
                    <td className="px-4 py-3.5 font-mono">
                      {r.completed_tests}/{r.total_tests}
                    </td>
                    <td className="px-4 py-3.5">
                      {r.composite_score !== null && r.composite_score !== undefined ? (
                        <span className="font-bold text-white font-mono">
                          {Math.round(r.composite_score * 100)}%
                        </span>
                      ) : (
                        <span className="text-slate-500 font-mono">--</span>
                      )}
                    </td>
                    <td className="px-4 py-3.5">
                      {r.is_demo ? (
                        <span className="text-[9px] font-mono uppercase bg-amber-500/10 text-amber-300 border border-amber-500/30 px-1.5 py-0.5 rounded font-semibold">
                          DEMO
                        </span>
                      ) : (
                        <span className="text-[9px] font-mono uppercase bg-sky-500/10 text-sky-400 border border-sky-500/30 px-1.5 py-0.5 rounded font-semibold">
                          LIVE
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3.5">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          r.status === "COMPLETED"
                            ? "bg-emerald-950/60 text-emerald-400 border border-emerald-800/60"
                            : r.status === "RUNNING"
                            ? "bg-sky-950/60 text-sky-400 border border-sky-800/60 animate-pulse"
                            : "bg-slate-800 text-slate-400 border border-slate-700"
                        }`}
                      >
                        {r.status}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      <Link
                        href={`/runs/${r.id}`}
                        className="text-xs font-semibold text-sky-400 hover:text-sky-300 inline-flex items-center space-x-1"
                      >
                        <span>Inspect</span>
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
