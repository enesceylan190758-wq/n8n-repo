#!/usr/bin/env python3
"""10 Geo SEO paketi + blog yazısını canlıya yazar (supabase-proxy).

Görseller: assets/geo-seo-covers/geo-seo-01..10.png
Kapak URL: GitHub raw (branch/main push sonrası).

  export NEFALIX_INTERNAL_KEY=...
  python3 execution/publish-geo-seo-10.py --dry-run
  python3 execution/publish-geo-seo-10.py --start today
  python3 execution/publish-geo-seo-10.py --include-future  # sitemap için önerilmez
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

SITE = "https://nefalix.com"
PROXY = os.environ.get(
    "N8N_SUPABASE_PROXY_URL",
    "https://api.nefalixai.com/webhook/nefalix/supabase-proxy",
)
INTERNAL_KEY = os.environ.get("NEFALIX_INTERNAL_KEY", "")
REPO = "enesceylan190758-wq/n8n-repo"
BRANCH = os.environ.get("GEO_SEO_ASSET_BRANCH", "cursor/geo-seo-10-packs-c5e3")

def resolve_start(value: str | None) -> date:
    """İlk paket günü — default bugün; gelecek tarih sitemap'e gitmemeli."""
    if value is None or value == "today":
        return date.today()
    return date.fromisoformat(value)


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:80] or "yazi"


def cover_raw(filename: str) -> str:
    path = f"assets/geo-seo-covers/{filename}"
    return (
        f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{path}"
    )


def cover_api(kind: str, tag: str, title: str) -> str:
    q = urllib.parse.urlencode(
        {"action": "cover", "kind": kind, "tag": tag, "t": title, "v": "10"}
    )
    return f"{SITE}/api/blog?{q}"


PACKS = [
    {
        "file": "geo-seo-01-saglik-turizmi-kuresel.png",
        "bucket": "problem",
        "tag": "GEO",
        "title": "Sağlık Turizminde Küresel Geo SEO: Hastaları Google Haritalar'dan Çekin",
        "prompt": "Sağlık turizminde küresel Geo SEO ile Google Haritalar'dan hasta nasıl çekilir?",
        "direct_answer": (
            "Sağlık turizminde küresel Geo SEO, hedef şehirlerde (İstanbul, Londra, Berlin, Dubai) "
            "Google İşletme Profili + çok dilli hizmet sayfaları + yorum sinyali ile hastanın "
            "harita ve AI önerilerinde sizi bulmasını sağlar. NAP tutarlılığı, şehir+branş "
            "landing’leri ve yorum daveti uluslararası görünürlüğün temelidir. Alıntılanabilir "
            "SSS ve süreç sayfaları ChatGPT/Perplexity önerilerini güçlendirir."
        ),
        "bullets": [
            "Hedef ülke dillerinde şehir+branş sayfaları yayınlayın",
            "Google İşletme Profilini İngilizce/Arapça kategorilerle güçlendirin",
            "Tedavi sonrası yorum davetini 24–72 saatte otomatikleştirin",
            "Küresel citation için answer-first GEO sayfaları ekleyin",
        ],
        "faq": [
            {
                "q": "Yalnızca İngilizce site yeterli mi?",
                "a": "Hayır. Hedef pazar dilinde hizmet+SSS ve yerel NAP tutarlılığı gerekir.",
            },
            {
                "q": "Harita mı yoksa AI mı önce?",
                "a": "İkisi birlikte: Harita yorum/NAP sinyali, AI için public cevap sayfaları.",
            },
            {
                "q": "İlk ölçüm ne olmalı?",
                "a": "Hedef şehir+branş promptlarında mention/citation oranını haftalık skorlayın.",
            },
        ],
        "sections": [
            (
                "Küresel hasta araması nasıl değişti?",
                "Uluslararası hastalar tedavi seçerken yalnızca klasik arama sonuçlarına değil, Google Haritalar paketlerine ve ChatGPT/Perplexity önerilerine bakıyor. Klinik entity’si (adres, branş, dil, yorum) net değilse öneri listesinde görünmezsiniz.",
            ),
            (
                "Google Haritalar sinyalini güçlendirin",
                "Profil kategorisi, çalışma saati, tedavi fotoğrafları ve çok dilli açıklama tutarlı olmalı. Memnun hasta yorumu güncel akış, yerel güven skorunu yükseltir.",
            ),
            (
                "Şehir hub’ları kurun",
                "İstanbul saç ekimi, Londra diş, Dubai estetik gibi hedef sorgular için ayrı landing + SSS üretin. Her sayfa answer-first giriş ve FAQPage şeması taşısın.",
            ),
        ],
        "path": "/sektorler#saglik",
    },
    {
        "file": "geo-seo-02-onpage-klinik.png",
        "bucket": "kategori",
        "tag": "GEO",
        "title": "Yerel Klinikler İçin On-Page Geo SEO Rehberi",
        "prompt": "Yerel klinikler için on-page Geo SEO nasıl yapılır?",
        "direct_answer": (
            "Yerel klinik on-page Geo SEO; şehir+branş başlıkları, answer-first giriş, hizmet "
            "H2’leri, görünür SSS, NAP bloğu ve iç linklerle kurulur. Her kritik sayfada "
            "soruyu ilk 40–70 kelimede yanıtlayın; FAQPage şeması görünür metinle aynı olsun. "
            "İletişim ve hizmet sayfalarını semt anahtar kelimeleriyle güçlendirin."
        ),
        "bullets": [
            "Title/H1’e şehir + branş ekleyin",
            "İlk paragrafta doğrudan cevap verin",
            "Hizmet sayfalarına 5–10 SSS koyun",
            "NAP’i footer ve iletişimde birebir tutun",
        ],
        "faq": [
            {
                "q": "Keyword stuffing gerekir mi?",
                "a": "Hayır. Doğal şehir+hizmet tekrarı yeter; abartı kaliteyi düşürür.",
            },
            {
                "q": "Hangi sayfalar öncelikli?",
                "a": "Ana sayfa, hizmet, iletişim ve en çok aranan 3 tedavi sayfası.",
            },
            {
                "q": "Schema şart mı?",
                "a": "FAQPage ve LocalBusiness/MedicalClinic işaretleri alıntı şansını artırır.",
            },
        ],
        "sections": [
            (
                "Sayfa iskeleti",
                "H1 soruyu/yanıtı çerçeveler, ardından uygulanabilir maddeler ve SSS gelir. Kullanıcı ve AI aynı yapıyı okur.",
            ),
            (
                "Yerel dil",
                "Semt adlarını zorla doldurmak yerine gerçek hizmet kapsamı ve ulaşım bilgisiyle bağlayın.",
            ),
            (
                "İç link ağı",
                "Hizmet → SSS → iletişim → GEO paketi zinciri entity’yi güçlendirir.",
            ),
        ],
        "path": "/blog",
    },
    {
        "file": "geo-seo-03-yorum-itibar.png",
        "bucket": "problem",
        "tag": "İtibar",
        "title": "Yapay Zeka Destekli Geo SEO ile Hasta Yorumlarını Nasıl Yönetirsiniz?",
        "prompt": "Yapay zeka destekli Geo SEO ile hasta yorumları nasıl yönetilir?",
        "direct_answer": (
            "AI destekli yorum yönetimi; memnun hastaya zamanında davet, tüm yorumlara hızlı "
            "yanıt ve düşük puanda geri arama görevinden oluşur. Duygu analizi olumsuzları "
            "erken işaretler; yanıt taslakları tonu korur. Güncel olumlu akış Google ve AI "
            "görünürlüğünü birlikte yükseltir. Sahte yorum yerine organik süreç hedeflenir."
        ),
        "bullets": [
            "Memnun (promoter) hastaya 24–72 saat içinde davet gönderin",
            "48 saat kuralıyla tüm yorumlara yanıt verin",
            "Detractor için geri arama görevi açın",
            "Haftalık yorum hacmi/puanı citation ölçümüne bağlayın",
        ],
        "faq": [
            {
                "q": "AI yanıtı otomatik yayınlanmalı mı?",
                "a": "Taslak + insan onayı daha güvenli; kriz tonunda otomatik yayın risklidir.",
            },
            {
                "q": "Olumsuz yorum silinmeli mi?",
                "a": "Politika dışı değilse silmek yerine çözüm odaklı yanıt ve offline iletişim tercih edilir.",
            },
            {
                "q": "GEO ile bağlantısı nedir?",
                "a": "Yorum sinyali entity güvenini artırır; AI motorları bunu öneride kullanır.",
            },
        ],
        "sections": [
            (
                "Davet zamanlaması",
                "Tedavi sonrası erken ama baskısız davet, dönüşümü artırır. WhatsApp veya SMS ile izinli gönderim şarttır.",
            ),
            (
                "Duygu analizi",
                "Negatif tonu erken yakalayıp yönetici kuyruğuna almak kriz büyümesini keser.",
            ),
            (
                "Yanıt çerçevesi",
                "Empati + somut sonraki adım; tartışmaya girmeden çözüm teklif edin.",
            ),
        ],
        "path": "/urunler#yorum-asistani",
    },
    {
        "file": "geo-seo-04-yerel-icerik-kule.png",
        "bucket": "kategori",
        "tag": "GEO",
        "title": "SEO Uyumlu Blog İçerikleri ile Yerel Otorite Kurun",
        "prompt": "SEO uyumlu blog içerikleriyle yerel otorite nasıl kurulur?",
        "direct_answer": (
            "Yerel otorite, semt+hizmet odaklı answer-first içeriklerin düzenli yayınlanmasıyla "
            "kurulur. Her yazı bir alıcı sorusunu yanıtlar, SSS ekler ve hizmet/iletişim "
            "sayfalarına bağlanır. ‘Sarıyer’de diş beyazlatma’ gibi sayfalar harita ve AI "
            "için entity derinliği yaratır. Blog uzun playbook, GEO paketi kısa alıntı birimidir."
        ),
        "bullets": [
            "Ayda en az 4 semt+hizmet konusu planlayın",
            "Her yazıyı ilgili hizmet sayfasına linkleyin",
            "Aynı sorunun kısa GEO versiyonunu /geo’da yayınlayın",
            "İçerik kulesini sitemap’e ekleyin",
        ],
        "faq": [
            {
                "q": "Tek mega yazı yeter mi?",
                "a": "Hayır. Semt/hizmet kombinasyonları ayrı sayfalarda daha iyi eşleşir.",
            },
            {
                "q": "Blog GEO yerine geçer mi?",
                "a": "Geçmez. Blog derinleştirir; GEO kısa alıntı yüzeyi sağlar.",
            },
            {
                "q": "Hangi metrik?",
                "a": "Organik yerel tıklama, harita aksiyonları ve AI citation oranı.",
            },
        ],
        "sections": [
            (
                "İçerik kulesi modeli",
                "Hub hizmet sayfası + semt blogları + GEO paketleri birbirini besler.",
            ),
            (
                "Başlık disiplini",
                "Tıklama tuzağı yerine soru-cevap başlıkları AI ve kullanıcı için daha nettir.",
            ),
            (
                "Güncelleme ritmi",
                "Eski semt yazılarını yılda bir güncellemek taze sinyal verir.",
            ),
        ],
        "path": "/blog",
    },
    {
        "file": "geo-seo-05-gmb-checklist.png",
        "bucket": "problem",
        "tag": "Google",
        "title": "Klinikler İçin Google İşletme Profili Optimizasyon Rehberi",
        "prompt": "Klinikler için Google İşletme Profili nasıl adım adım optimize edilir?",
        "direct_answer": (
            "Google İşletme Profili optimizasyonu adres doğrulama, kategori, saat, hizmet, "
            "fotoğraf, yorum ve performans takibi adımlarını sırayla tamamlamaktır. NAP "
            "siteyle birebir olmalı; hizmet listesi ve SSS güncel tutulmalıdır. Haftalık "
            "fotoğraf/yorum aktivitesi profili taze tutar. Eksik adım harita paketini zayıflatır."
        ),
        "bullets": [
            "Adres ve telefonu doğrulayın (NAP=site)",
            "Birincil+ikincil kategorileri netleştirin",
            "Hizmet ve fotoğrafları haftalık güncelleyin",
            "Yorum yanıtı ve Insights metriklerini izleyin",
        ],
        "faq": [
            {
                "q": "Kaç kategori seçilmeli?",
                "a": "Bir birincil + ilgili ikinciller; alakasız kategori eklemeyin.",
            },
            {
                "q": "Sahte yorum riski?",
                "a": "Organik davet ve politika uyumu; satın alınmış yorum kullanmayın.",
            },
            {
                "q": "Ne sıklıkla kontrol?",
                "a": "Haftalık Insights + aylık tam checklist tarama.",
            },
        ],
        "sections": [
            (
                "Doğrulama ve NAP",
                "Yanlış adres veya farklı telefon, harita güvenini kırar. Site footer ile eşleştirin.",
            ),
            (
                "Görsel ve hizmet",
                "Gerçek klinik fotoğrafları ve net hizmet adları tıklama/yol tarifi oranını artırır.",
            ),
            (
                "Performans",
                "Arama/harita görüntüleme, yol tarifi ve arama tıklamalarını ay ay karşılaştırın.",
            ),
        ],
        "path": "/platformlar",
    },
    {
        "file": "geo-seo-06-sesli-arama.png",
        "bucket": "problem",
        "tag": "GEO",
        "title": "Sesli Arama ve Geo SEO: Yakınımdaki Klinikleri Bul",
        "prompt": "Sesli arama ve 'yakınımdaki klinikler' sorgularında Geo SEO nasıl çalışır?",
        "direct_answer": (
            "‘Yakınımdaki klinikler’ sesli aramaları mesafe, açık olma, kategori eşleşmesi ve "
            "yorum sinyaline göre sonuç döner. Geo SEO burada mobil uyum, hızlı sayfa, doğru "
            "GBP kategorisi ve konuşma dili SSS ile kazanılır. Konuşma sorgularına answer-first "
            "cevaplar hazırlayın. Konum izni açıkken harita paketi baskındır."
        ),
        "bullets": [
            "SSS’yi konuşma sorusu formatında yazın",
            "Mobil hızı (LCP) lokal rakiplerden iyi tutun",
            "GBP’de ‘açık şimdi’ bilgisini doğru tutun",
            "Semt bazlı kısa cevap sayfaları yayınlayın",
        ],
        "faq": [
            {
                "q": "Sesli arama ayrı bir kanal mı?",
                "a": "Ayrı indeks değil; mobil yerel sinyaller + doğal dil eşleşmesi baskındır.",
            },
            {
                "q": "En kritik sinyal?",
                "a": "Yakınlık + kategori + yorum/puan kombinasyonu.",
            },
            {
                "q": "Ne yazmalı?",
                "a": "‘Yakınımdaki diş kliniği nasıl seçilir?’ gibi soru-cevap blokları.",
            },
        ],
        "sections": [
            (
                "Konuşma dili",
                "Kullanıcılar tam cümle sorar; SSS ve GEO paketleri bu dile uymalıdır.",
            ),
            (
                "Mobil gerçeklik",
                "Yavaş site yol tarifi tıklamasını düşürür; Core Web Vitals yerel paketi etkiler.",
            ),
            (
                "Harita + site",
                "GBP ve site birlikte çalışır; yalnızca birini optimize etmek yetmez.",
            ),
        ],
        "path": "/geo",
    },
    {
        "file": "geo-seo-07-veri-isi-haritasi.png",
        "bucket": "problem",
        "tag": "Operasyon",
        "title": "Veri Odaklı Geo SEO: Hangi Bölgelerden Hasta Geliyor?",
        "prompt": "Veri odaklı Geo SEO ile hangi bölgelerden hasta geldiği nasıl ölçülür?",
        "direct_answer": (
            "Bölgesel hasta kaynağı; Analytics konum/şehir, GBP Insights ve CRM/HBYS şube "
            "kayıtlarının birleştirilmesiyle ölçülür. Isı haritası hangi semtlerin dönüştüğünü "
            "gösterir; içerik ve reklam bütçesi buna göre kaydırılır. Kaynak kanalları "
            "(Maps, Search, Social, Direct) ayrı izlenmelidir. Aylık trend olmadan tahmin kör kalır."
        ),
        "bullets": [
            "GA4 şehir + landing page raporunu sabitleyin",
            "GBP Insights yol tarifi/arama kırılımını alın",
            "HBYS’te şube/semt alanını doldurun",
            "Aylık ısı haritasıyla içerik önceliği seçin",
        ],
        "faq": [
            {
                "q": "Tek kaynak yeter mi?",
                "a": "Hayır. Web, harita ve klinik kayıtları birlikte doğrulanır.",
            },
            {
                "q": "KVKK?",
                "a": "Bireysel adres yerine aggregate semt/şehir analizi kullanın.",
            },
            {
                "q": "Ne sıklıkla?",
                "a": "Haftalık operasyon özeti, aylık strateji ısı haritası.",
            },
        ],
        "sections": [
            (
                "Veri birleştirme",
                "Aynı dönem için web, harita ve randevu verisini tek panele alın.",
            ),
            (
                "Karar",
                "Yüksek niyetli semtlere içerik/GMB fotoğrafı; düşük dönüşümlülere süreç düzeltmesi.",
            ),
            (
                "AI citation ölçümü",
                "Bölgesel promptlarla mention oranını ayrıca skorlayın.",
            ),
        ],
        "path": "/urunler",
    },
    {
        "file": "geo-seo-08-yerel-backlink.png",
        "bucket": "karsilastirma",
        "tag": "GEO",
        "title": "Yerel Link Building: Geo SEO'nun Gizli Silahı",
        "prompt": "Yerel backlink (link building) Geo SEO'da neden kritik ve nasıl yapılır?",
        "direct_answer": (
            "Yerel backlink’ler klinik entity’sine şehir içi güven oyları ekler: yerel haber, "
            "rehber, sağlık blogu, etkinlik ve randevu platformları. Merkezde güçlenen klinik "
            "sitesi harita ve AI önerilerinde daha sık geçer. Kalite > miktar; spam dizinlerden "
            "kaçının. İşbirliği ve faydalı içerik doğal link üretir."
        ),
        "bullets": [
            "Yerel haber/rehberlerde tutarlı NAP kaydı açın",
            "Sağlık bloglarıyla uzman röportajı planlayın",
            "DoktorTakvimi vb. platform profillerini güncelleyin",
            "Her çeyrekte toksik link denetimi yapın",
        ],
        "faq": [
            {
                "q": "Link satın alınır mı?",
                "a": "Riskli ve genelde değersizdir; editorial/yerel ortaklık tercih edilir.",
            },
            {
                "q": "Kaç link ideal?",
                "a": "Sayı değil; ilgili, yerel, takip edilebilir kaynaklar önemlidir.",
            },
            {
                "q": "Anchor text?",
                "a": "Marka + doğal şehir/hizmet varyasyonları; aşırı optimize etmeyin.",
            },
        ],
        "sections": [
            (
                "Yerel grafik",
                "Haber, rehber, blog, etkinlik ve randevu siteleri klinik etrafında güven ağı kurar.",
            ),
            (
                "İçerik yemi",
                "Veri odaklı yerel raporlar ve uzman görüşleri doğal backlink çeker.",
            ),
            (
                "Ölçüm",
                "Referring domain kalitesi ve marka araması artışı takip edilir.",
            ),
        ],
        "path": "/kaynaklar",
    },
    {
        "file": "geo-seo-09-mobil-hiz.png",
        "bucket": "problem",
        "tag": "GEO",
        "title": "Mobil Öncelikli Geo SEO: Klinik Siteniz Mobil Uyumlu mu?",
        "prompt": "Mobil öncelikli Geo SEO için klinik web sitesi neyi sağlamalı?",
        "direct_answer": (
            "Mobil öncelikli Geo SEO için site hızlı yüklenmeli, tıklanabilir CTA’lar "
            "(ara, yol tarifi, randevu) üstte olmalı ve Core Web Vitals hedefleri "
            "karşılanmalıdır. ‘Yakınımdaki klinik’ trafiğinin çoğu mobildir; yavaş sayfa "
            "harita tıklamasını boşa çıkarır. AMP şart değil; iyi performans ve net NAP yeter."
        ),
        "bullets": [
            "LCP/INP/CLS değerlerini ölçüp düzeltin",
            "Üstte Ara / Yol Tarifi / Randevu butonları koyun",
            "Görselleri sıkıştırın, gereksiz script kesin",
            "Mobil formları 3 alandan fazla tutmayın",
        ],
        "faq": [
            {
                "q": "Masaüstü iyi, mobil kötüyse?",
                "a": "Google mobil-first tarar; yerel pakette mobil deneyim baskındır.",
            },
            {
                "q": "Hız skoru hedefi?",
                "a": "PageSpeed mobil ‘iyi’ bandı; rakiplerden belirgin yavaş kalmayın.",
            },
            {
                "q": "PWA gerekir mi?",
                "a": "Şart değil; hızlı, güvenli (HTTPS) ve mobil UX önceliklidir.",
            },
        ],
        "sections": [
            (
                "Hız = hasta",
                "Yavaşlık sembollerini kırın: sıkıştırma, cache, kritik CSS.",
            ),
            (
                "Yerel CTA",
                "Tek elle arama ve yol tarifi, sesli/harita trafiğini randevuya çevirir.",
            ),
            (
                "Ölçüm",
                "Search Console mobil usability + CrUX verisini aylık izleyin.",
            ),
        ],
        "path": "/",
    },
    {
        "file": "geo-seo-10-otomasyon-kontrol.png",
        "bucket": "marka",
        "tag": "GEO",
        "title": "Nefalix AI ile Geo SEO Otomasyonu: Zaman Kazanın, Hasta Sayısını Artırın",
        "prompt": "Nefalix AI ile Geo SEO otomasyonu ne işe yarar?",
        "direct_answer": (
            "Nefalix AI Geo SEO otomasyonu; yorum yanıtlama taslakları, yerel içerik/GEO "
            "paket planı, sıralama-citation takibi ve hasta kaynak analizini tek operasyon "
            "disiplininde birleştirir. Amaç manuel checklist’i azaltıp tutarlı public "
            "sinyal üretmektir. Otomasyon, insan onayını kaldırmaz; hızlandırır. Ölçüm "
            "haftalık citation ve yorum akışıyla yapılır."
        ),
        "bullets": [
            "Günlük GEO paketini yayınlayın (/geo/tarih)",
            "Yorum taslağını onay kuyruğuna alın",
            "Semt içerik takvimini otomatik önerin",
            "Citation + GBP Insights’ı haftalık raporlayın",
        ],
        "faq": [
            {
                "q": "Tamamen otomatik mi?",
                "a": "Kritik yayınlar (yorum/kriz) onaylıdır; üretim ve hatırlatma otomatiktir.",
            },
            {
                "q": "Blog ile farkı?",
                "a": "Blog playbook; GEO paketi AI alıntı birimi; ikisi birlikte çalışır.",
            },
            {
                "q": "Başarı metriği?",
                "a": "Citation rate, yorum hacmi, harita aksiyonları ve randevu kaynağı.",
            },
        ],
        "sections": [
            (
                "Kontrol odası",
                "Yorum, içerik, sıralama, rakip ve SEO sağlık panelleri aynı bakışta izlenir.",
            ),
            (
                "Zaman kazancı",
                "Tekrarlayan checklist’ler otomasyona; strateji insana kalır.",
            ),
            (
                "Büyüme döngüsü",
                "Veri topla → analiz et → uygula → ölç → yeniden planla.",
            ),
        ],
        "path": "/geo",
    },
]


def proxy(method: str, table: str, query: str = "", body=None):
    if not INTERNAL_KEY:
        raise SystemExit("NEFALIX_INTERNAL_KEY eksik")
    payload = {
        "method": method,
        "table": table,
        "query": query,
        "prefer": "return=representation",
    }
    if body is not None:
        payload["body"] = body
    req = urllib.request.Request(
        PROXY,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Nefalix-Internal-Key": INTERNAL_KEY,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"proxy {e.code}: {e.read().decode()[:600]}") from e


def to_answer_html(prompt: str, direct: str, bullets: list, faq: list, links: list) -> str:
    parts = [
        f"<h2>{html.escape(prompt)}</h2>",
        f"<p><strong>{html.escape(direct)}</strong></p>",
        "<ul>",
    ]
    for b in bullets:
        parts.append(f"<li>{html.escape(b)}</li>")
    parts.append("</ul><h3>Sık sorulanlar</h3><dl>")
    for item in faq:
        parts.append(
            f"<dt><strong>{html.escape(item['q'])}</strong></dt><dd>{html.escape(item['a'])}</dd>"
        )
    parts.append("</dl><p>İlgili: ")
    parts.append(
        " · ".join(f'<a href="{html.escape(u)}">{html.escape(u)}</a>' for u in links)
    )
    parts.append("</p>")
    return "\n".join(parts)


def blog_html(pack: dict, cover: str) -> str:
    parts = [
        f'<p class="blog-lede"><strong>{html.escape(pack["direct_answer"])}</strong></p>',
        '<div class="blog-takeaways"><h2>Öne çıkanlar</h2><ul>',
    ]
    for b in pack["bullets"]:
        parts.append(f"<li>{html.escape(b)}</li>")
    parts.append("</ul></div>")
    for h, body in pack["sections"]:
        parts.append(f"<h2>{html.escape(h)}</h2>")
        parts.append(f"<p>{html.escape(body)}</p>")
    parts.append('<div class="blog-checklist"><h2>Uygulama kontrol listesi</h2><ul>')
    for b in pack["bullets"]:
        parts.append(f"<li>{html.escape(b)}</li>")
    parts.append("</ul></div>")
    parts.append("<h2>Sık sorulan sorular</h2>")
    for item in pack["faq"]:
        parts.append(
            f'<div class="faq-item"><h3>{html.escape(item["q"])}</h3>'
            f'<p>{html.escape(item["a"])}</p></div>'
        )
    parts.append(
        f'<p><img src="{html.escape(cover)}" alt="" loading="lazy" '
        f'style="max-width:100%;border-radius:16px;margin:1.5em 0;"></p>'
    )
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--geo-only", action="store_true")
    parser.add_argument("--blog-only", action="store_true")
    parser.add_argument(
        "--start",
        default="today",
        help="İlk paket günü: today veya YYYY-MM-DD (default: today)",
    )
    parser.add_argument(
        "--include-future",
        action="store_true",
        help="run_date > bugün olan paketleri de yaz (sitemap için önerilmez)",
    )
    args = parser.parse_args()

    start = resolve_start(args.start)
    today = date.today()
    results: dict = {"geo": [], "blog": [], "skipped": []}
    for i, pack in enumerate(PACKS):
        run_date_obj = start + timedelta(days=i)
        if run_date_obj > today and not args.include_future:
            results["skipped"].append(
                {
                    "index": i,
                    "run_date": run_date_obj.isoformat(),
                    "reason": "future_date",
                }
            )
            continue
        run_date = run_date_obj.isoformat()
        geo_url = f"{SITE}/geo/{run_date}"
        links = [
            geo_url,
            f"{SITE}{pack['path']}",
            f"{SITE}/geo",
            f"{SITE}/blog",
        ]
        cover = cover_raw(pack["file"])
        # fallback API cover if raw 404 later; still set raw first
        geo_row = {
            "run_date": run_date,
            "bucket": pack["bucket"],
            "prompt": pack["prompt"],
            "direct_answer": pack["direct_answer"],
            "bullets": pack["bullets"],
            "faq": pack["faq"],
            "internal_links": links,
            "linkedin_one_liner": pack["direct_answer"][:220],
            "answer_html": to_answer_html(
                pack["prompt"], pack["direct_answer"], pack["bullets"], pack["faq"], links
            ),
            "status": "published",
        }
        slug = slugify(pack["title"])
        published_at = datetime(
            run_date_obj.year,
            run_date_obj.month,
            run_date_obj.day,
            9,
            5,
            tzinfo=timezone.utc,
        )
        blog_row = {
            "slug": slug,
            "title": pack["title"],
            "tag": pack["tag"],
            "excerpt": pack["direct_answer"][:220],
            "body_html": blog_html(pack, cover),
            "meta_description": pack["direct_answer"][:155],
            "status": "published",
            "published_at": published_at.isoformat(),
            "cover_image_url": cover,
            "footer_image_url": cover_api("footer", pack["tag"], "Nefalix"),
        }

        if args.dry_run:
            if not args.blog_only:
                results["geo"].append({"run_date": run_date, "prompt": pack["prompt"], "cover": cover})
            if not args.geo_only:
                results["blog"].append({"slug": slug, "title": pack["title"], "cover": cover})
            continue

        if not args.blog_only:
            # upsert: delete day then insert (unique run_date)
            proxy("DELETE", "geo_daily_runs", query=f"run_date=eq.{run_date}")
            out = proxy("POST", "geo_daily_runs", body=geo_row)
            results["geo"].append(
                {"run_date": run_date, "ok": bool(out.get("ok", True)), "url": geo_url}
            )

        if not args.geo_only:
            # upsert by slug
            proxy("DELETE", "blog_posts", query=f"slug=eq.{slug}")
            out = proxy("POST", "blog_posts", body=blog_row)
            results["blog"].append(
                {
                    "slug": slug,
                    "ok": bool(out.get("ok", True)),
                    "url": f"{SITE}/blog/{slug}",
                    "cover": cover,
                }
            )

    print(json.dumps({"ok": True, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
