-- Nefalix günlük blog (kaynaklar + /blog/:slug)
CREATE TABLE IF NOT EXISTS blog_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  tag TEXT DEFAULT 'Rehber',
  excerpt TEXT NOT NULL,
  body_html TEXT NOT NULL,
  meta_description TEXT,
  status TEXT NOT NULL DEFAULT 'published' CHECK (status IN ('draft', 'published')),
  published_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_blog_posts_published
  ON blog_posts (published_at DESC)
  WHERE status = 'published';

ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_blog_posts"
  ON blog_posts FOR ALL TO service_role
  USING (true) WITH CHECK (true);

CREATE POLICY "anon_read_published_blog_posts"
  ON blog_posts FOR SELECT TO anon
  USING (status = 'published');

GRANT SELECT ON blog_posts TO anon;
GRANT ALL ON blog_posts TO service_role;

INSERT INTO blog_posts (slug, title, tag, excerpt, body_html, meta_description, status, published_at)
VALUES (
  'kliniklerde-nps-anketi-neden-onemli',
  'Kliniklerde NPS Anketi Neden Önemli?',
  'NPS',
  'Randevu sonrası memnuniyet ölçümü, olumsuz deneyimi içeride tutarken promoter hastaları Google yorumuna yönlendirmenin en pratik yoludur.',
  '<p>Hasta deneyimi artık sadece muayene odasında bitmiyor. Randevu sonrası ilk 24 saat, hastanın kliniğinizi nasıl anlatacağını belirleyen kritik penceredir.</p>
<p>NPS (Net Promoter Score) anketi bu pencerede net bir soru sorar: Bizi bir yakınınıza önerir misiniz? 9–10 puan veren hastalar Google yorumu için doğal bir adaydır; 1–7 puan verenler ise iç süreçte çözülmeli, kamuya yansımadan önce.</p>
<p>Manuel anket süreçleri çoğu klinikte yarım kalır. WhatsApp üzerinden otomatik, KVKK uyumlu ve HBYS entegrasyonlu akışlar ise ölçülebilir sonuç verir.</p>
<p>Nefalix, Estesoft gibi sistemlerde randevu tamamlandığında NPS taslağını üretir; yönetici onayından sonra mesaj gider. Böylece her gün düzenli geri bildirim toplarsınız.</p>',
  'Kliniklerde NPS anketi: randevu sonrası memnuniyet ölçümü, Google yorumu ve olumsuz geri bildirim yönetimi rehberi.',
  'published',
  now()
) ON CONFLICT (slug) DO NOTHING;
