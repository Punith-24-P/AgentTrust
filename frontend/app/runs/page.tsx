"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Layers,
  Play,
  ArrowRight,
  Clock,
  Plus,
  ExternalLink,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ShieldCheck,
  RefreshCw,
} from "lucide-react";
import {
  fetchRuns,
  fetchAgents,
  fetchDatasets,
  triggerNewRun,
  triggerOneClickDemo,
  preflightRunCheck,
} from "@/lib/api";
import { RunItem, Agent, Dataset, PreFlightResult } from "@/types";

export default function RunsPage() {
  const [runs, setRuns] = useState<RunItem[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);

  // Search & Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [filterMode, setFilterMode] = useState<"ALL" | "REAL" | "DEMO">("ALL");
  const [filterAgent, setFilterAgent] = useState<string>("ALL");

  // New run modal state
  const [showModal, setShowModal] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [selectedDataset, setSelectedDataset] = useState("");
  const [concurrency, setConcurrency] = useState(2);
  const [testLimit, setTestLimit] = useState<string>("");
  const [startingRun, setStartingRun] = useState(false);

  // Pre-flight check state
  const [preflightLoading, setPreflightLoading] = useState(false);
  const [preflightResult, setPreflightResult] = useState<PreFlightResult | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [rData, aData, dData] = await Promise.all([
        fetchRuns(),
        fetchAgents(),
        fetchDatasets(),
      ]);
      setRuns(rData);
      setAgents(aData);
      setDatasets(dData);
      if (aData.length > 0) setSelectedAgent(aData[0].id);
      if (dData.length > 0) setSelectedDataset(dData[0].id);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Pre-flight verification
  const runPreflight = async () => {
    if (!selectedAgent || !selectedDataset) return;
    try {
      setPreflightLoading(true);
      const res = await preflightRunCheck({
        agent_id: selectedAgent,
        dataset_id: selectedDataset,
      });
      setPreflightResult(res);
    } catch (err: any) {
      setPreflightResult({
        status: "BLOCKED",
        agent_reachable: false,
        dataset_valid: false,
        evaluation_profile_valid: false,
        llm_provider_configured: false,
        documents_available: false,
        total_test_cases: 0,
        issues: [err.message || "Failed to execute preflight checks."],
        warnings: [],
      });
    } finally {
      setPreflightLoading(false);
    }
  };

  useEffect(() => {
    if (showModal && selectedAgent && selectedDataset) {
      runPreflight();
    }
  }, [showModal, selectedAgent, selectedDataset]);

  const handleCreateRun = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAgent || !selectedDataset) {
      alert("Please select both an agent and a dataset.");
      return;
    }
    const agentObj = agents.find((a) => a.id === selectedAgent);
    if (!agentObj) return;

    try {
      setStartingRun(true);
      const res = await triggerNewRun({
        project_id: agentObj.project_id,
        agent_id: selectedAgent,
        dataset_id: selectedDataset,
        concurrency: Number(concurrency) || 2,
        limit: testLimit ? Number(testLimit) : undefined,
      });
      setShowModal(false);
      window.location.href = `/runs/${res.id}`;
    } catch (err: any) {
      alert("Failed to start run: " + err.message);
    } finally {
      setStartingRun(false);
    }
  };

  // Filtering
  const filteredRuns = runs.filter((r) => {
    const matchesSearch =
      r.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.agent_name || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.dataset_name || "").toLowerCase().includes(searchQuery.toLowerCase());
    const matchesMode =
      filterMode === "ALL"
        ? true
        : filterMode === "DEMO"
        ? r.is_demo === true
        : r.is_demo !== true;
    const matchesAgent = filterAgent === "ALL" ? true : r.agent_id === filterAgent;
    return matchesSearch && matchesMode && matchesAgent;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center space-x-2.5">
            <Layers className="w-6 h-6 text-sky-400" />
            <span>Evaluation Runs</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Historical trace logs, reliability benchmarks, and reproducible execution records
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => {
              setShowModal(true);
            }}
            className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-bold transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New Evaluation Run</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by Run ID, Agent, or Dataset..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          {/* Mode Filter */}
          <div className="flex items-center bg-slate-950 border border-slate-800 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => setFilterMode("ALL")}
              className={`px-3 py-1 rounded-md font-medium transition-colors ${
                filterMode === "ALL"
                  ? "bg-sky-500 text-slate-950 font-bold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              All Runs
            </button>
            <button
              onClick={() => setFilterMode("REAL")}
              className={`px-3 py-1 rounded-md font-medium transition-colors ${
                filterMode === "REAL"
                  ? "bg-sky-500 text-slate-950 font-bold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Production
            </button>
            <button
              onClick={() => setFilterMode("DEMO")}
              className={`px-3 py-1 rounded-md font-medium transition-colors ${
                filterMode === "DEMO"
                  ? "bg-purple-600 text-slate-100 font-bold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Demo / Simulation
            </button>
          </div>

          {/* Agent Filter */}
          <select
            value={filterAgent}
            onChange={(e) => setFilterAgent(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-sky-500"
          >
            <option value="ALL">All Agents</option>
            {agents.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name} ({a.version})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Runs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-8 text-center text-xs text-slate-500">Loading runs...</div>
        ) : filteredRuns.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <p className="text-slate-400 text-sm">No evaluation runs match your criteria.</p>
            {runs.length === 0 && (
              <button
                onClick={() => triggerOneClickDemo().then(() => loadData())}
                className="px-4 py-2 rounded-lg bg-sky-500 text-slate-950 text-xs font-bold"
              >
                Run Controlled Demo Evaluation
              </button>
            )}
          </div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase font-semibold text-[11px] border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">Run ID & Type</th>
                <th className="px-4 py-3.5">Agent</th>
                <th className="px-4 py-3.5">Version</th>
                <th className="px-4 py-3.5">Dataset</th>
                <th className="px-4 py-3.5">Tests Completed</th>
                <th className="px-4 py-3.5">Composite Score</th>
                <th className="px-4 py-3.5">Duration</th>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-6 py-3.5 text-right">View</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filteredRuns.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <Link
                        href={`/runs/${r.id}`}
                        className="font-mono font-bold text-sky-400 hover:underline"
                      >
                        {r.id.slice(0, 8)}
                      </Link>
                      {r.is_demo && (
                        <span className="text-[9px] font-bold uppercase tracking-wider bg-purple-950/80 text-purple-300 border border-purple-800/80 px-1.5 py-0.5 rounded">
                          DEMO
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4 font-semibold text-slate-100">{r.agent_name}</td>
                  <td className="px-4 py-4 font-mono text-slate-400">{r.agent_version}</td>
                  <td className="px-4 py-4 text-slate-300">{r.dataset_name}</td>
                  <td className="px-4 py-4 font-mono">
                    {r.completed_tests}/{r.total_tests}
                  </td>
                  <td className="px-4 py-4">
                    {r.composite_score !== null && r.composite_score !== undefined ? (
                      <span className="font-extrabold text-sm text-slate-100">
                        {Math.round(r.composite_score * 100)}%
                      </span>
                    ) : (
                      <span className="text-slate-500">In Progress</span>
                    )}
                  </td>
                  <td className="px-4 py-4 text-slate-400 font-mono">
                    {r.duration_seconds ? `${r.duration_seconds}s` : "-"}
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

      {/* New Run Modal with Pre-Flight Checks */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-sky-400" />
                <span>Launch Evaluation Run</span>
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-slate-200 text-sm font-bold"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleCreateRun} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">
                  Select Registered Agent
                </label>
                <select
                  value={selectedAgent}
                  onChange={(e) => setSelectedAgent(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                >
                  {agents.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name} ({a.version}) [{a.adapter_type.toUpperCase()}]
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">
                  Select Benchmark Dataset
                </label>
                <select
                  value={selectedDataset}
                  onChange={(e) => setSelectedDataset(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                >
                  {datasets.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name} ({d.version})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">
                    Concurrency
                  </label>
                  <select
                    value={concurrency}
                    onChange={(e) => setConcurrency(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                  >
                    <option value={1}>1 (Sequential)</option>
                    <option value={2}>2 Concurrent Workers</option>
                    <option value={4}>4 Concurrent Workers</option>
                    <option value={8}>8 Concurrent Workers</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-medium mb-1">
                    Test Subset Limit (Optional)
                  </label>
                  <input
                    type="number"
                    placeholder="All tests"
                    value={testLimit}
                    onChange={(e) => setTestLimit(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
              </div>

              {/* Pre-flight Check Status Box */}
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-3.5 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-300 text-[11px] uppercase tracking-wider">
                    Pre-Flight Readiness Check
                  </span>
                  {preflightLoading ? (
                    <span className="flex items-center text-slate-400 text-[10px]">
                      <RefreshCw className="w-3 h-3 animate-spin mr-1 text-sky-400" />
                      Validating...
                    </span>
                  ) : preflightResult?.status === "READY" ? (
                    <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-bold">
                      READY FOR EXECUTION
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800 text-[10px] font-bold">
                      EXECUTION BLOCKED
                    </span>
                  )}
                </div>

                {preflightResult && (
                  <div className="space-y-1 pt-1">
                    <div className="grid grid-cols-2 gap-2 text-[11px]">
                      <div className="flex items-center space-x-1.5">
                        {preflightResult.agent_reachable ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <XCircle className="w-3.5 h-3.5 text-rose-400" />
                        )}
                        <span className="text-slate-400">Agent Reachable</span>
                      </div>
                      <div className="flex items-center space-x-1.5">
                        {preflightResult.dataset_valid ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <XCircle className="w-3.5 h-3.5 text-rose-400" />
                        )}
                        <span className="text-slate-400">Dataset Valid</span>
                      </div>
                      <div className="flex items-center space-x-1.5">
                        {preflightResult.evaluation_profile_valid ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <XCircle className="w-3.5 h-3.5 text-rose-400" />
                        )}
                        <span className="text-slate-400">Profile Valid</span>
                      </div>
                      <div className="flex items-center space-x-1.5">
                        {preflightResult.llm_provider_configured ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                        )}
                        <span className="text-slate-400">Provider Configured</span>
                      </div>
                    </div>

                    {preflightResult.issues && preflightResult.issues.length > 0 && (
                      <div className="mt-2 p-2 bg-rose-950/40 border border-rose-900/60 rounded text-rose-300 text-[11px]">
                        {preflightResult.issues.map((r, i) => (
                          <div key={i}>• {r}</div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="pt-3 flex justify-end space-x-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={Boolean(startingRun || (preflightResult && preflightResult.status !== "READY"))}
                  className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  {startingRun ? "Launching Run..." : "Execute Evaluation"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
