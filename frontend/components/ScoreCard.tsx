import React from "react";

interface ScoreCardProps {
  label: string;
  score: number;
  passRate?: number;
  weight?: string;
  description?: string;
  icon?: React.ReactNode;
  statusBadge?: string;
}

export default function ScoreCard({
  label,
  score,
  passRate,
  weight,
  description,
  icon,
  statusBadge,
}: ScoreCardProps) {
  const percentage = Math.round(score * 100);

  const getScoreColor = (pct: number) => {
    if (pct >= 85) return "text-emerald-400";
    if (pct >= 70) return "text-amber-400";
    return "text-rose-400";
  };

  const getProgressColor = (pct: number) => {
    if (pct >= 85) return "bg-emerald-500";
    if (pct >= 70) return "bg-amber-500";
    return "bg-rose-500";
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {icon && <div className="text-slate-400">{icon}</div>}
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
        </div>
        {weight && (
          <span className="text-[11px] font-mono text-slate-500 bg-slate-800/80 px-2 py-0.5 rounded">
            Weight: {weight}
          </span>
        )}
      </div>

      <div className="mt-3 flex items-baseline justify-between">
        <div className={`text-3xl font-extrabold tracking-tight ${getScoreColor(percentage)}`}>
          {percentage}%
        </div>
        {passRate !== undefined && (
          <div className="text-xs text-slate-400">
            Pass rate: <span className="font-semibold text-slate-200">{Math.round(passRate * 100)}%</span>
          </div>
        )}
      </div>

      {/* Progress bar */}
      <div className="mt-3 w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${getProgressColor(percentage)}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>

      {description && <p className="mt-2 text-xs text-slate-400 leading-relaxed">{description}</p>}
    </div>
  );
}
