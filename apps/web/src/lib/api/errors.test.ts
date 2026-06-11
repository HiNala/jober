import { describe, expect, it } from "vitest";

import { ApiError } from "@/lib/api/client";
import { formatApiError } from "@/lib/api/errors";

describe("formatApiError", () => {
  it("uses pydantic field messages from 422 bodies", () => {
    const body = JSON.stringify({
      detail: [{ loc: ["body", "api_key"], msg: "String should have at least 8 characters" }],
    });
    const message = formatApiError(new ApiError("API 422", 422, body), "Could not save API key");
    expect(message).toContain("8 characters");
  });

  it("uses caller fallback when body is empty", () => {
    expect(formatApiError(new ApiError("API 422", 422), "Cover letter generation failed")).toBe(
      "Cover letter generation failed",
    );
  });

  it("maps 402 budget errors", () => {
    expect(formatApiError(new ApiError("API 402", 402), "fallback")).toContain("budget");
  });
});
