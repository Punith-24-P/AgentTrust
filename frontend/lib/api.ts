import {
  User,
  Workspace,
  Project,
  Agent,
  AgentConnectionTestResult,
  Dataset,
  DatasetValidationReport,
  DatasetVersion,
  TestCase,
  EvaluationProfile,
  RunItem,
  TestResultItem,
  RunMetrics,
  RunComparison,
  PreFlightResult,
  RegressionAnalysis,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("agenttrust_token");
}

export function setAuthToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("agenttrust_token", token);
  }
}

export function removeAuthToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("agenttrust_token");
    localStorage.removeItem("agenttrust_user");
  }
}

function getHeaders(customHeaders: Record<string, string> = {}): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...customHeaders,
  };
  const token = getAuthToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// ----------------- Auth API -----------------
export async function registerUser(data: {
  name: string;
  email: string;
  password: string;
  confirm_password?: string;
}): Promise<{ access_token: string; user: User; workspace_id?: string }> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Registration failed");
  }
  const result = await res.json();
  setAuthToken(result.access_token);
  if (typeof window !== "undefined") {
    localStorage.setItem("agenttrust_user", JSON.stringify(result.user));
  }
  return result;
}

export async function loginUser(data: {
  email: string;
  password: string;
  remember?: boolean;
}): Promise<{ access_token: string; user: User; workspace_id?: string }> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Invalid email or password");
  }
  const result = await res.json();
  setAuthToken(result.access_token);
  if (typeof window !== "undefined") {
    localStorage.setItem("agenttrust_user", JSON.stringify(result.user));
  }
  return result;
}

export async function getCurrentUser(): Promise<User | null> {
  const token = getAuthToken();
  if (!token) return null;
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: getHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    removeAuthToken();
    return null;
  }
  return res.json();
}

export async function logoutUser(): Promise<void> {
  try {
    await fetch(`${API_BASE}/auth/logout`, {
      method: "POST",
      headers: getHeaders(),
    });
  } catch (e) {
    // Ignore network error on logout
  }
  removeAuthToken();
}

export async function forgotPassword(email: string): Promise<any> {
  const res = await fetch(`${API_BASE}/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  return res.json();
}

// ----------------- Projects API -----------------
export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/projects`, { headers: getHeaders(), cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

export async function createProject(data: { name: string; description?: string }): Promise<Project> {
  const res = await fetch(`${API_BASE}/projects`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create project");
  return res.json();
}

// ----------------- Agents API -----------------
export async function fetchAgents(projectId?: string): Promise<Agent[]> {
  const url = projectId ? `${API_BASE}/agents?project_id=${projectId}` : `${API_BASE}/agents`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
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
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create agent");
  return res.json();
}

export async function testAgentConnection(agentId: string): Promise<AgentConnectionTestResult> {
  const res = await fetch(`${API_BASE}/agents/${agentId}/test-connection`, {
    method: "POST",
    headers: getHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Connection test failed");
  }
  return res.json();
}

// ----------------- Datasets API -----------------
export async function fetchDatasets(projectId?: string): Promise<Dataset[]> {
  const url = projectId ? `${API_BASE}/datasets?project_id=${projectId}` : `${API_BASE}/datasets`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch datasets");
  return res.json();
}

export async function createDataset(data: {
  project_id: string;
  name: string;
  description?: string;
  version?: string;
}): Promise<Dataset> {
  const res = await fetch(`${API_BASE}/datasets`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create dataset");
  return res.json();
}

export async function validateDataset(datasetId: string): Promise<DatasetValidationReport> {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/validate`, {
    headers: getHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to validate dataset");
  return res.json();
}

export async function publishDatasetVersion(
  datasetId: string,
  version: string,
  changelog?: string
): Promise<DatasetVersion> {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/versions`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ version, changelog }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to publish version");
  }
  return res.json();
}

export async function duplicateDataset(datasetId: string): Promise<Dataset> {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/duplicate`, {
    method: "POST",
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error("Failed to duplicate dataset");
  return res.json();
}

export async function fetchTestCases(datasetId: string, language?: string): Promise<TestCase[]> {
  const url = language
    ? `${API_BASE}/datasets/${datasetId}/test-cases?language=${language}`
    : `${API_BASE}/datasets/${datasetId}/test-cases`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch test cases");
  return res.json();
}

export async function createTestCase(datasetId: string, data: any): Promise<TestCase> {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/test-cases`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create test case");
  return res.json();
}

// ----------------- Evaluation Profiles API -----------------
export async function fetchEvaluationProfiles(): Promise<EvaluationProfile[]> {
  const res = await fetch(`${API_BASE}/evaluation-profiles`, {
    headers: getHeaders(),
    cache: "no-store",
  });
  if (!res.ok) return [];
  return res.json();
}

// ----------------- Runs API -----------------
export async function preflightCheck(data: {
  agent_id: string;
  dataset_id: string;
  evaluation_profile_id?: string;
}): Promise<PreFlightResult> {
  const res = await fetch(`${API_BASE}/runs/preflight`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Preflight check request failed");
  return res.json();
}

export async function triggerNewRun(data: {
  project_id: string;
  agent_id: string;
  dataset_id: string;
  agent_version?: string;
  dataset_version?: string;
  evaluation_profile_id?: string;
  evaluators_config?: Record<string, boolean>;
  concurrency?: number;
  test_case_subset?: string[];
  limit?: number;
  is_demo?: boolean;
}): Promise<RunItem> {
  const res = await fetch(`${API_BASE}/runs`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to trigger run");
  return res.json();
}

export async function preflightRunCheck(data: {
  agent_id: string;
  dataset_id: string;
  evaluation_profile_id?: string;
  dataset_version?: string;
}): Promise<PreFlightResult> {
  const res = await fetch(`${API_BASE}/runs/preflight`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to execute preflight check");
  return res.json();
}

export async function fetchRuns(projectId?: string): Promise<RunItem[]> {
  const url = projectId ? `${API_BASE}/runs?project_id=${projectId}` : `${API_BASE}/runs`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch runs");
  return res.json();
}

export async function fetchRun(runId: string): Promise<RunItem> {
  const res = await fetch(`${API_BASE}/runs/${runId}`, { headers: getHeaders(), cache: "no-store" });
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
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch run results");
  return res.json();
}

export async function fetchResultDrilldown(resultId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/results/${resultId}`, { headers: getHeaders(), cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch result drilldown");
  return res.json();
}

export async function fetchRunMetrics(runId: string): Promise<RunMetrics> {
  const res = await fetch(`${API_BASE}/runs/${runId}/metrics`, { headers: getHeaders(), cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch run metrics");
  return res.json();
}

export async function fetchRunComparison(beforeRunId: string, afterRunId: string): Promise<RunComparison> {
  const res = await fetch(`${API_BASE}/runs/${beforeRunId}/compare/${afterRunId}`, {
    headers: getHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to compare runs");
  return res.json();
}

export async function fetchRunRegression(runId: string, baselineRunId?: string): Promise<RegressionAnalysis> {
  const url = baselineRunId
    ? `${API_BASE}/runs/${runId}/regression?baseline_run_id=${baselineRunId}`
    : `${API_BASE}/runs/${runId}/regression`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch regression analysis");
  return res.json();
}

// ----------------- Settings API -----------------
export async function fetchProviderSettings(): Promise<any> {
  const res = await fetch(`${API_BASE}/settings/provider`, { headers: getHeaders(), cache: "no-store" });
  if (!res.ok) return {};
  return res.json();
}

export async function updateProviderSettings(data: any): Promise<any> {
  const res = await fetch(`${API_BASE}/settings/provider`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update provider settings");
  return res.json();
}

// ----------------- Demo & Reports API -----------------
export async function triggerOneClickDemo(): Promise<{
  status: string;
  message: string;
  project_id: string;
  baseline_run_id: string;
  optimized_run_id: string;
}> {
  const res = await fetch(`${API_BASE}/demo/run`, {
    method: "POST",
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error("Failed to trigger demo evaluation");
  return res.json();
}

export function getExportUrl(runId: string, format: "html" | "json" | "csv"): string {
  return `${API_BASE}/reports/${runId}/${format}`;
}
