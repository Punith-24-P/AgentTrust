"use client";

import React, { useEffect, useState } from "react";
import {
  Database,
  Plus,
  Search,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Copy,
  Tag,
  Upload,
  ShieldAlert,
} from "lucide-react";
import {
  fetchDatasets,
  fetchTestCases,
  createTestCase,
  validateDataset,
  publishDatasetVersion,
  duplicateDataset,
} from "@/lib/api";
import { Dataset, TestCase, DatasetValidationReport } from "@/types";

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Validation report state
  const [validationReport, setValidationReport] = useState<DatasetValidationReport | null>(null);
  const [validating, setValidating] = useState(false);

  // Version modal state
  const [showVersionModal, setShowVersionModal] = useState(false);
  const [newVersion, setNewVersion] = useState("1.1.0");
  const [changelog, setChangelog] = useState("");

  // Add Test Case Modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [externalId, setExternalId] = useState("");
  const [language, setLanguage] = useState("en");
  const [category, setCategory] = useState("correctness");
  const [question, setQuestion] = useState("");
  const [expectedAnswer, setExpectedAnswer] = useState("");
  const [docId, setDocId] = useState("CIVIC-ACT-2024");
  const [secId, setSecId] = useState("Section 12(a)");
  const [factType, setFactType] = useState("number");
  const [factExpected, setFactExpected] = useState("30");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      setLoading(true);
      const data = await fetchDatasets();
      setDatasets(data);
      if (data.length > 0 && !selectedDatasetId) {
        setSelectedDatasetId(data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedDatasetId) {
      fetchTestCases(
        selectedDatasetId,
        selectedLanguage !== "all" ? selectedLanguage : undefined
      ).then((tc) => setTestCases(tc));
      setValidationReport(null);
    }
  }, [selectedDatasetId, selectedLanguage]);

  const handleValidate = async () => {
    if (!selectedDatasetId) return;
    try {
      setValidating(true);
      const report = await validateDataset(selectedDatasetId);
      setValidationReport(report);
    } catch (err: any) {
      alert("Validation failed: " + err.message);
    } finally {
      setValidating(false);
    }
  };

  const handlePublishVersion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDatasetId) return;
    try {
      await publishDatasetVersion(selectedDatasetId, newVersion, changelog);
      setShowVersionModal(false);
      setChangelog("");
      loadDatasets();
    } catch (err: any) {
      alert("Failed to publish version: " + err.message);
    }
  };

  const handleDuplicate = async () => {
    if (!selectedDatasetId) return;
    try {
      const copy = await duplicateDataset(selectedDatasetId);
      await loadDatasets();
      setSelectedDatasetId(copy.id);
    } catch (err: any) {
      alert("Failed to duplicate dataset: " + err.message);
    }
  };

  const handleAddTestCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDatasetId) return;

    try {
      setSubmitting(true);
      await createTestCase(selectedDatasetId, {
        external_id: externalId || `TC-${Date.now().toString().slice(-4)}`,
        language,
        category,
        question,
        expected_answer: expectedAnswer,
        source_documents: [{ document_id: docId, section_id: secId }],
        required_facts: [{ id: "fact-1", type: factType, expected: factExpected }],
        potential_traps: ["Ambiguous timeline"],
      });
      setShowAddModal(false);
      setQuestion("");
      setExpectedAnswer("");
      setExternalId("");
      const tc = await fetchTestCases(
        selectedDatasetId,
        selectedLanguage !== "all" ? selectedLanguage : undefined
      );
      setTestCases(tc);
    } catch (err: any) {
      alert("Failed to add test case: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const selectedDataset = datasets.find((d) => d.id === selectedDatasetId);

  const filteredTestCases = testCases.filter((tc) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      tc.external_id.toLowerCase().includes(q) ||
      tc.question.toLowerCase().includes(q) ||
      tc.expected_answer.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center space-x-2.5">
            <Database className="w-6 h-6 text-sky-400" />
            <span>Evaluation Datasets</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Version-controlled evaluation datasets with required fact schemas and pre-run validation.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleValidate}
            disabled={!selectedDatasetId || validating}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-medium transition disabled:opacity-50"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-sky-400" />
            <span>{validating ? "Validating..." : "Validate Dataset"}</span>
          </button>

          <button
            onClick={() => setShowVersionModal(true)}
            disabled={!selectedDatasetId}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-medium transition disabled:opacity-50"
          >
            <Tag className="w-3.5 h-3.5 text-indigo-400" />
            <span>Publish Version</span>
          </button>

          <button
            onClick={handleDuplicate}
            disabled={!selectedDatasetId}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-medium transition disabled:opacity-50"
          >
            <Copy className="w-3.5 h-3.5 text-slate-400" />
            <span>Duplicate</span>
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            disabled={!selectedDatasetId}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-semibold transition disabled:opacity-50"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Test Case</span>
          </button>
        </div>
      </div>

      {/* Validation Banner if validated */}
      {validationReport && (
        <div
          className={`p-4 rounded-xl border ${
            validationReport.is_valid
              ? "bg-emerald-950/30 border-emerald-800/40 text-emerald-300"
              : "bg-red-950/30 border-red-800/40 text-red-300"
          } space-y-2`}
        >
          <div className="flex items-center justify-between text-xs font-semibold">
            <div className="flex items-center gap-2">
              {validationReport.is_valid ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <XCircle className="w-4 h-4 text-red-400" />
              )}
              <span>
                {validationReport.is_valid
                  ? "Dataset Validation Passed: Ready for Evaluation"
                  : "Dataset Validation Found Blocking Issues"}
              </span>
            </div>
            <div className="font-mono text-[11px]">
              {validationReport.errors_count} Errors • {validationReport.warnings_count} Warnings
            </div>
          </div>

          {validationReport.issues.length > 0 && (
            <ul className="text-xs space-y-1 pt-1 max-h-36 overflow-y-auto">
              {validationReport.issues.map((iss, idx) => (
                <li key={idx} className="flex items-center gap-2">
                  <span
                    className={`text-[9px] font-mono px-1.5 py-0.5 rounded ${
                      iss.level === "ERROR"
                        ? "bg-red-950 border border-red-800 text-red-400"
                        : "bg-amber-950 border border-amber-800 text-amber-400"
                    }`}
                  >
                    {iss.level}
                  </span>
                  <span className="text-slate-300">{iss.message}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Datasets Sidebar */}
        <div className="lg:col-span-1 space-y-3">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
            Datasets
          </span>

          <div className="space-y-2">
            {datasets.map((d) => (
              <button
                key={d.id}
                onClick={() => setSelectedDatasetId(d.id)}
                className={`w-full text-left p-4 rounded-xl border transition-all ${
                  selectedDatasetId === d.id
                    ? "bg-[#111827] border-sky-500 shadow-sm"
                    : "bg-[#111827]/60 border-[#1e293b] hover:border-slate-700"
                }`}
              >
                <div className="font-bold text-xs text-white">{d.name}</div>
                <div className="flex items-center gap-2 text-[11px] text-slate-400 mt-1">
                  <span>Version:</span>
                  <span className="font-mono text-sky-400 font-semibold">{d.version}</span>
                </div>
                <div className="text-[11px] font-mono text-slate-400 mt-2">
                  {d.test_cases_count !== undefined ? d.test_cases_count : testCases.length} Test Cases
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Test Cases Viewer */}
        <div className="lg:col-span-3 space-y-4">
          <div className="bg-[#111827] border border-[#1e293b] rounded-xl p-3.5 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <span className="text-xs font-bold text-white uppercase tracking-wider whitespace-nowrap">
                Test Cases ({filteredTestCases.length})
              </span>
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <div className="relative flex-1 sm:w-64">
                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search test ID or question..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
                />
              </div>

              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="bg-[#0b0f19] border border-[#1e293b] rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
              >
                <option value="all">All Languages</option>
                <option value="en">English (EN)</option>
                <option value="kn">Kannada (KN)</option>
                <option value="hi">Hindi (HI)</option>
                <option value="te">Telugu (TE)</option>
              </select>
            </div>
          </div>

          <div className="space-y-3">
            {filteredTestCases.map((tc) => (
              <div
                key={tc.id}
                className="bg-[#111827] border border-[#1e293b] rounded-xl p-4 space-y-3 text-xs"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-sky-400 text-xs">{tc.external_id}</span>
                    <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {tc.language}
                    </span>
                    <span className="text-[10px] uppercase px-2 py-0.5 rounded bg-slate-800/60 text-slate-400">
                      {tc.category}
                    </span>
                  </div>
                </div>

                <div>
                  <span className="font-semibold text-slate-400 block mb-0.5">Question:</span>
                  <p className="text-slate-100 text-sm leading-relaxed">{tc.question}</p>
                </div>

                <div className="bg-[#0b0f19] p-3 rounded-lg border border-[#1e293b]">
                  <span className="font-semibold text-emerald-400 block mb-0.5">Expected Answer:</span>
                  <p className="text-slate-300 text-xs leading-relaxed">{tc.expected_answer}</p>
                </div>

                {tc.required_facts && tc.required_facts.length > 0 && (
                  <div>
                    <span className="font-semibold text-slate-400 block mb-1">
                      Required Empirical Facts:
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {tc.required_facts.map((f) => (
                        <span
                          key={f.id}
                          className="px-2 py-1 bg-[#0b0f19] border border-[#1e293b] rounded text-[11px] text-slate-300 font-mono"
                        >
                          {f.type}: <strong className="text-sky-400">{f.expected}</strong>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Publish Version Modal */}
      {showVersionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-[#111827] border border-[#1e293b] rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Publish New Dataset Version</h3>
            <p className="text-xs text-slate-400">
              Create an immutable version snapshot for reproducible benchmark evaluation.
            </p>

            <form onSubmit={handlePublishVersion} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Semantic Version</label>
                <input
                  type="text"
                  required
                  placeholder="1.1.0"
                  value={newVersion}
                  onChange={(e) => setNewVersion(e.target.value)}
                  className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 font-mono focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Changelog Notes</label>
                <textarea
                  rows={3}
                  placeholder="Describe added or updated test cases..."
                  value={changelog}
                  onChange={(e) => setChangelog(e.target.value)}
                  className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowVersionModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold"
                >
                  Publish Version
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Test Case Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-[#111827] border border-[#1e293b] rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Add Structured Test Case</h3>

            <form onSubmit={handleAddTestCase} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Test ID</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. EN-010"
                    value={externalId}
                    onChange={(e) => setExternalId(e.target.value)}
                    className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Language</label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                  >
                    <option value="en">English (EN)</option>
                    <option value="kn">Kannada (KN)</option>
                    <option value="hi">Hindi (HI)</option>
                    <option value="te">Telugu (TE)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Question</label>
                <textarea
                  rows={2}
                  required
                  placeholder="Enter the factual evaluation question..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Expected Ground-Truth Answer</label>
                <textarea
                  rows={2}
                  required
                  placeholder="The ground-truth answer with evidence citations..."
                  value={expectedAnswer}
                  onChange={(e) => setExpectedAnswer(e.target.value)}
                  className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Source Document</label>
                  <input
                    type="text"
                    required
                    value={docId}
                    onChange={(e) => setDocId(e.target.value)}
                    className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Section</label>
                  <input
                    type="text"
                    required
                    value={secId}
                    onChange={(e) => setSecId(e.target.value)}
                    className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Fact Type</label>
                  <select
                    value={factType}
                    onChange={(e) => setFactType(e.target.value)}
                    className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                  >
                    <option value="number">number</option>
                    <option value="date">date</option>
                    <option value="duration">duration</option>
                    <option value="section">section</option>
                    <option value="authority">authority</option>
                    <option value="named_entity">named_entity</option>
                    <option value="condition">condition</option>
                    <option value="exception">exception</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Required Exact Fact</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 30"
                    value={factExpected}
                    onChange={(e) => setFactExpected(e.target.value)}
                    className="w-full bg-[#0b0f19] border border-[#1e293b] rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
              </div>

              <div className="pt-3 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold disabled:opacity-50"
                >
                  {submitting ? "Adding..." : "Save Test Case"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
