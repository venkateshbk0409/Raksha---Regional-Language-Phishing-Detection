import React, { useState } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  ArrowRight,
  RotateCcw,
  CheckCircle,
  Copy,
  Check,
  Globe,
  Info,
  Activity,
  Layers,
} from "lucide-react";
import { IndicatorBadge } from "./IndicatorBadge";

export function ResultCard({ result, onReset }) {
  const [copied, setCopied] = useState(false);

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
    verdictSub: "No high-risk social-engineering or malicious link threats detected.",
    zoneText: "Safe Zone (< 0.40)",
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
      verdictSub: "Potential threat signals or lexical anomalies detected. Proceed with caution.",
      zoneText: "Suspicious Zone (0.40 - 0.74)",
    };
  } else if (classification === "Phishing") {
    theme = {
      badgeBg: "bg-rose-500/10 text-rose-400 border-rose-500/30",
      border: "border-rose-500/40",
      cardGlow: "shadow-rose-500/10",
      barColor: "bg-rose-500",
      iconBg: "bg-rose-500/20 text-rose-400",
      Icon: ShieldAlert,
      label: "Phishing Threat Detected",
      verdictSub: "High-confidence social engineering, urgency, or malicious URL threat detected.",
      zoneText: "High-Risk Phishing Zone (≥ 0.75)",
    };
  }

  const { Icon } = theme;
  const scorePercent = Math.min(100, Math.max(0, Math.round(risk_score * 100)));

  // Format language display name
  const langLabelMap = {
    kannada: "Native Kannada (ಕನ್ನಡ)",
    english: "Standard English",
    "code-mixed": "Code-Mixed / Kanglish",
    unknown: "Unrecognized / Symbolic",
  };
  const langDisplay = langLabelMap[language_detected] || language_detected;

  const handleCopyAction = async () => {
    try {
      await navigator.clipboard.writeText(recommended_action);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard fallback
    }
  };

  return (
    <div className={`glass-card rounded-2xl p-6 sm:p-8 border ${theme.border} shadow-2xl ${theme.cardGlow} transition-all duration-300 space-y-6`}>
      {/* Top Header with Classification and Quantitative Score */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-800">
        <div className="flex items-start sm:items-center space-x-4">
          <div className={`p-4 rounded-2xl ${theme.iconBg} flex-shrink-0 shadow-lg`}>
            <Icon className="w-9 h-9" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className={`text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider border ${theme.badgeBg}`}>
                {classification}
              </span>
              <span className="text-xs px-2.5 py-1 rounded-full bg-slate-800/90 text-slate-300 border border-slate-700 font-mono flex items-center gap-1.5">
                <Globe className="w-3 h-3 text-cyan-400" />
                <span>{langDisplay}</span>
              </span>
            </div>
            <h3 className="text-2xl font-extrabold text-white mt-1.5">{theme.label}</h3>
            <p className="text-xs sm:text-sm text-slate-400 mt-0.5">{theme.verdictSub}</p>
          </div>
        </div>

        {/* Dynamic Risk Gauge & Score Card */}
        <div className="bg-slate-900/90 rounded-2xl p-4 sm:p-5 border border-slate-800 md:min-w-[220px] shadow-inner">
          <div className="flex items-baseline justify-between mb-2">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1">
              <Activity className="w-3.5 h-3.5 text-cyan-400" />
              Risk Index
            </span>
            <span className="text-2xl font-black font-mono text-white">
              {(risk_score).toFixed(2)}
            </span>
          </div>

          {/* Calibrated Meter */}
          <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden p-0.5">
            <div
              className={`h-full ${theme.barColor} transition-all duration-700 rounded-full`}
              style={{ width: `${scorePercent}%` }}
            />
          </div>

          <div className="flex justify-between items-center text-[10px] text-slate-400 mt-2 font-mono">
            <span>0.00 (Safe)</span>
            <span className="text-cyan-400 font-medium">{theme.zoneText}</span>
            <span>1.00</span>
          </div>
        </div>
      </div>

      {/* Recommended Action Alert Box */}
      <div className="p-5 rounded-2xl bg-slate-900/95 border border-slate-800/90 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-start space-x-3.5">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 flex-shrink-0 mt-0.5">
            <ArrowRight className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                Actionable Guidance
              </h4>
            </div>
            <p className="text-sm font-semibold text-slate-100 mt-1 leading-relaxed">
              {recommended_action}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleCopyAction}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-white border border-slate-700 text-xs font-medium transition-all active:scale-95 flex-shrink-0"
          title="Copy recommended action"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy Advice</span>
            </>
          )}
        </button>
      </div>

      {/* Threat Signals & Explainability Breakdown */}
      <div className="space-y-3 pt-1">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-cyan-400" />
            Detected Threat Signals ({indicators?.length || 0})
          </h4>
          <span className="text-[11px] text-slate-500 italic">
            Click any badge for signal explanation
          </span>
        </div>

        {indicators && indicators.length > 0 ? (
          <div className="flex flex-wrap gap-2.5 pt-1">
            {indicators.map((ind, idx) => (
              <IndicatorBadge
                key={idx}
                indicator={ind}
                classification={classification}
              />
            ))}
          </div>
        ) : (
          <div className="flex items-center space-x-3 text-xs text-slate-400 bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
            <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>No malicious lexical patterns, urgent social-engineering tactics, or phishing links were detected.</span>
          </div>
        )}
      </div>

      {/* Scan Another Message & Reset */}
      <div className="pt-4 border-t border-slate-800/90 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
        <span className="flex items-center gap-1">
          <Info className="w-3.5 h-3.5 text-cyan-400" />
          <span>Anonymous metadata (excluding message content) is logged for system improvement.</span>
        </span>
        <button
          onClick={onReset}
          className="w-full sm:w-auto flex items-center justify-center space-x-2 font-medium text-slate-200 hover:text-white px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-750 border border-slate-700 transition-all active:scale-95 shadow-md"
        >
          <RotateCcw className="w-4 h-4 text-cyan-400" />
          <span>Scan Another Message</span>
        </button>
      </div>
    </div>
  );
}
