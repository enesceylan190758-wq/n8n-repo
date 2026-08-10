import { requireAuth } from '../_lib/auth.js';

export default async function handler(req, res) {
  const user = requireAuth(req, res);
  if (!user) return;

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { phone, text, messageId, clinicId } = req.body || {};
  if (!phone || !text) {
    res.status(400).json({ error: 'Telefon ve mesaj metni gerekli' });
    return;
  }

  const upstream = process.env.N8N_INBOX_SEND_URL;
  if (!upstream) {
    res.status(503).json({ error: 'Inbox gönderim API bağlı değil (N8N_INBOX_SEND_URL).' });
    return;
  }

  try {
    const apiRes = await fetch(upstream, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        phone: String(phone).replace(/\D/g, ''),
        text,
        messageId: messageId || null,
        clinicId: clinicId || user.clinicId || null,
        sentBy: user.email,
      }),
    });
    const data = await apiRes.json().catch(() => ({}));
    if (!apiRes.ok) {
      res.status(apiRes.status).json({ error: data.message || 'Gönderim başarısız', detail: data });
      return;
    }
    const body = data?.ok !== undefined ? data : data?.json ?? data?.[0]?.json ?? { ok: true };
    if (body.skipped && body.reason === 'whatsapp_disabled') {
      res.status(403).json({
        error:
          'WhatsApp gönderim şu an kapalı (güvenlik kilidi). Açmak için yöneticiye «gönderimi aç» deyin.',
        skipped: true,
        reason: 'whatsapp_disabled',
      });
      return;
    }
    if (body.sent === false && body.blocked) {
      res.status(429).json({
        error: `Rate limit: ${body.reason || 'bekleyin'}`,
        retryAfterSec: body.retryAfterSec,
      });
      return;
    }
    res.status(200).json(body);
  } catch (err) {
    res.status(502).json({ error: 'WhatsApp gönderilemedi', detail: err.message });
  }
}
