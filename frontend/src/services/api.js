/**
 * API Service for interacting with Raksha Backend
 */

import { MAX_CONTENT_LENGTH } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_URL || "";

/**
 * Analyzes text or URL for regional phishing signals.
 * @param {string} content - Input string (1-2000 chars)
 * @returns {Promise<{ classification: string, risk_score: number, language_detected: string, indicators: string[], recommended_action: string }>}
 */
export async function analyzeContent(content) {
  if (!content || !content.trim()) {
    throw new Error("Please enter text or a URL to analyze.");
  }

  if (content.length > MAX_CONTENT_LENGTH) {
    throw new Error(`Content exceeds maximum allowed length of ${MAX_CONTENT_LENGTH} characters.`);
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content }),
  });

  const data = await response.json();

  if (!response.ok) {
    const errorMessage = data?.message || "Failed to analyze message. Please try again.";
    const error = new Error(errorMessage);
    error.status = response.status;
    error.error_type = data?.error_type || "api_error";
    throw error;
  }

  return data;
}
