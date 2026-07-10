/** Build-time flag — set true when Stripe Checkout is live for this deploy. */
export function isStripeEnabled(): boolean {
  return process.env.NEXT_PUBLIC_STRIPE_ENABLED === "true";
}
