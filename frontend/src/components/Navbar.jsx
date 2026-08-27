import React from "react";
import { ShieldCheck, Info, ScanLine } from "lucide-react";

export function Navbar({ activeTab, onTabChange }) {
  return (
    <header className="sticky top-0 z-50 bg-[#f6f5f0]/90 backdrop-blur-md border-b border-[#e7e5dc]">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={() => onTabChange("scanner")}
          className="flex items-center space-x-3 cursor-pointer group select-none"
        >
          <div className="p-2 rounded-xl bg-brand-600 text-white shadow-xs group-hover:bg-brand-700 transition-colors">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-bold tracking-tight text-stone-900">RAKSHA</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-[#edeae1] text-stone-700 border border-[#dedad0] font-medium font-kannada">
                ರಕ್ಷಾ
              </span>
            </div>
            <p className="text-[11px] text-stone-500 hidden sm:block">Regional Phishing & Fraud Shield</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-1.5">
          <button
            onClick={() => onTabChange("scanner")}
            className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all ${
              activeTab === "scanner"
                ? "bg-white text-stone-900 border border-[#e0ded4] font-semibold shadow-xs"
                : "text-stone-600 hover:text-stone-900 hover:bg-[#edeae1]/70"
            }`}
          >
            <ScanLine className="w-3.5 h-3.5" />
            <span>Scanner</span>
          </button>
          <button
            onClick={() => onTabChange("about")}
            className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all ${
              activeTab === "about"
                ? "bg-white text-stone-900 border border-[#e0ded4] font-semibold shadow-xs"
                : "text-stone-600 hover:text-stone-900 hover:bg-[#edeae1]/70"
            }`}
          >
            <Info className="w-3.5 h-3.5" />
            <span>Methodology</span>
          </button>
        </nav>
      </div>
    </header>
  );
}
