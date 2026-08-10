/**
 * Public firma başvurusu + admin kuyruk.
 * POST  — public (hesap açılmaz, durum=yeni)
 * GET   — admin: bekleyen (yeni|iletisimde)
 * PATCH — admin: durum güncelle (Kurulumu tamamla → tamamlandi)
 *
 * Opsiyonel: N8N_FIRMA_BASVURU_WEBHOOK → Slack/WA bildirimi forward
 */
import { requireAuth } from './auth.js';
import { sbRequest } from './supabase.js';

const PLANS = new Set(['standart', 'profesyonel']);
const DURUMLAR = new Set(['yeni', 'iletisimde', 'tamamlandi']);
const SECTORS = new Set([
  'Diş Kliniği',
  'Saç Ekimi Kliniği',
  'Estetik Klinik',
  'Otel',
  'Oto Servis',
  'Diğer',
]);

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PATCH,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function trimStr(v, max = 200) {
  return String(v ?? '')
    .trim()
    .slice(0, max);
}

function normalizePlan(p) {
  const s = String(p || '')
    .trim()
    .toLowerCase();
  if (s === 'standard' || s === 'standart') return 'standart';
  if (s === 'professional' || s === 'profesyonel' || s === 'pro') return 'profesyonel';
  return '';
}

async function forwardN8n(payload) {
  const url = (process.env.N8N_FIRMA_BASVURU_WEBHOOK || '').trim();
  if (!url) return;
  try {
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    console.warn('[firma-basvuru] n8n forward failed', err?.message || err);
  }
}

function relativeTimeTr(iso) {
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return '';
  const diff = Date.now() - t;
  const m = Math.floor(diff / 60000);
  if (m < 60) return `${Math.max(1, m)} dk önce`;
  const h = Math.floor(m / 60);
  if (h < 48) return `${h} saat önce`;
  const d = Math.floor(h / 24);
  return `${d} gün önce`;
}

export default async function handler(req, res) {
  cors(res);
  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }

  try {
    if (req.method === 'POST') {
      const body = req.body || {};
      const firma_adi = trimStr(body.firmaAdi || body.firma_adi, 160);
      const sektor = trimStr(body.sektor, 80) || 'Diş Kliniği';
      const sehir = trimStr(body.sehir, 120);
      const yetkili_adi = trimStr(body.yetkiliAdi || body.yetkili_adi, 120);
      const telefon = trimStr(body.telefon, 40);
      const eposta = trimStr(body.eposta || body.email, 160).toLowerCase();
      const website = trimStr(body.website, 200);
      const plan = normalizePlan(body.plan);

      if (!firma_adi) {
        res.status(400).json({ error: 'Firma adı gerekli.' });
        return;
      }
      if (!telefon && !eposta) {
        res.status(400).json({ error: 'Telefon veya e-posta gerekli.' });
        return;
      }
      if (!plan || !PLANS.has(plan)) {
        res.status(400).json({ error: 'Geçerli paket seçin (standart / profesyonel).' });
        return;
      }
      if (sektor && !SECTORS.has(sektor) && sektor.length < 2) {
        res.status(400).json({ error: 'Geçersiz sektör.' });
        return;
      }

      const row = {
        firma_adi,
        sektor,
        sehir: sehir || null,
        yetkili_adi: yetkili_adi || null,
        telefon: telefon || null,
        eposta: eposta || null,
        website: website || null,
        plan,
        durum: 'yeni',
        updated_at: new Date().toISOString(),
      };

      let created;
      try {
        created = await sbRequest('POST', 'firma_basvurulari', {
          body: row,
          prefer: 'return=representation',
        });
      } catch (err) {
        console.error('[firma-basvuru] insert', err);
        res.status(503).json({
          error:
            'Başvuru kaydı şu an alınamadı. Lütfen biraz sonra tekrar deneyin veya iletisim@nefalix.com yazın.',
        });
        return;
      }

      const record = Array.isArray(created) ? created[0] : created;
      await forwardN8n({
        event: 'firma_basvuru',
        ...row,
        id: record?.id,
        created_at: record?.created_at,
      });

      res.status(201).json({
        ok: true,
        message: 'Başvurunuz alındı. 24 saat içinde sizinle iletişime geçeceğiz.',
        id: record?.id || null,
      });
      return;
    }

    if (req.method === 'GET') {
      const user = requireAuth(req, res);
      if (!user) return;
      if (user.role !== 'admin') {
        res.status(403).json({ error: 'Sadece yönetici başvuruları görebilir.' });
        return;
      }

      let rows = [];
      try {
        rows = await sbRequest('GET', 'firma_basvurulari', {
          query:
            'durum=in.(yeni,iletisimde)&select=*&order=created_at.desc&limit=100',
        });
      } catch (err) {
        console.warn('[firma-basvuru] list', err?.message || err);
        rows = [];
      }

      const applications = (Array.isArray(rows) ? rows : []).map((r) => ({
        id: r.id,
        firma: r.firma_adi,
        sektor: r.sektor,
        sehir: r.sehir || '',
        yetkili: r.yetkili_adi || '',
        telefon: r.telefon || '',
        eposta: r.eposta || '',
        website: r.website || '',
        plan: r.plan === 'standart' ? 'Standart' : 'Profesyonel',
        planId: r.plan,
        durum: r.durum,
        zaman: relativeTimeTr(r.created_at),
        created_at: r.created_at,
      }));

      res.status(200).json({ applications, demo: false });
      return;
    }

    if (req.method === 'PATCH') {
      const user = requireAuth(req, res);
      if (!user) return;
      if (user.role !== 'admin') {
        res.status(403).json({ error: 'Sadece yönetici güncelleyebilir.' });
        return;
      }

      const body = req.body || {};
      const id = trimStr(body.id, 80);
      const durum = trimStr(body.durum, 40);
      if (!id || !DURUMLAR.has(durum)) {
        res.status(400).json({ error: 'id ve geçerli durum gerekli.' });
        return;
      }

      await sbRequest('PATCH', 'firma_basvurulari', {
        query: `id=eq.${encodeURIComponent(id)}`,
        body: { durum, updated_at: new Date().toISOString() },
        prefer: 'return=minimal',
      });

      res.status(200).json({ ok: true, id, durum });
      return;
    }

    res.status(405).json({ error: 'Method not allowed' });
  } catch (err) {
    console.error('[firma-basvuru]', err);
    res.status(500).json({ error: err.message || 'Sunucu hatası' });
  }
}
