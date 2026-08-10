export const OUTREACH = {
  "templates": [
    {
      "id": "t1",
      "channel": "E-posta",
      "stage": "Tanışma",
      "title": "Tanışma & iş birliği (uzun)",
      "subject": "[Firma] × Nefalix | Tanışma ve çözüm görüşmesi",
      "body": "Merhaba Sayın [İsim],\n\nBen {name}, Nefalix'in {titleShort}. Nefalix; sağlık kuruluşları, oteller ve otomotiv servislerinin müşteri deneyimini, dijital itibarını ve operasyonel geri bildirimlerini yapay zekâ desteğiyle tek merkezden yönetmelerine yardımcı olan yeni nesil bir Experience Intelligence platformudur.\n\nPlatformumuzla kurumların; müşteri yorumlarını takip etmesini, geri bildirimleri anlamlandırıp kategorilere ayırmasını, memnuniyet ve şikâyet eğilimlerini analiz etmesini, yapay zekâ destekli yanıt önerileri oluşturmasını ve yönetim için ölçülebilir raporlar üretmesini hedefliyoruz.\n\nBu kapsamda [Firma] ile 20–30 dakikalık kısa bir tanışma görüşmesi gerçekleştirmek isteriz. Görüşmede Nefalix'i tanıtabilir, mevcut süreçlerinizi dinleyebilir, uygun olması hâlinde bir pilot çalışmayı değerlendirebiliriz.\n\nSize uygun gün ve saat aralığını paylaşmanız hâlinde görüşmeyi memnuniyetle planlarız.\n\nSaygılarımla,\n{name}\n{title} · Nefalix\n{phone} · {email} · {web}"
    },
    {
      "id": "t2",
      "channel": "E-posta",
      "stage": "Tanışma",
      "title": "Tanışma (kısa & sıcak)",
      "subject": "Nefalix tanışma görüşmesi",
      "body": "Merhaba [İsim] Bey/Hanım,\n\nBen {name}, Nefalix'in {titleShort}. Nefalix; sağlık, otelcilik ve otomotiv servisleri için müşteri deneyimi, dijital itibar ve geri bildirim süreçlerini yapay zekâ desteğiyle tek merkezden yönetmeyi amaçlayan yeni nesil bir platformdur.\n\nMüşteri yorumlarının analizi, memnuniyet ve şikâyet eğilimlerinin tespiti, yapay zekâ destekli yanıt önerileri ve yönetim raporlaması gibi süreçleri daha ölçülebilir hâle getiriyoruz.\n\nHem sizi tanımak hem de Nefalix'in [Firma] için sağlayabileceği katkıları değerlendirmek üzere 20–30 dakikalık kısa bir görüşme yapmak isteriz. Size uygun bir zaman paylaşabilirseniz memnuniyetle planlarız.\nTakvimden seçmek isterseniz: {calUrl}\n\nSaygılarımla,\n{name}\n{title} | Nefalix · {email} · {web}"
    },
    {
      "id": "t3",
      "channel": "E-posta",
      "stage": "Takip",
      "title": "Cevap gelmezse — takip",
      "subject": "Nefalix görüşme talebi hakkında",
      "body": "Merhaba [İsim] Bey/Hanım,\n\nGeçtiğimiz günlerde Nefalix ve olası bir tanışma görüşmesi hakkında kısa bir mesaj iletmiştim. Yoğunluğunuzda gözden kaçmış olabileceğini düşünerek tekrar ulaşmak istedim.\n\nMüşteri deneyimi, dijital itibar ve yapay zekâ destekli geri bildirim analizi üzerine 20 dakikalık kısa bir görüşmenin [Firma] açısından faydalı olabileceğini düşünüyorum.\n\nUygun olduğunuz bir tarih ve saat aralığını paylaşmanız hâlinde takvimi memnuniyetle oluşturabiliriz.\n\nSaygılarımla,\n{name} — {title} | Nefalix"
    }
  ],
  "senders": {
    "kadir": {
      "key": "kadir",
      "name": "Abdülkadir Yaşar",
      "title": "Kurucu & CEO",
      "email": "abdulkadir@nefalix.com",
      "phone": "+90 507 821 06 96",
      "web": "www.nefalix.com",
      "address": "Kartal, İstanbul",
      "linkedin": "https://www.linkedin.com/company/nefalixai/",
      "instagram": "https://www.instagram.com/nefalixai/",
      "youtube": "https://www.youtube.com/@Nefalixai",
      "slogan": "Müşterinizi anlayın. Deneyimi yönetin. İtibarınızı büyütün.",
      "calUrl": "https://cal.com/enes-ceylan/15min"
    },
    "enes": {
      "key": "enes",
      "name": "Enes Ceylan",
      "title": "Kurucu Ortak & CTO",
      "email": "enes@nefalix.com",
      "phone": "+90 535 928 82 50",
      "web": "www.nefalix.com",
      "address": "Kartal, İstanbul",
      "linkedin": "https://www.linkedin.com/company/nefalixai/",
      "instagram": "https://www.instagram.com/nefalixai/",
      "youtube": "https://www.youtube.com/@Nefalixai",
      "slogan": "Müşterinizi anlayın. Deneyimi yönetin. İtibarınızı büyütün.",
      "calUrl": "https://cal.com/enes-ceylan/15min"
    },
    "kader": {
      "key": "kader",
      "name": "Kader Hanım",
      "title": "Kurumsal İletişim",
      "email": "info@nefalix.com",
      "phone": "+90 535 928 82 50",
      "web": "www.nefalix.com",
      "address": "Kartal, İstanbul",
      "linkedin": "https://www.linkedin.com/company/nefalixai/",
      "instagram": "https://www.instagram.com/nefalixai/",
      "youtube": "https://www.youtube.com/@Nefalixai",
      "slogan": "Müşterinizi anlayın. Deneyimi yönetin. İtibarınızı büyütün.",
      "calUrl": "https://cal.com/enes-ceylan/15min"
    }
  }
};

export function titleShort(t) {
  if (/CEO/i.test(t || '')) return 'kurucusu';
  if (/CTO/i.test(t || '')) return 'kurucu ortağı';
  if (/İletişim/i.test(t || '')) return 'iletişim ekibinden';
  return 'kurucusu';
}

function escHtml(s) {
  return String(s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function webHref(web) {
  const w = String(web || 'www.nefalix.com').trim();
  if (/^https?:\/\//i.test(w)) return w;
  return 'https://' + w.replace(/^\/+/, '');
}

/** /iletisim/imza ile aynı tablo imza (gönderen profile göre). */
export function buildSignatureHtml(sender) {
  const p = sender || {};
  const name = escHtml(p.name || 'Nefalix');
  const title = escHtml(p.title || '');
  const phone = escHtml(p.phone || '');
  const email = escHtml(p.email || '');
  const web = String(p.web || 'www.nefalix.com').replace(/^https?:\/\//i, '');
  const webUrl = webHref(p.web);
  const address = escHtml(p.address || 'Kartal, İstanbul');
  const linkedin = escHtml(p.linkedin || 'https://www.linkedin.com/company/nefalixai/');
  const instagram = escHtml(p.instagram || 'https://www.instagram.com/nefalixai/');
  const youtube = escHtml(p.youtube || 'https://www.youtube.com/@Nefalixai');
  const slogan = escHtml(
    p.slogan || 'Müşterinizi anlayın. Deneyimi yönetin. İtibarınızı büyütün.'
  );

  return `<table cellpadding="0" cellspacing="0" border="0" role="presentation" style="font-family:Arial,Helvetica,sans-serif; border-collapse:collapse; margin-top:20px;">
  <tr>
    <td valign="middle" style="padding:2px 18px 2px 0;">
      <table cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td valign="middle" style="padding-right:10px;">
            <table cellpadding="0" cellspacing="0" border="0" role="presentation" width="34" style="width:34px;">
              <tr><td height="7" bgcolor="#17727E" style="line-height:7px; font-size:0; border-radius:3px;">&nbsp;</td></tr>
              <tr><td height="4" style="line-height:4px; font-size:0;">&nbsp;</td></tr>
              <tr><td height="7" bgcolor="#0C2A31" style="line-height:7px; font-size:0; border-radius:3px;">&nbsp;</td></tr>
              <tr><td height="4" style="line-height:4px; font-size:0;">&nbsp;</td></tr>
              <tr><td height="7" bgcolor="#E8734A" style="line-height:7px; font-size:0; border-radius:3px;">&nbsp;</td></tr>
            </table>
          </td>
          <td valign="middle">
            <div style="font-size:20px; font-weight:bold; letter-spacing:2.5px; color:#17727E;">NEFALIX</div>
            <div style="font-size:10px; color:#5E7075; letter-spacing:.4px; margin-top:2px;">Experience Intelligence Platform</div>
          </td>
        </tr>
      </table>
    </td>
    <td width="1" bgcolor="#DDE7E7" style="width:1px; line-height:1px; font-size:0;">&nbsp;</td>
    <td valign="middle" style="padding:2px 0 2px 18px; color:#33474C;">
      <div style="font-size:15px; font-weight:bold; color:#0C2A31;">${name}</div>
      <div style="font-size:12.5px; font-weight:bold; color:#17727E; padding-bottom:6px;">${title}</div>
      <div style="font-size:12.5px; padding:1px 0;"><span style="color:#17727E; font-weight:bold;">M</span>&nbsp;&nbsp;${phone}</div>
      <div style="font-size:12.5px; padding:1px 0;"><span style="color:#17727E; font-weight:bold;">E</span>&nbsp;&nbsp;<a href="mailto:${email}" style="color:#33474C; text-decoration:none;">${email}</a></div>
      <div style="font-size:12.5px; padding:1px 0;"><span style="color:#17727E; font-weight:bold;">W</span>&nbsp;&nbsp;<a href="${escHtml(webUrl)}" style="color:#33474C; text-decoration:none;">${escHtml(web)}</a></div>
      <div style="font-size:12.5px; padding:1px 0;"><span style="color:#17727E; font-weight:bold;">A</span>&nbsp;&nbsp;${address}</div>
      <div style="font-size:12px; font-weight:bold; padding-top:7px;">
        <a href="${linkedin}" style="color:#17727E; text-decoration:none;">LinkedIn</a>&nbsp;&nbsp;·&nbsp;&nbsp;
        <a href="${instagram}" style="color:#17727E; text-decoration:none;">Instagram</a>&nbsp;&nbsp;·&nbsp;&nbsp;
        <a href="${youtube}" style="color:#17727E; text-decoration:none;">YouTube</a>
      </div>
    </td>
  </tr>
  <tr>
    <td colspan="3" style="padding-top:12px;">
      <div style="border-top:1px solid #DDE7E7; padding-top:8px; font-size:11px; color:#5E7075;">${slogan}</div>
    </td>
  </tr>
</table>`;
}

export function buildSignaturePlain(sender) {
  const p = sender || {};
  const web = String(p.web || 'www.nefalix.com').replace(/^https?:\/\//i, '');
  return [
    '',
    '--',
    p.name || 'Nefalix',
    p.title || '',
    p.phone || '',
    p.email || '',
    web,
    p.address || 'Kartal, İstanbul',
  ]
    .filter((line, i) => i < 2 || line)
    .join('\n');
}

export function hitapSuffix(hitap) {
  const key = String(hitap || 'unknown').trim().toLowerCase();
  if (['bey', 'erkek', 'male', 'm'].includes(key)) return ' Bey';
  if (['hanim', 'hanım', 'kadin', 'kadın', 'female', 'f'].includes(key)) return ' Hanım';
  return '';
}

export function applyHitap(text, hitap) {
  const suf = hitapSuffix(hitap);
  let out = String(text || '');
  out = out.replaceAll('[Hitap]', suf);
  out = out.replaceAll(' Bey/Hanım', suf);
  out = out.replaceAll('Bey/Hanım', suf ? suf.trim() : '');
  return out;
}

export function fillOutreach(template, sender, recip) {
  const p = sender || {};
  const name = recip?.name || '[İsim]';
  const firm = recip?.firm || '[Firma]';
  const fill = (s) => applyHitap(
    String(s || '')
      .replaceAll('{name}', p.name || '')
      .replaceAll('{title}', p.title || '')
      .replaceAll('{titleShort}', titleShort(p.title))
      .replaceAll('{email}', p.email || '')
      .replaceAll('{phone}', p.phone || '')
      .replaceAll('{web}', p.web || '')
      .replaceAll('{calUrl}', p.calUrl || 'https://cal.com/enes-ceylan/15min')
      .replaceAll('[İsim]', name)
      .replaceAll('[Firma]', firm),
    recip?.hitap || 'unknown'
  );
  return { subject: fill(template.subject), body: fill(template.body) };
}

export function listEmailTemplates() {
  return (OUTREACH.templates || []).filter((t) => t.channel === 'E-posta');
}
