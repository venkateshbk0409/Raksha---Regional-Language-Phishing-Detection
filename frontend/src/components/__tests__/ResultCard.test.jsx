import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import { ResultCard } from "../ResultCard";

describe("ResultCard Component", () => {
  it("renders safe classification details correctly", () => {
    const mockSafeResult = {
      classification: "Safe",
      risk_score: 0.12,
      language_detected: "kannada",
      indicators: [],
      recommended_action: "No immediate threat detected. Standard vigilance advised.",
    };

    render(<ResultCard result={mockSafeResult} onReset={vi.fn()} />);

    expect(screen.getByText("Safe")).toBeInTheDocument();
    expect(screen.getByText("Safe Content")).toBeInTheDocument();
    expect(screen.getByText("0.12")).toBeInTheDocument();
    expect(screen.getByText("Lang: kannada")).toBeInTheDocument();
    expect(screen.getByText("No immediate threat detected. Standard vigilance advised.")).toBeInTheDocument();
  });

  it("renders suspicious classification correctly", () => {
    const mockSuspiciousResult = {
      classification: "Suspicious",
      risk_score: 0.55,
      language_detected: "english",
      indicators: ["Suspicious security/banking keywords in URL"],
      recommended_action: "Exercise caution. Do not click links or share credentials.",
    };

    render(<ResultCard result={mockSuspiciousResult} onReset={vi.fn()} />);

    expect(screen.getByText("Suspicious")).toBeInTheDocument();
    expect(screen.getByText("Suspicious Content")).toBeInTheDocument();
    expect(screen.getByText("0.55")).toBeInTheDocument();
    expect(screen.getByText("Suspicious security/banking keywords in URL")).toBeInTheDocument();
    expect(screen.getByText("Exercise caution. Do not click links or share credentials.")).toBeInTheDocument();
  });

  it("renders phishing classification and indicators correctly", () => {
    const mockPhishingResult = {
      classification: "Phishing",
      risk_score: 0.88,
      language_detected: "code-mixed",
      indicators: ["High phishing intent detected in message text", "IP address used instead of domain name"],
      recommended_action: "Do not click any links or share sensitive information. Report and delete this message.",
    };

    const handleReset = vi.fn();
    render(<ResultCard result={mockPhishingResult} onReset={handleReset} />);

    expect(screen.getByText("Phishing")).toBeInTheDocument();
    expect(screen.getByText("Phishing Detected")).toBeInTheDocument();
    expect(screen.getByText("0.88")).toBeInTheDocument();
    expect(screen.getByText("High phishing intent detected in message text")).toBeInTheDocument();
    expect(screen.getByText("IP address used instead of domain name")).toBeInTheDocument();
    expect(screen.getByText("Do not click any links or share sensitive information. Report and delete this message.")).toBeInTheDocument();

    const resetBtn = screen.getByRole("button", { name: /Scan Another Message/i });
    fireEvent.click(resetBtn);
    expect(handleReset).toHaveBeenCalledTimes(1);
  });
});
