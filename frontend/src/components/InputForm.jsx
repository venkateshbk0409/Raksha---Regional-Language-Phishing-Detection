import React from "react";
import { Send, Loader2, Sparkles, X, Languages, CornerDownLeft } from "lucide-react";
import { MAX_CONTENT_LENGTH } from "../types/api";

const DEMO_PRESETS = [
  {
    category: "Kannada Phishing",
    tag: "Native Kannada",
    badgeColor: "border-rose-800/80 bg-rose-950/40 text-rose-300",
    text: "ಪ್ರಿಯ ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ SBI ಖಾತೆಯನ್ನು ತಕ್ಷಣ KYC ಅಪ್‌ಡೇಟ್ ಮಾಡದಿದ್ದರೆ 24 ಗಂಟೆಗಳಲ್ಲಿ ಸ್ಥಗಿತಗೊಳಿಸಲಾಗುವುದು. ಲಿಂಕ್ ಕ್ಲಿಕ್ ಮಾಡಿ: http://sbi-kyc-update.phish-bank.in",
  },
  {
    category: "Kanglish Urgency",
    tag: "Transliterated",
    badgeColor: "border-amber-800/80 bg-amber-950/40 text-amber-300",
    text: "Urgent: Nimma electricity bill unpaid ide! Power cut agathe within 2 hours. Koodale verify madi: http://192.168.1.100/billpay",
  },
  {
    category: "Cash Reward Scam",
    tag: "Code-Mixed",
    badgeColor: "border-amber-800/80 bg-amber-950/40 text-amber-300",
    text: "Congratulations! You have won ₹50,000 cash prize in festive lottery. Claim refund koodale at http://free-rewards.top/claim?id=992",
  },
  {
    category: "Benign Kannada OTP",
    tag: "Safe Message",
    badgeColor: "border-emerald-800/80 bg-emerald-950/40 text-emerald-300",
    text: "ಆತ್ಮೀಯ ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ ಖಾತೆಯ OTP ಸಂಖ್ಯೆ 492810 ಆಗಿದೆ. ಈ OTP ಯನ್ನು ಬ್ಯಾಂಕ್ ಅಧಿಕಾರಿಗಳು ಸೇರಿದಂತೆ ಯಾರೊಂದಿಗೂ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.",
  },
  {
    category: "Benign English Alert",
    tag: "Safe Message",
    badgeColor: "border-emerald-800/80 bg-emerald-950/40 text-emerald-300",
    text: "Dear Customer, your electricity bill payment of Rs 1,450 for consumer ID 849201 has been received successfully with receipt #REC9402.",
  },
];

export function InputForm({ content, onContentChange, onSubmit, isLoading, onClear }) {
  const charCount = content.length;
  const isOverLimit = charCount > MAX_CONTENT_LENGTH;
  const isEmpty = charCount === 0 || !content.trim();

  const handleSampleClick = (sampleText) => {
    onContentChange(sampleText);
  };

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      if (!isEmpty && !isOverLimit && !isLoading) {
        onSubmit();
      }
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!isEmpty && !isOverLimit && !isLoading) {
      onSubmit();
    }
  };

  const charPercent = Math.min(100, (charCount / MAX_CONTENT_LENGTH) * 100);

  return (
    <div className="glass-card rounded-2xl p-5 sm:p-7 shadow-xl border border-slate-800 space-y-5">
      {/* Interactive Quick Demo Scenarios */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Interactive Demo Scenarios</span>
          </div>
          <span className="text-[11px] text-slate-500 hidden sm:inline">
            Click any scenario to populate scanner
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {DEMO_PRESETS.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              disabled={isLoading}
              onClick={() => handleSampleClick(sample.text)}
              className="text-left p-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 transition-all active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none group"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300 transition-colors">
                  {sample.category}
                </span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium border ${sample.badgeColor}`}>
                  {sample.tag}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 line-clamp-1 font-kannada">
                {sample.text}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Main Input Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <textarea
            id="message-input"
            rows={5}
            maxLength={MAX_CONTENT_LENGTH}
            disabled={isLoading}
            value={content}
            onKeyDown={handleKeyDown}
            onChange={(e) => onContentChange(e.target.value)}
            placeholder="Paste suspicious SMS, WhatsApp message, email, or URL in Kannada, English, or Code-mixed (Kanglish) text..."
            className="w-full bg-slate-900/90 text-slate-100 placeholder-slate-500 rounded-xl p-4 text-sm sm:text-base border border-slate-700/80 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all resize-y disabled:opacity-60 disabled:cursor-not-allowed outline-none font-sans font-kannada leading-relaxed"
          />

          {content && !isLoading && (
            <button
              type="button"
              onClick={onClear}
              className="absolute top-3 right-3 p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors border border-transparent hover:border-slate-700"
              title="Clear input text"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Action Toolbar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-1">
          <div className="flex items-center space-x-3 text-xs w-full sm:w-auto">
            {/* Character Meter */}
            <div className="flex items-center space-x-2">
              <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-full ${isOverLimit ? "bg-rose-500" : charPercent > 80 ? "bg-amber-500" : "bg-cyan-500"} transition-all duration-300`}
                  style={{ width: `${charPercent}%` }}
                />
              </div>
              <span className={`font-mono text-[11px] ${isOverLimit ? "text-rose-400 font-bold" : charCount > 1800 ? "text-amber-400" : "text-slate-400"}`}>
                {charCount} / {MAX_CONTENT_LENGTH}
              </span>
            </div>

            <span className="text-slate-700 hidden sm:inline">•</span>

            <span className="text-slate-400 flex items-center gap-1 text-[11px]">
              <Languages className="w-3.5 h-3.5 text-cyan-400" />
              <span>ಕನ್ನಡ / Kanglish / English</span>
            </span>
          </div>

          <div className="flex items-center space-x-3 w-full sm:w-auto">
            <span className="text-[11px] text-slate-500 hidden md:flex items-center gap-1">
              <span>Press</span>
              <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-mono text-[10px]">
                Ctrl + Enter
              </kbd>
            </span>

            <button
              type="submit"
              disabled={isEmpty || isOverLimit || isLoading}
              className="w-full sm:w-auto px-7 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none transition-all flex items-center justify-center space-x-2 active:scale-95"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Analyzing Content...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Scan for Phishing</span>
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
