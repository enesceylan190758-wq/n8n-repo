import Stripe from 'stripe';

export function stripeClient() {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error('STRIPE_SECRET_KEY eksik');
  return new Stripe(key, { apiVersion: '2025-05-28.basil' });
}

export const PLAN_PRICE_ENV = {
  standard: 'STRIPE_PRICE_STANDARD',
  professional: 'STRIPE_PRICE_PROFESSIONAL',
};

export function priceForPlan(plan) {
  const envName = PLAN_PRICE_ENV[plan];
  if (!envName) throw new Error('Geçersiz plan');
  const price = process.env[envName];
  if (!price) throw new Error(`${envName} eksik`);
  return price;
}

export function planFromPrice(priceId) {
  for (const [plan, envName] of Object.entries(PLAN_PRICE_ENV)) {
    if (process.env[envName] && process.env[envName] === priceId) return plan;
  }
  return null;
}
