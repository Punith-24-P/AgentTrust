"use client";

import React, { useState } from "react";
import { X, AlertTriangle, CheckCircle2, XCircle, Clock, BookOpen, Quote, Languages, Activity } from "lucide-react";
import { TestResultItem } from "@/types";

interface FailureDrilldownModalProps {
  item: TestResultItem | null;
  onClose: () => void;
}

export default function FailureDrilldownModal({ item, onClose }: FailureDrilldownModalProps) {
  const [activeTab, setActiveTab] = useState<"overview" | "claims" | "evidence" | "translation" | "trace">("overview");

  if (!item) return null;

  const ev = item.evaluation_result;

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return "bg-rose-950/80 text-rose-300 border-rose-700/60";
      case "HIGH":
        return "bg-amber-950/80 text-amber-300 border-amber-700/60";
      case "MEDIUM":
        return "bg-yellow-950/80 text-yellow-300 border-yellow-700/60";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <span className="font-mono text-xs font-bold bg-sky-950 text-sky-400 border border-sky-800/60 px-2.5 py-1 rounded">
              {item.external_id}
            </span>
            <span className="text-xs uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
              Lang: {item.language.toUpperCase()}
            </span>
            <span className={`text-[11px] font-bold uppercase px-2.5 py-0.5 rounded-full border ${getSeverityBadge(ev.severity)}`}>
              {ev.severity} Severity
            </span>
            <span
              className={`text-[11px] font-bold uppercase px-2.5 py-0.5 rounded-full ${
                ev.overall_status === "PASS"
                  ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                  : "bg-rose-950 text-rose-400 border border-rose-800"
              }`}
            >
              {ev.overall_status}
            </span>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 border-b border-slate-800 bg-slate-950/30 flex space-x-4">
          <button
            onClick={() => setActiveTab("overview")}
            className={`py-3 text-xs font-semibold border-b-2 flex items-center space-x-1.5 transition-colors ${
              activeTab === "overview"
                ? "border-sky-500 text-sky-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Diagnostics Overview</span>
          </button>

          <button
            onClick={() => setActiveTab("claims")}
            className={`py-3 text-xs font-semibold border-b-2 flex items-center space-x-1.5 transition-colors ${
              activeTab === "claims"
                ? "border-sky-500 text-sky-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Claims & Grounding ({ev.claims?.length || 0})</span>
          </button>

          <button
            onClick={() => setActiveTab("evidence")}
            className={`py-3 text-xs font-semibold border-b-2 flex items-center space-x-1.5 transition-colors ${
              activeTab === "evidence"
                ? "border-sky-500 text-sky-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Quote className="w-3.5 h-3.5" />
            <span>Citations & Sources</span>
          </button>

          {item.language !== "en" && (
            <button
              onClick={() => setActiveTab("translation")}
              className={`py-3 text-xs font-semibold border-b-2 flex items-center space-x-1.5 transition-colors ${
                activeTab === "translation"
                  ? "border-sky-500 text-sky-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Languages className="w-3.5 h-3.5" />
              <span>Translation Drift</span>
            </button>
          )}

          <button
            onClick={() => setActiveTab("trace")}
            className={`py-3 text-xs font-semibold border-b-2 flex items-center space-x-1.5 transition-colors ${
              activeTab === "trace"
                ? "border-sky-500 text-sky-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Observable Trace ({item.trace_events?.length || 0})</span>
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-xs">
          {activeTab === "overview" && (
            <div className="space-y-6">
              {/* Question & Expected */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Evaluated Question
                  </span>
                  <p className="text-slate-200 text-sm font-medium leading-relaxed">{item.question}</p>
                </div>

                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                  <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider block mb-1">
                    Expected Statutory Answer
                  </span>
                  <p className="text-slate-300 text-sm leading-relaxed">{item.expected_answer}</p>
                </div>
              </div>

              {/* Agent Answer */}
              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <span className="text-[11px] font-semibold text-sky-400 uppercase tracking-wider block mb-1">
                  Agent Answer Under Test
                </span>
                <p className="text-slate-100 text-sm leading-relaxed font-mono whitespace-pre-wrap">
                  {item.final_answer}
                </p>
              </div>

              {/* Evaluators Diagnostic Summary */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                <div className="bg-slate-950/80 p-3.5 rounded-lg border border-slate-800">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-semibold text-slate-300">Correctness</span>
                    <span className="font-mono text-xs font-bold text-sky-400">
                      {Math.round(ev.correctness_score * 100)}%
                    </span>
                  </div>
                  <p className="text-slate-400 text-[11px] leading-tight">{ev.correctness_reason}</p>
                </div>

                <div className="bg-slate-950/80 p-3.5 rounded-lg border border-slate-800">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-semibold text-slate-300">Grounding</span>
                    <span className="font-mono text-xs font-bold text-sky-400">
                      {Math.round(ev.grounding_score * 100)}%
                    </span>
                  </div>
                  <p className="text-slate-400 text-[11px] leading-tight">{ev.grounding_reason}</p>
                </div>

                <div className="bg-slate-950/80 p-3.5 rounded-lg border border-slate-800">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-semibold text-slate-300">Citations</span>
                    <span className="font-mono text-xs font-bold text-sky-400">
                      {Math.round(ev.citation_score * 100)}%
                    </span>
                  </div>
                  <p className="text-slate-400 text-[11px] leading-tight">{ev.citation_reason}</p>
                </div>

                <div className="bg-slate-950/80 p-3.5 rounded-lg border border-slate-800">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-semibold text-slate-300">Translation Fidelity</span>
                    <span className="font-mono text-xs font-bold text-sky-400">
                      {Math.round(ev.translation_score * 100)}%
                    </span>
                  </div>
                  <p className="text-slate-400 text-[11px] leading-tight">{ev.translation_reason}</p>
                </div>

                <div className="bg-slate-950/80 p-3.5 rounded-lg border border-slate-800">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-semibold text-slate-300">Trajectory</span>
                    <span className="font-mono text-xs font-bold text-sky-400">
                      {Math.round(ev.trajectory_score * 100)}%
                    </span>
                  </div>
                  <p className="text-slate-400 text-[11px] leading-tight">{ev.trajectory_reason}</p>
                </div>

                <div className="bg-slate-950/80 p-3.5 rounded-lg border border-slate-800">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-semibold text-slate-300">Execution Latency</span>
                    <span className="font-mono text-xs font-bold text-slate-300">{item.latency_ms} ms</span>
                  </div>
                  <p className="text-slate-400 text-[11px] leading-tight">
                    Captured from initial dispatch to completion.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === "claims" && (
            <div className="space-y-3">
              <p className="text-xs text-slate-400">
                Each empirical claim from the agent output is cross-referenced with retrieved statutory sections.
              </p>
              {ev.claims && ev.claims.length > 0 ? (
                ev.claims.map((claim, idx) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-xl border ${
                      claim.status === "SUPPORTED"
                        ? "bg-slate-950/50 border-emerald-900/40"
                        : claim.status === "CONTRADICTED"
                        ? "bg-rose-950/30 border-rose-800/60"
                        : "bg-amber-950/30 border-amber-800/60"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-slate-200 text-xs">{claim.claim_text}</span>
                      <span
                        className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                          claim.status === "SUPPORTED"
                            ? "bg-emerald-900/60 text-emerald-300 border border-emerald-700/60"
                            : claim.status === "CONTRADICTED"
                            ? "bg-rose-900/60 text-rose-300 border border-rose-700/60"
                            : "bg-amber-900/60 text-amber-300 border border-amber-700/60"
                        }`}
                      >
                        {claim.status}
                      </span>
                    </div>

                    {claim.evidence_text && (
                      <div className="mt-2 bg-slate-900 p-2.5 rounded border border-slate-800 text-[11px] text-slate-300">
                        <span className="font-semibold text-slate-400 block mb-0.5">
                          Corroborating Evidence ({claim.document_id} {claim.section_id}):
                        </span>
                        &quot;{claim.evidence_text}&quot;
                      </div>
                    )}

                    <p className="mt-2 text-xs text-slate-400">{claim.reason}</p>
                  </div>
                ))
              ) : (
                <p className="text-slate-500">No structured claims evaluated for this item.</p>
              )}
            </div>
          )}

          {activeTab === "evidence" && (
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-slate-200 mb-2">Citations Verification</h4>
                {ev.citations && ev.citations.length > 0 ? (
                  <div className="space-y-2">
                    {ev.citations.map((c, i) => (
                      <div key={i} className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg flex items-center justify-between">
                        <div>
                          <div className="font-mono text-xs font-bold text-sky-400">{c.citation_text}</div>
                          <p className="text-slate-400 text-xs mt-1">{c.reason}</p>
                        </div>
                        <span
                          className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                            c.status === "VALID"
                              ? "bg-emerald-900/60 text-emerald-300 border border-emerald-700/60"
                              : "bg-rose-900/60 text-rose-300 border border-rose-700/60"
                          }`}
                        >
                          {c.status}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 bg-amber-950/20 border border-amber-900/40 rounded-xl text-amber-300">
                    No formal citations were provided in the agent response.
                  </div>
                )}
              </div>

              <div>
                <h4 className="font-semibold text-slate-200 mb-2">Retrieved Document Chunks</h4>
                <div className="space-y-2">
                  {item.retrieved_documents && item.retrieved_documents.length > 0 ? (
                    item.retrieved_documents.map((doc, idx) => (
                      <div key={idx} className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-xl space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-mono font-bold text-sky-400 text-xs">
                            {doc.document_id} {doc.section_id}
                          </span>
                          <span className="text-[11px] text-slate-400">{doc.heading}</span>
                        </div>
                        <p className="text-slate-300 text-xs italic">&quot;{doc.content}&quot;</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-500">No documents were retrieved during this execution.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === "translation" && (
            <div className="space-y-4">
              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Original Multilingual Answer ({item.language.toUpperCase()})
                </span>
                <p className="text-slate-200 text-sm font-medium">{item.final_answer}</p>
              </div>

              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider block mb-1">
                  Back-Translated to English (Semantic Preservation Check)
                </span>
                <p className="text-slate-200 text-sm font-medium">{ev.back_translation || "N/A"}</p>
              </div>

              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-1">
                  Evaluator Drift Diagnosis
                </span>
                <p className="text-slate-300 text-xs">{ev.translation_reason}</p>
              </div>
            </div>
          )}

          {activeTab === "trace" && (
            <div className="space-y-3">
              <p className="text-xs text-slate-400">
                Chronological sequence of observable agent execution events (no hidden CoT).
              </p>
              <div className="space-y-2">
                {item.trace_events && item.trace_events.length > 0 ? (
                  item.trace_events.map((te) => (
                    <div key={te.step} className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg flex items-start space-x-3">
                      <span className="font-mono text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                        #{te.step}
                      </span>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-bold text-xs uppercase text-sky-400">{te.event_type}</span>
                          <span className="text-[10px] text-slate-500 font-mono">
                            {new Date(te.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="mt-1 text-[11px] text-slate-400 font-mono bg-slate-900/60 p-2 rounded overflow-x-auto">
                          {JSON.stringify({ input: te.input_data, output: te.output_data }, null, 2)}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-slate-500">No trace events captured.</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
