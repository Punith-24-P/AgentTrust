"use client";

import React, { useState, useEffect } from "react";
import { fetchProviderSettings, updateProviderSettings, getCurrentUser } from "@/lib/api";
import { User } from "@/types";
import { Settings as SettingsIcon, Key, Sliders, Globe, Shield, CheckCircle } from "lucide-react";

export default function SettingsPage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [llmProvider, setLlmProvider] = useState("mock");
  const [llmModel, setLlmModel] = useState("gpt-4o-mini");
  const [llmBaseUrl, setLlmBaseUrl] = useState("https://api.openai.com/v1");
  const [llmApiKey, setLlmApiKey] = useState("");
  const [apiKeyConfigured, setApiKeyConfigured] = useState(false);
  const [translationProvider, setTranslationProvider] = useState("mock");

  useEffect(() => {
    async function loadData() {
      try {
        const [u, s] = await Promise.all([getCurrentUser(), fetchProviderSettings()]);
        if (u) setCurrentUser(u);
        if (s) {
          setLlmProvider(s.llm_provider || "mock");
          setLlmModel(s.llm_model || "gpt-4o-mini");
          setLlmBaseUrl(s.llm_base_url || "https://api.openai.com/v1");
          setApiKeyConfigured(Boolean(s.llm_api_key_configured));
          setTranslationProvider(s.translation_provider || "mock");
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMessage(null);
    try {
      const updateData: any = {
        llm_provider: llmProvider,
        llm_model: llmModel,
        llm_base_url: llmBaseUrl,
        translation_provider: translationProvider,
      };
      if (llmApiKey.trim()) {
        updateData.llm_api_key = llmApiKey.trim();
      }
      const res = await updateProviderSettings(updateData);
      setApiKeyConfigured(res.llm_api_key_configured);
      setLlmApiKey("");
      setSuccessMessage("Settings successfully updated.");
    } catch (err: any) {
      alert("Failed to update settings: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-slate-400">
        Loading settings...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-sky-400" />
          Settings & Provider Configuration
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Manage your AI evaluation providers, API credentials, and multilingual parameters safely.
        </p>
      </div>

      {successMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-800/40 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-400" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Account Info */}
      <div className="bg-[#111827] border border-[#1e293b] rounded-xl p-6 space-y-4">
        <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
          <Shield className="w-4 h-4 text-sky-400" />
          Workspace & Identity
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-slate-400 block mb-1">User</span>
            <span className="text-white font-medium">{currentUser?.name || "Local Administrator"}</span>
          </div>
          <div>
            <span className="text-slate-400 block mb-1">Email</span>
            <span className="text-white font-mono">{currentUser?.email || "admin@agenttrust.local"}</span>
          </div>
        </div>
      </div>

      {/* Provider Settings */}
      <form onSubmit={handleSave} className="bg-[#111827] border border-[#1e293b] rounded-xl p-6 space-y-6">
        <div>
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <Key className="w-4 h-4 text-sky-400" />
            LLM Evaluation Provider
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            AgentTrust uses hybrid evaluation: strict deterministic rules for facts/dates/numbers and structured LLM judge for semantic alignment.
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              LLM Provider Architecture
            </label>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-lg bg-[#0b0f19] border border-[#1e293b] text-slate-100 text-xs focus:border-sky-500 focus:outline-none"
            >
              <option value="mock">Local Deterministic Evaluator (Zero-API Dependency / Fast)</option>
              <option value="openai">OpenAI (Direct API)</option>
              <option value="openai_compatible">OpenAI-Compatible (Self-hosted vLLM / Ollama / LocalAI)</option>
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Evaluation Model Name
              </label>
              <input
                type="text"
                value={llmModel}
                onChange={(e) => setLlmModel(e.target.value)}
                placeholder="gpt-4o-mini"
                className="w-full px-3.5 py-2.5 rounded-lg bg-[#0b0f19] border border-[#1e293b] text-slate-100 text-xs focus:border-sky-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Base URL
              </label>
              <input
                type="text"
                value={llmBaseUrl}
                onChange={(e) => setLlmBaseUrl(e.target.value)}
                placeholder="https://api.openai.com/v1"
                className="w-full px-3.5 py-2.5 rounded-lg bg-[#0b0f19] border border-[#1e293b] text-slate-100 text-xs focus:border-sky-500 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="block text-xs font-medium text-slate-300">
                Provider API Key
              </label>
              <span
                className={`text-[11px] px-2 py-0.5 rounded font-mono ${
                  apiKeyConfigured
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                    : "bg-slate-800 text-slate-400"
                }`}
              >
                {apiKeyConfigured ? "Configured on Backend" : "Not Configured"}
              </span>
            </div>
            <input
              type="password"
              value={llmApiKey}
              onChange={(e) => setLlmApiKey(e.target.value)}
              placeholder={apiKeyConfigured ? "•••••••••••••••••••••••• (Leave blank to keep existing)" : "Enter API key"}
              className="w-full px-3.5 py-2.5 rounded-lg bg-[#0b0f19] border border-[#1e293b] text-slate-100 text-xs focus:border-sky-500 focus:outline-none"
            />
            <p className="text-[11px] text-slate-500 mt-1">
              Secret keys are stored securely on the backend and are never transmitted to browser responses.
            </p>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Cross-Lingual Translation Service
            </label>
            <select
              value={translationProvider}
              onChange={(e) => setTranslationProvider(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-lg bg-[#0b0f19] border border-[#1e293b] text-slate-100 text-xs focus:border-sky-500 focus:outline-none"
            >
              <option value="mock">Built-in Semantic Translator (Zero-Config)</option>
              <option value="llm">LLM Cross-Lingual Back-Translation</option>
            </select>
          </div>
        </div>

        <div className="pt-4 border-t border-[#1e293b] flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-xs transition shadow-sm disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Settings"}
          </button>
        </div>
      </form>
    </div>
  );
}
