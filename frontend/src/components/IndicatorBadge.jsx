import React, { useState } from "react";
import {
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  Globe,
  Link as LinkIcon,
  Server,
  AlertOctagon,
  FileWarning,
  Info,
  HelpCircle,
} from "lucide-react";

// Intelligent indicator categorization & descriptive explainability mapping
const INDICATOR_EXPLANATIONS = {
  "IP address host detected": {
    category: "url",
    description: "The link points directly to a numeric IP address rather than a registered domain name, a classic tactic to bypass domain reputation checks.",
    icon: Server,
  },
  "Suspicious TLD detected": {
    category: "url",
    description: "The domain uses a top-level domain (e.g., .xyz, .top, .tk) statistically associated with high rates of malicious phishing disposable infrastructure.",
    icon: LinkIcon,
  },
  "Excessive subdomains": {
    category: "url",
    description: "The URL has 3 or more subdomain levels, often used to create lookalike names (e.g. sbi.bank.login.phish.com) to deceive mobile users.",
    icon: LinkIcon,
  },
  "Excessive hyphens in host": {
    category: "url",
    description: "Multiple hyphens in domain names are frequently used in typosquatting and deceptive brand imitation.",
    icon: LinkIcon,
  },
  "Userinfo (@) symbol in URL": {
    category: "url",
    description: "The '@' character causes browsers to ignore preceding text as authentication info, hiding the real destination domain.",
    icon: AlertOctagon,
  },
  "Hex-encoded/obfuscated characters": {
    category: "url",
    description: "Percent-encoded characters (%20, %2e, etc.) are used to disguise malicious paths and bypass keyword filters.",
    icon: FileWarning,
  },
  "Suspicious port detected": {
    category: "url",
    description: "The URL connects over a non-standard web port (e.g. :8080, :8888, :3000), typical of rogue phishing servers.",
    icon: Server,
  },
  "Punycode/homoglyph domain detected": {
    category: "url",
    description: "Uses internationalized characters or visual lookalikes (homoglyphs) to impersonate trusted brand names.",
    icon: AlertOctagon,
  },
  "Suspicious keywords in URL path": {
    category: "url",
    description: "Contains high-risk credential-harvesting keywords like 'login', 'verify', 'update', 'banking', or 'otp' in the URL path.",
    icon: LinkIcon,
  },
  "Insecure HTTP link detected": {
    category: "url",
    description: "The link uses unencrypted HTTP instead of HTTPS, leaving any submitted sensitive information vulnerable to interception.",
    icon: LinkIcon,
  },
  "Malformed link detected": {
    category: "url",
    description: "The URL structure is syntactically invalid or intentionally broken to prevent automated parser inspection.",
    icon: FileWarning,
  },
  "Urgent call-to-action detected": {
    category: "nlp",
    description: "Uses artificial time pressure (e.g. 'immediately', 'within 2 hours', 'account will be suspended') to trigger panic and bypass critical thinking.",
    icon: AlertTriangle,
  },
  "Account suspension threat": {
    category: "nlp",
    description: "Threatens punitive action against your bank, electricity, or SIM card services to coerce rapid compliance.",
    icon: AlertOctagon,
  },
  "Financial / reward incentive": {
    category: "nlp",
    description: "Promises unverified cash prizes, lottery payouts, or refunds (e.g. ₹50,000 lottery) to entice user engagement.",
    icon: AlertTriangle,
  },
  "Kannada language detected": {
    category: "lang",
    description: "Content is composed in native Kannada script, analyzed through Raksha's Indic NLP lexical pipeline.",
    icon: Globe,
  },
  "Code-mixed / Kanglish detected": {
    category: "lang",
    description: "Text mixes Kannada and English or uses Latin-script transliterated Kannada (Kanglish) to bypass monolingual filters.",
    icon: Globe,
  },
  "Analysis partially degraded.": {
    category: "system",
    description: "NLP model inference encountered a recoverable exception; conservative fallback baseline risk applied.",
    icon: Info,
  },
};

export function IndicatorBadge({ indicator, classification }) {
  const [showTooltip, setShowTooltip] = useState(false);

  // Match known explanation or fallback
  const info = INDICATOR_EXPLANATIONS[indicator] || {
    category: classification === "Phishing" ? "nlp" : "info",
    description: `Risk signal detected during automated lexical & intent scanning: "${indicator}"`,
    icon: classification === "Phishing" ? ShieldAlert : AlertTriangle,
  };

  const Icon = info.icon;

  let badgeStyle = "bg-amber-500/10 text-amber-300 border-amber-500/30 hover:border-amber-400/60";
  if (classification === "Phishing" || info.category === "url") {
    badgeStyle = "bg-rose-500/10 text-rose-300 border-rose-500/30 hover:border-rose-400/60";
  } else if (classification === "Safe") {
    badgeStyle = "bg-emerald-500/10 text-emerald-300 border-emerald-500/30 hover:border-emerald-400/60";
  } else if (info.category === "lang") {
    badgeStyle = "bg-cyan-500/10 text-cyan-300 border-cyan-500/30 hover:border-cyan-400/60";
  }

  return (
    <div className="relative inline-block">
      <button
        type="button"
        onClick={() => setShowTooltip(!showTooltip)}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border ${badgeStyle} transition-all cursor-help select-none`}
        aria-label={`Indicator: ${indicator}`}
      >
        <Icon className="w-3.5 h-3.5 flex-shrink-0" />
        <span>{indicator}</span>
        <HelpCircle className="w-3 h-3 opacity-60 ml-0.5" />
      </button>

      {/* Popover / Tooltip */}
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 p-3 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl z-30 text-left animate-fadeIn">
          <div className="flex items-center space-x-1.5 pb-1 mb-1.5 border-b border-slate-800 text-[11px] font-semibold uppercase tracking-wider text-slate-300">
            <Icon className="w-3.5 h-3.5 text-cyan-400" />
            <span>Threat Explanation</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {info.description}
          </p>
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-slate-700" />
        </div>
      )}
    </div>
  );
}
