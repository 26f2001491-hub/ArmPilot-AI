"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import {
  api,
  type Benchmark,
  type RecommendationReport,
  type SystemMetrics,
} from "../../lib/api";
import { useAuth } from "../../lib/auth";

const RUNTIMES = ["onnxruntime", "llama_cpp", "ollama", "openai"];

function severityColor(severity: string): string {
  if (severity === "critical") return "text-red-600";
  if (severity === "warning") return "text-amber-600";
  return "text-emerald-600";
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, loading, logout } = useAuth();

  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [benchmarks, setBenchmarks] = useState<Benchmark[]>([]);
  const [report, setReport] = useState<RecommendationReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    model_name: "",
    runtime: "onnxruntime",
    quantization: "",
    latency_ms: "",
    generated_tokens: "",
    memory_mb: "",
    cpu_percent: "",
  });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  const refreshBenchmarks = useCallback(async () => {
    try {
      setBenchmarks(await api.listBenchmarks());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load benchmarks");
    }
  }, []);

  useEffect(() => {
    if (!user) return;
    void refreshBenchmarks();
  }, [user, refreshBenchmarks]);

  useEffect(() => {
    if (!user) return;
    let active = true;
    const poll = async () => {
      try {
        const m = await api.metrics();
        if (active) setMetrics(m);
      } catch {
        /* transient; ignore */
      }
    };
    void poll();
    const id = setInterval(poll, 3000);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, [user]);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    setError(null);
    try {
      await api.createBenchmark({
        model_name: form.model_name,
        runtime: form.runtime,
        quantization: form.quantization || null,
        latency_ms: form.latency_ms ? Number(form.latency_ms) : null,
        generated_tokens: form.generated_tokens ? Number(form.generated_tokens) : 0,
        memory_mb: form.memory_mb ? Number(form.memory_mb) : null,
        cpu_percent: form.cpu_percent ? Number(form.cpu_percent) : null,
      });
      setForm({ ...form, model_name: "", quantization: "", latency_ms: "", generated_tokens: "", memory_mb: "", cpu_percent: "" });
      await refreshBenchmarks();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create benchmark");
    } finally {
      setCreating(false);
    }
  }

  async function onDelete(id: number) {
    await api.deleteBenchmark(id);
    if (report?.benchmark_id === id) setReport(null);
    await refreshBenchmarks();
  }

  async function onAnalyze(id: number) {
    setReport(await api.getRecommendations(id));
  }

  if (loading || !user) {
    return (
      <div className="flex flex-1 items-center justify-center text-zinc-500">
        Loading…
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-5xl flex-1 px-6 py-8">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">
            Dashboard
          </h1>
          <p className="text-sm text-zinc-500">{user.email}</p>
        </div>
        <button
          onClick={logout}
          className="rounded-lg border border-zinc-300 px-4 py-2 text-sm hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900"
        >
          Sign out
        </button>
      </header>

      {error && (
        <p className="mb-6 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-400">
          {error}
        </p>
      )}

      <section className="mb-8">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-zinc-500">
          Live system metrics
        </h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <MetricCard label="CPU" value={metrics ? `${metrics.cpu_percent.toFixed(0)}%` : "—"} />
          <MetricCard label="Memory" value={metrics ? `${metrics.memory_percent.toFixed(0)}%` : "—"} />
          <MetricCard label="Cores" value={metrics ? String(metrics.cpu_count) : "—"} />
          <MetricCard label="Arch" value={metrics ? metrics.architecture : "—"} />
        </div>
      </section>

      <section className="mb-8 rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
        <h2 className="mb-4 text-lg font-semibold">Record a benchmark</h2>
        <form onSubmit={onCreate} className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <input
            required
            placeholder="Model name"
            value={form.model_name}
            onChange={(e) => setForm({ ...form, model_name: e.target.value })}
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
          />
          <select
            value={form.runtime}
            onChange={(e) => setForm({ ...form, runtime: e.target.value })}
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
          >
            {RUNTIMES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
          <input
            placeholder="Quantization (e.g. Q4_0)"
            value={form.quantization}
            onChange={(e) => setForm({ ...form, quantization: e.target.value })}
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
          />
          <input
            type="number"
            placeholder="Latency (ms)"
            value={form.latency_ms}
            onChange={(e) => setForm({ ...form, latency_ms: e.target.value })}
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
          />
          <input
            type="number"
            placeholder="Generated tokens"
            value={form.generated_tokens}
            onChange={(e) => setForm({ ...form, generated_tokens: e.target.value })}
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
          />
          <input
            type="number"
            placeholder="Memory (MB)"
            value={form.memory_mb}
            onChange={(e) => setForm({ ...form, memory_mb: e.target.value })}
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
          />
          <button
            type="submit"
            disabled={creating}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-60 sm:col-span-3"
          >
            {creating ? "Saving…" : "Add benchmark"}
          </button>
        </form>
      </section>

      <section className="mb-8">
        <h2 className="mb-3 text-lg font-semibold">Benchmark runs</h2>
        {benchmarks.length === 0 ? (
          <p className="text-sm text-zinc-500">No benchmarks yet.</p>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-zinc-200 dark:border-zinc-800">
            <table className="w-full text-sm">
              <thead className="bg-zinc-50 text-left text-zinc-500 dark:bg-zinc-900">
                <tr>
                  <th className="px-4 py-2">Model</th>
                  <th className="px-4 py-2">Runtime</th>
                  <th className="px-4 py-2">Quant</th>
                  <th className="px-4 py-2">Latency</th>
                  <th className="px-4 py-2">Tokens/s</th>
                  <th className="px-4 py-2"></th>
                </tr>
              </thead>
              <tbody>
                {benchmarks.map((b) => (
                  <tr key={b.id} className="border-t border-zinc-100 dark:border-zinc-800">
                    <td className="px-4 py-2 font-medium">{b.model_name}</td>
                    <td className="px-4 py-2">{b.runtime}</td>
                    <td className="px-4 py-2">{b.quantization ?? "—"}</td>
                    <td className="px-4 py-2">{b.latency_ms ?? "—"}</td>
                    <td className="px-4 py-2">{b.throughput_tps ?? "—"}</td>
                    <td className="px-4 py-2 text-right">
                      <button
                        onClick={() => onAnalyze(b.id)}
                        className="mr-3 text-emerald-600 hover:underline"
                      >
                        Analyze
                      </button>
                      <button
                        onClick={() => onDelete(b.id)}
                        className="text-red-600 hover:underline"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {report && (
        <section className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              Recommendations · {report.model_name}
            </h2>
            <span className="rounded-full bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-700 dark:bg-emerald-950/40">
              Score {report.score}
            </span>
          </div>
          <ul className="space-y-4">
            {report.recommendations.map((r, i) => (
              <li key={i} className="border-l-2 border-zinc-200 pl-4 dark:border-zinc-700">
                <p className={`text-sm font-semibold ${severityColor(r.severity)}`}>
                  {r.title}
                </p>
                <p className="text-sm text-zinc-600 dark:text-zinc-400">{r.detail}</p>
                <p className="mt-1 text-sm text-zinc-800 dark:text-zinc-200">
                  → {r.suggested_action}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
      <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
        {label}
      </p>
      <p className="mt-1 text-2xl font-bold text-zinc-900 dark:text-zinc-50">
        {value}
      </p>
    </div>
  );
}
