"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  ShieldCheck,
  Play,
  Layers,
  GitCompare,
  Database,
  Bot,
  Settings as SettingsIcon,
  LogOut,
  User as UserIcon,
} from "lucide-react";
import { triggerOneClickDemo, getCurrentUser, logoutUser } from "@/lib/api";
import { User } from "@/types";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isRunningDemo, setIsRunningDemo] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    getCurrentUser().then((u) => {
      if (u) setCurrentUser(u);
    });
  }, [pathname]);

  const handleQuickDemo = async () => {
    try {
      setIsRunningDemo(true);
      const res = await triggerOneClickDemo();
      window.location.href = `/runs/${res.baseline_run_id}`;
    } catch (err: any) {
      alert("Failed to start demo: " + err.message);
      setIsRunningDemo(false);
    }
  };

  const handleLogout = async () => {
    await logoutUser();
    setCurrentUser(null);
    router.push("/login");
  };

  const navLinks = [
    { name: "Overview", href: "/", icon: ShieldCheck },
    { name: "Evaluation Runs", href: "/runs", icon: Layers },
    { name: "Datasets", href: "/datasets", icon: Database },
    { name: "Agents", href: "/agents", icon: Bot },
    { name: "Comparisons", href: "/compare", icon: GitCompare },
    { name: "Settings", href: "/settings", icon: SettingsIcon },
  ];

  // Don't render full navbar on auth pages
  if (pathname === "/login" || pathname === "/register" || pathname === "/forgot-password") {
    return null;
  }

  return (
    <header className="border-b border-[#1e293b] bg-[#0b0f19]/90 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400 group-hover:border-sky-400 transition-colors">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <div className="font-bold text-sm tracking-tight text-white flex items-center space-x-2">
                <span>AgentTrust</span>
                <span className="text-[10px] uppercase font-semibold bg-sky-500/15 text-sky-400 border border-sky-500/30 px-1.5 py-0.2 rounded">
                  v1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Multilingual AI Reliability Evaluator
              </p>
            </div>
          </Link>

          <nav className="hidden md:flex space-x-1">
            {navLinks.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-colors ${
                    isActive
                      ? "bg-slate-800/90 text-sky-400 border border-slate-700/60"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center space-x-3">
          {/* Explicitly Labeled Demo Trigger */}
          <button
            onClick={handleQuickDemo}
            disabled={isRunningDemo}
            title="Runs showcase baseline & optimized evaluation with controlled seed data"
            className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border border-amber-500/40 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 transition-colors disabled:opacity-50"
          >
            <Play className={`w-3 h-3 fill-current ${isRunningDemo ? "animate-spin" : ""}`} />
            <span>{isRunningDemo ? "Simulating..." : "DEMO / SIMULATION"}</span>
          </button>

          {/* User Account Menu */}
          {currentUser ? (
            <div className="relative">
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="flex items-center space-x-2 px-2.5 py-1.5 rounded-lg bg-slate-900 border border-[#1e293b] hover:border-slate-700 text-xs text-slate-300 transition"
              >
                <div className="w-5 h-5 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold text-[10px]">
                  {currentUser.name.charAt(0).toUpperCase()}
                </div>
                <span className="hidden sm:inline max-w-[120px] truncate">{currentUser.name}</span>
              </button>

              {menuOpen && (
                <div className="absolute right-0 mt-2 w-52 bg-[#111827] border border-[#1e293b] rounded-xl shadow-2xl py-1 text-xs text-slate-300 z-50 animate-in fade-in">
                  <div className="px-3 py-2 border-b border-[#1e293b]">
                    <div className="font-semibold text-white">{currentUser.name}</div>
                    <div className="text-[11px] text-slate-400 truncate">{currentUser.email}</div>
                  </div>
                  <Link
                    href="/settings"
                    onClick={() => setMenuOpen(false)}
                    className="flex items-center space-x-2 px-3 py-2 hover:bg-slate-800/80 transition"
                  >
                    <SettingsIcon className="w-3.5 h-3.5 text-slate-400" />
                    <span>Workspace Settings</span>
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left flex items-center space-x-2 px-3 py-2 hover:bg-red-950/40 text-red-400 transition"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Link
                href="/login"
                className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 transition"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
