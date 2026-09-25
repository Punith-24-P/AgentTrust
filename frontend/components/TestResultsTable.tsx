"use client";

import React, { useState } from "react";
import { Search, Filter, AlertCircle, CheckCircle2, ChevronRight, ArrowUpDown } from "lucide-react";
import { TestResultItem } from "@/types";
import FailureDrilldownModal from "@/components/FailureDrilldownModal";

interface TestResultsTableProps {
  results: TestResultItem[];
}

export default function TestResultsTable({ results }: TestResultsTableProps) {
  const [search, setSearch] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [selectedSeverity, setSelectedSeverity] = useState("all");
  const [selectedItem, setSelectedItem] = useState<TestResultItem | null>(null);

  const filtered = results.filter((item) => {
    const ev = item.evaluation_result;
    if (selectedLanguage !== "all" && item.language.toLowerCase() !== selectedLanguage.toLowerCase()) {
      return false;
    }
    if (selectedStatus !== "all" && ev.overall_status !== selectedStatus) {
      return false;
    }
    if (selectedSeverity !== "all" && ev.severity !== selectedSeverity) {
      return false;
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      const matchId = item.external_id.toLowerCase().includes(q);
      const matchQ = item.question.toLowerCase().includes(q);
      const matchA = item.final_answer.toLowerCase().includes(q);
      if (!matchId && !matchQ && !matchA) return false;
    }
    return true;
  });

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return "bg-rose-950/80 text-rose-300 border-rose-800/80";
      case "HIGH":
        return "bg-amber-950/80 text-amber-300 border-amber-800/80";
      case "MEDIUM":
        return "bg-yellow-950/80 text-yellow-300 border-yellow-800/80";
      default:
        return "bg-slate-800 text-slate-400 border-slate-700";
    }
  };

  const getStatusBadge = (status: string) => {
    return status === "PASS"
      ? "bg-emerald-950/80 text-emerald-300 border-emerald-800/80"
      : "bg-rose-950/80 text-rose-300 border-rose-800/80";
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
      {/* Table Header & Controls */}
      <div className="p-4 border-b border-slate-800 bg-slate-950/50 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center space-x-2">
            <span>Test Case Results</span>
            <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full font-mono">
              {filtered.length} of {results.length}
            </span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Click on any test case to open the full evidence diagnostic view
          </p>
        </div>

        {/* Filter Toolbar */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search tests..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-slate-900 border border-slate-700/80 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 w-44"
            />
          </div>

          {/* Language filter */}
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
          >
            <option value="all">All Languages</option>
            <option value="en">English (EN)</option>
            <option value="kn">Kannada (KN)</option>
            <option value="hi">Hindi (HI)</option>
            <option value="te">Telugu (TE)</option>
          </select>

          {/* Status filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
          >
            <option value="all">All Statuses</option>
            <option value="PASS">PASS Only</option>
            <option value="FAIL">FAIL Only</option>
          </select>

          {/* Severity filter */}
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
          >
            <option value="all">All Severities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/40 text-slate-400 uppercase font-semibold text-[11px] border-b border-slate-800">
            <tr>
              <th className="px-5 py-3">Test ID</th>
              <th className="px-3 py-3">Lang</th>
              <th className="px-3 py-3">Status</th>
              <th className="px-3 py-3">Correctness</th>
              <th className="px-3 py-3">Grounding</th>
              <th className="px-3 py-3">Citation</th>
              <th className="px-3 py-3">Translation</th>
              <th className="px-3 py-3">Trajectory</th>
              <th className="px-3 py-3">Severity</th>
              <th className="px-4 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={10} className="px-6 py-8 text-center text-slate-500">
                  No evaluation test cases matched the selected criteria.
                </td>
              </tr>
            ) : (
              filtered.map((item) => {
                const ev = item.evaluation_result;
                return (
                  <tr
                    key={item.id}
                    onClick={() => setSelectedItem(item)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="px-5 py-3.5 font-mono font-bold text-sky-400">
                      {item.external_id}
                    </td>
                    <td className="px-3 py-3.5 uppercase font-mono text-[10px] text-slate-400">
                      {item.language}
                    </td>
                    <td className="px-3 py-3.5">
                      <span className={`inline-block px-2 py-0.5 rounded-full font-bold border text-[10px] uppercase ${getStatusBadge(ev.overall_status)}`}>
                        {ev.overall_status}
                      </span>
                    </td>
                    <td className="px-3 py-3.5">
                      <span className={ev.correctness_status === "PASS" ? "text-emerald-400" : "text-rose-400 font-semibold"}>
                        {ev.correctness_status}
                      </span>
                    </td>
                    <td className="px-3 py-3.5">
                      <span className={ev.grounding_status === "SUPPORTED" ? "text-emerald-400" : "text-rose-400 font-semibold"}>
                        {ev.grounding_status}
                      </span>
                    </td>
                    <td className="px-3 py-3.5">
                      <span className={ev.citation_status === "VALID" ? "text-emerald-400" : "text-amber-400 font-semibold"}>
                        {ev.citation_status}
                      </span>
                    </td>
                    <td className="px-3 py-3.5">
                      {item.language === "en" ? (
                        <span className="text-slate-600 font-mono text-[10px]">N/A</span>
                      ) : (
                        <span className={ev.translation_status === "PASS" ? "text-emerald-400" : "text-amber-400 font-semibold"}>
                          {ev.translation_status}
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-3.5">
                      <span className={ev.trajectory_status === "PASS" ? "text-emerald-400" : "text-amber-400 font-semibold"}>
                        {ev.trajectory_status}
                      </span>
                    </td>
                    <td className="px-3 py-3.5">
                      <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${getSeverityBadge(ev.severity)}`}>
                        {ev.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-right text-slate-400 hover:text-sky-400">
                      <span className="text-xs font-semibold flex items-center justify-end space-x-1">
                        <span>Inspect</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Drill-down Modal */}
      <FailureDrilldownModal item={selectedItem} onClose={() => setSelectedItem(null)} />
    </div>
  );
}
