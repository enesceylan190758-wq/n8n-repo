import { requireAuth } from './_lib/auth.js';

/** Admin: Vertex AI durumu — yanıltıcı sabit kredi göstermez */
export default async function handler(req, res) {
  const user = requireAuth(req, res);
  if (!user) return;
  if (user.role !== 'admin') {
    res.status(403).json({ error: 'Sadece yönetici görüntüleyebilir.' });
    return;
  }

  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  res.setHeader('Cache-Control', 'no-store');

  const gcpProject = process.env.GCP_PROJECT_ID || 'utility-cumulus-484107-v3';
  const model = process.env.VERTEX_GEMINI_MODEL || 'gemini-2.5-flash';
  const creditStatus = process.env.GCP_CREDIT_STATUS || 'expired';
  const creditsRemaining = Number(process.env.GCP_CREDITS_REMAINING_TRY || 0);

  let creditNote = 'Trial süresi doldu — kullanım karttan (düşük hacim)';
  let note =
    'Free Trial kredisi expire oldu (kullanılmadan). Vertex çalışıyor; maliyet pay-as-you-go. Budget alarmı önerilir.';

  if (creditStatus === 'active' && creditsRemaining > 0) {
    creditNote = `₺${creditsRemaining.toLocaleString('tr-TR')} promosyon kredisi`;
    note = 'Aktif GCP promosyon kredisi — Vertex harcaması buradan düşer.';
  } else if (process.env.GCP_CREDIT_NOTE) {
    creditNote = process.env.GCP_CREDIT_NOTE;
  }

  res.status(200).json({
    provider: 'vertex_gemini',
    model,
    googleCloud: {
      projectId: gcpProject,
      creditStatus,
      creditsRemainingTry: creditsRemaining,
      creditNote,
      note,
    },
    vertexStudioUrl:
      'https://console.cloud.google.com/vertex-ai/studio?project=' + encodeURIComponent(gcpProject),
  });
}
