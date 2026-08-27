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
    <div className="space-y-8 animate-fadeIn pb-6">
      {/* SECTION 1: COMPACT HERO INTRODUCTION */}
      <div className="text-center max-w-xl mx-auto space-y-2 pt-1">
        <div className="inline-flex items-center space-x-2 px-3 py-0.5 rounded-full bg-[#edeae1] border border-[#dedad0] text-stone-700 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-brand-600" />
          <span>ರಕ್ಷಾ • Regional Phishing Guard</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-stone-900">
          Check Messages in Regional Indian Languages
        </h1>
        <p className="text-xs sm:text-sm text-stone-600 leading-relaxed">
          Paste a suspicious message or link below. Raksha will calmly explain whether you should trust it.
        </p>
      </div>

      {/* SECTION 2: CENTERPIECE INPUT WORKSPACE */}
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

        {/* SECTION 3: COMPACT EXAMPLE SCENARIOS */}
        <div className="pt-1">
          <div className="flex items-center space-x-1.5 text-xs font-semibold text-stone-500 mb-2">
            <Compass className="w-3.5 h-3.5 text-brand-600" />
            <span>Not sure what to try? Test an example:</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {DEMO_PRESETS.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                disabled={status === "loading"}
                onClick={() => handleSampleClick(sample.text)}
                className="text-left p-2.5 rounded-xl bg-white hover:bg-[#faf9f4] border border-[#e2dfd4] hover:border-[#cfcbc0] transition-all active:scale-[0.99] disabled:opacity-50 disabled:pointer-events-none group shadow-xs"
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
        <div className="surface-card p-6 animate-pulse space-y-4">
          <div className="flex items-center space-x-3.5">
            <div className="w-10 h-10 rounded-xl bg-[#edeae1]" />
            <div className="space-y-1.5 flex-1">
              <div className="h-3.5 bg-[#edeae1] rounded w-1/4" />
              <div className="h-2.5 bg-[#edeae1] rounded w-1/2" />
            </div>
          </div>
          <div className="h-16 bg-[#fbfaf7] rounded-xl mt-3 border border-[#e7e5dc]" />
          <div className="flex gap-2">
            <div className="h-5 w-20 bg-[#edeae1] rounded-md" />
            <div className="h-5 w-24 bg-[#edeae1] rounded-md" />
          </div>
        </div>
      )}

      {/* Error Alert State */}
      {status === "error" && (
        <div className="p-4 rounded-xl bg-[#fdf0ee] border border-[#f9c6c0] text-[#881c1c] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
          <div className="flex items-start space-x-2.5">
            <AlertCircle className="w-4 h-4 text-[#c53030] flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold text-[#881c1c]">Analysis Request Failed</h4>
              <p className="text-[11px] text-[#991b1b] mt-0.5">{errorMessage}</p>
            </div>
          </div>
          <button
            onClick={handleAnalyze}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-[#dc2626] hover:bg-[#b91c1c] text-white text-xs font-semibold shadow-xs transition-all active:scale-95 flex-shrink-0"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Try Again</span>
          </button>
        </div>
      )}

      {/* SECTION 4: AUTO-SCROLLING RESULT CONTAINER */}
      {status === "success" && result && (
        <div ref={resultRef} className="scroll-mt-20 pt-1">
          <ResultCard result={result} onReset={handleReset} />
        </div>
      )}

      {/* SECTION 5: ULTRA-SCANNABLE TRUST & PRIVACY HIGHLIGHTS */}
      <div className="pt-6 border-t border-[#e7e5dc]">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-start space-x-3">
            <div className="p-1.5 rounded-lg bg-[#eef2ff] text-brand-600 flex-shrink-0 mt-0.5">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-stone-900">Regional Language Support</h4>
              <p className="text-xs text-stone-600 mt-0.5">
                Understands Kannada, Kanglish, and English.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="p-1.5 rounded-lg bg-[#ecf7ed] text-emerald-700 flex-shrink-0 mt-0.5">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-stone-900">Local Link Analysis</h4>
              <p className="text-xs text-stone-600 mt-0.5">
                Checks suspicious URLs without opening them.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="p-1.5 rounded-lg bg-[#f0eee6] text-stone-700 flex-shrink-0 mt-0.5">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-stone-900">Privacy First</h4>
              <p className="text-xs text-stone-600 mt-0.5">
                Messages are processed without storing their contents.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
