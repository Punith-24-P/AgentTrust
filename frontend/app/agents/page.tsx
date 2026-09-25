"use client";

import React, { useEffect, useState } from "react";
import { Bot, Plus, Globe, Server, CheckCircle2 } from "lucide-react";
import { fetchAgents, fetchProjects, createAgent } from "@/lib/api";
import { Agent, Project } from "@/types";

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  // New Agent Form
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [adapterType, setAdapterType] = useState<"demo" | "http">("http");
  const [endpoint, setEndpoint] = useState("http://localhost:5000/run");
  const [version, setVersion] = useState("1.0.0");
  const [model, setModel] = useState("gpt-4o-mini");
  const [submitting, setSubmitting] = useState(false);

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

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projects.length) {
      alert("No active project found.");
      return;
    }

    try {
      setSubmitting(true);
      await createAgent({
        project_id: projects[0].id,
        name,
        description,
        adapter_type: adapterType,
        endpoint: adapterType === "http" ? endpoint : undefined,
        version,
        model,
        supported_languages: ["en", "kn", "hi", "te"],
      });
      setShowModal(false);
      setName("");
      setDescription("");
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
            <span>Registered AI Agents</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Register built-in simulation agents or connect external agent endpoints via standard HTTP adapter
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-bold transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Register New Agent</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {agents.map((ag) => (
          <div key={ag.id} className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4 shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="font-bold text-slate-100 text-base">{ag.name}</h3>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-sky-400 border border-slate-700">
                    {ag.adapter_type.toUpperCase()}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1">{ag.description || "No description provided."}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              <div>
                <span className="text-slate-500 block text-[11px]">Version:</span>
                <span className="font-mono text-slate-300 font-semibold">{ag.version}</span>
              </div>

              <div>
                <span className="text-slate-500 block text-[11px]">Model Architecture:</span>
                <span className="font-mono text-slate-300 font-semibold">{ag.model}</span>
              </div>

              {ag.endpoint && (
                <div className="col-span-2">
                  <span className="text-slate-500 block text-[11px]">Endpoint URL:</span>
                  <span className="font-mono text-sky-400 text-[11px] truncate block">{ag.endpoint}</span>
                </div>
              )}
            </div>

            <div className="text-xs text-slate-400 flex items-center space-x-1.5">
              <span>Supported Languages:</span>
              <div className="flex space-x-1">
                {ag.supported_languages?.map((lang) => (
                  <span key={lang} className="font-mono text-[10px] uppercase bg-slate-800 px-1.5 py-0.5 rounded text-slate-300">
                    {lang}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Registration Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-xl">
            <h3 className="text-base font-bold text-slate-100">Register Agent Under Test</h3>

            <form onSubmit={handleRegister} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Agent Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. LegalAdvisor-v2"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Adapter Type</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setAdapterType("http")}
                    className={`p-3 rounded-lg border text-left ${
                      adapterType === "http"
                        ? "bg-sky-950/40 border-sky-500 text-sky-400"
                        : "bg-slate-950 border-slate-800 text-slate-400"
                    }`}
                  >
                    <div className="font-bold">HTTP Agent</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">External endpoint POST /run</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setAdapterType("demo")}
                    className={`p-3 rounded-lg border text-left ${
                      adapterType === "demo"
                        ? "bg-sky-950/40 border-sky-500 text-sky-400"
                        : "bg-slate-950 border-slate-800 text-slate-400"
                    }`}
                  >
                    <div className="font-bold">Demo Agent</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">Built-in RAG with simulation modes</div>
                  </button>
                </div>
              </div>

              {adapterType === "http" && (
                <div>
                  <label className="block text-slate-400 font-medium mb-1">HTTP Endpoint URL</label>
                  <input
                    type="url"
                    required
                    placeholder="https://your-agent.internal/api/run"
                    value={endpoint}
                    onChange={(e) => setEndpoint(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Version Tag</label>
                  <input
                    type="text"
                    required
                    placeholder="1.0.0"
                    value={version}
                    onChange={(e) => setVersion(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-medium mb-1">Model Architecture</label>
                  <input
                    type="text"
                    required
                    placeholder="gpt-4o-mini"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Description</label>
                <textarea
                  rows={2}
                  placeholder="Notes about agent configuration, system prompt, or retrieval model..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                />
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
                  disabled={submitting}
                  className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold disabled:opacity-50"
                >
                  {submitting ? "Registering..." : "Save Agent"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
