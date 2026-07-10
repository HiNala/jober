import { afterEach, describe, expect, it } from "vitest";

import { isStripeEnabled } from "./stripe-enabled";

describe("isStripeEnabled", () => {
  const original = process.env.NEXT_PUBLIC_STRIPE_ENABLED;

  afterEach(() => {
    if (original === undefined) delete process.env.NEXT_PUBLIC_STRIPE_ENABLED;
    else process.env.NEXT_PUBLIC_STRIPE_ENABLED = original;
  });

  it("is false by default", () => {
    delete process.env.NEXT_PUBLIC_STRIPE_ENABLED;
    expect(isStripeEnabled()).toBe(false);
  });

  it("is true only when env is exactly true", () => {
    process.env.NEXT_PUBLIC_STRIPE_ENABLED = "true";
    expect(isStripeEnabled()).toBe(true);
    process.env.NEXT_PUBLIC_STRIPE_ENABLED = "1";
    expect(isStripeEnabled()).toBe(false);
  });
});
