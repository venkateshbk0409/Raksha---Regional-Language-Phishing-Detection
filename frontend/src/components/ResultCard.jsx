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

  // Semantic color theming based on warm design system
  let theme = {
    badgeBg: "bg-[#ecf7ed] text-[#14532d] border-[#c3e6cb]",
    border: "border-[#c3e6cb]",
    barColor: "bg-[#16a34a]",
    iconBg: "bg-[#dcfce7] text-[#15803d]",
    Icon: ShieldCheck,
    label: "Safe Content",
    verdictSub: "No high-risk social-engineering or malicious link threats detected.",
    zoneText: "Safe Zone (< 0.40)",
    actionBg: "bg-[#f4fbf5] border-[#c3e6cb]",
    actionTitleColor: "text-[#15803d]",
  };

  if (classification === "Suspicious") {
    theme = {
      badgeBg: "bg-[#fef6e7] text-[#783e08] border-[#fde1ab]",
      border: "border-[#fde1ab]",
      barColor: "bg-[#d97706]",
      iconBg: "bg-[#fef3c7] text-[#b45309]",
      Icon: AlertTriangle,
      label: "Suspicious Content",
      verdictSub: "Potential threat signals or lexical anomalies detected. Proceed with caution.",
      zoneText: "Suspicious Zone (0.40 - 0.74)",
      actionBg: "bg-[#fffbf2] border-[#fde1ab]",
      actionTitleColor: "text-[#b45309]",
    };
  } else if (classification === "Phishing") {
    theme = {
      badgeBg: "bg-[#fdf0ee] text-[#881c1c] border-[#f9c6c0]",
      border: "border-[#f9c6c0]",
      barColor: "bg-[#dc2626]",
      iconBg: "bg-[#fee2e2] text-[#b91c1c]",
      Icon: ShieldAlert,
      label: "Phishing Threat Detected",
      verdictSub: "High-confidence social engineering, urgency, or malicious URL threat detected.",
      zoneText: "High-Risk Phishing Zone (≥ 0.75)",
      actionBg: "bg-[#fff7f6] border-[#f9c6c0]",
      actionTitleColor: "text-[#b91c1c]",
    };
  }

  // Detect low-evidence / short / ambiguous input for calm contextual guidance
  const isLowEvidence =
    classification === "Suspicious" &&
    (language_detected === "unknown" ||
      !indicators ||
      indicators.length === 0 ||
      (indicators.length === 1 &&
        (indicators[0].includes("degraded") || indicators[0].includes("linguistic"))));

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
    <div className={`surface-elevated p-6 sm:p-8 border ${theme.border} space-y-6 animate-fadeIn`}>
      {/* SECTION 1: VERDICT & RISK METER (The Focal Point) */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-[#e7e5dc]">
        <div className="flex items-start sm:items-center space-x-4">
          <div className={`p-3.5 rounded-2xl ${theme.iconBg} flex-shrink-0 shadow-xs`}>
            <Icon className="w-8 h-8" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className={`text-xs px-3 py-0.5 rounded-full font-bold uppercase tracking-wider border ${theme.badgeBg}`}>
                {classification}
              </span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#f0eee6] text-stone-700 border border-[#e2dfd4] font-mono flex items-center gap-1.5">
                <Globe className="w-3 h-3 text-brand-600" />
                <span>{langDisplay}</span>
              </span>
            </div>
            <h3 className="text-2xl font-bold text-stone-900 mt-1.5">{theme.label}</h3>
            <p className="text-xs sm:text-sm text-stone-600 mt-0.5">{theme.verdictSub}</p>
          </div>
        </div>

        {/* Calibrated Risk Index Gauge */}
        <div className="bg-[#fbfaf7] rounded-2xl p-4 sm:p-5 border border-[#e2dfd4] md:min-w-[230px]">
          <div className="flex items-baseline justify-between mb-2">
            <span className="text-xs text-stone-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-brand-600" />
              Risk Index
            </span>
            <span className="text-2xl font-bold font-mono text-stone-900">
              {(risk_score).toFixed(2)}
            </span>
          </div>

          {/* Calibrated Meter */}
          <div className="w-full bg-[#e7e5dc] rounded-full h-2 overflow-hidden p-0.5">
            <div
              className={`h-full ${theme.barColor} transition-all duration-700 rounded-full`}
              style={{ width: `${scorePercent}%` }}
            />
          </div>

          <div className="flex justify-between items-center text-[10px] text-stone-500 mt-2 font-mono">
            <span>0.00 (Safe)</span>
            <span className="text-stone-700 font-semibold">{theme.zoneText}</span>
            <span>1.00</span>
          </div>
        </div>
      </div>

      {/* Calm contextual alert for low-evidence / ambiguous input */}
      {isLowEvidence && (
        <div className="p-4 rounded-xl bg-[#fef6e7] border border-[#fde1ab] flex items-start space-x-3 text-xs text-[#783e08]">
          <Info className="w-4 h-4 text-[#b45309] flex-shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-semibold">Not enough context to assess this message. </span>
            <span className="text-[#92400e]">
              Paste the complete SMS, WhatsApp message, email, or suspicious link for a more useful analysis.
            </span>
          </div>
        </div>
      )}

      {/* SECTION 2: WHAT THE USER SHOULD DO (Actionable Guidance) */}
      <div className={`p-5 rounded-2xl border ${theme.actionBg} flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4`}>
        <div className="flex items-start space-x-3.5">
          <div className="p-2 rounded-xl bg-white text-brand-600 border border-[#e2dfd4] flex-shrink-0 mt-0.5 shadow-xs">
            <ArrowRight className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-stone-600">
              Actionable Guidance
            </h4>
            <p className="text-sm font-semibold text-stone-900 mt-0.5 leading-relaxed">
              {recommended_action}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleCopyAction}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-white hover:bg-[#faf9f4] text-stone-700 hover:text-stone-900 border border-[#dedad0] text-xs font-semibold shadow-xs transition-all active:scale-95 flex-shrink-0"
          title="Copy recommended action"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              <span className="text-emerald-700">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5 text-stone-500" />
              <span>Copy Advice</span>
            </>
          )}
        </button>
      </div>

      {/* SECTION 3: WHY THIS VERDICT WAS REACHED (Detected Threat Signals) */}
      <div className="space-y-3 pt-1">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-bold uppercase tracking-wider text-stone-500 flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-brand-600" />
            Detected Threat Signals ({indicators?.length || 0})
          </h4>
          <span className="text-[11px] text-stone-400">
            Hover or tap any badge for details
          </span>
        </div>

        {indicators && indicators.length > 0 ? (
          <div className="flex flex-wrap gap-2 pt-1">
            {indicators.map((ind, idx) => (
              <IndicatorBadge
                key={idx}
                indicator={ind}
                classification={classification}
              />
            ))}
          </div>
        ) : (
          <div className="flex items-center space-x-3 text-xs text-stone-600 bg-[#fbfaf7] p-4 rounded-xl border border-[#e7e5dc]">
            <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>No malicious lexical patterns, urgent social-engineering tactics, or phishing links were detected.</span>
          </div>
        )}
      </div>

      {/* Reset & Privacy Reassurance */}
      <div className="pt-4 border-t border-[#e7e5dc] flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-stone-500">
        <span className="flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-brand-600" />
          <span>No message content is stored. Stateless privacy by default.</span>
        </span>
        <button
          onClick={onReset}
          className="w-full sm:w-auto flex items-center justify-center space-x-2 font-semibold text-stone-700 hover:text-stone-900 px-5 py-2.5 rounded-xl bg-[#f0eee6] hover:bg-[#e7e4d8] border border-[#dedad0] transition-all active:scale-95 shadow-xs"
        >
          <RotateCcw className="w-3.5 h-3.5 text-brand-600" />
          <span>Scan Another Message</span>
        </button>
      </div>
    </div>
  );
}
