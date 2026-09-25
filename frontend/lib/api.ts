import {
  Project,
  Agent,
  Dataset,
  TestCase,
  RunItem,
  TestResultItem,
  RunMetrics,
  RunComparison
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/projects`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

export async function createProject(data: { name: string; description?: string }): Promise<Project> {
  const res = await fetch(`${API_BASE}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create project");
  return res.json();
}

export async function fetchAgents(projectId?: string): Promise<Agent[]> {
  const url = projectId ? `${API_BASE}/agents?project_id=${projectId}` : `${API_BASE}/agents`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch agents");
  return res.json();
}

export async function createAgent(data: {
  project_id: string;
  name: string;
  description?: string;
  adapter_type: "demo" | "http";
  endpoint?: string;
  version: string;
  model: string;
  supported_languages: string[];
  config_json?: Record<string, any>;
}): Promise<Agent> {
  const res = await fetch(`${API_BASE}/agents`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create agent");
  return res.json();
}

export async function fetchDatasets(projectId?: string): Promise<Dataset[]> {
  const url = projectId ? `${API_BASE}/datasets?project_id=${projectId}` : `${API_BASE}/datasets`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch datasets");
  return res.json();
}

export async function fetchTestCases(datasetId: string, language?: string): Promise<TestCase[]> {
  const url = language
    ? `${API_BASE}/datasets/${datasetId}/test-cases?language=${language}`
    : `${API_BASE}/datasets/${datasetId}/test-cases`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch test cases");
  return res.json();
}

export async function createTestCase(datasetId: string, data: any): Promise<TestCase> {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/test-cases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create test case");
  return res.json();
}

export async function fetchRuns(projectId?: string): Promise<RunItem[]> {
  const url = projectId ? `${API_BASE}/runs?project_id=${projectId}` : `${API_BASE}/runs`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch runs");
  return res.json();
}

export async function fetchRun(runId: string): Promise<RunItem> {
  const res = await fetch(`${API_BASE}/runs/${runId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch run");
  return res.json();
}

export async function fetchRunResults(
  runId: string,
  params?: { language?: string; status?: string; severity?: string; evaluator?: string; search?: string }
): Promise<TestResultItem[]> {
  const searchParams = new URLSearchParams();
  if (params?.language) searchParams.append("language", params.language);
  if (params?.status) searchParams.append("status", params.status);
  if (params?.severity) searchParams.append("severity", params.severity);
  if (params?.evaluator) searchParams.append("evaluator", params.evaluator);
  if (params?.search) searchParams.append("search", params.search);

  const query = searchParams.toString();
  const url = query ? `${API_BASE}/runs/${runId}/results?${query}` : `${API_BASE}/runs/${runId}/results`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch run results");
  return res.json();
}

export async function fetchResultDrilldown(resultId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/results/${resultId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch result drilldown");
  return res.json();
}

export async function fetchRunMetrics(runId: string): Promise<RunMetrics> {
  const res = await fetch(`${API_BASE}/runs/${runId}/metrics`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch run metrics");
  return res.json();
}

export async function fetchRunComparison(beforeRunId: string, afterRunId: string): Promise<RunComparison> {
  const res = await fetch(`${API_BASE}/runs/${beforeRunId}/compare/${afterRunId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to compare runs");
  return res.json();
}

export async function triggerNewRun(data: {
  project_id: string;
  agent_id: string;
  dataset_id: string;
  evaluators_config?: Record<string, boolean>;
}): Promise<RunItem> {
  const res = await fetch(`${API_BASE}/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to trigger run");
  return res.json();
}

export async function triggerOneClickDemo(): Promise<{
  status: string;
  message: string;
  project_id: string;
  baseline_run_id: string;
  optimized_run_id: string;
}> {
  const res = await fetch(`${API_BASE}/demo/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Failed to trigger demo evaluation");
  return res.json();
}

export function getExportUrl(runId: string, format: "html" | "json" | "csv"): string {
  return `${API_BASE}/reports/${runId}/${format}`;
}
