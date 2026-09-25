"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, Play, Layers, GitCompare, Database, Bot, FileText } from "lucide-react";
import { useState } from "react";
import { triggerOneClickDemo } from "@/lib/api";

export default function Navbar() {
  const pathname = usePathname();
  const [isRunningDemo, setIsRunningDemo] = useState(false);

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

  const navLinks = [
    { name: "Overview", href: "/", icon: ShieldCheck },
    { name: "Evaluation Runs", href: "/runs", icon: Layers },
    { name: "Before/After Compare", href: "/compare", icon: GitCompare },
    { name: "Datasets", href: "/datasets", icon: Database },
    { name: "Agents", href: "/agents", icon: Bot },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-9 h-9 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400 group-hover:border-sky-400 transition-colors">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="font-bold text-base tracking-tight text-white flex items-center space-x-2">
                <span>AgentTrust</span>
                <span className="text-[10px] uppercase font-semibold bg-sky-500/20 text-sky-400 border border-sky-500/30 px-1.5 py-0.5 rounded">
                  MVP
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">AI Reliability Evaluator</p>
            </div>
          </Link>

          <nav className="hidden md:flex space-x-1">
            {navLinks.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition-colors ${
                    isActive
                      ? "bg-slate-800 text-sky-400"
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
          <button
            onClick={handleQuickDemo}
            disabled={isRunningDemo}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 transition-colors shadow-sm disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 fill-current ${isRunningDemo ? "animate-spin" : ""}`} />
            <span>{isRunningDemo ? "Executing Demo..." : "Run Demo"}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
