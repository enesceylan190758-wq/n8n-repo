import { requireAuth } from '../_lib/auth.js';
import { sbRequest } from '../_lib/supabase.js';

export default async function handler(req, res) {
  const user = requireAuth(req, res);
  if (!user) return;

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { id, note } = req.body || {};
  if (!id || !String(note || '').trim()) {
    res.status(400).json({ error: 'Kayıt ID ve not metni gerekli' });
    return;
  }

  try {
    const existing = await sbRequest('GET', 'nps_responses', {
      query: `id=eq.${encodeURIComponent(id)}&select=id,flow,clinic_id,patient_phone,score`,
    });
    const row = Array.isArray(existing) ? existing[0] : null;
    if (!row) {
      res.status(404).json({ error: 'NPS kaydı bulunamadı' });
      return;
    }
    if (row.flow !== 'detractor') {
      res.status(400).json({ error: 'Yalnızca düşük puan (kriz) kayıtları tamamlanabilir' });
      return;
    }

    const resolvedBy = user.email || user.name || 'dashboard';
    const noteText = String(note).trim();
    const now = new Date().toISOString();

    const updated = await sbRequest('PATCH', 'nps_responses', {
      query: `id=eq.${encodeURIComponent(id)}`,
      body: {
        manager_note: noteText,
        resolution_status: 'resolved',
        resolved_at: now,
        resolved_by: resolvedBy,
      },
      prefer: 'return=representation',
    });

    const phone = String(row.patient_phone || '').replace(/\D/g, '');
    if (phone) {
      try {
        const alerts = await sbRequest('GET', 'inbox_messages', {
          query: `message_kind=eq.nps_alert&sender_phone=eq.${phone}&status=eq.open&select=id&order=created_at.desc&limit=3`,
        });
        for (const alert of alerts || []) {
          await sbRequest('PATCH', 'inbox_messages', {
            query: `id=eq.${alert.id}`,
            body: { status: 'closed' },
            prefer: 'return=minimal',
          });
        }
      } catch {
        /* inbox kapatma opsiyonel */
      }
    }

    const saved = Array.isArray(updated) ? updated[0] : updated;
    res.status(200).json({ ok: true, row: saved });
  } catch (err) {
    res.status(502).json({ error: 'NPS notu kaydedilemedi', detail: err.message });
  }
}
