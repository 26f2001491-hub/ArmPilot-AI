// Typed client for the ArmPilot-AI backend API.

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";
export const API_V1 = `${API_BASE}/api/v1`;

const TOKEN_KEY = "armpilot_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window !== "undefined") window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window !== "undefined") window.localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_V1}${path}`, { ...options, headers });

  if (res.status === 204) return undefined as T;

  const text = await res.text();
  const body = text ? JSON.parse(text) : null;

  if (!res.ok) {
    const detail =
      (body && (body.detail as string)) || `Request failed (${res.status})`;
    throw new ApiError(detail, res.status);
  }
  return body as T;
}

// ---- Types ----
export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface Benchmark {
  id: number;
  owner_id: number;
  model_name: string;
  runtime: string;
  quantization: string | null;
  prompt_tokens: number;
  generated_tokens: number;
  latency_ms: number | null;
  throughput_tps: number | null;
  ttft_ms: number | null;
  memory_mb: number | null;
  cpu_percent: number | null;
  status: string;
  notes: string | null;
  created_at: string;
}

export interface SystemMetrics {
  cpu_percent: number;
  cpu_count: number;
  load_average: number[];
  memory_total_mb: number;
  memory_used_mb: number;
  memory_percent: number;
  architecture: string;
  processor: string;
  timestamp: string;
}

export interface Recommendation {
  category: string;
  severity: string;
  title: string;
  detail: string;
  suggested_action: string;
}

export interface RecommendationReport {
  benchmark_id: number;
  model_name: string;
  score: number;
  recommendations: Recommendation[];
}

// ---- Endpoints ----
export const api = {
  register: (email: string, password: string) =>
    request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: async (email: string, password: string) => {
    const token = await request<{ access_token: string; token_type: string }>(
      "/auth/login",
      { method: "POST", body: JSON.stringify({ email, password }) },
    );
    setToken(token.access_token);
    return token;
  },

  me: () => request<User>("/auth/me"),

  listBenchmarks: () => request<Benchmark[]>("/benchmark"),

  createBenchmark: (payload: Partial<Benchmark>) =>
    request<Benchmark>("/benchmark", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  deleteBenchmark: (id: number) =>
    request<void>(`/benchmark/${id}`, { method: "DELETE" }),

  getRecommendations: (benchmarkId: number) =>
    request<RecommendationReport>(`/recommendation/${benchmarkId}`),

  metrics: () => request<SystemMetrics>("/metrics"),
};
