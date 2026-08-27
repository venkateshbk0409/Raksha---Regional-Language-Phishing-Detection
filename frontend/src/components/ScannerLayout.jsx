import React from "react";
import { Shield } from "lucide-react";

export function ScannerLayout({ children }) {
  return (
    <div className="min-h-screen bg-[#f6f5f0] text-stone-900 flex flex-col relative">
      {/* Main Content Area */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-[#e7e5dc] bg-[#f0eee6]/60 py-6 mt-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-stone-500">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-brand-600" />
            <span className="font-medium text-stone-700">Raksha Regional Phishing Shield</span>
            <span className="text-stone-400">•</span>
            <span>100% In-Memory & Stateless</span>
          </div>
          <div>
            <span>Developed by Venkatesh B Kulkarni & Prajwal Angadi</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
