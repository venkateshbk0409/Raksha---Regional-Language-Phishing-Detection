import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import { ResultCard } from "../ResultCard";

describe("ResultCard Component", () => {
  it("renders safe classification details correctly", () => {
    const mockSafeResult = {
      classification: "Safe",
      risk_score: 0.12,
      language_detected: "kannada",
      indicators: [],
      recommended_action: "No action required.",
    };

    render(<ResultCard result={mockSafeResult} onReset={vi.fn()} />);

    expect(screen.getByText("Safe")).toBeInTheDocument();
    expect(screen.getByText("Safe Content")).toBeInTheDocument();
    expect(screen.getByText("0.12")).toBeInTheDocument();
    expect(screen.getByText("Lang: kannada")).toBeInTheDocument();
    expect(screen.getByText("No action required.")).toBeInTheDocument();
  });

  it("renders phishing classification and indicators correctly", () => {
    const mockPhishingResult = {
      classification: "Phishing",
      risk_score: 0.88,
      language_detected: "code-mixed",
      indicators: ["Urgency keyword detected", "Suspicious IP-based URL"],
      recommended_action: "Do not click links or share credentials.",
    };

    render(<ResultCard result={mockPhishingResult} onReset={vi.fn()} />);

    expect(screen.getByText("Phishing")).toBeInTheDocument();
    expect(screen.getByText("Phishing Detected")).toBeInTheDocument();
    expect(screen.getByText("0.88")).toBeInTheDocument();
    expect(screen.getByText("Urgency keyword detected")).toBeInTheDocument();
    expect(screen.getByText("Suspicious IP-based URL")).toBeInTheDocument();
    expect(screen.getByText("Do not click links or share credentials.")).toBeInTheDocument();
  });
});
