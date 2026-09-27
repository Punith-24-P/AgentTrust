"use client";

import React, { useEffect, useState } from "react";
import { Bot, Plus, Globe, Activity, CheckCircle2, XCircle, AlertCircle, Key, RefreshCw } from "lucide-react";
import { fetchAgents, fetchProjects, createAgent, testAgentConnection } from "@/lib/api";
import { Agent, Project, AgentConnectionTestResult } from "@/types";

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  // New Agent Form Modal
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [adapterType, setAdapterType] = useState<"demo" | "http">("http");
  const [endpoint, setEndpoint] = useState("http://localhost:5001/run");
  const [apiKey, setApiKey] = useState("");
  const [version, setVersion] = useState("1.0.0");
  const [model, setModel] = useState("gpt-4o-mini");
  const [submitting, setSubmitting] = useState(false);

  // Connection Probe State
  const [testingAgentId, setTestingAgentId] = useState<string | null>(null);
  const [probeResult, setProbeResult] = useState<{
    agentName: string;
    result: AgentConnectionTestResult;
  } | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [aData, pData] = await Promise.all([fetchAgents(), fetchProjects()]);
      setAgents(aData);
      setProjects(pData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async (ag: Agent) => {
    try {
      setTestingAgentId(ag.id);
      const res = await testAgentConnection(ag.id);
      setProbeResult({ agentName: ag.name, result: res });
    } catch (err: any) {
      setProbeResult({
        agentName: ag.name,
        result: {
          status: "ERROR",
          latency_ms: 0,
          message: err.message || "Failed to reach endpoint.",
          details: { error: err.message },
        },
      });
    } finally {
      setTestingAgentId(null);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projects.length) {
      alert("No active project found. Please create a project first.");
      return;
    }

    try {
      setSubmitting(true);
      const configJson: Record<string, any> = {};
      if (apiKey.trim()) {
        configJson.api_key = apiKey.trim();
      }

      await createAgent({
        project_id: projects[0].id,
        name,
        description,
        adapter_type: adapterType,
        endpoint: adapterType === "http" ? endpoint.trim() : undefined,
        version,
        model,
        supported_languages: ["en", "kn", "hi", "te"],
        config_json: configJson,
      });
      setShowModal(false);
      setName("");
      setDescription("");
      setApiKey("");
      loadData();
    } catch (err: any) {
      alert("Failed to register agent: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center space-x-2.5">
            <Bot className="w-6 h-6 text-sky-400" />
            <span>AI Agents Under Test</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Connect external AI agents via standard HTTP REST contract or use internal simulated agents.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-semibold transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>Connect Agent</span>
        </button>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading agents...</div>
      ) : agents.length === 0 ? (
        /* Empty State */
        <div className="bg-[#111827] border border-[#1e293b] rounded-2xl p-12 text-center max-w-lg mx-auto space-y-4">
          <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 mx-auto flex items-center justify-center text-slate-400">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">No agents connected yet</h3>
            <p className="text-xs text-slate-400 mt-1">
              Connect your first HTTP agent endpoint or initialize the built-in demo agent to start running reliability evaluations.
            </p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-semibold transition"
          >
            Connect your first agent
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {agents.map((ag) => (
            <div
              key={ag.id}
              className="bg-[#111827] border border-[#1e293b] rounded-xl p-5 space-y-4 hover:border-slate-700 transition"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-bold text-slate-100 text-sm">{ag.name}</h3>
                    <span
                      className={`text-[10px] uppercase font-mono px-2 py-0.5 rounded border ${
                        ag.adapter_type === "http"
                          ? "bg-sky-950/40 text-sky-400 border-sky-800/60"
                          : "bg-amber-950/40 text-amber-300 border-amber-800/60"
                      }`}
                    >
                      {ag.adapter_type.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                    {ag.description || "No description provided."}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs bg-[#0b0f19] p-3 rounded-lg border border-[#1e293b]">
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase tracking-wider">Version</span>
                  <span className="font-mono text-slate-300 font-semibold">{ag.version}</span>
                </div>

                <div>
                  <span className="text-slate-500 block text-[10px] uppercase tracking-wider">Model</span>
                  <span className="font-mono text-slate-300 font-semibold">{ag.model}</span>
                </div>

                {ag.endpoint && (
                  <div className="col-span-2 pt-1 border-t border-[#1e293b]/60">
                    <span className="text-slate-500 block text-[10px] uppercase tracking-wider">Endpoint URL</span>
                    <span className="font-mono text-sky-400 text-[11px] truncate block">{ag.endpoint}</span>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-[#1e293b]">
                <div className="flex space-x-1">
                  {ag.supported_languages?.map((lang) => (
                    <span
                      key={lang}
                      className="font-mono text-[10px] uppercase bg-slate-800/80 px-1.5 py-0.5 rounded text-slate-300"
                    >
                      {lang}
                    </span>
                  ))}
                </div>

                <button
                  onClick={() => handleTestConnection(ag)}
                  disabled={testingAgentId === ag.id}
                  className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-200 transition disabled:opacity-50"
                >
                  <Activity
                    className={`w-3.5 h-3.5 text-sky-400 ${
                      testingAgentId === ag.id ? "animate-pulse" : ""
                    }`}
                  />
                  <span>{testingAgentId === ag.id ? "Testing..." : "Test Connection"}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Connection Probe Modal */}
      {probeResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-[#111827] border border-[#1e293b] rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {probeResult.result.status === "SUCCESS" ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-400" />
                )}
                <h3 className="font-bold text-white text-base">
                  Connection Probe: {probeResult.agentName}
                </h3>
              </div>
              <span
                className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                  probeResult.result.status === "SUCCESS"
                    ? "bg-emerald-950/40 text-emerald-400 border border-emerald-800/40"
                    : "bg-red-950/40 text-red-400 border border-red-800/40"
                }`}
              >
                {probeResult.result.status}
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">{probeResult.result.message}</p>

            <div className="bg-[#0b0f19] border border-[#1e293b] rounded-xl p-3 text-xs space-y-2">
              <div className="flex justify-between text-slate-400">
                <span>Observed Round-trip Latency:</span>
                <span className="font-mono text-white">{probeResult.result.latency_ms} ms</span>
              </div>
              {probeResult.result.status_code && (
                <div className="flex justify-between text-slate-400">
                  <span>HTTP Response Status:</span>
                  <span className="font-mono text-white">{probeResult.result.status_code}</span>
                </div>
              )}
            </div>

            {probeResult.result.details && Object.keys(probeResult.result.details).length > 0 && (
              <div className="space-y-1">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Probe Diagnostic Details
                </span>
                <pre className="p-3 rounded-lg bg-[#0b0f19] border border-[#1e293b] text-[11px] font-mono text-slate-300 overflow-x-auto max-h-40">
                  {JSON.stringify(probeResult.result.details, null, 2)}
                </pre>
              </div>
            )}

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setProbeResult(null)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Registration Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-[#111827] border border-[#1e293b] rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Connect Agent Under Test</h3>
            <p className="text-xs text-slate-400">
              Configure your agent endpoint to receive AgentTrust test case evaluation payloads.
            </p>

            <form onSubmit={handleRegister} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Agent Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. SupportAssistant-v2"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Integration Type</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setAdapterType("http")}
                    className={`p-3 rounded-lg border text-left transition ${
                      adapterType === "http"
                        ? "bg-sky-950/40 border-sky-500 text-sky-400"
                        : "bg-[#0b0f19] border-[#1e293b] text-slate-400"
                    }`}
                  >
                    <div className="font-bold">HTTP Agent</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">POST /run JSON contract</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setAdapterType("demo")}
                    className={`p-3 rounded-lg border text-left transition ${
                      adapterType === "demo"
                        ? "bg-amber-950/40 border-amber-500 text-amber-300"
                        : "bg-[#0b0f19] border-[#1e293b] text-slate-400"
                    }`}
                  >
                    <div className="font-bold">Demo Simulation</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">Built-in local reference agent</div>
                  </button>
                </div>
              </div>

              {adapterType === "http" && (
                <>
                  <div>
                    <label className="block text-slate-300 font-medium mb-1">HTTP Endpoint URL</label>
                    <input
                      type="url"
                      required
                      placeholder="http://localhost:5001/run or https://agent.internal/run"
                      value={endpoint}
                      onChange={(e) => setEndpoint(e.target.value)}
                      className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-300 font-medium mb-1">
                      Authorization Header / API Key (Optional)
                    </label>
                    <input
                      type="password"
                      placeholder="Bearer token or custom key"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                    />
                  </div>
                </>
              )}

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Version Tag</label>
                  <input
                    type="text"
                    required
                    placeholder="1.0.0"
                    value={version}
                    onChange={(e) => setVersion(e.target.value)}
                    className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Model Architecture</label>
                  <input
                    type="text"
                    required
                    placeholder="gpt-4o-mini"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Description</label>
                <textarea
                  rows={2}
                  placeholder="Notes about agent configuration, tools, system prompts..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div className="pt-3 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 font-medium hover:bg-slate-700 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold disabled:opacity-50 transition"
                >
                  {submitting ? "Connecting..." : "Save Agent"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
