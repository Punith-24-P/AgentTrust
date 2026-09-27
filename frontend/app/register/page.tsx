"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { registerUser } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Simple password strength calculation
  const getPasswordStrength = (pass: string) => {
    let score = 0;
    if (pass.length >= 8) score += 1;
    if (/[A-Z]/.test(pass)) score += 1;
    if (/[0-9]/.test(pass)) score += 1;
    if (/[^A-Za-z0-9]/.test(pass)) score += 1;
    return score;
  };

  const strength = getPasswordStrength(password);
  const strengthLabels = ["Weak", "Fair", "Good", "Strong"];
  const strengthColors = ["bg-red-500", "bg-amber-500", "bg-sky-500", "bg-emerald-500"];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }
    if (!agreed) {
      setError("Please accept the terms of service to continue");
      return;
    }

    setLoading(true);
    try {
      await registerUser({
        name,
        email,
        password,
        confirm_password: confirmPassword,
      });
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to create account. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-[#0b0f19] text-slate-100">
      {/* Left side: Hero & Identity */}
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

        <div className="max-w-md my-auto space-y-6">
          <h1 className="text-3xl font-bold tracking-tight text-white leading-tight">
            Deploy AI agents with measurable, reproducible confidence.
          </h1>
          <p className="text-slate-400 text-sm leading-relaxed">
            Register your team workspace to run objective evaluations across factual claims, statutory evidence, cross-lingual fidelity, and observable trajectories.
          </p>
          <div className="space-y-3 pt-2">
            <div className="flex items-center gap-3 text-xs text-slate-300">
              <span className="text-emerald-400">✓</span> Evidence-backed fact grounding & citation verification
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-300">
              <span className="text-emerald-400">✓</span> High-assurance multilingual translation drift diagnostics
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-300">
              <span className="text-emerald-400">✓</span> Automated regression detection on subsequent agent versions
            </div>
          </div>
        </div>

        <div className="text-xs text-slate-500">
          AgentTrust Platform v1.0 • Multi-tenant Workspace Architecture
        </div>
      </div>

      {/* Right side: Registration Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md space-y-8">
          <div>
            <div className="lg:hidden flex items-center gap-2 mb-6">
              <div className="w-7 h-7 rounded-md bg-sky-500/20 border border-sky-500/40 flex items-center justify-center font-bold text-sky-400 text-sm">
                AT
              </div>
              <span className="font-bold text-lg text-white">AgentTrust</span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-white">Create an account</h2>
            <p className="text-sm text-slate-400 mt-1">
              Start evaluating your AI agents with evidence-backed diagnostics.
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
                Full Name
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Alex Mercer"
                className="w-full px-3.5 py-2.5 rounded-lg bg-[#111827] border border-[#1e293b] text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-sm transition"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-1.5">
                Work Email
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
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 8 characters"
                className="w-full px-3.5 py-2.5 rounded-lg bg-[#111827] border border-[#1e293b] text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-sm transition"
              />
              {password && (
                <div className="mt-2 space-y-1">
                  <div className="flex gap-1 h-1.5 w-full">
                    {[1, 2, 3, 4].map((step) => (
                      <div
                        key={step}
                        className={`h-full flex-1 rounded-sm transition ${
                          strength >= step ? strengthColors[strength - 1] : "bg-slate-800"
                        }`}
                      />
                    ))}
                  </div>
                  <div className="text-[11px] text-slate-400 text-right">
                    Strength: {strengthLabels[Math.max(0, strength - 1)]}
                  </div>
                </div>
              )}
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-1.5">
                Confirm Password
              </label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter password"
                className="w-full px-3.5 py-2.5 rounded-lg bg-[#111827] border border-[#1e293b] text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-sm transition"
              />
            </div>

            <div className="flex items-start pt-1">
              <input
                id="terms"
                type="checkbox"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
                className="w-4 h-4 mt-0.5 rounded border-[#1e293b] bg-[#111827] text-sky-500 focus:ring-sky-500 focus:ring-offset-0"
              />
              <label htmlFor="terms" className="ml-2 text-xs text-slate-400 leading-normal">
                I agree to the terms of evaluation and acknowledge that metrics represent empirical evaluation results rather than absolute trustworthiness.
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
                "Create Account & Workspace"
              )}
            </button>
          </form>

          <div className="pt-4 border-t border-[#1e293b] text-center text-xs text-slate-400">
            Already have an account?{" "}
            <Link href="/login" className="text-sky-400 hover:text-sky-300 font-medium">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
