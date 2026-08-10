import { createHmac, timingSafeEqual } from 'crypto';
import { requireAuth } from './_lib/auth.js';
import { sbRequest } from './_lib/supabase.js';
import { planFromPrice, priceForPlan, stripeClient } from './_lib/stripe.js';

export const config = {
  api: {
    bodyParser: false,
  },
};

async function readRawBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(Buffer.from(chunk));
  return Buffer.concat(chunks);
}

function origin(req) {
  const proto = req.headers['x-forwarded-proto'] || 'https';
  const host = req.headers['x-forwarded-host'] || req.headers.host;
  return `${proto}://${host}`;
}

async function readJson(req) {
  const raw = await readRawBody(req);
  if (!raw.length) return {};
  return JSON.parse(raw.toString('utf8'));
}

function readForm(raw) {
  return Object.fromEntries(new URLSearchParams(raw.toString('utf8')).entries());
}

function getUserIp(req) {
  const forwarded = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  return forwarded || req.socket?.remoteAddress || '127.0.0.1';
}

const PUBLIC_PLAN_MAP = {
  standard: {
    packageKey: 'starter',
    label: 'NefalixAI Başlangıç Paketi',
    baseMonthly: 9500,
  },
  professional: {
    packageKey: 'pro',
    label: 'NefalixAI Profesyonel Paket',
    baseMonthly: 14900,
  },
};

const SECTOR_MULT = { health: 1, hotel: 0.92, auto: 0.88 };
const STAFF_MULT = { '1-5': 1, '6-15': 1.12, '16-30': 1.28, '30+': 1.45 };
const PREMIUM_ADD = { sentinel: 3500, recall: 2500 };

function normalizeBool(value) {
  return value === true || value === 'true' || value === 1 || value === '1';
}

function normalizePricing(body = {}) {
  const sector = ['health', 'hotel', 'auto'].includes(body.sector) ? body.sector : 'health';
  const staff = ['1-5', '6-15', '16-30', '30+'].includes(body.staff) ? body.staff : '1-5';
  const branches = Math.min(20, Math.max(1, Number.parseInt(body.branches, 10) || 1));
  const modules = {
    feedback: normalizeBool(body.modules?.feedback ?? true),
    inbox: normalizeBool(body.modules?.inbox ?? true),
    reviews: normalizeBool(body.modules?.reviews ?? true),
    enps: normalizeBool(body.modules?.enps ?? true),
    sentinel: normalizeBool(body.modules?.sentinel),
    recall: normalizeBool(body.modules?.recall),
  };
  return { sector, staff, branches, modules };
}

function calcPublicAmount(plan, pricing) {
  const meta = PUBLIC_PLAN_MAP[plan];
  if (!meta) throw new Error('Geçersiz plan');

  let amount = meta.baseMonthly * (SECTOR_MULT[pricing.sector] || 1) * (STAFF_MULT[pricing.staff] || 1);
  if (pricing.branches > 1) amount *= 1 + (pricing.branches - 1) * 0.18;
  if (meta.packageKey !== 'starter') {
    if (pricing.modules.sentinel) amount += PREMIUM_ADD.sentinel;
    if (pricing.modules.recall) amount += PREMIUM_ADD.recall;
  }
  return Math.round(amount);
}

function requirePublicCustomer(customer = {}) {
  const fullName = String(customer.fullName || '').trim();
  const email = String(customer.email || '').trim().toLowerCase();
  const phone = String(customer.phone || '').trim();
  const address = String(customer.address || '').trim();
  const company = String(customer.company || '').trim();
  if (!fullName || fullName.length < 3) throw new Error('Ad soyad gerekli');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new Error('Geçerli bir e-posta girin');
  if (phone.replace(/\D/g, '').length < 10) throw new Error('Geçerli bir telefon girin');
  if (address.length < 6) throw new Error('Fatura adresi gerekli');
  return { fullName, email, phone, address, company };
}

function paytrConfig() {
  const merchantId = process.env.PAYTR_MERCHANT_ID || '';
  const merchantKey = process.env.PAYTR_MERCHANT_KEY || '';
  const merchantSalt = process.env.PAYTR_MERCHANT_SALT || '';
  if (!merchantId || !merchantKey || !merchantSalt) {
    throw new Error('PAYTR_MERCHANT_ID / PAYTR_MERCHANT_KEY / PAYTR_MERCHANT_SALT eksik');
  }
  return {
    merchantId,
    merchantKey,
    merchantSalt,
    testMode: process.env.PAYTR_TEST_MODE === '1' ? '1' : '0',
    debugOn: process.env.PAYTR_DEBUG === '0' ? '0' : '1',
  };
}

function paytrToken(cfg, values) {
  const hashStr =
    `${cfg.merchantId}${values.user_ip}${values.merchant_oid}${values.email}` +
    `${values.payment_amount}${values.user_basket}${values.no_installment}` +
    `${values.max_installment}${values.currency}${values.test_mode}`;
  return createHmac('sha256', cfg.merchantKey)
    .update(`${hashStr}${cfg.merchantSalt}`)
    .digest('base64');
}

async function startPaytrIframe(req, payload) {
  const cfg = paytrConfig();
  const res = await fetch('https://www.paytr.com/odeme/api/get-token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      ...payload,
      merchant_id: cfg.merchantId,
      test_mode: cfg.testMode,
      debug_on: cfg.debugOn,
      paytr_token: paytrToken(cfg, { ...payload, test_mode: cfg.testMode }),
    }),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.status !== 'success' || !data.token) {
    throw new Error(data.reason || data.err_msg || 'PayTR ödeme oturumu başlatılamadı');
  }
  return `https://www.paytr.com/odeme/guvenli/${data.token}`;
}

async function handlePaytrCallback(req, res) {
  const cfg = paytrConfig();
  const raw = await readRawBody(req);
  const body = readForm(raw);
  const hash = createHmac('sha256', cfg.merchantKey)
    .update(`${body.merchant_oid || ''}${cfg.merchantSalt}${body.status || ''}${body.total_amount || ''}`)
    .digest('base64');
  const incoming = Buffer.from(String(body.hash || ''));
  const expected = Buffer.from(hash);
  if (!incoming.length || incoming.length !== expected.length || !timingSafeEqual(incoming, expected)) {
    return res.status(400).send('PAYTR notification failed: bad hash');
  }
  return res.status(200).send('OK');
}

async function markEvent(event) {
  try {
    await sbRequest('POST', 'stripe_webhook_events', {
      body: { event_id: event.id, event_type: event.type },
      prefer: 'return=minimal',
    });
    return true;
  } catch (err) {
    if (String(err.message || '').includes('duplicate')) return false;
    throw err;
  }
}

async function syncSubscription(stripe, subscriptionId, fallback = {}) {
  const sub = typeof subscriptionId === 'string'
    ? await stripe.subscriptions.retrieve(subscriptionId)
    : subscriptionId;
  const clinicId = sub.metadata?.clinic_id || fallback.clinic_id;
  if (!clinicId) return;
  const priceId = sub.items?.data?.[0]?.price?.id || null;
  const plan = sub.metadata?.plan || planFromPrice(priceId) || fallback.plan || null;
  await sbRequest('PATCH', 'clinics', {
    query: `id=eq.${encodeURIComponent(clinicId)}`,
    body: {
      stripe_customer_id: typeof sub.customer === 'string' ? sub.customer : sub.customer?.id,
      stripe_subscription_id: sub.id,
      plan_tier: plan,
      subscription_status: sub.status || 'none',
      subscription_current_period_end: sub.current_period_end ? new Date(sub.current_period_end * 1000).toISOString() : null,
    },
    prefer: 'return=minimal',
  });
}

async function handleWebhook(req, res) {
  const stripe = stripeClient();
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!secret) return res.status(500).send('STRIPE_WEBHOOK_SECRET eksik');
  let event;
  try {
    const raw = await readRawBody(req);
    event = stripe.webhooks.constructEvent(raw, req.headers['stripe-signature'], secret);
  } catch (err) {
    return res.status(400).send(`Webhook imza hatası: ${err.message}`);
  }
  const first = await markEvent(event);
  if (!first) return res.status(200).json({ received: true, duplicate: true });
  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    if (session.subscription) await syncSubscription(stripe, session.subscription, session.metadata || {});
  } else if (event.type === 'customer.subscription.updated' || event.type === 'customer.subscription.deleted') {
    await syncSubscription(stripe, event.data.object);
  }
  return res.status(200).json({ received: true });
}

async function handlePublicCheckout(req, res, body) {
  const plan = String(body.plan || '').trim();
  const pricing = normalizePricing(body);
  const customer = requirePublicCustomer(body.customer);
  const amountTl = calcPublicAmount(plan, pricing);
  const merchantOid = `nfx-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  const userBasket = Buffer.from(JSON.stringify([
    [PUBLIC_PLAN_MAP[plan].label, amountTl.toFixed(2), 1],
  ])).toString('base64');

  const url = await startPaytrIframe(req, {
    user_ip: getUserIp(req),
    merchant_oid: merchantOid,
    email: customer.email,
    payment_amount: String(amountTl * 100),
    currency: 'TL',
    user_basket: userBasket,
    no_installment: '0',
    max_installment: '0',
    user_name: customer.fullName,
    user_address: customer.address,
    user_phone: customer.phone,
    merchant_ok_url: process.env.PAYTR_OK_URL || `${origin(req)}/fiyatlar?payment=success`,
    merchant_fail_url: process.env.PAYTR_FAIL_URL || `${origin(req)}/fiyatlar?payment=failed`,
    timeout_limit: '30',
    lang: 'tr',
  });

  return res.status(200).json({
    ok: true,
    url,
    provider: 'paytr',
    amountTl,
    note: customer.company || null,
  });
}

async function handleDashboardCheckout(req, res, body) {
  const user = requireAuth(req, res);
  if (!user) return null;
  const plan = String(body.plan || '').trim();
  const clinicId = user.role === 'admin' ? body.clinicId : user.clinicId;
  if (!clinicId) return res.status(400).json({ error: 'Ödeme için firma seçin' });
  const rows = await sbRequest('GET', 'clinics', {
    query: `id=eq.${encodeURIComponent(clinicId)}&select=id,name,email,sector,slug,stripe_customer_id&limit=1`,
  });
  const clinic = Array.isArray(rows) ? rows[0] : null;
  if (!clinic) return res.status(404).json({ error: 'Firma bulunamadı' });
  const metadata = {
    clinic_id: clinic.id,
    clinic_name: clinic.name || '',
    plan,
    sector: clinic.sector || 'clinic',
    initiated_by: user.email || '',
  };
  const session = await stripeClient().checkout.sessions.create({
    mode: 'subscription',
    customer: clinic.stripe_customer_id || undefined,
    customer_email: clinic.stripe_customer_id ? undefined : clinic.email || user.email,
    line_items: [{ price: priceForPlan(plan), quantity: 1 }],
    allow_promotion_codes: true,
    client_reference_id: clinic.id,
    metadata,
    subscription_data: { metadata },
    success_url: process.env.STRIPE_SUCCESS_URL || `${origin(req)}/dashboard#billing`,
    cancel_url: process.env.STRIPE_CANCEL_URL || `${origin(req)}/dashboard#billing`,
  });
  return res.status(200).json({ ok: true, url: session.url });
}

export default async function handler(req, res) {
  const action = String(req.query?.action || '').trim();
  try {
    if (action === 'webhook') return await handleWebhook(req, res);
    if (action === 'paytr-callback') return await handlePaytrCallback(req, res);
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
    const body = await readJson(req);
    if (action === 'checkout-public') return await handlePublicCheckout(req, res, body);
    if (action === 'checkout') return await handleDashboardCheckout(req, res, body);
    return res.status(400).json({ error: 'Geçersiz billing işlemi' });
  } catch (err) {
    return res.status(500).json({ error: err.message || 'Billing işlemi başarısız' });
  }
}
