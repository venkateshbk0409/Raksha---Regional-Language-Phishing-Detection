import React, { useState } from "react";
import { Shield, AlertCircle, RefreshCw, Sparkles, CheckCircle2 } from "lucide-react";
import { InputForm } from "../components/InputForm";
import { ResultCard } from "../components/ResultCard";
import { analyzeContent } from "../services/api";

export function ScannerPage() {
  const [content, setContent] = useState("");
  const [status, setStatus] = useState("idle"); // 'idle' | 'loading' | 'success' | 'error'
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  const handleAnalyze = async () => {
    if (!content.trim()) return;

    setStatus("loading");
    setErrorMessage("");

    try {
      const data = await analyzeContent(content);
      setResult(data);
      setStatus("success");
    } catch (err) {
      setErrorMessage(err.message || "An unexpected error occurred while analyzing the content.");
      setStatus("error");
    }
  };

  const handleReset = () => {
    setContent("");
    setResult(null);
    setStatus("idle");
    setErrorMessage("");
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Header */}
      <div className="text-center max-w-2xl mx-auto space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800 text-cyan-400 text-xs font-medium mb-1">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Regional-Language & Code-Mixed NLP Phishing Guard</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
          Scan Regional Messages & Suspicious Links
        </h1>
        <p className="text-sm sm:text-base text-slate-400">
          Verify Kannada SMS, transliterated WhatsApp alerts, social-engineering scams, and suspicious links with instant explainability.
        </p>
      </div>

      {/* Main Scanner Section */}
      <div className="space-y-6">
        <InputForm
          content={content}
          onContentChange={(val) => {
            setContent(val);
            if (status === "error") setStatus("idle");
          }}
          onSubmit={handleAnalyze}
          isLoading={status === "loading"}
          onClear={() => {
            setContent("");
            if (status !== "idle") setStatus("idle");
          }}
        />

        {/* Loading State Skeleton */}
        {status === "loading" && (
          <div className="glass-card rounded-2xl p-8 border border-slate-800 animate-pulse space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-xl bg-slate-800" />
              <div className="space-y-2 flex-1">
                <div className="h-4 bg-slate-800 rounded w-1/4" />
                <div className="h-3 bg-slate-800 rounded w-1/2" />
              </div>
            </div>
            <div className="h-20 bg-slate-900/60 rounded-xl mt-4" />
            <div className="flex gap-2">
              <div className="h-6 w-20 bg-slate-800 rounded-md" />
              <div className="h-6 w-24 bg-slate-800 rounded-md" />
            </div>
          </div>
        )}

        {/* Error Alert State */}
        {status === "error" && (
          <div className="glass-card rounded-2xl p-6 border border-rose-900/60 bg-rose-950/20 text-rose-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-semibold text-rose-300">Analysis Request Failed</h4>
                <p className="text-xs text-rose-200/80 mt-0.5">{errorMessage}</p>
              </div>
            </div>
            <button
              onClick={handleAnalyze}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-rose-900/50 hover:bg-rose-900 text-rose-100 text-xs font-semibold border border-rose-700 transition-all active:scale-95 flex-shrink-0"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Try Again</span>
            </button>
          </div>
        )}

        {/* Success State Result */}
        {status === "success" && result && (
          <ResultCard result={result} onReset={handleReset} />
        )}
      </div>

      {/* Feature Highlights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6">
        <div className="glass-card rounded-xl p-5 border border-slate-800/80">
          <div className="flex items-center space-x-2.5 mb-2">
            <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-semibold text-white">Regional NLP</h4>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Detects Kannada script, transliterated Latin script, and code-mixed phrasing commonly used to bypass English spam filters.
          </p>
        </div>

        <div className="glass-card rounded-xl p-5 border border-slate-800/80">
          <div className="flex items-center space-x-2.5 mb-2">
            <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-semibold text-white">Local Lexical URL Analysis</h4>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Inspects homoglyphs, IP hosts, suspicious TLDs, and path patterns entirely offline without network requests or SSRF risk.
          </p>
        </div>

        <div className="glass-card rounded-xl p-5 border border-slate-800/80">
          <div className="flex items-center space-x-2.5 mb-2">
            <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-semibold text-white">Privacy-First Architecture</h4>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Message text and PII are never stored. Only anonymous, non-identifiable telemetry metadata is retained for system evaluation.
          </p>
        </div>
      </div>
    </div>
  );
}
