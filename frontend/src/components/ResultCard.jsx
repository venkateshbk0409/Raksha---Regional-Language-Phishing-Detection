import React from "react";
import { ShieldCheck, ShieldAlert, AlertTriangle, ArrowRight, RotateCcw, CheckCircle } from "lucide-react";
import { IndicatorBadge } from "./IndicatorBadge";

export function ResultCard({ result, onReset }) {
  if (!result) return null;

  const { classification, risk_score, language_detected, indicators, recommended_action } = result;

  // Semantic color theming based on design-system.md
  let theme = {
    badgeBg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    border: "border-emerald-500/40",
    cardGlow: "shadow-emerald-500/10",
    barColor: "bg-emerald-500",
    iconBg: "bg-emerald-500/20 text-emerald-400",
    Icon: ShieldCheck,
    label: "Safe Content",
    description: "No significant phishing or malicious indicators detected.",
  };

  if (classification === "Suspicious") {
    theme = {
      badgeBg: "bg-amber-500/10 text-amber-400 border-amber-500/30",
      border: "border-amber-500/40",
      cardGlow: "shadow-amber-500/10",
      barColor: "bg-amber-500",
      iconBg: "bg-amber-500/20 text-amber-400",
      Icon: AlertTriangle,
      label: "Suspicious Content",
      description: "Potential risk patterns or anomalies detected. Proceed with caution.",
    };
  } else if (classification === "Phishing") {
    theme = {
      badgeBg: "bg-rose-500/10 text-rose-400 border-rose-500/30",
      border: "border-rose-500/40",
      cardGlow: "shadow-rose-500/10",
      barColor: "bg-rose-500",
      iconBg: "bg-rose-500/20 text-rose-400",
      Icon: ShieldAlert,
      label: "Phishing Detected",
      description: "High confidence social-engineering or malicious link threat detected.",
    };
  }

  const { Icon } = theme;
  const scorePercent = Math.min(100, Math.max(0, Math.round(risk_score * 100)));

  return (
    <div className={`glass-card rounded-2xl p-6 sm:p-8 border ${theme.border} shadow-2xl ${theme.cardGlow} transition-all duration-300`}>
      {/* Header with Classification and Score */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div className="flex items-center space-x-4">
          <div className={`p-3.5 rounded-2xl ${theme.iconBg} flex-shrink-0`}>
            <Icon className="w-8 h-8" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold uppercase tracking-wider border ${theme.badgeBg}`}>
                {classification}
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                Lang: {language_detected}
              </span>
            </div>
            <h3 className="text-xl font-bold text-white mt-1">{theme.label}</h3>
            <p className="text-xs text-slate-400 mt-0.5">{theme.description}</p>
          </div>
        </div>

        {/* Risk Score Meter */}
        <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-800 sm:min-w-[180px]">
          <div className="flex items-baseline justify-between mb-1.5">
            <span className="text-xs text-slate-400 font-medium">Risk Score</span>
            <span className="text-lg font-bold font-mono text-white">{(risk_score).toFixed(2)}</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full ${theme.barColor} transition-all duration-500 rounded-full`}
              style={{ width: `${scorePercent}%` }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
            <span>0.0 (Safe)</span>
            <span>1.0 (Phishing)</span>
          </div>
        </div>
      </div>

      {/* Recommended Action Callout */}
      <div className="my-6 p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start space-x-3.5">
        <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 mt-0.5 flex-shrink-0">
          <ArrowRight className="w-4 h-4" />
        </div>
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
            Recommended Action
          </h4>
          <p className="text-sm font-medium text-slate-200 mt-1">
            {recommended_action}
          </p>
        </div>
      </div>

      {/* Indicators Breakdown */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Detected Threat Signals ({indicators?.length || 0})
          </h4>
        </div>
        {indicators && indicators.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {indicators.map((ind, idx) => (
              <IndicatorBadge
                key={idx}
                indicator={ind}
                classification={classification}
              />
            ))}
          </div>
        ) : (
          <div className="flex items-center space-x-2 text-xs text-slate-400 bg-slate-900/50 p-3 rounded-lg border border-slate-800/80">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>No malicious lexical patterns or high-risk keywords found.</span>
          </div>
        )}
      </div>

      {/* Scan Another Button */}
      <div className="mt-8 pt-4 border-t border-slate-800 flex justify-end">
        <button
          onClick={onReset}
          className="flex items-center space-x-2 text-xs font-medium text-slate-300 hover:text-white px-4 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-800 border border-slate-700 transition-all active:scale-95"
        >
          <RotateCcw className="w-3.5 h-3.5 text-cyan-400" />
          <span>Scan Another Message</span>
        </button>
      </div>
    </div>
  );
}
