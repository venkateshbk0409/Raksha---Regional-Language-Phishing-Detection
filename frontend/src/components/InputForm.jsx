import React from "react";
import { Send, Loader2, Sparkles, X, Languages } from "lucide-react";
import { MAX_CONTENT_LENGTH } from "../types/api";

const SAMPLE_PROMPTS = [
  {
    label: "Kannada Phishing",
    lang: "kn",
    text: "ಪ್ರಿಯ ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ SBI ಖಾತೆಯನ್ನು ತಕ್ಷಣ KYC ಅಪ್‌ಡೇಟ್ ಮಾಡದಿದ್ದರೆ ಸ್ಥಗಿತಗೊಳಿಸಲಾಗುವುದು. ಲಿಂಕ್ ಕ್ಲಿಕ್ ಮಾಡಿ: http://sbi-kyc-update.phish-bank.in",
  },
  {
    label: "Code-Mixed Kannada",
    lang: "code-mixed",
    text: "Nimma electricity bill unpaid ide! Power cut agathe within 2 hours. Call officer 9876543210 or pay at http://quick-kptcl-pay.com",
  },
  {
    label: "English Phishing",
    lang: "en",
    text: "URGENT: Your account has been locked due to suspicious login attempts. Verify immediately at http://192.168.1.1/login.php",
  },
  {
    label: "Legitimate Message",
    lang: "en",
    text: "Dear customer, your OTP for transaction at Amazon is 492810. Do not share this OTP with anyone, including bank officials.",
  },
];

export function InputForm({ content, onContentChange, onSubmit, isLoading, onClear }) {
  const charCount = content.length;
  const isOverLimit = charCount > MAX_CONTENT_LENGTH;
  const isEmpty = charCount === 0 || !content.trim();

  const handleSampleClick = (sampleText) => {
    onContentChange(sampleText);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!isEmpty && !isOverLimit && !isLoading) {
      onSubmit();
    }
  };

  return (
    <div className="glass-card rounded-2xl p-5 sm:p-6 shadow-xl border border-slate-800">
      {/* Sample presets */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 text-xs text-slate-400 font-medium mb-2.5">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Try quick sample messages:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {SAMPLE_PROMPTS.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              disabled={isLoading}
              onClick={() => handleSampleClick(sample.text)}
              className="text-xs px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-750 text-slate-300 hover:text-cyan-300 border border-slate-700/80 hover:border-cyan-700/60 transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
            >
              {sample.label}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <textarea
            id="message-input"
            rows={5}
            maxLength={MAX_CONTENT_LENGTH}
            disabled={isLoading}
            value={content}
            onChange={(e) => onContentChange(e.target.value)}
            placeholder="Paste suspicious SMS, WhatsApp message, email, or URL in Kannada, English, or Code-mixed text..."
            className="w-full bg-slate-900/90 text-slate-100 placeholder-slate-500 rounded-xl p-4 text-sm sm:text-base border border-slate-700/80 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all resize-y disabled:opacity-60 disabled:cursor-not-allowed outline-none font-sans"
          />
          {content && !isLoading && (
            <button
              type="button"
              onClick={onClear}
              className="absolute top-3 right-3 p-1.5 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
              title="Clear input"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Action bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-1">
          <div className="flex items-center space-x-2 text-xs">
            <span className={`font-mono ${isOverLimit ? "text-rose-400 font-bold" : charCount > 1800 ? "text-amber-400" : "text-slate-400"}`}>
              {charCount} / {MAX_CONTENT_LENGTH}
            </span>
            <span className="text-slate-600">•</span>
            <span className="text-slate-400 flex items-center gap-1">
              <Languages className="w-3 h-3 text-cyan-400" /> Kannada / Transliterated / English
            </span>
          </div>

          <button
            type="submit"
            disabled={isEmpty || isOverLimit || isLoading}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none transition-all flex items-center justify-center space-x-2 active:scale-95"
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
      </form>
    </div>
  );
}
