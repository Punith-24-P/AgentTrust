"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ShieldCheck,
  CheckCircle2,
  FileCheck2,
  Quote,
  Languages,
  Activity,
  Download,
  FileText,
  GitCompare,
  ArrowLeft,
  Clock,
  RefreshCw,
  ExternalLink,
} from "lucide-react";
import { fetchRun, fetchRunMetrics, fetchRunResults, getExportUrl } from "@/lib/api";
import { RunItem, RunMetrics, TestResultItem } from "@/types";
import ScoreCard from "@/components/ScoreCard";
import LanguageBreakdownTable from "@/components/LanguageBreakdownTable";
import TestResultsTable from "@/components/TestResultsTable";

export default function RunDashboardPage() {
  const params = useParams();
  const runId = params.id as string;

  const [run, setRun] = useState<RunItem | null>(null);
  const [metrics, setMetrics] = useState<RunMetrics | null>(null);
  const [results, setResults] = useState<TestResultItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (runId) {
      loadRunData();
    }
  }, [runId]);

  const loadRunData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [rData, mData, resData] = await Promise.all([
        fetchRun(runId),
        fetchRunMetrics(runId).catch(() => null),
        fetchRunResults(runId).catch(() => []),
      ]);
      setRun(rData);
      setMetrics(mData);
      setResults(resData);
    } catch (err: any) {
      setError(err.message || "Failed to load run details.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-3">
        <div className="w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs text-slate-400">Loading reliability report for run {runId?.slice(0, 8)}...</p>
      </div>
    );
  }

  if (error || !run) {
    return (
      <div className="py-16 text-center space-y-4">
        <p className="text-rose-400 font-semibold">{error || "Run not found"}</p>
        <Link href="/runs" className="text-xs text-sky-400 hover:underline">
          &larr; Back to all runs
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="space-y-1">
          <Link
            href="/runs"
            className="text-xs text-slate-400 hover:text-slate-200 inline-flex items-center space-x-1 mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>All Evaluation Runs</span>
          </Link>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-extrabold text-slate-100 flex items-center space-x-2">
              <span>Run #{run.id.slice(0, 8)}</span>
              <span
                className={`text-[11px] font-bold uppercase px-2.5 py-0.5 rounded-full ${
                  run.status === "COMPLETED"
                    ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                    : "bg-sky-950 text-sky-400 border border-sky-800 animate-pulse"
                }`}
              >
                {run.status}
              </span>
            </h1>
          </div>
          <div className="text-xs text-slate-400 flex flex-wrap items-center gap-x-4 gap-y-1 pt-1">
            <span>
              Agent: <strong className="text-slate-200">{run.agent_name}</strong> ({run.agent_version})
            </span>
            <span>
              Dataset: <strong className="text-slate-200">{run.dataset_name}</strong>
            </span>
            <span>
              Duration: <strong className="text-slate-200">{run.duration_seconds || "-"}s</strong>
            </span>
          </div>
        </div>

        {/* Export and Compare Toolbar */}
        <div className="flex flex-wrap items-center gap-2">
          <Link
            href={`/compare?before=${run.id}`}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
          >
            <GitCompare className="w-3.5 h-3.5" />
            <span>Compare Run</span>
          </Link>

          <a
            href={getExportUrl(run.id, "html")}
            target="_blank"
            rel="noreferrer"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
          >
            <FileText className="w-3.5 h-3.5 text-sky-400" />
            <span>HTML Report</span>
          </a>

          <a
            href={getExportUrl(run.id, "csv")}
            download
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>CSV</span>
          </a>

          <a
            href={getExportUrl(run.id, "json")}
            download
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>JSON</span>
          </a>
        </div>
      </div>

      {/* Primary KPI Grid */}
      {metrics && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
            {/* Overall Composite Score Card (Spans 2 columns) */}
            <div className="sm:col-span-2 bg-gradient-to-br from-slate-900 via-slate-900 to-sky-950/40 border border-sky-900/40 rounded-xl p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-sky-400 uppercase tracking-wider flex items-center space-x-1.5">
                  <ShieldCheck className="w-4 h-4" />
                  <span>Composite Reliability Score</span>
                </span>
                <span className="text-[10px] font-mono text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded">
                  Formula: 30/30/15/15/10
                </span>
              </div>

              <div className="mt-3 flex items-baseline space-x-3">
                <div className="text-4xl font-extrabold tracking-tight text-white">
                  {Math.round(metrics.composite_score * 100)}%
                </div>
                <div className="text-xs text-slate-400">
                  Passed tests: <strong className="text-slate-100">{metrics.passed_tests}</strong> / {metrics.total_tests}
                </div>
              </div>

              <div className="mt-3 w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="h-full bg-sky-400 rounded-full transition-all duration-700"
                  style={{ width: `${Math.round(metrics.composite_score * 100)}%` }}
                />
              </div>

              <p className="mt-3 text-[11px] text-slate-400 leading-relaxed">
                Normalized weighted reliability across factual accuracy, source grounding, citation validity, and trajectory fidelity.
              </p>
            </div>

            {/* 1. Correctness */}
            <ScoreCard
              label="Correctness"
              score={metrics.correctness.score}
              passRate={metrics.correctness.pass_rate}
              weight="30%"
              icon={<CheckCircle2 className="w-4 h-4 text-emerald-400" />}
              description="Statutory facts, sections, and semantic meaning."
            />

            {/* 2. Grounding */}
            <ScoreCard
              label="Grounding"
              score={metrics.grounding.score}
              weight="30%"
              icon={<FileCheck2 className="w-4 h-4 text-sky-400" />}
              description={`${metrics.grounding.supported} supported, ${metrics.grounding.unsupported} unsupported, ${metrics.grounding.contradicted} contradicted.`}
            />

            {/* 3. Citation */}
            <ScoreCard
              label="Citation"
              score={metrics.citation.score}
              weight="15%"
              icon={<Quote className="w-4 h-4 text-indigo-400" />}
              description={`${metrics.citation.valid} valid, ${metrics.citation.mismatch} mismatches.`}
            />

            {/* 4. Translation */}
            <ScoreCard
              label="Translation"
              score={metrics.translation.score}
              weight="15%"
              icon={<Languages className="w-4 h-4 text-purple-400" />}
              description={`Back-translation drift: ${Math.round(metrics.translation.major_drift_rate * 100)}% major drift.`}
            />
          </div>

          {/* Severity Alert Strip */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl px-5 py-3 flex flex-wrap items-center justify-between text-xs gap-3">
            <span className="font-semibold text-slate-400 uppercase tracking-wider text-[11px]">
              Failure Severity Distribution:
            </span>
            <div className="flex items-center space-x-4">
              <span className="flex items-center space-x-1.5 text-rose-400">
                <span className="w-2 h-2 rounded-full bg-rose-500" />
                <span>Critical: {metrics.severity_breakdown.CRITICAL || 0}</span>
              </span>
              <span className="flex items-center space-x-1.5 text-amber-400">
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                <span>High: {metrics.severity_breakdown.HIGH || 0}</span>
              </span>
              <span className="flex items-center space-x-1.5 text-yellow-400">
                <span className="w-2 h-2 rounded-full bg-yellow-500" />
                <span>Medium: {metrics.severity_breakdown.MEDIUM || 0}</span>
              </span>
              <span className="flex items-center space-x-1.5 text-slate-400">
                <span className="w-2 h-2 rounded-full bg-slate-500" />
                <span>Low: {metrics.severity_breakdown.LOW || 0}</span>
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Multilingual Breakdown */}
      {metrics && metrics.language_breakdown && (
        <LanguageBreakdownTable data={metrics.language_breakdown} />
      )}

      {/* Filterable Test Results Table */}
      <TestResultsTable results={results} />
    </div>
  );
}
