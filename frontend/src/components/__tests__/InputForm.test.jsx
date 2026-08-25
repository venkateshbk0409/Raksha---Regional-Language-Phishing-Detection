import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import { InputForm } from "../InputForm";

describe("InputForm Component", () => {
  it("renders textarea with placeholder and character counter", () => {
    const handleContentChange = vi.fn();
    const handleSubmit = vi.fn();

    render(
      <InputForm
        content="Test message"
        onContentChange={handleContentChange}
        onSubmit={handleSubmit}
        isLoading={false}
        onClear={vi.fn()}
      />
    );

    const textarea = screen.getByPlaceholderText(/Paste suspicious SMS/i);
    expect(textarea).toBeInTheDocument();
    expect(textarea.value).toBe("Test message");

    // Character counter shows 12 / 2000
    expect(screen.getByText(/12 \/ 2000/)).toBeInTheDocument();
  });

  it("disables submit button when input is empty", () => {
    render(
      <InputForm
        content=""
        onContentChange={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={false}
        onClear={vi.fn()}
      />
    );

    const submitBtn = screen.getByRole("button", { name: /Scan for Phishing/i });
    expect(submitBtn).toBeDisabled();
  });

  it("disables input and shows loading state when isLoading is true", () => {
    render(
      <InputForm
        content="Suspicious text"
        onContentChange={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={true}
        onClear={vi.fn()}
      />
    );

    const textarea = screen.getByPlaceholderText(/Paste suspicious SMS/i);
    expect(textarea).toBeDisabled();

    const loadingBtn = screen.getByRole("button", { name: /Analyzing Content.../i });
    expect(loadingBtn).toBeDisabled();
  });
});
