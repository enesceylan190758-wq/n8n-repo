/** WhatsApp mod durumu — dashboard banner */
export default async function handler(req, res) {
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const sendEnabled = String(process.env.WHATSAPP_SEND_ENABLED ?? 'false').toLowerCase() === 'true';

  res.setHeader('Cache-Control', 'no-store');
  res.status(200).json({
    receiveEnabled: true,
    sendEnabled,
    mode: sendEnabled ? 'full' : 'receive_only',
    message: sendEnabled
      ? 'WhatsApp gönderim açık.'
      : 'WhatsApp alım açık — giden mesajlar siz onaylayana kadar kapalı.',
  });
}
