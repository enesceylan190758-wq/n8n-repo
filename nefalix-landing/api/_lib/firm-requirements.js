/** Firma onboarding gereksinimleri — panel ve API ortak mantık */

export const FIRM_FIELD_LABELS = {
  name: 'Firma adı',
  sector: 'Sektör',
  address: 'Adres',
  email: 'E-posta',
  website_url: 'Web sitesi',
  booking_url: 'Randevu / rezervasyon linki',
  whatsapp_phone: 'WhatsApp iş hattı',
  manager_whatsapp_phone: 'Yönetici WhatsApp (alarm)',
  google_maps_url: 'Google Haritalar linki',
  google_review_url: 'Google yorum linki',
  google_place_id: 'Google Place ID',
  crm_type: 'CRM / HBYS türü',
  evolution_instance_name: 'Evolution WhatsApp instance adı',
  logo_url: 'Logo URL',
  complaint_form_url: 'Şikayet formu linki',
  sikayetvar_url: 'Şikayetvar profili',
};

export const INTEGRATION_LABELS = {
  crm_api_key: 'CRM API anahtarı',
  crm_webhook_configured: 'CRM tamamlanma webhook’u kuruldu',
  evolution_connected: 'WhatsApp (Evolution) bağlı',
  pms_webhook_configured: 'PMS / rezervasyon webhook’u',
  manual_trigger_ok: 'Manuel NPS tetikleme kabul (pilot)',
  appointment_webhook_configured: 'Servis tamamlanma webhook’u',
};

const BASE_FIELDS = [
  'name',
  'sector',
  'address',
  'email',
  'website_url',
  'whatsapp_phone',
  'manager_whatsapp_phone',
  'google_maps_url',
  'google_review_url',
];

const SECTOR_FIELDS = {
  clinic: ['booking_url', 'crm_type', 'evolution_instance_name', 'google_place_id'],
  hotel: ['booking_url'],
  auto: ['booking_url'],
};

const SECTOR_INTEGRATION = {
  clinic: ['crm_api_key', 'crm_webhook_configured', 'evolution_connected'],
  hotel: ['pms_webhook_configured'], // veya manual_trigger_ok
  auto: ['appointment_webhook_configured'],
};

function filled(v) {
  return v != null && String(v).trim() !== '';
}

export function slugify(name) {
  return String(name || '')
    .toLowerCase()
    .replace(/[ıİ]/g, 'i')
    .replace(/[ğĞ]/g, 'g')
    .replace(/[üÜ]/g, 'u')
    .replace(/[şŞ]/g, 's')
    .replace(/[öÖ]/g, 'o')
    .replace(/[çÇ]/g, 'c')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 48);
}

export function assessFirmReadiness(clinic, integrationConfig = {}) {
  const cfg = integrationConfig || {};
  const sector = clinic.sector || 'clinic';
  const missing = [];

  for (const f of BASE_FIELDS) {
    if (!filled(clinic[f])) missing.push(f);
  }
  for (const f of SECTOR_FIELDS[sector] || []) {
    if (!filled(clinic[f])) missing.push(f);
  }

  if (sector === 'clinic') {
    if (!filled(cfg.crm_api_key)) missing.push('crm_api_key');
    if (!cfg.crm_webhook_configured) missing.push('crm_webhook_configured');
    if (!cfg.evolution_connected) missing.push('evolution_connected');
  } else if (sector === 'hotel') {
    if (!cfg.pms_webhook_configured && !cfg.manual_trigger_ok) missing.push('pms_webhook_configured');
  } else if (sector === 'auto') {
    if (!cfg.appointment_webhook_configured && !cfg.manual_trigger_ok) missing.push('appointment_webhook_configured');
  }

  const total =
    BASE_FIELDS.length +
    (SECTOR_FIELDS[sector]?.length || 0) +
    (SECTOR_INTEGRATION[sector]?.length || 0);
  const done = total - missing.length;

  return {
    complete: missing.length === 0,
    missing,
    progress: total ? Math.round((done / total) * 100) : 0,
    total,
    done,
  };
}

export function buildIntegrationConfig(body, existing = {}) {
  const cfg = { ...existing };
  const secrets = body.integration || {};
  if (secrets.crm_api_key) cfg.crm_api_key = secrets.crm_api_key;
  if (typeof secrets.crm_webhook_configured === 'boolean') {
    cfg.crm_webhook_configured = secrets.crm_webhook_configured;
  }
  if (typeof secrets.evolution_connected === 'boolean') {
    cfg.evolution_connected = secrets.evolution_connected;
  }
  if (typeof secrets.pms_webhook_configured === 'boolean') {
    cfg.pms_webhook_configured = secrets.pms_webhook_configured;
  }
  if (typeof secrets.appointment_webhook_configured === 'boolean') {
    cfg.appointment_webhook_configured = secrets.appointment_webhook_configured;
  }
  if (typeof secrets.manual_trigger_ok === 'boolean') {
    cfg.manual_trigger_ok = secrets.manual_trigger_ok;
  }
  if (secrets.notes) cfg.notes = secrets.notes;
  return cfg;
}
