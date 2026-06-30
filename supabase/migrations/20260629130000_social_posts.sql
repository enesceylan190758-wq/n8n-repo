-- Nefalix sosyal medya otomasyonu — içerik kuyruğu + şablonlar
-- wf-17: nefalix-17-social-media.json

CREATE TABLE IF NOT EXISTS social_post_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  post_number INT NOT NULL UNIQUE CHECK (post_number BETWEEN 1 AND 99),
  eyebrow TEXT,
  headline_html TEXT NOT NULL,
  subtitle TEXT,
  badges JSONB NOT NULL DEFAULT '[]'::jsonb,
  caption_template TEXT NOT NULL,
  hashtags TEXT NOT NULL DEFAULT '',
  active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS social_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id UUID REFERENCES social_post_templates(id) ON DELETE SET NULL,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN (
    'draft', 'pending_approval', 'approved', 'scheduled', 'published', 'rejected', 'failed'
  )),
  platform TEXT NOT NULL DEFAULT 'both' CHECK (platform IN ('instagram', 'linkedin', 'both')),
  headline TEXT,
  caption TEXT,
  hashtags TEXT,
  image_path TEXT,
  image_url TEXT,
  approval_token TEXT UNIQUE NOT NULL DEFAULT encode(gen_random_bytes(16), 'hex'),
  scheduled_at TIMESTAMPTZ,
  published_at TIMESTAMPTZ,
  publish_error TEXT,
  instagram_post_id TEXT,
  linkedin_post_id TEXT,
  approved_by TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_social_posts_status ON social_posts(status, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_social_posts_template ON social_posts(template_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_social_posts_approval_token ON social_posts(approval_token);

ALTER TABLE social_post_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_posts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_social_templates"
  ON social_post_templates FOR ALL TO service_role
  USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_social_posts"
  ON social_posts FOR ALL TO service_role
  USING (true) WITH CHECK (true);

GRANT ALL ON social_post_templates TO service_role;
GRANT ALL ON social_posts TO service_role;

-- 10 post şablonu (NefalixAI marka + ürün modülleri)
INSERT INTO social_post_templates (
  slug, post_number, eyebrow, headline_html, subtitle, badges, caption_template, hashtags
) VALUES
(
  'post_01_brand_hero', 1,
  'YAPAY ZEKÂ DESTEKLİ PLATFORM',
  'Kliniğinizin<br/>Dijital İtibarını<br/><em>Siz Uyurken</em> Yönetin.',
  'WhatsApp-first hasta deneyimi, otomatik NPS, Google yorum yönetimi ve itibar koruması — tek panelde, 7/24.',
  '["85+ Klinik Araştırması", "KVKK Uyumlu", "~1 Hafta Kurulum"]'::jsonb,
  E'NefalixAI, klinik ve hizmet işletmeleri için yapay zekâ destekli hasta deneyimi platformudur.\n\nTedavi sonrası geri bildirim, Google yorumları, WhatsApp mesajları ve itibar takibi — tek panelde, otomatik.\n\n📩 nefalixai@gmail.com\n🌐 nefalixai.com',
  '#NefalixAI #SağlıkTurizmi #KlinikYönetimi #HastaDeneyimi #Dijitalİtibar #WhatsApp #YapayZeka'
),
(
  'post_02_nps_flow', 2,
  'AKILLI GERİ BİLDİRİM',
  'Randevu bitti.<br/><em>3 saniye sonra</em><br/>hasta zaten cevapladı.',
  'Tedavi sonrası otomatik WhatsApp NPS anketi — memnun hastayı Google''a, memnuniyetsizi size yönlendirir.',
  '["Otomatik Tetikleme", "Tek Soru NPS", "Akıllı Yönlendirme"]'::jsonb,
  E'Çoğu klinik tedavi sonrası hastayı takip etmiyor.\n\nNefalixAI Akıllı Geri Bildirim:\n✅ Randevu bitince otomatik WhatsApp anketi\n✅ Tek soru, 3 saniyede yanıt\n✅ Memnun hasta → Google yorum daveti\n✅ Memnuniyetsiz hasta → önce siz, sonra çözüm\n\n📩 nefalixai@gmail.com',
  '#NPS #HastaMemnuniyeti #DişKliniği #GoogleYorumları #NefalixAI'
),
(
  'post_03_promoter_rule', 3,
  'NPS İŞ KURALI',
  '<em>8–10 puan</em> = Google''a davet<br/>Olumsuzu internete taşımayın.',
  'Memnun hastayı Google''a yönlendirin; memnuniyetsizliği klinik içinde çözün.',
  '["Promoter → Google", "Detractor → Alarm", "İtibar Koruması"]'::jsonb,
  E'Nefalix''te NPS sadece anket değil — akıllı yönlendirme motoru.\n\n8–10 (promoter): Google yorum linki\n7 ve altı (detractor): Google istenmez; yöneticiye WhatsApp alarmı\n\nSonuç: Daha fazla gerçek yorum, daha az kamuya açık kriz.\n\n📩 nefalixai@gmail.com | nefalixai.com',
  '#Googleİşletmem #Onlineİtibar #KlinikPazarlama #NefalixAI'
),
(
  'post_04_sentinel', 4,
  'SENTINEL — İTİBAR KORUMA',
  'Şikayetvar''da yeni şikayet mi?<br/><em>Yöneticiniz</em> anında haberdar.',
  'Google düşük puan + Şikayetvar tarama → AI duygu analizi → kritik olanlar WhatsApp alarmı.',
  '["Google İzleme", "Şikayetvar Sync", "Kriz Erken Uyarı"]'::jsonb,
  E'Olumsuz yorumu geç görmek = geç müdahale.\n\nSentinel modülü:\n🔍 Google düşük puanları izler\n🔍 Şikayetvar sayfanızı tarar\n🤖 AI duygu + risk skoru\n📲 Kritik olanlar yöneticiye WhatsApp özetiyle gider\n\n📩 nefalixai@gmail.com',
  '#İtibarYönetimi #Şikayetvar #KrizYönetimi #NefalixAI #Sentinel'
),
(
  'post_05_review_assistant', 5,
  'YORUM ASİSTANI',
  'Google''da yeni yorum geldi.<br/><em>Yanıt taslağı</em> 10 saniyede hazır.',
  'YZ destekli yanıt taslağı — siz onaylarsınız, tek tıkla yayınlanır.',
  '["Duygu Analizi", "Marka Tonu", "Tek Tık Onay"]'::jsonb,
  E'Her Google yorumuna saatler harcamak zorunda değilsiniz.\n\nNefalixAI Yorum Asistanı:\n• Yeni yorumları otomatik tespit eder\n• Duygu analizi yapar\n• Marka tonunuza uygun taslak üretir\n• Siz onaylarsınız\n\n📩 nefalixai@gmail.com',
  '#GoogleYorumları #YapayZeka #Klinikİletişimi #NefalixAI'
),
(
  'post_06_inbox', 6,
  'AKILLI MESAJ YÖNETİMİ',
  'WhatsApp + web sohbet<br/>= <em>Tek panel.</em>',
  'Tüm kanallar tek gelen kutusunda — AI taslak yanıt, insan onayıyla gönderim.',
  '["Ortak Inbox", "AI Taslak", "İnsan Onayı"]'::jsonb,
  E'Resepsiyon WhatsApp''a bakıyor, web sitesi ayrı… Hiçbir mesaj kaybolmamalı.\n\nNefalixAI Akıllı Mesaj Yönetimi:\n💬 WhatsApp ve site sohbeti tek gelen kutusunda\n🤖 AI taslak yanıt hazırlar\n✅ İnsan onayıyla gönderilir\n\n📩 nefalixai@gmail.com | nefalixai.com',
  '#WhatsAppBusiness #KlinikOtomasyon #Hastaİletişimi #NefalixAI'
),
(
  'post_07_recall', 7,
  'RECALL — GERİ KAZANIM',
  '6 aydır gelmeyen hasta<br/>= <em>Kayıp gelir değil,</em> fırsat.',
  'Uzun süredir gelmeyen hastaları tespit eder, kişiselleştirilmiş WhatsApp hatırlatması gönderir.',
  '["Kayıp Hasta Tespiti", "WhatsApp Hatırlatma", "Gelir Artışı"]'::jsonb,
  E'Yeni hasta bulmak, mevcut hastayı geri getirmekten pahalıdır.\n\nRecall modülü uzun süredir gelmeyen hastaları tespit eder ve kişiselleştirilmiş WhatsApp hatırlatması gönderir.\n\n📩 nefalixai@gmail.com',
  '#Recall #HastaGeriKazanım #DişKliniği #NefalixAI'
),
(
  'post_08_enps', 8,
  'ÇALIŞAN DENEYİMİ',
  'Hasta memnuniyeti kadar<br/><em>ekip nabzı</em> da önemli.',
  'Haftalık eNPS nabız anketi, trend takibi ve aksiyon maddeleri dashboard''da.',
  '["Haftalık eNPS", "Trend Takibi", "Aksiyon Listesi"]'::jsonb,
  E'İtibar sadece hastadan gelmez — ekibinizden de gelir.\n\nNefalixAI Çalışan Deneyimi:\n📊 Haftalık eNPS nabız anketi\n📈 Trend takibi\n✅ Aksiyon maddeleri dashboard''da\n\n📩 nefalixai@gmail.com',
  '#eNPS #KlinikYönetimi #NefalixAI'
),
(
  'post_09_kvkk', 9,
  'GÜVEN & KVKK',
  'Hasta verisi ciddi iş.<br/><em>KVKK uyumlu</em> altyapı.',
  'YZ yanıtları insan onayından geçer; veri güvenliği önceliklidir.',
  '["KVKK Uyumlu", "İnsan Onayı", "Veri Güvenliği"]'::jsonb,
  E'Sağlık verisiyle çalışan bir platformda hız, güvenin önüne geçmemeli.\n\nNefalixAI:\n🔒 KVKK uyumlu veri mimarisi\n🔒 YZ yanıtları insan onayından geçer\n🔒 Ticari WhatsApp öncesi İYS izin kontrolü\n\n📩 nefalixai@gmail.com | nefalixai.com/kvkk',
  '#KVKK #SağlıkTeknolojisi #VeriGüvenliği #NefalixAI'
),
(
  'post_10_demo_cta', 10,
  'CANLI DEMO',
  '15 dakikada canlı demo.<br/><em>Kliniğinize özel</em> akışı kuralım.',
  '6 modül, tek omurga — kurulum ~1 hafta, pilot kliniklerle sahadan doğrulanmış.',
  '["6 Modül", "~1 Hafta Kurulum", "Canlı Demo"]'::jsonb,
  E'NefalixAI 6 modül, tek omurga:\n⭐ Akıllı Geri Bildirim\n💬 Mesaj Yönetimi\n🛡️ Yorum Asistanı\n👥 Çalışan Deneyimi\n🔍 Sentinel\n🔁 Recall\n\nDemo için yazın:\n📩 nefalixai@gmail.com\n🌐 nefalixai.com',
  '#NefalixAI #Demo #SağlıkTurizmi #KlinikDijitalleşme #WhatsApp'
)
ON CONFLICT (slug) DO NOTHING;
