import type { Metadata } from "next";
import Navbar from "@/components/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentTrust | Multilingual AI Reliability Evaluator",
  description: "Evidence-backed reliability reports for AI agents across correctness, grounding, citations, translation, and trajectory.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <div>
              <strong>AgentTrust</strong> — Evidence-backed diagnostics for AI agents.
            </div>
            <div>
              Measures selected reliability properties under defined evaluation methodologies.
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
