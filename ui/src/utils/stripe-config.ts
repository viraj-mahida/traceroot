/**
 * Utility to check if Stripe is properly configured
 */

export const isStripeConfigured = (): boolean => {
  const stripeMode = process.env.NEXT_PUBLIC_STRIPE_MODE;

  // Check if Stripe mode is set and not empty
  if (!stripeMode || stripeMode.trim() === '' || stripeMode === 'disabled') {
    return false;
  }

  // Optionally check if required Stripe keys are present
  if (stripeMode === 'test') {
    return !!process.env.NEXT_PUBLIC_TEST_STRIPE_PUBLISHABLE_KEY;
  } else if (stripeMode === 'production') {
    return !!process.env.NEXT_PUBLIC_PRODUCTION_STRIPE_PUBLISHABLE_KEY;
  }

  return false;
};

/**
 * Check if any payment features should be shown
 */
export const shouldShowPaymentFeatures = (): boolean => {
  return isStripeConfigured();
};
