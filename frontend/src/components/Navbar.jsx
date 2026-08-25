import React from "react";
import { ShieldCheck, Info, ScanLine } from "lucide-react";

export function Navbar({ activeTab, onTabChange }) {
  return (
    <header className="sticky top-0 z-50 glass-card border-b border-slate-800/80">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={() => onTabChange("scanner")}
          className="flex items-center space-x-3 cursor-pointer group"
        >
          <div className="p-2 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 shadow-md shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-all">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-white">RAKSHA</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800 font-medium">
                ರಕ್ಷಾ
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Multilingual Regional Phishing Shield</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <button
            onClick={() => onTabChange("scanner")}
            className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === "scanner"
                ? "bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-850"
            }`}
          >
            <ScanLine className="w-4 h-4" />
            <span>Scanner</span>
          </button>
          <button
            onClick={() => onTabChange("about")}
            className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === "about"
                ? "bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-850"
            }`}
          >
            <Info className="w-4 h-4" />
            <span>Methodology</span>
          </button>
        </nav>
      </div>
    </header>
  );
}
