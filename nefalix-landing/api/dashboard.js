import { requireAuth } from './_lib/auth.js';
import { sbRequest } from './_lib/supabase.js';

const DAYS_30_MS = 30 * 24 * 60 * 60 * 1000;

function avgScore(rows) {
  const scores = (rows || []).map((r) => Number(r.score)).filter((n) => Number.isFinite(n));
  if (!scores.length) return null;
  return Number((scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1));
}

function npsSurveyLog(row) {
  const source = String(row.source_workflow || '').toLowerCase();
  const preview = String(row.message_preview || '');
  return (
    source === 'nps-outbound' ||
    source === 'inbox-send' && /1\s*[-–]\s*10|puan|değerlendir|memnuniyet/i.test(preview)
  );
}

function scopeBody(user, body) {
  if (user.role === 'admin' || !user.clinicId) return body;
  const clinicId = user.clinicId;
  const filter = (rows) => (Array.isArray(rows) ? rows.filter((r) => r.clinic_id === clinicId || r.id === clinicId) : []);
  return {
    ...body,
    clinics: filter(body.clinics),
    nps: filter(body.nps),
    reviews: filter(body.reviews),
    enps: filter(body.enps),
    mentions: filter(body.mentions),
    recall: filter(body.recall),
    inbox: filter(body.inbox),
  };
}

async function buildMetrics(user, body) {
  const clinicId = user.role === 'admin' ? null : user.clinicId;
  const sinceIso = new Date(Date.now() - DAYS_30_MS).toISOString();
  const clinicFilter = clinicId ? `&clinic_id=eq.${clinicId}` : '';

  const [logs, nps, reviews] = await Promise.all([
    sbRequest('GET', 'whatsapp_send_log', {
      query: `select=clinic_id,source_workflow,message_preview,status,created_at&status=eq.sent&created_at=gte.${encodeURIComponent(sinceIso)}${clinicFilter}&limit=1000`,
    }).catch(() => []),
    sbRequest('GET', 'nps_responses', {
      query: `select=clinic_id,score,created_at&created_at=gte.${encodeURIComponent(sinceIso)}${clinicFilter}&limit=1000`,
    }).catch(() => (body.nps || []).filter((r) => new Date(r.created_at).getTime() >= Date.now() - DAYS_30_MS)),
    sbRequest('GET', 'google_reviews', {
      query: `select=clinic_id,created_at&created_at=gte.${encodeURIComponent(sinceIso)}${clinicFilter}&limit=1000`,
    }).catch(() => (body.reviews || []).filter((r) => new Date(r.created_at).getTime() >= Date.now() - DAYS_30_MS)),
  ]);

  return {
    periodDays: 30,
    surveysSent30d: (logs || []).filter(npsSurveyLog).length,
    avgNps30d: avgScore(nps || []),
    googleReviews30d: (reviews || []).length,
  };
}

async function buildBilling(user) {
  const clinicId = user.role === 'admin' ? null : user.clinicId;
  if (!clinicId) return null;
  const rows = await sbRequest('GET', 'clinics', {
    query: `id=eq.${clinicId}&select=id,plan_tier,subscription_status,stripe_customer_id,stripe_subscription_id,subscription_current_period_end&limit=1`,
  }).catch(() => []);
  return Array.isArray(rows) ? rows[0] || null : null;
}

/** Vercel proxy — nefalix.com/dashboard → n8n Dashboard API (tunnel) */
export default async function handler(req, res) {
  const user = requireAuth(req, res);
  if (!user) return;

  res.setHeader('Cache-Control', 'no-store');

  const upstream = process.env.N8N_DASHBOARD_URL;
  if (!upstream) {
    res.status(503).json({
      error:
        'Dashboard API bağlı değil. Mac + n8n + cloudflared tunnel çalışıyor olmalı.',
    });
    return;
  }

  try {
    const apiRes = await fetch(upstream, { headers: { Accept: 'application/json' } });
    const text = await apiRes.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      res.status(502).json({
        error: 'Geçersiz JSON yanıtı — VPS API veya oturum sorunu olabilir.',
        detail: text.slice(0, 300),
        hint: upstream.includes('/dashboard') && !upstream.includes('/dashboard/data')
          ? 'N8N_DASHBOARD_URL sonu /webhook/nefalix/dashboard/data olmalı'
          : undefined,
      });
      return;
    }

    if (!apiRes.ok) {
      res.status(apiRes.status).json(data);
      return;
    }

    const body = scopeBody(user, data?.clinics ? data : data?.json ?? data?.[0]?.json ?? data);
    const [metrics, billing] = await Promise.all([
      buildMetrics(user, body),
      buildBilling(user),
    ]);
    res.status(200).json({ ...body, metrics, billing });
  } catch (err) {
    res.status(502).json({
      error: 'Mac üzerindeki n8n/Supabase erişilemiyor.',
      detail: err.message,
    });
  }
}
