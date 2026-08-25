import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";
import { ResultCard } from "../ResultCard";

describe("ResultCard Component", () => {
  beforeEach(() => {
    // Mock navigator.clipboard
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  it("renders safe classification details correctly with gauge and action", () => {
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
    expect(screen.getByText(/Native Kannada/i)).toBeInTheDocument();
    expect(screen.getByText("Safe Zone (< 0.40)")).toBeInTheDocument();
    expect(screen.getByText("No immediate threat detected. Standard vigilance advised.")).toBeInTheDocument();
    expect(screen.getByText(/No malicious lexical patterns/i)).toBeInTheDocument();
  });

  it("renders suspicious classification and allows copying advice", async () => {
    const mockSuspiciousResult = {
      classification: "Suspicious",
      risk_score: 0.55,
      language_detected: "english",
      indicators: ["Suspicious TLD detected"],
      recommended_action: "Exercise caution. Do not click links or share credentials.",
    };

    render(<ResultCard result={mockSuspiciousResult} onReset={vi.fn()} />);

    expect(screen.getByText("Suspicious")).toBeInTheDocument();
    expect(screen.getByText("Suspicious Content")).toBeInTheDocument();
    expect(screen.getByText("0.55")).toBeInTheDocument();
    expect(screen.getByText("Suspicious Zone (0.40 - 0.74)")).toBeInTheDocument();
    expect(screen.getByText("Suspicious TLD detected")).toBeInTheDocument();
    expect(screen.getByText("Exercise caution. Do not click links or share credentials.")).toBeInTheDocument();

    // Test Copy Advice button
    const copyBtn = screen.getByRole("button", { name: /Copy Advice/i });
    fireEvent.click(copyBtn);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockSuspiciousResult.recommended_action);

    await waitFor(() => {
      expect(screen.getByText("Copied!")).toBeInTheDocument();
    });
  });

  it("renders phishing threat classification, indicators, and tooltip on interaction", async () => {
    const mockPhishingResult = {
      classification: "Phishing",
      risk_score: 0.88,
      language_detected: "code-mixed",
      indicators: ["IP address host detected", "Urgent call-to-action detected"],
      recommended_action: "Do not click any links or share sensitive information. Report and delete this message.",
    };

    const handleReset = vi.fn();
    render(<ResultCard result={mockPhishingResult} onReset={handleReset} />);

    expect(screen.getByText("Phishing")).toBeInTheDocument();
    expect(screen.getByText("Phishing Threat Detected")).toBeInTheDocument();
    expect(screen.getByText("0.88")).toBeInTheDocument();
    expect(screen.getByText("High-Risk Phishing Zone (≥ 0.75)")).toBeInTheDocument();
    expect(screen.getByText("IP address host detected")).toBeInTheDocument();
    expect(screen.getByText("Urgent call-to-action detected")).toBeInTheDocument();

    // Interact with indicator badge to display explainability tooltip
    const indicatorBtn = screen.getByRole("button", { name: /Indicator: IP address host detected/i });
    fireEvent.mouseEnter(indicatorBtn);

    await waitFor(() => {
      expect(screen.getByText("Threat Explanation")).toBeInTheDocument();
      expect(screen.getByText(/numeric IP address rather than a registered domain/i)).toBeInTheDocument();
    });

    // Test Reset
    const resetBtn = screen.getByRole("button", { name: /Scan Another Message/i });
    fireEvent.click(resetBtn);
    expect(handleReset).toHaveBeenCalledTimes(1);
  });
});
