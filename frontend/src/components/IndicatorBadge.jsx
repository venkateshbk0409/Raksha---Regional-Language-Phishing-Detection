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
    friendlyTitle: "Direct IP link (no domain name)",
    description: "The link points directly to a numeric IP address rather than a registered domain name, which is a common technique used to hide fraudulent websites.",
    icon: Server,
  },
  "Suspicious TLD detected": {
    category: "url",
    friendlyTitle: "Unusual web extension",
    description: "The web address uses an unconventional extension (such as .xyz, .top, or .tk) frequently associated with disposable scam pages.",
    icon: LinkIcon,
  },
  "Excessive subdomains": {
    category: "url",
    friendlyTitle: "Deceptive lookalike domain",
    description: "The link has multiple nested subdomains (e.g., sbi.bank.login.phish.com) designed to deceive mobile users by hiding the real destination.",
    icon: LinkIcon,
  },
  "Excessive hyphens in host": {
    category: "url",
    friendlyTitle: "Brand imitation with hyphens",
    description: "Multiple hyphens in the domain name are often used to create close lookalikes of trusted brands and banks.",
    icon: LinkIcon,
  },
  "Userinfo (@) symbol in URL": {
    category: "url",
    friendlyTitle: "Hidden destination link",
    description: "The '@' symbol in a web address causes browsers to ignore the front part of the link, redirecting you to a different, hidden destination.",
    icon: AlertOctagon,
  },
  "Hex-encoded/obfuscated characters": {
    category: "url",
    friendlyTitle: "Scrambled / hidden web address",
    description: "Special encoded characters are used to disguise the real destination and evade automated security inspection.",
    icon: FileWarning,
  },
  "Suspicious port detected": {
    category: "url",
    friendlyTitle: "Non-standard connection port",
    description: "The link connects over an unusual port rather than standard secure web ports, typical of unverified temporary servers.",
    icon: Server,
  },
  "Punycode/homoglyph domain detected": {
    category: "url",
    friendlyTitle: "Lookalike visual alphabet tricks",
    description: "Uses characters from other alphabets that look identical to normal letters to impersonate legitimate brand names.",
    icon: AlertOctagon,
  },
  "Suspicious keywords in URL path": {
    category: "url",
    friendlyTitle: "Sensitive action keyword in link",
    description: "Contains credential-harvesting words like 'login', 'verify', 'update', or 'otp' aiming to collect confidential credentials.",
    icon: LinkIcon,
  },
  "Insecure HTTP link detected": {
    category: "url",
    friendlyTitle: "Unencrypted web connection (HTTP)",
    description: "The link uses unencrypted HTTP instead of secure HTTPS, meaning sensitive information entered on the page is not protected.",
    icon: LinkIcon,
  },
  "Malformed link detected": {
    category: "url",
    friendlyTitle: "Abnormal or broken link structure",
    description: "The link is syntactically broken or formatted in an unusual way to bypass standard safety checks.",
    icon: FileWarning,
  },
  "Urgent call-to-action detected": {
    category: "nlp",
    friendlyTitle: "Panic / Artificial urgency",
    description: "Uses urgent time pressure ('within 2 hours', 'immediately') to cause panic so you act quickly without verifying.",
    icon: AlertTriangle,
  },
  "Account suspension threat": {
    category: "nlp",
    friendlyTitle: "Service suspension warning",
    description: "Threatens to block your bank account, electricity, or SIM card to coerce immediate compliance.",
    icon: AlertOctagon,
  },
  "Financial / reward incentive": {
    category: "nlp",
    friendlyTitle: "Unverified cash or prize offer",
    description: "Promises unexpected lottery winnings, cash rewards, or refunds to entice you into opening the link.",
    icon: AlertTriangle,
  },
  "High phishing intent detected in message text": {
    category: "nlp",
    friendlyTitle: "Known scam language pattern",
    description: "The message language closely matches patterns found in regional social-engineering and financial scam campaigns.",
    icon: ShieldAlert,
  },
  "Suspicious linguistic patterns detected in message": {
    category: "nlp",
    friendlyTitle: "Unusual phrasing pattern",
    description: "Contains coercive or suspicious phrasing common in phishing messages.",
    icon: AlertTriangle,
  },
  "Kannada language detected": {
    category: "lang",
    friendlyTitle: "Native Kannada text",
    description: "Content is composed in native Kannada script and processed by Raksha's regional language analyzer.",
    icon: Globe,
  },
  "Code-mixed / Kanglish detected": {
    category: "lang",
    friendlyTitle: "Kanglish / Transliterated text",
    description: "The message mixes Kannada and English words or spells Kannada phrases in English letters (Kanglish).",
    icon: Globe,
  },
  "Analysis partially degraded.": {
    category: "system",
    friendlyTitle: "Limited text context",
    description: "The text was very short or ambiguous; conservative baseline safety evaluation applied.",
    icon: Info,
  },
};

export function IndicatorBadge({ indicator, classification }) {
  const [showTooltip, setShowTooltip] = useState(false);

  const info = INDICATOR_EXPLANATIONS[indicator] || {
    category: classification === "Phishing" ? "nlp" : "info",
    friendlyTitle: indicator,
    description: `Signal detected during automated inspection: "${indicator}"`,
    icon: classification === "Phishing" ? ShieldAlert : AlertTriangle,
  };

  const Icon = info.icon;

  let badgeStyle = "bg-[#fef6e7] text-[#783e08] border-[#fde1ab] hover:bg-[#fdeece]";
  if (classification === "Phishing" || info.category === "url") {
    badgeStyle = "bg-[#fdf0ee] text-[#881c1c] border-[#f9c6c0] hover:bg-[#fae2de]";
  } else if (classification === "Safe") {
    badgeStyle = "bg-[#ecf7ed] text-[#14532d] border-[#c3e6cb] hover:bg-[#dff0e1]";
  } else if (info.category === "lang") {
    badgeStyle = "bg-[#eef2ff] text-[#312e81] border-[#c7d2fe] hover:bg-[#e0e7ff]";
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
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-72 p-3.5 rounded-xl bg-white border border-[#dedad0] shadow-elevated z-30 text-left animate-fadeIn">
          <div className="flex items-center space-x-1.5 pb-1.5 mb-1.5 border-b border-[#e7e5dc] text-[11px] font-bold uppercase tracking-wider text-stone-700">
            <Icon className="w-3.5 h-3.5 text-brand-600" />
            <span>Threat Explanation</span>
          </div>
          <p className="text-xs text-stone-600 leading-relaxed font-normal">
            {info.description}
          </p>
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-[#dedad0]" />
        </div>
      )}
    </div>
  );
}
