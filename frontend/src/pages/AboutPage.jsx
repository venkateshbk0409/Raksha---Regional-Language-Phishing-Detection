import React from "react";
import {
  Shield,
  Brain,
  Globe,
  Lock,
  Cpu,
  CheckCircle,
  FileCode2,
  Terminal,
  Activity,
  Layers,
  Search,
  BookOpen,
} from "lucide-react";

export function AboutPage() {
  return (
    <div className="space-y-12 max-w-4xl mx-auto animate-fadeIn pb-12">
      {/* Title & Introduction */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800 text-cyan-400 text-xs font-semibold">
          <BookOpen className="w-3.5 h-3.5" />
          <span>System Architecture & Explainability Methodology</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
          About Raksha (ರಕ್ಷಾ)
        </h1>
        <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto leading-relaxed">
          An AI-powered multilingual cybersecurity defense system specifically engineered to detect regional Indian language phishing attacks, transliterated social-engineering scams, and deceptive URLs.
        </p>
      </div>

      {/* The Threat Landscape & Solution Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card rounded-2xl p-6 sm:p-7 border border-slate-800 space-y-3">
          <div className="flex items-center space-x-3 text-rose-400">
            <div className="p-2.5 rounded-xl bg-rose-500/10">
              <Globe className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">The Regional Phishing Gap</h3>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Conventional anti-phishing algorithms are predominantly trained on standard English corpora. Threat actors exploit this vulnerability by distributing fraudulent KYC updates, electricity cut-off threats, and lottery scams in Kannada script, Latin transliterations (Kanglish), or informal code-mixed text to evade spam filters.
          </p>
        </div>

        <div className="glass-card rounded-2xl p-6 sm:p-7 border border-slate-800 space-y-3">
          <div className="flex items-center space-x-3 text-cyan-400">
            <div className="p-2.5 rounded-xl bg-cyan-500/10">
              <Brain className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">The Raksha Architecture</h3>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Raksha provides a dedicated multi-stage pipeline combining script detection, transliteration normalization, multilingual NLP intent analysis, and local lexical URL inspection to deliver deterministic risk scoring with clear, actionable explanations.
          </p>
        </div>
      </div>

      {/* Deep-Dive: The Dual-Track Risk Engine */}
      <div className="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
        <div className="flex items-center space-x-3 pb-4 border-b border-slate-800">
          <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Dual-Track Detection Engine</h3>
            <p className="text-xs text-slate-400">Deterministic synthesis of linguistic intent and local URL lexical structure</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Track 1: NLP Intent Pipeline */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
            <div className="flex items-center space-x-2 text-cyan-400 text-sm font-bold">
              <Brain className="w-4 h-4" />
              <span>Track 1: Indic NLP Pipeline</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Standardizes Unicode NFC, identifies script ratios (native Kannada, Latin, mixed), contextualizes Kanglish transliterations while strictly preserving English loanwords, and calculates textual threat probabilities using FeatureUnion TF-IDF and Logistic Regression.
            </p>
          </div>

          {/* Track 2: Local URL Lexical Parser */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
            <div className="flex items-center space-x-2 text-emerald-400 text-sm font-bold">
              <Search className="w-4 h-4" />
              <span>Track 2: Local URL Lexical Parser</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Parses URLs entirely offline using lexical heuristics: raw IP hostnames, suspicious TLDs (.xyz, .top, .tk), excessive subdomains (&ge;3), userinfo '@' symbol tricks, obfuscated percent-encoded characters, homoglyphs, and non-standard ports with strictly zero outbound network requests.
            </p>
          </div>
        </div>

        {/* Mathematical Synthesis Formula */}
        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 space-y-2">
          <div className="text-slate-400 font-semibold flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            <span>Deterministic Risk Formula</span>
          </div>
          <div className="p-3 bg-slate-900/90 rounded-lg text-cyan-300 text-xs sm:text-sm overflow-x-auto">
            Risk_total = (0.50 &times; S_nlp) + (0.50 &times; S_url) + Modifiers
          </div>
          <div className="flex flex-wrap gap-4 text-[11px] text-slate-400 pt-1">
            <span>• Safe: &lt; 0.40</span>
            <span>• Suspicious: 0.40 &ndash; 0.74</span>
            <span>• Phishing: &ge; 0.75</span>
          </div>
        </div>
      </div>

      {/* Core Engineering Standards */}
      <div className="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
        <h3 className="text-lg font-bold text-white flex items-center space-x-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          <span>Core Engineering & Security Standards</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs sm:text-sm">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
            <h4 className="font-semibold text-cyan-400 flex items-center gap-1.5">
              <Lock className="w-4 h-4" /> Stateless Privacy by Default
            </h4>
            <p className="text-slate-400 leading-relaxed">
              No raw user text, messages, URLs, phone numbers, or PII are stored in a database. All scanning runs transiently in-memory with zero data retention liability.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
            <h4 className="font-semibold text-emerald-400 flex items-center gap-1.5">
              <Shield className="w-4 h-4" /> Strict SSRF Protection
            </h4>
            <p className="text-slate-400 leading-relaxed">
              The backend never performs HTTP requests, DNS lookups, or pings against user-submitted URLs, guaranteeing total immunity against Server-Side Request Forgery.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
            <h4 className="font-semibold text-amber-400 flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4" /> Evidence-Based ML Modeling
            </h4>
            <p className="text-slate-400 leading-relaxed">
              Trained and empirically tested on leakage-free group-based splits (70/15/15) with zero data overlap and dedicated held-out regional test subsets.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
            <h4 className="font-semibold text-rose-400 flex items-center gap-1.5">
              <Activity className="w-4 h-4" /> Graceful Degradation
            </h4>
            <p className="text-slate-400 leading-relaxed">
              Should model inference encounter unexpected anomalies, the system returns a safe conservative fallback score (0.50 Suspicious) with transparent status reporting.
            </p>
          </div>
        </div>
      </div>

      {/* Project Team */}
      <div className="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-4">
        <h3 className="text-lg font-bold text-white">Project Contributors</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800">
            <h4 className="font-bold text-white text-base">Venkatesh B Kulkarni</h4>
            <p className="text-xs text-cyan-400 font-semibold mt-0.5">Team Lead • Full-Stack & Security Integration</p>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">Architecture specification, React frontend explainability UI, FastAPI backend wiring, and SSRF security enforcement.</p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800">
            <h4 className="font-bold text-white text-base">Prajwal Angadi</h4>
            <p className="text-xs text-indigo-400 font-semibold mt-0.5">ML / NLP & Risk Engine Architecture</p>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">Regional dataset curation, transliteration processing, TF-IDF baseline model training, and transformer candidate evaluation.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
