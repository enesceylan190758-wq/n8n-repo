import { requireAuth } from './_lib/auth.js';
import { setupToken, tokenHash } from './_lib/auth.js';
import { sbRequest } from './_lib/supabase.js';
import {
  assessFirmReadiness,
  buildIntegrationConfig,
  slugify,
} from './_lib/firm-requirements.js';

const CLINIC_COLUMNS =
  'id,name,slug,sector,address,email,website_url,booking_url,whatsapp_phone,manager_whatsapp_phone,google_maps_url,google_review_url,google_place_id,logo_url,complaint_form_url,sikayetvar_url,crm_type,evolution_instance_name,automation_enabled,integration_config,created_at';

function pickClinicBody(body) {
  const allowed = [
    'name',
    'sector',
    'slug',
    'address',
    'email',
    'website_url',
    'booking_url',
    'whatsapp_phone',
    'manager_whatsapp_phone',
    'google_maps_url',
    'google_review_url',
    'google_place_id',
    'logo_url',
    'complaint_form_url',
    'sikayetvar_url',
    'crm_type',
    'evolution_instance_name',
  ];
  const row = {};
  for (const k of allowed) {
    if (body[k] !== undefined) row[k] = body[k];
  }
  return row;
}

function publicOrigin(req) {
  const proto = req.headers['x-forwarded-proto'] || 'https';
  const host = req.headers['x-forwarded-host'] || req.headers.host;
  return `${proto}://${host}`;
}

async function ensureDashboardUser(clinic, req) {
  const email = String(clinic?.email || '').trim().toLowerCase();
  if (!email || !clinic?.id) return null;
  const token = setupToken();
  const token_hash = tokenHash(token);
  const expires = new Date(Date.now() + 7 * 24 * 3600000).toISOString();
  const first = String(clinic.name || 'Firma').split(/\s+/)[0] || 'Firma';
  const payload = {
    email,
    role: 'manager',
    clinic_id: clinic.id,
    first_name: first,
    last_name: 'Yöneticisi',
    phone: clinic.manager_whatsapp_phone || clinic.whatsapp_phone || null,
    status: 'pending',
    setup_token_hash: token_hash,
    setup_token_expires_at: expires,
    updated_at: new Date().toISOString(),
  };

  const existing = await sbRequest('GET', 'dashboard_users', {
    query: `email=eq.${encodeURIComponent(email)}&select=id,status&limit=1`,
  }).catch(() => []);
  if (Array.isArray(existing) && existing[0]?.id) {
    await sbRequest('PATCH', 'dashboard_users', {
      query: `id=eq.${existing[0].id}`,
      body: payload,
      prefer: 'return=minimal',
    });
  } else {
    await sbRequest('POST', 'dashboard_users', { body: payload, prefer: 'return=minimal' });
  }

  return `${publicOrigin(req)}/dashboard/setup?token=${encodeURIComponent(token)}`;
}

export default async function handler(req, res) {
  const user = requireAuth(req, res);
  if (!user) return;
  if (user.role !== 'admin') {
    res.status(403).json({ error: 'Sadece sistem yöneticisi firma ekleyebilir.' });
    return;
  }

  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_ROLE_KEY) {
    if (process.env.N8N_SUPABASE_PROXY_URL === '0' || !process.env.NEFALIX_INTERNAL_KEY) {
      res.status(503).json({
        error: 'Firma kaydı için Supabase yapılandırması gerekli (Vercel env).',
      });
      return;
    }
  }

  try {
    if (req.method === 'GET') {
      const rows = await sbRequest('GET', 'clinics', {
        query: `select=${CLINIC_COLUMNS}&order=name.asc`,
      });
      const firms = (rows || []).map((c) => ({
        ...c,
        readiness: assessFirmReadiness(c, c.integration_config || {}),
      }));
      res.status(200).json({ firms });
      return;
    }

    if (req.method === 'POST') {
      const body = req.body || {};
      if (!body.name?.trim()) {
        res.status(400).json({ error: 'Firma adı gerekli.' });
        return;
      }
      const sector = body.sector || 'clinic';
      if (!['clinic', 'hotel', 'auto'].includes(sector)) {
        res.status(400).json({ error: 'Geçersiz sektör.' });
        return;
      }

      const row = pickClinicBody(body);
      row.sector = sector;
      row.slug = (body.slug || slugify(body.name)).trim() || slugify(body.name);
      row.integration_config = buildIntegrationConfig(body, {});
      const readiness = assessFirmReadiness(row, row.integration_config);
      row.automation_enabled = readiness.complete;

      const created = await sbRequest('POST', 'clinics', { body: row });
      const clinic = Array.isArray(created) ? created[0] : created;
      const setupUrl = await ensureDashboardUser(clinic, req);
      res.status(201).json({
        clinic,
        setupUrl,
        readiness: assessFirmReadiness(clinic, clinic.integration_config || {}),
        saved: true,
        warning: readiness.complete
          ? null
          : 'Kayıt oluşturuldu. Eksik alanlar tamamlanınca otomasyon açılacak.',
      });
      return;
    }

    if (req.method === 'PATCH') {
      const { id, ...rest } = req.body || {};
      if (!id) {
        res.status(400).json({ error: 'Firma id gerekli.' });
        return;
      }

      const existingRows = await sbRequest('GET', 'clinics', {
        query: `select=${CLINIC_COLUMNS}&id=eq.${id}&limit=1`,
      });
      const existing = Array.isArray(existingRows) ? existingRows[0] : null;
      if (!existing) {
        res.status(404).json({ error: 'Firma bulunamadı.' });
        return;
      }

      const row = pickClinicBody(rest);
      row.integration_config = buildIntegrationConfig(rest, existing.integration_config || {});
      const merged = { ...existing, ...row };
      const readiness = assessFirmReadiness(merged, row.integration_config);
      row.automation_enabled = readiness.complete;

      const updated = await sbRequest('PATCH', 'clinics', {
        query: `id=eq.${id}`,
        body: row,
      });
      const clinic = Array.isArray(updated) ? updated[0] : { ...merged, ...row };
      const setupUrl = await ensureDashboardUser(clinic, req);
      res.status(200).json({
        clinic,
        setupUrl,
        readiness: assessFirmReadiness(clinic, clinic.integration_config || row.integration_config),
        saved: true,
        warning: readiness.complete
          ? null
          : 'Kayıt güncellendi. Eksik alanlar tamamlanınca otomasyon açılacak.',
      });
      return;
    }

    res.status(405).json({ error: 'Method not allowed' });
  } catch (err) {
    res.status(500).json({ error: err.message || 'Firma kaydı başarısız' });
  }
}
