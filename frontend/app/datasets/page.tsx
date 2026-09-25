"use client";

import React, { useEffect, useState } from "react";
import { Database, Plus, Search, ChevronRight, FileCode, CheckCircle2 } from "lucide-react";
import { fetchDatasets, fetchTestCases, createTestCase, fetchProjects } from "@/lib/api";
import { Dataset, TestCase, Project } from "@/types";

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState("all");

  // Add Test Case Modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [externalId, setExternalId] = useState("");
  const [language, setLanguage] = useState("en");
  const [category, setCategory] = useState("correctness");
  const [question, setQuestion] = useState("");
  const [expectedAnswer, setExpectedAnswer] = useState("");
  const [docId, setDocId] = useState("DOC-CP-001");
  const [secId, setSecId] = useState("§4");
  const [factType, setFactType] = useState("deadline");
  const [factExpected, setFactExpected] = useState("30 calendar days");
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
      fetchTestCases(selectedDatasetId, selectedLanguage !== "all" ? selectedLanguage : undefined).then((tc) =>
        setTestCases(tc)
      );
    }
  }, [selectedDatasetId, selectedLanguage]);

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
        potential_traps: ["Statutory discrepancy"],
      });
      setShowAddModal(false);
      setQuestion("");
      setExpectedAnswer("");
      // Reload test cases
      const tc = await fetchTestCases(selectedDatasetId, selectedLanguage !== "all" ? selectedLanguage : undefined);
      setTestCases(tc);
    } catch (err: any) {
      alert("Failed to add test case: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center space-x-2.5">
            <Database className="w-6 h-6 text-sky-400" />
            <span>Test Datasets</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Structured benchmark test cases across English, Kannada, Hindi, and Telugu
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          disabled={!selectedDatasetId}
          className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-bold transition-colors disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          <span>Add Test Case</span>
        </button>
      </div>

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
                    ? "bg-slate-900 border-sky-500 shadow-sm"
                    : "bg-slate-950/60 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="font-bold text-xs text-slate-200">{d.name}</div>
                <div className="text-[11px] text-slate-400 mt-1">Version: {d.version}</div>
                <div className="text-[11px] font-mono text-sky-400 mt-2">
                  {d.test_cases_count || testCases.length} Test Cases
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Test Cases Viewer */}
        <div className="lg:col-span-3 space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Test Cases ({testCases.length})
            </span>

            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
            >
              <option value="all">All Languages</option>
              <option value="en">English (EN)</option>
              <option value="kn">Kannada (KN)</option>
              <option value="hi">Hindi (HI)</option>
              <option value="te">Telugu (TE)</option>
            </select>
          </div>

          <div className="space-y-3">
            {testCases.map((tc) => (
              <div key={tc.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3 text-xs">
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
                  <p className="text-slate-100 text-sm">{tc.question}</p>
                </div>

                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                  <span className="font-semibold text-emerald-400 block mb-0.5">Expected Answer:</span>
                  <p className="text-slate-300 text-xs">{tc.expected_answer}</p>
                </div>

                {tc.required_facts && tc.required_facts.length > 0 && (
                  <div>
                    <span className="font-semibold text-slate-400 block mb-1">Required Empirical Facts:</span>
                    <div className="flex flex-wrap gap-2">
                      {tc.required_facts.map((f) => (
                        <span key={f.id} className="px-2 py-1 bg-slate-950 border border-slate-800 rounded text-[11px] text-slate-300 font-mono">
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

      {/* Add Test Case Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-xl">
            <h3 className="text-base font-bold text-slate-100">Add New Structured Test Case</h3>

            <form onSubmit={handleAddTestCase} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Test ID</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. EN-009 or KN-009"
                    value={externalId}
                    onChange={(e) => setExternalId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-medium mb-1">Language</label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                  >
                    <option value="en">English (EN)</option>
                    <option value="kn">Kannada (KN)</option>
                    <option value="hi">Hindi (HI)</option>
                    <option value="te">Telugu (TE)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Question</label>
                <textarea
                  rows={2}
                  required
                  placeholder="Enter the factual or legal question..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Expected Statutory Answer</label>
                <textarea
                  rows={2}
                  required
                  placeholder="The ground-truth answer with citations..."
                  value={expectedAnswer}
                  onChange={(e) => setExpectedAnswer(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Source Document</label>
                  <input
                    type="text"
                    required
                    value={docId}
                    onChange={(e) => setDocId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Section ID</label>
                  <input
                    type="text"
                    required
                    value={secId}
                    onChange={(e) => setSecId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Required Fact Type</label>
                  <select
                    value={factType}
                    onChange={(e) => setFactType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
                  >
                    <option value="deadline">deadline</option>
                    <option value="section">section</option>
                    <option value="number">number</option>
                    <option value="authority">authority</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Required Exact Fact</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 30 calendar days"
                    value={factExpected}
                    onChange={(e) => setFactExpected(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
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
