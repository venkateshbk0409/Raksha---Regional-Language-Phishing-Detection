import React from "react";
import { AlertTriangle, AlertCircle, ShieldAlert, CheckCircle2 } from "lucide-react";

export function IndicatorBadge({ indicator, classification }) {
  let badgeStyle = "bg-amber-950/40 text-amber-300 border-amber-800/60";
  let Icon = AlertTriangle;

  if (classification === "Phishing") {
    badgeStyle = "bg-rose-950/40 text-rose-300 border-rose-800/60";
    Icon = ShieldAlert;
  } else if (classification === "Safe") {
    badgeStyle = "bg-emerald-950/40 text-emerald-300 border-emerald-800/60";
    Icon = CheckCircle2;
  }

  return (
    <span className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium border ${badgeStyle}`}>
      <Icon className="w-3.5 h-3.5 flex-shrink-0" />
      <span>{indicator}</span>
    </span>
  );
}
