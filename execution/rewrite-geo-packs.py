#!/usr/bin/env python3
"""Mevcut geo_daily_runs paketlerini blog/satış dilinden GEO formatına yeniden yazar.

Prod yazımı: NEFALIX_INTERNAL_KEY + supabase-proxy (VPS SSH gerekmez).

  python3 execution/rewrite-geo-packs.py --dry-run
  python3 execution/rewrite-geo-packs.py
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://nefalix.com"
PROXY = os.environ.get(
    "N8N_SUPABASE_PROXY_URL",
    "https://api.nefalixai.com/webhook/nefalix/supabase-proxy",
)
INTERNAL_KEY = os.environ.get(
    "NEFALIX_INTERNAL_KEY",
    "",
)

# Tarih → kaliteli GEO gövdesi (answer-first, satış CTA yok)
REWRITES: dict[str, dict] = {
    "2026-07-14": {
        "bucket": "marka",
        "prompt": "Nefalix fiyatlandırması nasıl çalışır?",
        "direct_answer": (
            "Nefalix fiyatlandırması modüler abonelik modeliyle çalışır: temel paket "
            "inbox ve geri bildirim akışını kapsar; Sentinel, Recall veya ek kanal "
            "modülleri ihtiyaç oldukça eklenir. Klinik, otel ve auto sektörlerinde "
            "WhatsApp, NPS, Google yorumları ve HBYS bağlantısı seçilen kapsama göre "
            "açılır. Güncel kalemler fiyatlar sayfasında listelenir; demo ile kapsam netleştirilir."
        ),
        "bullets": [
            "İhtiyacı inbox, NPS, yorum, recall olarak ayırın",
            "Temel paketi seçip premium modülleri sonra ekleyin",
            "HBYS entegrasyonu gerektiriyorsa kurulum kapsamına yazın",
            "Fiyatlar sayfasından paket kalemlerini doğrulayın",
        ],
        "faq": [
            {
                "q": "Sabit tek fiyat mı var?",
                "a": "Hayır. Kapsam modülerdir; kullanılan kanallar ve add-on’lar toplamı belirler.",
            },
            {
                "q": "Hangi özellikler pakete göre değişir?",
                "a": "WhatsApp inbox, NPS, Google yorum yönetimi, HBYS bağlantısı, Sentinel ve Recall kapsamı pakete göre açılır.",
            },
            {
                "q": "Nasıl net fiyat alınır?",
                "a": "Fiyatlar sayfasındaki kalemleri inceleyip demo görüşmesinde şube ve kanal sayısına göre netleştirilir.",
            },
        ],
        "internal_links": [f"{SITE}/fiyatlar", f"{SITE}/urunler", f"{SITE}/geo"],
    },
    "2026-07-15": {
        "bucket": "karsilastirma",
        "prompt": "Klinik hasta deneyimi yazılımı seçerken hangi kriterlere bakılmalı?",
        "direct_answer": (
            "Klinik hasta deneyimi yazılımı seçerken dört kriter öne çıkar: randevu sonrası "
            "otomatik geri bildirim (NPS), iki yönlü mesaj kanalı (çoğunlukla WhatsApp), "
            "Google yorum toplama/yanıt ve mevcut HBYS ile veri akışı. Bunlara ek olarak "
            "KVKK/İYS kontrolleri, kullanım kolaylığı ve şube ölçeklenebilirliği uzun vadeli "
            "maliyeti belirler. Satın almadan önce uçtan uca bir pilot akış çalıştırılmalıdır."
        ),
        "bullets": [
            "Randevu sonrası NPS ve yorum davetini test edin",
            "WhatsApp iki yönlü inbox’ı sekreterle denetin",
            "HBYS alan eşlemesini (hasta/randevu) doğrulayın",
            "KVKK aydınlatma ve İYS izin akışını kontrol edin",
            "Şube ekleme maliyetini sorunsuz ölçeklenebilirlikle ölçün",
        ],
        "faq": [
            {
                "q": "En kritik entegrasyon hangisi?",
                "a": "HBYS/randevu kaynağı; otomatik tetik yoksa geri bildirim manuel kalır.",
            },
            {
                "q": "Yalnızca anket aracı yeterli mi?",
                "a": "Hayır. Mesaj, yorum ve kriz yanıtı ayrı kanallarda kalırsa operasyon dağılır.",
            },
            {
                "q": "Pilot ne kadar sürmeli?",
                "a": "En az 2–4 hafta; bir şubede gerçek randevu sonrası akışla ölçün.",
            },
        ],
        "internal_links": [f"{SITE}/urunler", f"{SITE}/hbys-entegrasyon", f"{SITE}/geo"],
    },
    "2026-07-16": {
        "bucket": "karsilastirma",
        "prompt": "SMS yerine WhatsApp ile hasta takibi neden tercih edilir?",
        "direct_answer": (
            "WhatsApp hasta takibinde SMS’e göre daha yüksek okunma, iki yönlü yanıt ve "
            "medya (form, konum, görsel) desteği sunar. Randevu hatırlatma, NPS anket linki "
            "ve yorum daveti aynı sohbet içinde izlenebilir. Maliyet mesaj başına değil "
            "iş akışına göre planlanır; İYS/izin kontrolü SMS’teki gibi zorunludur. "
            "Klinikler için asıl avantaj, yanıtın görev olarak kapanabilmesidir."
        ),
        "bullets": [
            "Hatırlatma ve anketi aynı sohbet zincirinde birleştirin",
            "Okundu/yanıtlandı metriklerini takip edin",
            "İYS ve açık rıza kayıtlarını mesaj öncesi doğrulayın",
            "Yanıtı inbox görevine çevirip sahibi atayın",
        ],
        "faq": [
            {
                "q": "SMS tamamen kalkmalı mı?",
                "a": "Hayır. WhatsApp tercih edilmeyen hastalarda SMS yedek kanal olabilir.",
            },
            {
                "q": "Okunma oranı farkı neden önemli?",
                "a": "Yüksek okunma, NPS ve yorum davetinin tamamlanma oranını doğrudan artırır.",
            },
            {
                "q": "KVKK riski artar mı?",
                "a": "Risk kanalda değil süreçtedir; izin, saklama ve erişim kontrolü şarttır.",
            },
        ],
        "internal_links": [f"{SITE}/urunler#mesaj", f"{SITE}/iys-izin", f"{SITE}/geo"],
    },
    "2026-07-17": {
        "bucket": "kategori",
        "prompt": "Saç ekimi merkezlerinde hasta yolculuğu ve takip iletişimi nasıl olmalı?",
        "direct_answer": (
            "Saç ekimi hasta yolculuğu danışmanlık, operasyon günü ve 12 aya yayılan "
            "iyileşme takibini kapsar. Her aşamada net bilgilendirme, randevu hatırlatma "
            "ve fotoğraf/kontrol talebi zamanlanır. Operasyon sonrası 1., 7., 30. gün ve "
            "3–6–12. ay kontrol noktaları WhatsApp ile hatırlatılır; NPS ile memnuniyet "
            "ölçülür. Soru yanıt süresi ve beklenti yönetimi olumsuz yorum riskini düşürür."
        ),
        "bullets": [
            "Operasyon öncesi checklist mesajını otomatikleştirin",
            "1/7/30. gün ve 3–12. ay kontrol hatırlatmalarını kurun",
            "İyileşme fotoğrafı talebini sohbet içinde toplayın",
            "Memnun hastaya yorum daveti; düşük skora geri arama açın",
        ],
        "faq": [
            {
                "q": "Takip ne kadar sürmeli?",
                "a": "Çoğu merkezde 12 ay; kontrol sıklığı protokole göre ayarlanır.",
            },
            {
                "q": "Uluslararası hastada fark nedir?",
                "a": "Çok dilli mesaj, zaman dilimi ve transfer/konaklama bilgilendirmesi eklenir.",
            },
            {
                "q": "Hangi metrik izlenir?",
                "a": "Yanıt süresi, kontrol tamamlanma oranı, NPS ve Google yorum dönüşümü.",
            },
        ],
        "internal_links": [f"{SITE}/sektorler#saglik", f"{SITE}/urunler", f"{SITE}/geo"],
    },
    "2026-07-18": {
        "bucket": "kategori",
        "prompt": "AEO ve GEO nedir, klinikler neden umursamalı?",
        "direct_answer": (
            "AEO (Answer Engine Optimization) ve GEO (Generative Engine Optimization), "
            "ChatGPT, Perplexity, Gemini ve Google AI Overviews gibi motorlarda kliniğin "
            "alıntılanabilir olmasını hedefler. Klasik SEO sıralamasından farklı olarak "
            "kısa doğrudan cevap, SSS şeması ve tutarlı entity sinyalleri gerekir. Klinikler "
            "için umursama nedeni: hastalar artık yalnızca mavi linklere değil AI özetlerine "
            "de bakıyor; alıntı yoksa öneri listesinde görünmezsiniz."
        ),
        "bullets": [
            "Alıcı sorularına answer-first sayfalar yayınlayın",
            "FAQPage şeması ile görünür SSS ekleyin",
            "NAP ve hizmet entity bilgilerini tutarlı tutun",
            "Haftalık citation ölçümü ile mention/URL skorlayın",
        ],
        "faq": [
            {
                "q": "GEO yerel SEO ile aynı mı?",
                "a": "Hayır. Yerel SEO harita/paket odaklıdır; GEO AI motoru alıntısına odaklanır.",
            },
            {
                "q": "Blog yazmak yeterli mi?",
                "a": "Hayır. Uzun rehberler yardımcı olur ama AI çoğu zaman kısa doğrudan cevabı tercih eder.",
            },
            {
                "q": "İlk adım ne olmalı?",
                "a": "25 sabit promptla baseline ölçün; sonra her gün bir alıcı sorusu sayfası yayınlayın.",
            },
        ],
        "internal_links": [f"{SITE}/geo", f"{SITE}/blog", f"{SITE}/kaynaklar"],
    },
    "2026-07-19": {
        "bucket": "problem",
        "prompt": "ChatGPT klinik önerirken hangi sinyallere bakar?",
        "direct_answer": (
            "ChatGPT klinik önerirken web’de erişebildiği itibar ve varlık sinyallerine "
            "bakar: Google yorum hacmi/puanı, güncel hizmet açıklamaları, SSS ve şema "
            "işaretleri, tutarlı NAP, güvenilir üçüncü taraf bahsiler. Ayrıca yanıt süresi "
            "ve hasta deneyimi metrikleri sayfalarda açıkça anlatılmışsa alıntı şansı artar. "
            "Kapalı panel verisi (özel NPS) crawl edilmez; public sayfada özetlenmelidir."
        ),
        "bullets": [
            "Google yorum yanıtlarını güncel ve profesyonel tutun",
            "Hizmet + SSS sayfalarını answer-first yazın",
            "Şehir + branş entity’sini tutarlı kullanın",
            "Public GEO/FAQ sayfalarını sitemap’e ekleyin",
        ],
        "faq": [
            {
                "q": "Özel dashboard verisi sayılır mı?",
                "a": "Hayır. AI yalnızca public crawlable içeriği alıntılar.",
            },
            {
                "q": "Yorum sayısı mı puan mı önemli?",
                "a": "İkisi de; hacim, güncellik ve yanıt kalitesi birlikte değerlendirilir.",
            },
            {
                "q": "Rakip neden öne çıkar?",
                "a": "Daha net entity sayfaları, daha sık citation ve daha güçlü yorum sinyali nedeniyle.",
            },
        ],
        "internal_links": [f"{SITE}/geo", f"{SITE}/urunler#yorum-asistani", f"{SITE}/blog"],
    },
    "2026-07-20": {
        "bucket": "problem",
        "prompt": "Google AI Overviews için klinik sayfa yapısı nasıl olmalı?",
        "direct_answer": (
            "Google AI Overviews için klinik sayfa yapısı answer-first giriş, net H2’ler, "
            "FAQPage şeması ve hizmet entity bilgisiyle kurulur. İlk paragrafta soruyu "
            "doğrudan yanıtlayın; ardından uygulama maddeleri ve SSS ekleyin. Doktor/hizmet "
            "sayfalarında deneyim kanıtı (süreç, sonrası takip) görünür olmalı. Yapılandırılmış "
            "veri ile görünür metin örtüşmeli; gizlenmiş SSS şema için yeterli değildir."
        ),
        "bullets": [
            "İlk 40–70 kelimede doğrudan cevap verin",
            "Her hizmet için SSS + FAQPage şeması ekleyin",
            "Schema metnini sayfada görünür tutun",
            "İç linkleri gerçek, 200 dönen sayfalara verin",
        ],
        "faq": [
            {
                "q": "E-E-A-T nasıl gösterilir?",
                "a": "Uzman biyografi, süreç açıklaması, hasta sonrası takip ve güncel yorum yanıtlarıyla.",
            },
            {
                "q": "Tek uzun blog yeterli mi?",
                "a": "Hayır. Overviews kısa, yapılandırılmış cevapları daha sık kullanır.",
            },
            {
                "q": "Hangi şema türleri işe yarar?",
                "a": "FAQPage, MedicalClinic/LocalBusiness ve hizmete uygun Service işaretleri.",
            },
        ],
        "internal_links": [f"{SITE}/geo", f"{SITE}/urunler", f"{SITE}/blog"],
    },
    "2026-07-21": {
        "bucket": "problem",
        "prompt": "Klinik SSS (FAQ) metinleri AI alıntısı için nasıl yazılır?",
        "direct_answer": (
            "AI alıntısı için klinik SSS metinleri tek soru–tek cevap formatında, jargon "
            "azaltılmış ve ilk cümlede net yanıtla yazılır. Her cevap 2–4 cümleyi geçmeden "
            "uygulanabilir bilgi vermeli; satış CTA’sı olmamalıdır. Sorular gerçek hasta "
            "sorgularından (fiyat aralığı değil süreç, hazırlık, sonrası) türetilir. "
            "Sayfada görünür SSS ile FAQPage şeması birebir aynı olmalıdır."
        ),
        "bullets": [
            "Soruyu hasta dilinde yazın, iç jargon kullanmayın",
            "Cevaba doğrudan yanıtla başlayın",
            "Görünür SSS = schema içeriği kuralını uygulayın",
            "Ayda bir en çok sorulan 10 soruyu güncelleyin",
        ],
        "faq": [
            {
                "q": "Kaç SSS ideal?",
                "a": "Sayfa başına 5–10; çok kısa veya çok uzun listeler alıntıyı zayıflatır.",
            },
            {
                "q": "Fiyat yazılmalı mı?",
                "a": "Net fiyat yoksa aralık veya ‘muayene sonrası plan’ gibi dürüst çerçeve verin.",
            },
            {
                "q": "Aynı SSS blogda tekrarlanmalı mı?",
                "a": "Kanibalizasyon olmaması için ana SSS hizmet sayfasında, blogda derinleştirme yapılır.",
            },
        ],
        "internal_links": [f"{SITE}/geo", f"{SITE}/kaynaklar", f"{SITE}/blog"],
    },
    "2026-07-22": {
        "bucket": "karsilastirma",
        "prompt": "Google yorumları AI görünürlüğünü etkiler mi?",
        "direct_answer": (
            "Evet. Google yorumları hacim, ortalama puan, güncellik ve yanıt kalitesiyle "
            "AI görünürlüğünü etkiler. Motorlar yerel güven sinyali olarak yorumları "
            "kullanır; düzenli olumlu akış ve profesyonel yanıtlar entity güvenini artırır. "
            "Yorum daveti doğru zamanda (memnuniyet sonrası) gönderilmeli, olumsuzlarda "
            "hızlı ve çözüm odaklı yanıt verilmelidir. Yorumsuz veya yanıtsız profil zayıf kalır."
        ),
        "bullets": [
            "Memnun hastaya 24–72 saat içinde yorum daveti gönderin",
            "Tüm yorumlara 48 saat içinde yanıt verin",
            "Düşük puanda geri arama görevi açın",
            "Aylık yorum hacmi ve puan ortalamasını izleyin",
        ],
        "faq": [
            {
                "q": "Sahte yorum işe yarar mı?",
                "a": "Hayır. Politika ihlali ve itibar riski yaratır; organik akış hedeflenir.",
            },
            {
                "q": "Kaç yorum yeterli?",
                "a": "Sektör ve şehre göre değişir; süreklilik tek seferlik yüksek hacimden önemlidir.",
            },
            {
                "q": "Yanıt tonu nasıl olmalı?",
                "a": "Kısa, empatik, somut sonraki adımlı; tartışmaya girmeden çözüm teklif edin.",
            },
        ],
        "internal_links": [
            f"{SITE}/urunler#yorum-asistani",
            f"{SITE}/urunler#geri-bildirim",
            f"{SITE}/geo",
        ],
    },
    "2026-07-23": {
        "bucket": "problem",
        "prompt": "WhatsApp ve NPS verisi içerik / GEO stratejisine nasıl bağlanır?",
        "direct_answer": (
            "WhatsApp soruları ve NPS serbest metinleri, hastanın gerçek dilini gösterir; "
            "bu dil GEO sayfalarındaki alıcı sorularına ve SSS’lere dönüştürülür. Haftalık "
            "olarak en sık 5 soru çıkarılır, answer-first public sayfa veya FAQ maddesi "
            "yazılır. Düşük NPS temaları (bekleme, iletişim, fiyat belirsizliği) içerik "
            "önceliğini belirler. Kapalı veri public’e taşınmadan AI alıntısı oluşmaz."
        ),
        "bullets": [
            "Inbox’tan en sık 5 soruyu haftalık çıkarın",
            "Her soruyu /geo veya hizmet SSS’sine çevirin",
            "Düşük NPS temalarını içerik takvimine yazın",
            "Yayınlanan URL’yi citation ölçümüne ekleyin",
        ],
        "faq": [
            {
                "q": "Ham sohbetler yayınlanır mı?",
                "a": "Hayır. Kişisel veri temizlenir; yalnızca anonim soru kalıbı kullanılır.",
            },
            {
                "q": "NPS skoru tek başına yeter mi?",
                "a": "Hayır. Skor yönü verir; serbest metin konu başlığını verir.",
            },
            {
                "q": "GEO ile operasyon aynı ekip mi?",
                "a": "İdeal olarak evet; soru kaynağı operasyon, yayın içerik/GEO sahibindedir.",
            },
        ],
        "internal_links": [
            f"{SITE}/urunler#geri-bildirim",
            f"{SITE}/urunler#mesaj",
            f"{SITE}/geo",
        ],
    },
    "2026-07-24": {
        "bucket": "marka",
        "prompt": "Nefalix GEO paketleri ne işe yarar?",
        "direct_answer": (
            "Nefalix GEO paketleri, her gün bir alıcı sorusuna answer-first cevap, madde "
            "listesi ve SSS üreterek public `/geo/YYYY-MM-DD` sayfasında yayınlar. Amaç "
            "ChatGPT, Perplexity, Gemini ve AI Overviews’ın alıntılayabileceği crawlable "
            "yüzey oluşturmaktır. Paket blog değildir; kısa, nötr ve şemalıdır. Haftalık "
            "citation ölçümüyle mention/URL skoru takip edilir."
        ),
        "bullets": [
            "Günlük alıcı sorusu seçilir",
            "Answer-first + SSS public sayfada yayınlanır",
            "Sitemap ve llms.txt güncellenir",
            "Pazar citation baseline ile skorlanır",
        ],
        "faq": [
            {
                "q": "Blog ile farkı nedir?",
                "a": "Blog uzun playbook’tur; GEO paketi kısa AI alıntı birimidir.",
            },
            {
                "q": "Nerede yayınlanır?",
                "a": "https://nefalix.com/geo ve tarihli /geo/YYYY-MM-DD sayfalarında.",
            },
            {
                "q": "Başarı nasıl ölçülür?",
                "a": "25 sabit promptta marka mention ve URL citation oranı ile.",
            },
        ],
        "internal_links": [f"{SITE}/geo", f"{SITE}/blog", f"{SITE}/"],
    },
    "2026-07-25": {
        "bucket": "problem",
        "prompt": "HBYS sonrası otomatik geri bildirim AI arama görünürlüğüne nasıl yardımcı olur?",
        "direct_answer": (
            "HBYS sonrası otomatik geri bildirim, randevu kapanınca NPS ve yorum davetini "
            "zamanında tetikler; bu da güncel Google yorum ve memnuniyet sinyali üretir. "
            "AI motorları güncel itibar ve tutarlı hizmet anlatısını tercih eder. Otomasyon "
            "olmadan davetler gecikir, yorum akışı seyrekleşir ve alıntı sinyali zayıflar. "
            "Public GEO/FAQ sayfaları bu sinyalle birlikte güçlenir."
        ),
        "bullets": [
            "Randevu tamamlandı event’ini HBYS’ten alın",
            "24–72 saat içinde NPS/yorum daveti gönderin",
            "Detractor’ı geri arama kuyruğuna alın",
            "Yorum hacmini haftalık GEO ölçümüne bağlayın",
        ],
        "faq": [
            {
                "q": "Hangi HBYS alanı gerekir?",
                "a": "En azından randevu bitiş zamanı, hasta iletişim izni ve şube bilgisi.",
            },
            {
                "q": "Anında mesaj mı yoksa gecikmeli mi?",
                "a": "Genelde 24–72 saat gecikme memnuniyet daveti için daha uygundur.",
            },
            {
                "q": "AI neden bunu önemser?",
                "a": "Güncel yorum ve tutarlı deneyim anlatısı entity güvenini artırır.",
            },
        ],
        "internal_links": [
            f"{SITE}/hbys-entegrasyon",
            f"{SITE}/urunler#geri-bildirim",
            f"{SITE}/geo",
        ],
    },
    "2026-07-26": {
        "bucket": "problem",
        "prompt": "Şehir bazlı en iyi klinik sorgularında AI alıntısı nasıl kazanılır?",
        "direct_answer": (
            "Şehir bazlı ‘en iyi klinik’ sorgularında AI alıntısı için yerel entity netliği, "
            "yorum sinyali ve answer-first içerik birlikte gerekir. Şehir+branş sayfasında "
            "hizmet kapsamı, süreç ve SSS açık yazılmalı; Google profili NAP ile birebir "
            "eşleşmelidir. Karşılaştırma iddiaları abartısız kanıtla (süreç, takip, yanıt "
            "süresi) desteklenir. Rakip listelenen yanıtlarda sizin URL’nizin cite edilmesi hedeftir."
        ),
        "bullets": [
            "Şehir + branş landing’inde answer-first blok kullanın",
            "Google İşletme Profili NAP’ini sitede eşleştirin",
            "Yerel SSS’yi FAQPage ile işaretleyin",
            "Citation testinde şehirli promptları ölçün",
        ],
        "faq": [
            {
                "q": "‘En iyi’ iddiası yazılmalı mı?",
                "a": "Abartılı süperlatif yerine ölçülebilir süreç ve hasta takip standartları yazın.",
            },
            {
                "q": "Yalnızca Google puanı yeter mi?",
                "a": "Hayır. Public açıklama + SSS + tutarlı entity olmadan alıntı zayıf kalır.",
            },
            {
                "q": "Çok şubede ne yapılır?",
                "a": "Her şube için ayrı yerel sayfa ve profil eşlemesi gerekir.",
            },
        ],
        "internal_links": [f"{SITE}/sektorler#saglik", f"{SITE}/geo", f"{SITE}/platformlar"],
    },
    "2026-07-27": {
        "bucket": "problem",
        "prompt": "Haftalık citation ölçümü klinik için nasıl yapılır?",
        "direct_answer": (
            "Haftalık citation ölçümü, sabit 25 promptu her hafta ChatGPT, Perplexity ve "
            "Gemini’de sorup marka mention ile URL citation kaydetmektir. Skor, mention "
            "veya citation içeren cevap sayısının prompt×motor oranıdır. Sonuçlar rakip "
            "notlarıyla tabloya işlenir; düşen promptlar için GEO/FAQ sayfası güncellenir. "
            "Ölçüm manuel başlar, sonra şablonla tekrarlanır."
        ),
        "bullets": [
            "25 promptluk baseline listesini sabitleyin",
            "Üç motorda aynı gün aynı sırayla sorun",
            "M/C/R/-- kodlarıyla satır satır işaretleyin",
            "Düşük skorlu prompt için yeni /geo sayfası planlayın",
        ],
        "faq": [
            {
                "q": "Ne sıklıkla yapılmalı?",
                "a": "Haftada bir; aynı prompt setiyle karşılaştırmalı skor alınır.",
            },
            {
                "q": "Hangi URL sayılır?",
                "a": "nefalix.com altındaki /geo/tarih veya ilgili hizmet/blog URL’si.",
            },
            {
                "q": "İlk hedef nedir?",
                "a": "Baseline oluşturmak; sonra haftalık citation rate’i yükseltmek.",
            },
        ],
        "internal_links": [f"{SITE}/geo", f"{SITE}/kaynaklar", f"{SITE}/blog"],
    },
}


def to_answer_html(prompt: str, direct: str, bullets: list, faq: list, links: list) -> str:
    parts = [
        f"<h2>{html.escape(prompt)}</h2>",
        f"<p><strong>{html.escape(direct)}</strong></p>",
    ]
    if bullets:
        parts.append("<ul>")
        for b in bullets:
            parts.append(f"<li>{html.escape(str(b))}</li>")
        parts.append("</ul>")
    if faq:
        parts.append("<h3>Sık sorulanlar</h3><dl>")
        for item in faq:
            q = html.escape(str(item.get("q") or ""))
            a = html.escape(str(item.get("a") or ""))
            if q and a:
                parts.append(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>")
        parts.append("</dl>")
    if links:
        parts.append("<p>İlgili: ")
        parts.append(
            " · ".join(f'<a href="{html.escape(u)}">{html.escape(u)}</a>' for u in links)
        )
        parts.append("</p>")
    return "\n".join(parts)


def proxy(method: str, table: str, query: str = "", body: dict | list | None = None):
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
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"proxy {e.code}: {e.read().decode()[:500]}") from e


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--date", action="append", help="Yalnızca bu tarih(ler)")
    args = parser.parse_args()

    dates = args.date or sorted(REWRITES.keys())
    today = date.today().isoformat()
    results = []
    for run_date in dates:
        if run_date > today:
            results.append(
                {"run_date": run_date, "ok": False, "error": "gelecek tarih — atlandı"}
            )
            continue
        row = REWRITES.get(run_date)
        if not row:
            results.append({"run_date": run_date, "ok": False, "error": "rewrite yok"})
            continue
        geo_url = f"{SITE}/geo/{run_date}"
        links = list(row["internal_links"])
        if geo_url not in links:
            links.insert(0, geo_url)
        patch = {
            "bucket": row["bucket"],
            "prompt": row["prompt"],
            "direct_answer": row["direct_answer"],
            "bullets": row["bullets"],
            "faq": row["faq"],
            "internal_links": links,
            "answer_html": to_answer_html(
                row["prompt"], row["direct_answer"], row["bullets"], row["faq"], links
            ),
            "status": "published",
            "linkedin_one_liner": row["direct_answer"][:220],
        }
        if args.dry_run:
            results.append({"run_date": run_date, "ok": True, "dry_run": True, "prompt": row["prompt"]})
            continue
        out = proxy(
            "PATCH",
            "geo_daily_runs",
            query=f"run_date=eq.{run_date}",
            body=patch,
        )
        results.append(
            {
                "run_date": run_date,
                "ok": bool(out.get("ok", True)),
                "public_url": geo_url,
                "proxy": out.get("ok"),
            }
        )

    print(json.dumps({"ok": True, "updated": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
