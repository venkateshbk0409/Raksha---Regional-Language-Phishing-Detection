import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";
import { ScannerPage } from "../ScannerPage";
import * as apiService from "../../services/api";

describe("ScannerPage Integration", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("handles successful analysis flow and displays result", async () => {
    const mockApiResponse = {
      classification: "Safe",
      risk_score: 0.05,
      language_detected: "english",
      indicators: [],
      recommended_action: "No immediate threat detected. Standard vigilance advised.",
    };

    vi.spyOn(apiService, "analyzeContent").mockResolvedValue(mockApiResponse);

    render(<ScannerPage />);

    const textarea = screen.getByPlaceholderText(/Paste suspicious SMS/i);
    fireEvent.change(textarea, { target: { value: "Hello world" } });

    const submitBtn = screen.getByRole("button", { name: /Scan for Phishing/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText("Safe Content")).toBeInTheDocument();
      expect(screen.getByText("No immediate threat detected. Standard vigilance advised.")).toBeInTheDocument();
    });

    // Test resetting
    const resetBtn = screen.getByRole("button", { name: /Scan Another Message/i });
    fireEvent.click(resetBtn);

    expect(screen.queryByText("Safe Content")).not.toBeInTheDocument();
  });

  it("handles analysis failure and displays error with retry button", async () => {
    const mockAnalyze = vi.spyOn(apiService, "analyzeContent").mockRejectedValue(new Error("Network connection error"));

    render(<ScannerPage />);

    const textarea = screen.getByPlaceholderText(/Paste suspicious SMS/i);
    fireEvent.change(textarea, { target: { value: "Suspicious message" } });

    const submitBtn = screen.getByRole("button", { name: /Scan for Phishing/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText("Analysis Request Failed")).toBeInTheDocument();
      expect(screen.getByText("Network connection error")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /Try Again/i })).toBeInTheDocument();
    });

    // Test Retry
    mockAnalyze.mockResolvedValueOnce({
      classification: "Suspicious",
      risk_score: 0.60,
      language_detected: "kannada",
      indicators: ["Suspicious linguistic patterns detected in message"],
      recommended_action: "Exercise caution. Do not click links or share credentials.",
    });

    const retryBtn = screen.getByRole("button", { name: /Try Again/i });
    fireEvent.click(retryBtn);

    await waitFor(() => {
      expect(screen.getByText("Suspicious Content")).toBeInTheDocument();
    });
  });

  it("populates sample prompt when sample chip is clicked", () => {
    render(<ScannerPage />);

    const kannadaChip = screen.getByRole("button", { name: /Kannada Phishing/i });
    fireEvent.click(kannadaChip);

    const textarea = screen.getByPlaceholderText(/Paste suspicious SMS/i);
    expect(textarea.value).toContain("ಪ್ರಿಯ ಗ್ರಾಹಕರೇ");
  });

  it("automatically smooth-scrolls to the result card upon successful scan", async () => {
    const mockApiResponse = {
      classification: "Phishing",
      risk_score: 0.90,
      language_detected: "kannada",
      indicators: ["IP address host detected"],
      recommended_action: "Do not click any links or share sensitive information. Report and delete this message.",
    };

    vi.spyOn(apiService, "analyzeContent").mockResolvedValue(mockApiResponse);

    const scrollIntoViewMock = vi.fn();
    window.HTMLElement.prototype.scrollIntoView = scrollIntoViewMock;

    render(<ScannerPage />);

    const textarea = screen.getByPlaceholderText(/Paste suspicious SMS/i);
    fireEvent.change(textarea, { target: { value: "http://192.168.1.1/login" } });

    const submitBtn = screen.getByRole("button", { name: /Scan for Phishing/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText("Phishing Threat Detected")).toBeInTheDocument();
      expect(scrollIntoViewMock).toHaveBeenCalled();
    });
  });
});
