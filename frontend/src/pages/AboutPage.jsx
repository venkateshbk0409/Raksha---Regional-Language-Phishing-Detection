import React from "react";
import { Shield, Brain, Globe, Lock, Cpu, CheckCircle } from "lucide-react";

export function AboutPage() {
  return (
    <div className="space-y-10 max-w-4xl mx-auto animate-fadeIn">
      {/* Title */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          About Raksha (ರಕ್ಷಾ)
        </h1>
        <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto">
          An AI-powered regional-language cybersecurity defense against multilingual phishing, social-engineering scams, and deceptive links targeting Indian users.
        </p>
      </div>

      {/* The Problem & Solution Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3">
          <div className="flex items-center space-x-3 text-rose-400">
            <Globe className="w-6 h-6" />
            <h3 className="text-lg font-bold text-white">The Regional Phishing Threat</h3>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Conventional anti-phishing tools are trained predominantly on standard English text. Threat actors frequently exploit this gap by sending phishing messages in regional Indian languages (e.g., Kannada), transliterated Latin script (Manglish/Kanglish), or informal code-mixed patterns.
          </p>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3">
          <div className="flex items-center space-x-3 text-cyan-400">
            <Brain className="w-6 h-6" />
            <h3 className="text-lg font-bold text-white">The Raksha Solution</h3>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Raksha provides a dedicated multi-stage pipeline combining script detection, transliteration normalization, multilingual NLP intent analysis, and local lexical URL inspection to deliver deterministic risk scoring with clear explanations.
          </p>
        </div>
      </div>

      {/* Architecture & Engineering Standards */}
      <div className="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
        <h3 className="text-lg font-bold text-white flex items-center space-x-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          <span>Core Engineering & Architecture Standards</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs sm:text-sm">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
            <h4 className="font-semibold text-cyan-400 flex items-center gap-1.5">
              <Lock className="w-4 h-4" /> Stateless MVP
            </h4>
            <p className="text-slate-400 leading-relaxed">
              No raw user messages, URLs, phone numbers, or PII are stored in a database. All inference happens in-memory for zero data liability.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
            <h4 className="font-semibold text-emerald-400 flex items-center gap-1.5">
              <Shield className="w-4 h-4" /> Local Lexical URL Analysis
            </h4>
            <p className="text-slate-400 leading-relaxed">
              URLs are parsed strictly locally using heuristics (homoglyphs, IP hosts, path patterns). The backend never performs network requests to user URLs, preventing SSRF attacks.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
            <h4 className="font-semibold text-amber-400 flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4" /> Evidence-Based ML Pipeline
            </h4>
            <p className="text-slate-400 leading-relaxed">
              Mandatory TF-IDF + Logistic Regression baseline evaluated with precision, recall, F1-score, and false-positive metrics before evaluating Transformer models (MuRIL / XLM-RoBERTa).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
            <h4 className="font-semibold text-rose-400 flex items-center gap-1.5">
              <Shield className="w-4 h-4" /> Graceful Degradation
            </h4>
            <p className="text-slate-400 leading-relaxed">
              If an ML model encounters an execution error, the backend gracefully falls back to deterministic fallback scoring (HTTP 200, Suspicious) without leaking internal traces or crashing.
            </p>
          </div>
        </div>
      </div>

      {/* Team Details */}
      <div className="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-4">
        <h3 className="text-lg font-bold text-white">Project Contributors</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800">
            <h4 className="font-bold text-white text-base">Venkatesh B Kulkarni</h4>
            <p className="text-xs text-cyan-400 font-medium mt-0.5">Team Lead • Full-Stack & Integration</p>
            <p className="text-xs text-slate-400 mt-2">Architecture design, frontend engineering, backend API contracts, and security verification.</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800">
            <h4 className="font-bold text-white text-base">Prajwal Angadi</h4>
            <p className="text-xs text-indigo-400 font-medium mt-0.5">ML / NLP & Backend Logic</p>
            <p className="text-xs text-slate-400 mt-2">Dataset curation, regional transliteration processing, baseline ML modeling, and risk engine logic.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
