"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { loginUser } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await loginUser({ email, password, remember });
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to sign in. Please verify your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-[#0b0f19] text-slate-100">
      {/* Left side: Brand, Proposition & Architecture Flow */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12 bg-gradient-to-b from-[#0f172a] to-[#0b0f19] border-r border-[#1e293b]">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-sky-500/20 border border-sky-500/40 flex items-center justify-center font-bold text-sky-400">
              AT
            </div>
            <span className="font-bold text-xl tracking-tight text-white">AgentTrust</span>
          </div>
          <p className="text-xs text-sky-400 font-medium uppercase tracking-wider mt-1">
            Multilingual AI Reliability Evaluator
          </p>
        </div>

        <div className="max-w-md my-auto space-y-8">
          <div className="space-y-3">
            <h1 className="text-3xl font-bold tracking-tight text-white leading-tight">
              Evidence-backed reliability diagnostics for AI agents.
            </h1>
            <p className="text-slate-400 text-sm leading-relaxed">
              Evaluate correctness, grounding, citation validity, multilingual fidelity, and observable tool behavior with reproducible test runs.
            </p>
          </div>

          {/* Workflow Diagram */}
          <div className="bg-[#111827]/80 border border-[#1e293b] rounded-xl p-5 space-y-4">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Diagnostic Execution Pipeline
            </div>
            <div className="flex items-center justify-between text-xs text-slate-300">
              <div className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 font-mono text-center">
                Agent
              </div>
              <span className="text-slate-500 text-sm">→</span>
              <div className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 font-mono text-center">
                Evidence
              </div>
              <span className="text-slate-500 text-sm">→</span>
              <div className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 font-mono text-center">
                Evaluation
              </div>
              <span className="text-slate-500 text-sm">→</span>
              <div className="px-3 py-2 rounded-lg bg-sky-950/60 border border-sky-800/60 text-sky-300 font-mono font-semibold text-center">
                Reliability
              </div>
            </div>
          </div>
        </div>

        <div className="text-xs text-slate-500">
          AgentTrust Platform v1.0 • Honest Measurement & Diagnostics
        </div>
      </div>

      {/* Right side: Login Card */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md space-y-8">
          <div>
            <div className="lg:hidden flex items-center gap-2 mb-6">
              <div className="w-7 h-7 rounded-md bg-sky-500/20 border border-sky-500/40 flex items-center justify-center font-bold text-sky-400 text-sm">
                AT
              </div>
              <span className="font-bold text-lg text-white">AgentTrust</span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-white">Sign in to your workspace</h2>
            <p className="text-sm text-slate-400 mt-1">
              Enter your credentials to access your agents and benchmark runs.
            </p>
          </div>

          {error && (
            <div className="p-3.5 rounded-lg bg-red-950/40 border border-red-800/50 text-red-300 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                className="w-full px-3.5 py-2.5 rounded-lg bg-[#111827] border border-[#1e293b] text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-sm transition"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider">
                  Password
                </label>
                <Link
                  href="/forgot-password"
                  className="text-xs text-sky-400 hover:text-sky-300 transition"
                >
                  Forgot password?
                </Link>
              </div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-3.5 py-2.5 rounded-lg bg-[#111827] border border-[#1e293b] text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-sm transition"
              />
            </div>

            <div className="flex items-center">
              <input
                id="remember"
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="w-4 h-4 rounded border-[#1e293b] bg-[#111827] text-sky-500 focus:ring-sky-500 focus:ring-offset-0"
              />
              <label htmlFor="remember" className="ml-2 text-xs text-slate-400">
                Remember session for 30 days
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-sm transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <span className="inline-block w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
              ) : (
                "Sign In"
              )}
            </button>
          </form>

          <div className="pt-4 border-t border-[#1e293b] text-center text-xs text-slate-400">
            Don't have an account?{" "}
            <Link href="/register" className="text-sky-400 hover:text-sky-300 font-medium">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
