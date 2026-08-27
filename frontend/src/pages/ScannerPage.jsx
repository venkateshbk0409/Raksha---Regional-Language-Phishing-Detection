import React, { useState, useRef, useEffect } from "react";
import { Shield, AlertCircle, RefreshCw, Sparkles, CheckCircle2, ArrowDownRight, Compass } from "lucide-react";
import { InputForm, DEMO_PRESETS } from "../components/InputForm";
import { ResultCard } from "../components/ResultCard";
import { analyzeContent } from "../services/api";

export function ScannerPage() {
  const [content, setContent] = useState("");
  const [status, setStatus] = useState("idle"); // 'idle' | 'loading' | 'success' | 'error'
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const resultRef = useRef(null);

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

  // Automatically smooth-scroll to result upon successful scan
  useEffect(() => {
    if (status === "success" && resultRef.current) {
      const prefersReducedMotion =
        typeof window !== "undefined" &&
        typeof window.matchMedia === "function" &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

      // Small tick to ensure DOM is rendered
      const timeoutId = setTimeout(() => {
        if (typeof resultRef.current?.scrollIntoView === "function") {
          resultRef.current.scrollIntoView({
            behavior: prefersReducedMotion ? "auto" : "smooth",
            block: "start",
          });
        }
      }, 60);

      return () => clearTimeout(timeoutId);
    }
  }, [status]);

  const handleReset = () => {
    setContent("");
    setResult(null);
    setStatus("idle");
    setErrorMessage("");
    try {
      if (typeof window !== "undefined" && typeof window.scrollTo === "function") {
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    } catch {
      // jsdom environment fallback
    }
  };

  const handleSampleClick = (sampleText) => {
    setContent(sampleText);
    if (status === "error") setStatus("idle");
  };

  return (
    <div className="space-y-10 animate-fadeIn pb-8">
      {/* SECTION 1: HERO INTRODUCTION */}
      <div className="text-center max-w-2xl mx-auto space-y-3 pt-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#edeae1] border border-[#dedad0] text-stone-700 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-brand-600" />
          <span>Regional-Language & Code-Mixed Phishing Guard</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-stone-900">
          Scan Regional Messages & Suspicious Links
        </h1>
        <p className="text-sm sm:text-base text-stone-600 leading-relaxed">
          Verify Kannada SMS, transliterated WhatsApp alerts, social-engineering scams, and suspicious links with instant explainability.
        </p>
      </div>

      {/* SECTION 2: CENTERPIECE INPUT CANVAS */}
      <div className="space-y-4">
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

        {/* SECTION 3: DEDICATED DEMO SCENARIOS SECTION */}
        <div className="pt-2">
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-stone-500 mb-2.5">
            <Compass className="w-3.5 h-3.5 text-brand-600" />
            <span>Or test an example scenario:</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
            {DEMO_PRESETS.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                disabled={status === "loading"}
                onClick={() => handleSampleClick(sample.text)}
                className="text-left p-3 rounded-xl bg-white hover:bg-[#faf9f4] border border-[#e2dfd4] hover:border-[#cfcbc0] transition-all active:scale-[0.99] disabled:opacity-50 disabled:pointer-events-none group shadow-xs"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-stone-800 group-hover:text-brand-700 transition-colors">
                    {sample.category}
                  </span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium border ${sample.badgeColor}`}>
                    {sample.tag}
                  </span>
                </div>
                <p className="text-[11px] text-stone-500 line-clamp-1 font-kannada">
                  {sample.text}
                </p>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Loading Skeleton */}
      {status === "loading" && (
        <div className="surface-card p-8 animate-pulse space-y-4">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-2xl bg-[#edeae1]" />
            <div className="space-y-2 flex-1">
              <div className="h-4 bg-[#edeae1] rounded w-1/4" />
              <div className="h-3 bg-[#edeae1] rounded w-1/2" />
            </div>
          </div>
          <div className="h-20 bg-[#fbfaf7] rounded-xl mt-4 border border-[#e7e5dc]" />
          <div className="flex gap-2">
            <div className="h-6 w-20 bg-[#edeae1] rounded-md" />
            <div className="h-6 w-24 bg-[#edeae1] rounded-md" />
          </div>
        </div>
      )}

      {/* Error Alert State */}
      {status === "error" && (
        <div className="p-5 rounded-2xl bg-[#fdf0ee] border border-[#f9c6c0] text-[#881c1c] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xs">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-[#c53030] flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-bold text-[#881c1c]">Analysis Request Failed</h4>
              <p className="text-xs text-[#991b1b] mt-0.5">{errorMessage}</p>
            </div>
          </div>
          <button
            onClick={handleAnalyze}
            className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-[#dc2626] hover:bg-[#b91c1c] text-white text-xs font-semibold shadow-xs transition-all active:scale-95 flex-shrink-0"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Try Again</span>
          </button>
        </div>
      )}

      {/* SECTION 4: AUTO-SCROLLING RESULT CONTAINER */}
      {status === "success" && result && (
        <div ref={resultRef} className="scroll-mt-20 pt-2">
          <ResultCard result={result} onReset={handleReset} />
        </div>
      )}

      {/* SECTION 5: TRUST & PRIVACY HIGHLIGHTS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pt-8 border-t border-[#e7e5dc]">
        <div className="space-y-1.5">
          <div className="flex items-center space-x-2 mb-1">
            <div className="p-1.5 rounded-lg bg-[#eef2ff] text-brand-600">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-bold text-stone-900">Regional NLP</h4>
          </div>
          <p className="text-xs text-stone-600 leading-relaxed">
            Detects Kannada script, transliterated Latin script, and code-mixed phrasing commonly used to bypass English spam filters.
          </p>
        </div>

        <div className="space-y-1.5">
          <div className="flex items-center space-x-2 mb-1">
            <div className="p-1.5 rounded-lg bg-[#ecf7ed] text-emerald-700">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-bold text-stone-900">Local Lexical URL Analysis</h4>
          </div>
          <p className="text-xs text-stone-600 leading-relaxed">
            Inspects homoglyphs, IP hosts, suspicious TLDs, and path patterns entirely offline without network requests or SSRF risk.
          </p>
        </div>

        <div className="space-y-1.5">
          <div className="flex items-center space-x-2 mb-1">
            <div className="p-1.5 rounded-lg bg-[#f0eee6] text-stone-700">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-bold text-stone-900">Privacy-First Architecture</h4>
          </div>
          <p className="text-xs text-stone-600 leading-relaxed">
            Message text and PII are never stored. Only anonymous, non-identifiable telemetry metadata is retained for system evaluation.
          </p>
        </div>
      </div>
    </div>
  );
}
