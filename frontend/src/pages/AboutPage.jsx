import React, { useState } from "react";
import {
  Shield,
  Brain,
  Globe,
  Lock,
  Cpu,
  CheckCircle,
  Activity,
  Layers,
  Search,
  BookOpen,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
} from "lucide-react";

export function AboutPage() {
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);

  const steps = [
    {
      number: "01",
      title: "Message & Script Detection",
      icon: Globe,
      color: "bg-[#eef2ff] text-brand-700 border-[#c7d2fe]",
      description:
        "Raksha identifies whether incoming text is native Kannada script, standard English, or code-mixed Kannada written in English letters (Kanglish).",
    },
    {
      number: "02",
      title: "Urgency & Intent Analysis",
      icon: Brain,
      color: "bg-[#fef6e7] text-[#783e08] border-[#fde1ab]",
      description:
        "The language model checks for social-engineering tactics like fake electricity cut-off warnings, urgent KYC deadlines, or unverified cash rewards.",
    },
    {
      number: "03",
      title: "Safe Offline Link Inspection",
      icon: Search,
      color: "bg-[#ecf7ed] text-[#14532d] border-[#c3e6cb]",
      description:
        "Embedded links are verified locally for lookalike domains, raw IP hosts, or deceptive characters — completely offline without opening dangerous websites.",
    },
    {
      number: "04",
      title: "Clear Risk Score & Advice",
      icon: Shield,
      color: "bg-[#fdf0ee] text-[#881c1c] border-[#f9c6c0]",
      description:
        "Findings are combined into a straightforward safety verdict (Safe, Suspicious, or Phishing) with clear, actionable advice on what to do next.",
    },
  ];

  return (
    <div className="space-y-10 max-w-3xl mx-auto animate-fadeIn pb-12">
      {/* Title & Introduction */}
      <div className="text-center space-y-3 pt-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#edeae1] border border-[#dedad0] text-stone-700 text-xs font-semibold">
          <BookOpen className="w-3.5 h-3.5 text-brand-600" />
          <span>How Raksha Protects You</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold text-stone-900 tracking-tight">
          How Phishing Detection Works
        </h1>
        <p className="text-sm sm:text-base text-stone-600 max-w-xl mx-auto leading-relaxed">
          Raksha is an AI defense system designed to protect users against regional Indian language scams, transliterated messages, and deceptive links in 4 simple steps.
        </p>
      </div>

      {/* Why Regional Detection Matters */}
      <div className="surface-card p-5 sm:p-6 space-y-2.5">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-[#fef6e7] text-[#783e08] border border-[#fde1ab]">
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-stone-900">Why Regional Language Protection?</h3>
            <p className="text-xs text-stone-500">The gap in standard security filters</p>
          </div>
        </div>
        <p className="text-xs sm:text-sm text-stone-600 leading-relaxed pt-1">
          Most spam and phishing filters are built only for standard English. Scammers exploit this by sending fraudulent messages in Kannada script or Kanglish (e.g. <em>"Nimma electricity bill unpaid ide, power cut agathe"</em>) to bypass standard filters. Raksha bridges this gap with regional-language intelligence.
        </p>
      </div>

      {/* 4-Step Simplified Detection Process */}
      <div className="space-y-4">
        <div className="text-center">
          <h2 className="text-lg font-bold text-stone-900">The 4-Step Detection Pipeline</h2>
          <p className="text-xs text-stone-500">From raw message to trusted safety verdict</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div
                key={idx}
                className="surface-card p-5 flex flex-col justify-between space-y-3 shadow-xs"
              >
                <div className="flex items-center justify-between">
                  <div className={`p-2 rounded-xl border ${step.color}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="font-mono text-[11px] font-bold text-stone-400">
                    STEP {step.number}
                  </span>
                </div>
                <div>
                  <h3 className="text-sm font-bold text-stone-900 mb-1">{step.title}</h3>
                  <p className="text-xs text-stone-600 leading-relaxed">{step.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Collapsible Technical & Privacy Deep-Dive */}
      <div className="surface-card overflow-hidden">
        <button
          type="button"
          onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
          className="w-full p-5 flex items-center justify-between text-left hover:bg-[#fbfaf7] transition-colors"
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-[#eef2ff] text-brand-600">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-stone-900">
                Security & Privacy Architecture
              </h3>
              <p className="text-xs text-stone-500">
                Technical standards, zero data storage, and local offline URL verification
              </p>
            </div>
          </div>
          <div className="p-1.5 rounded-lg bg-[#f0eee6] text-stone-600">
            {showTechnicalDetails ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </div>
        </button>

        {showTechnicalDetails && (
          <div className="p-5 pt-0 border-t border-[#e7e5dc] space-y-3 text-xs text-stone-600 animate-fadeIn">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3">
              <div className="p-3.5 rounded-xl bg-[#fbfaf7] border border-[#e2dfd4] space-y-1">
                <div className="flex items-center space-x-1.5 font-semibold text-stone-900">
                  <Lock className="w-3.5 h-3.5 text-brand-600" />
                  <span>Stateless Privacy</span>
                </div>
                <p className="text-[11px] leading-relaxed">
                  No user message content, names, numbers, or URLs are ever stored in a database. All inspection runs strictly transient in-memory.
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-[#fbfaf7] border border-[#e2dfd4] space-y-1">
                <div className="flex items-center space-x-1.5 font-semibold text-stone-900">
                  <Shield className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Strict SSRF Protection</span>
                </div>
                <p className="text-[11px] leading-relaxed">
                  Raksha never makes outbound web requests to user links, preventing Server-Side Request Forgery and preventing malicious servers from logging scans.
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-[#fbfaf7] border border-[#e2dfd4] space-y-1">
                <div className="flex items-center space-x-1.5 font-semibold text-stone-900">
                  <CheckCircle className="w-3.5 h-3.5 text-amber-600" />
                  <span>Evidence-Based ML</span>
                </div>
                <p className="text-[11px] leading-relaxed">
                  Trained on leakage-free group splits (70/15/15) with dedicated regional evaluation datasets for Kannada and transliterated patterns.
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-[#fbfaf7] border border-[#e2dfd4] space-y-1">
                <div className="flex items-center space-x-1.5 font-semibold text-stone-900">
                  <Activity className="w-3.5 h-3.5 text-rose-600" />
                  <span>Safe Graceful Fallback</span>
                </div>
                <p className="text-[11px] leading-relaxed">
                  If an input is too sparse or unusual, the system reports limited confidence calmly without generating false high-risk alarms.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Project Contributors */}
      <div className="surface-card p-5 sm:p-6 space-y-3">
        <h3 className="text-sm font-bold text-stone-900">Project Team & Contributors</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-0.5">
          <div className="p-4 rounded-xl bg-[#fbfaf7] border border-[#e2dfd4]">
            <h4 className="font-bold text-stone-900 text-xs">Venkatesh B Kulkarni</h4>
            <p className="text-[11px] text-brand-700 font-semibold mt-0.5">Team Lead • Full-Stack & Security Integration</p>
            <p className="text-[11px] text-stone-600 mt-1.5 leading-relaxed">
              Architecture specification, explainable React frontend, FastAPI monolithic backend wiring, and SSRF security enforcement.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#fbfaf7] border border-[#e2dfd4]">
            <h4 className="font-bold text-stone-900 text-xs">Prajwal Angadi</h4>
            <p className="text-[11px] text-brand-700 font-semibold mt-0.5">ML / NLP & Risk Engine Architecture</p>
            <p className="text-[11px] text-stone-600 mt-1.5 leading-relaxed">
              Regional dataset curation, transliteration processing, TF-IDF baseline model training, and transformer candidate evaluation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
