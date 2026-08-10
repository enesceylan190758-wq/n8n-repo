import { requireAuth } from '../_lib/auth.js';
import { sbConfig } from '../_lib/supabase.js';
import { buildIntegrationConfig } from '../_lib/firm-requirements.js';
import {
  normalizeInstanceName,
  startQrSession,
  pollConnection,
  fetchConnectedPhone,
} from '../_lib/evolution.js';
import { sbRequest } from '../_lib/supabase.js';

const CLINIC_SELECT =
  'id,name,sector,evolution_instance_name,whatsapp_phone,integration_config,slug';

const N8N_CONNECT_URL =
  process.env.N8N_WHATSAPP_CONNECT_URL ||
  'https://api.nefalix.com/webhook/nefalix/whatsapp/connect';

async function loadClinic(clinicId) {
  const rows = await sbRequest('GET', 'clinics', {
    query: `select=${CLINIC_SELECT}&id=eq.${clinicId}&limit=1`,
  });
  return Array.isArray(rows) ? rows[0] : null;
}

function assertClinicAccess(user, clinic) {
  if (!clinic) {
    return { ok: false, status: 404, error: 'Firma bulunamadı' };
  }
  if (user.role === 'admin') return { ok: true };
  if (user.role === 'manager' && user.clinicId === clinic.id) return { ok: true };
  return { ok: false, status: 403, error: 'Bu firma için yetkiniz yok' };
}

function assertClinicIdAccess(user, clinicId) {
  if (user.role === 'admin') return { ok: true };
  if (user.role === 'manager' && user.clinicId === clinicId) return { ok: true };
  return { ok: false, status: 403, error: 'Bu firma için yetkiniz yok' };
}

function resolveInstance(clinic, bodyInstance) {
  const raw = bodyInstance || clinic.evolution_instance_name || clinic.slug;
  return normalizeInstanceName(raw);
}

async function markConnected(clinicId, existingConfig, { phone } = {}) {
  const integration_config = buildIntegrationConfig(
    { integration: { evolution_connected: true } },
    existingConfig || {}
  );
  const body = { integration_config };
  if (phone) body.whatsapp_phone = phone;
  await sbRequest('PATCH', 'clinics', {
    query: `id=eq.${clinicId}`,
    body,
  });
  return { integration_config, whatsapp_phone: phone || null };
}

async function proxyToN8n(body) {
  const apiRes = await fetch(N8N_CONNECT_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await apiRes.json().catch(() => ({}));
  if (!apiRes.ok) {
    const err = new Error(data.message || data.error || `n8n HTTP ${apiRes.status}`);
    err.status = apiRes.status;
    throw err;
  }
  return data?.json ?? data?.[0]?.json ?? data;
}

async function handleDirect(user, body) {
  if (!process.env.EVOLUTION_API_KEY) {
    const err = new Error('WhatsApp QR henüz yapılandırılmamış (EVOLUTION_API_KEY).');
    err.status = 503;
    throw err;
  }

  const clinicId = body.clinicId || body.clinic_id;
  const clinic = await loadClinic(clinicId);
  const access = assertClinicAccess(user, clinic);
  if (!access.ok) {
    const err = new Error(access.error);
    err.status = access.status;
    throw err;
  }

  if ((clinic.sector || 'clinic') !== 'clinic') {
    const err = new Error('WhatsApp QR şu an yalnızca klinik sektöründe');
    err.status = 400;
    throw err;
  }

  const instance = resolveInstance(clinic, body.instanceName || body.instance);
  const action = String(body.action || 'status').toLowerCase();

  if (body.instanceName && body.instanceName !== clinic.evolution_instance_name) {
    await sbRequest('PATCH', 'clinics', {
      query: `id=eq.${clinicId}`,
      body: { evolution_instance_name: instance },
    });
  }

  if (action === 'start' || action === 'refresh') {
    const reset = action === 'refresh' || Boolean(body.reset);
    const result = await startQrSession(instance, { reset });
    let phone = null;
    if (result.connected) {
      phone = await fetchConnectedPhone(instance);
      await markConnected(clinicId, clinic.integration_config, { phone });
    }
    return {
      ok: true,
      instance,
      state: result.state,
      connected: result.connected,
      qr: result.qr,
      whatsappPhone: phone,
      hint: result.connected
        ? phone
          ? `WhatsApp bağlı (${phone}). Kendi numaranızdan mesajlar gidecek.`
          : 'WhatsApp bağlı — Inbox webhook ayarlandı.'
        : 'Kendi telefonunuzda WhatsApp → Bağlı cihazlar → Cihaz bağla → QR okutun (60 sn).',
    };
  }

  if (action === 'status') {
    const result = await pollConnection(instance);
    let phone = null;
    if (result.connected) {
      phone = await fetchConnectedPhone(instance);
      await markConnected(clinicId, clinic.integration_config, { phone });
    }
    return {
      ok: true,
      instance,
      state: result.state,
      connected: result.connected,
      qr: result.qr,
      whatsappPhone: phone,
    };
  }

  const err = new Error('Geçersiz action (start | refresh | status)');
  err.status = 400;
  throw err;
}

export default async function handler(req, res) {
  const user = requireAuth(req, res);
  if (!user) return;

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    const body = req.body || {};
    const clinicId = body.clinicId || body.clinic_id;
    if (!clinicId) {
      res.status(400).json({ error: 'clinicId gerekli' });
      return;
    }

    const access = assertClinicIdAccess(user, clinicId);
    if (!access.ok) {
      res.status(access.status).json({ error: access.error });
      return;
    }

    const useProxy = process.env.N8N_WHATSAPP_CONNECT_URL !== '0' && !sbConfig();
    const result = useProxy
      ? await proxyToN8n(body)
      : await handleDirect(user, body);

    res.status(200).json(result);
  } catch (err) {
    res.status(err.status || 502).json({ error: err.message || 'WhatsApp bağlantı hatası' });
  }
}
