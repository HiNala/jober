import { describe, expect, it } from "vitest";

import {
  isStreamReconnecting,
  streamStatusLabel,
} from "@/lib/run-stream/stream-status";

describe("streamStatusLabel", () => {
  it("shows Reconnecting when connecting mid-run", () => {
    expect(streamStatusLabel("connecting", { hasEvents: true })).toBe("Reconnecting");
  });

  it("shows Connecting on first connect", () => {
    expect(streamStatusLabel("connecting", { hasEvents: false })).toBe("Connecting");
  });

  it("shows Live when open", () => {
    expect(streamStatusLabel("open")).toBe("Live");
  });
});

describe("isStreamReconnecting", () => {
  it("is true only when connecting with prior events", () => {
    expect(isStreamReconnecting("connecting", 3)).toBe(true);
    expect(isStreamReconnecting("connecting", 0)).toBe(false);
    expect(isStreamReconnecting("open", 3)).toBe(false);
  });
});
