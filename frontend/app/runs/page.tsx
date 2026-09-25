"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Layers, Play, ArrowRight, Clock, Plus, ExternalLink } from "lucide-react";
import { fetchRuns, fetchAgents, fetchDatasets, triggerNewRun, triggerOneClickDemo } from "@/lib/api";
import { RunItem, Agent, Dataset } from "@/types";

export default function RunsPage() {
  const [runs, setRuns] = useState<RunItem[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);

  // New run modal state
  const [showModal, setShowModal] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [selectedDataset, setSelectedDataset] = useState("");
  const [startingRun, setStartingRun] = useState(false);

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
      });
      setShowModal(false);
      window.location.href = `/runs/${res.id}`;
    } catch (err: any) {
      alert("Failed to start run: " + err.message);
    } finally {
      setStartingRun(false);
    }
  };

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
            Historical trace logs, reliability benchmarks, and reproducibility records
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-bold transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New Evaluation Run</span>
          </button>
        </div>
      </div>

      {/* Runs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-8 text-center text-xs text-slate-500">Loading runs...</div>
        ) : runs.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <p className="text-slate-400 text-sm">No evaluation runs recorded yet.</p>
            <button
              onClick={() => triggerOneClickDemo().then(() => loadData())}
              className="px-4 py-2 rounded-lg bg-sky-500 text-slate-950 text-xs font-bold"
            >
              Seed and Run Demo Evaluation
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
                <th className="px-4 py-3.5">Tests Completed</th>
                <th className="px-4 py-3.5">Composite Score</th>
                <th className="px-4 py-3.5">Duration</th>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-6 py-3.5 text-right">View</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {runs.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4 font-mono font-bold text-sky-400">
                    <Link href={`/runs/${r.id}`} className="hover:underline">
                      {r.id.slice(0, 8)}
                    </Link>
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

      {/* New Run Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-xl">
            <h3 className="text-base font-bold text-slate-100">Launch New Evaluation Run</h3>

            <form onSubmit={handleCreateRun} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Select Registered Agent</label>
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
                <label className="block text-slate-400 font-medium mb-1">Select Test Suite Dataset</label>
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

              <div className="pt-3 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={startingRun}
                  className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold disabled:opacity-50"
                >
                  {startingRun ? "Launching..." : "Execute Evaluation"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
