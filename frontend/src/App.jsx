import React, { useState } from "react";
import { Navbar } from "./components/Navbar";
import { ScannerLayout } from "./components/ScannerLayout";
import { ScannerPage } from "./pages/ScannerPage";
import { AboutPage } from "./pages/AboutPage";

export default function App() {
  const [activeTab, setActiveTab] = useState("scanner");

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f5f0] text-stone-900 font-sans selection:bg-brand-100 selection:text-brand-900">
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />
      <ScannerLayout>
        {activeTab === "scanner" && <ScannerPage />}
        {activeTab === "about" && <AboutPage />}
      </ScannerLayout>
    </div>
  );
}
