"use client";

import Link from "next/link";
import { useAuth } from "../lib/auth";

export default function Home() {
  const { user, loading } = useAuth();

  return (
    <div className="flex flex-1 items-center justify-center bg-zinc-50 px-6 dark:bg-black">
      <main className="w-full max-w-2xl text-center">
        <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-600">
          Arm64-first
        </p>
        <h1 className="text-4xl font-bold tracking-tight text-zinc-900 sm:text-5xl dark:text-zinc-50">
          ArmPilot-AI
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-zinc-600 dark:text-zinc-400">
          Deploy, benchmark, and auto-tune open-source LLMs on Arm with
          intelligent performance recommendations.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          {loading ? (
            <span className="text-zinc-500">Loading…</span>
          ) : user ? (
            <Link
              href="/dashboard"
              className="rounded-full bg-emerald-600 px-6 py-3 font-medium text-white transition-colors hover:bg-emerald-700"
            >
              Go to dashboard
            </Link>
          ) : (
            <Link
              href="/login"
              className="rounded-full bg-emerald-600 px-6 py-3 font-medium text-white transition-colors hover:bg-emerald-700"
            >
              Sign in
            </Link>
          )}
        </div>
      </main>
    </div>
  );
}
