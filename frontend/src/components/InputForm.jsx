import React from "react";
import { Send, Loader2, Sparkles, X, Languages, CornerDownLeft } from "lucide-react";
import { MAX_CONTENT_LENGTH } from "../types/api";

export const DEMO_PRESETS = [
  {
    category: "Kannada Phishing",
    tag: "Native Kannada",
    badgeColor: "border-[#f9c6c0] bg-[#fdf0ee] text-[#881c1c]",
    text: "ಪ್ರಿಯ ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ SBI ಖಾತೆಯನ್ನು ತಕ್ಷಣ KYC ಅಪ್‌ಡೇಟ್ ಮಾಡದಿದ್ದರೆ 24 ಗಂಟೆಗಳಲ್ಲಿ ಸ್ಥಗಿತಗೊಳಿಸಲಾಗುವುದು. ಲಿಂಕ್ ಕ್ಲಿಕ್ ಮಾಡಿ: http://sbi-kyc-update.phish-bank.in",
  },
  {
    category: "Kanglish Urgency",
    tag: "Transliterated",
    badgeColor: "border-[#fde1ab] bg-[#fef6e7] text-[#783e08]",
    text: "Urgent: Nimma electricity bill unpaid ide! Power cut agathe within 2 hours. Koodale verify madi: http://192.168.1.100/billpay",
  },
  {
    category: "Cash Reward Scam",
    tag: "Code-Mixed",
    badgeColor: "border-[#fde1ab] bg-[#fef6e7] text-[#783e08]",
    text: "Congratulations! You have won ₹50,000 cash prize in festive lottery. Claim refund koodale at http://free-rewards.top/claim?id=992",
  },
  {
    category: "Benign Kannada OTP",
    tag: "Safe Message",
    badgeColor: "border-[#c3e6cb] bg-[#ecf7ed] text-[#14532d]",
    text: "ಆತ್ಮೀಯ ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ ಖಾತೆಯ OTP ಸಂಖ್ಯೆ 492810 ಆಗಿದೆ. ಈ OTP ಯನ್ನು ಬ್ಯಾಂಕ್ ಅಧಿಕಾರಿಗಳು ಸೇರಿದಂತೆ ಯಾರೊಂದಿಗೂ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.",
  },
  {
    category: "Benign English Alert",
    tag: "Safe Message",
    badgeColor: "border-[#c3e6cb] bg-[#ecf7ed] text-[#14532d]",
    text: "Dear Customer, your electricity bill payment of Rs 1,450 for consumer ID 849201 has been received successfully with receipt #REC9402.",
  },
];

export function InputForm({ content, onContentChange, onSubmit, isLoading, onClear }) {
  const charCount = content.length;
  const isOverLimit = charCount > MAX_CONTENT_LENGTH;
  const isEmpty = charCount === 0 || !content.trim();

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
    <div className="surface-card p-4 sm:p-6 space-y-4">
      {/* Main Input Form */}
      <form onSubmit={handleSubmit} className="space-y-3.5">
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
            className="w-full bg-[#fbfaf7] hover:bg-[#faf9f4] focus:bg-white text-stone-900 placeholder-stone-400 rounded-xl p-4 text-sm sm:text-base border border-[#e2dfd4] focus:border-brand-500 focus:ring-3 focus:ring-brand-500/15 transition-all resize-y disabled:opacity-60 disabled:cursor-not-allowed outline-none font-sans font-kannada leading-relaxed"
          />

          {content && !isLoading && (
            <button
              type="button"
              onClick={onClear}
              className="absolute top-3.5 right-3.5 p-1.5 rounded-lg text-stone-400 hover:text-stone-700 hover:bg-[#edeae1] transition-colors"
              title="Clear input text"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Action Toolbar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-0.5">
          <div className="flex items-center space-x-3 text-xs w-full sm:w-auto">
            {/* Character Meter */}
            <div className="flex items-center space-x-2">
              <div className="w-16 bg-[#e7e5dc] rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-full ${isOverLimit ? "bg-rose-500" : charPercent > 80 ? "bg-amber-500" : "bg-brand-600"} transition-all duration-300`}
                  style={{ width: `${charPercent}%` }}
                />
              </div>
              <span className={`font-mono text-[11px] ${isOverLimit ? "text-rose-600 font-bold" : charCount > 1800 ? "text-amber-600" : "text-stone-500"}`}>
                {charCount} / {MAX_CONTENT_LENGTH}
              </span>
            </div>

            <span className="text-stone-300 hidden sm:inline">•</span>

            <span className="text-stone-500 flex items-center gap-1.5 text-[11px]">
              <Languages className="w-3.5 h-3.5 text-brand-600" />
              <span>ಕನ್ನಡ / Kanglish / English</span>
            </span>
          </div>

          <div className="flex items-center space-x-3 w-full sm:w-auto">
            <span className="text-[11px] text-stone-400 hidden md:flex items-center gap-1">
              <span>Press</span>
              <kbd className="px-1.5 py-0.5 rounded bg-[#edeae1] border border-[#dedad0] text-stone-600 font-mono text-[10px]">
                Ctrl + Enter
              </kbd>
            </span>

            <button
              type="submit"
              disabled={isEmpty || isOverLimit || isLoading}
              className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-medium text-sm shadow-xs hover:shadow-sm disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none transition-all flex items-center justify-center space-x-2 active:scale-95"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Analyzing Content...</span>
                </>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" />
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
