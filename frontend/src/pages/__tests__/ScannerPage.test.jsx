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
      risk_score: 0.0,
      language_detected: "english",
      indicators: [],
      recommended_action: "No action required.",
    };

    vi.spyOn(apiService, "analyzeContent").mockResolvedValue(mockApiResponse);

    render(<ScannerPage />);

    const textarea = screen.getByPlaceholderText(/Paste suspicious SMS/i);
    fireEvent.change(textarea, { target: { value: "Hello world" } });

    const submitBtn = screen.getByRole("button", { name: /Scan for Phishing/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText("Safe Content")).toBeInTheDocument();
      expect(screen.getByText("No action required.")).toBeInTheDocument();
    });
  });

  it("handles analysis failure and displays error with retry button", async () => {
    vi.spyOn(apiService, "analyzeContent").mockRejectedValue(new Error("Network connection error"));

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
  });
});
