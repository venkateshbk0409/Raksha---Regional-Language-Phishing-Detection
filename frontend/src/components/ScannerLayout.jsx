import React from "react";
import { Shield } from "lucide-react";

export function ScannerLayout({ children }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col relative overflow-hidden">
      {/* Dynamic ambient background glows */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-b from-cyan-900/15 via-indigo-950/10 to-transparent pointer-events-none blur-3xl -z-10" />
      <div className="absolute -top-32 right-10 w-96 h-96 bg-cyan-600/5 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-48 -left-20 w-80 h-80 bg-indigo-600/5 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Main Content Area */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 py-6">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-cyan-500" />
            <span>Raksha Multilingual Phishing Defense • Stateless MVP</span>
          </div>
          <div>
            <span>Built by Venkatesh B Kulkarni & Prajwal Angadi</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
