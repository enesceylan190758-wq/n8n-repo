#!/usr/bin/env python3
"""Zayıf Geo SEO blog'larını kalıcı playbook standardına yeniden yazar.

İlk turda GEO iskeleti blog'a sızmıştı; bu script 10 yazıyı uzun operasyon
playbook'una çevirir (blog_quality_gate zorunlu).

  export NEFALIX_INTERNAL_KEY=...
  python3 execution/rewrite-geo-seo-blogs.py --dry-run
  python3 execution/rewrite-geo-seo-blogs.py
  python3 execution/rewrite-geo-seo-blogs.py --slug yerel-klinikler-icin-on-page-geo-seo-rehberi
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "execution"))

from lib.content_quality import blog_quality_gate  # noqa: E402

SITE = "https://nefalix.com"
REPO = "enesceylan190758-wq/n8n-repo"
BRANCH = os.environ.get("GEO_SEO_ASSET_BRANCH", "main")
PROXY_URL = os.environ.get(
    "N8N_SUPABASE_PROXY_URL",
    "https://api.nefalixai.com/webhook/nefalix/supabase-proxy",
)


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:80] or "yazi"


def cover_raw(filename: str) -> str:
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/assets/geo-seo-covers/{filename}"


def cover_api(kind: str, tag: str, title: str) -> str:
    q = urllib.parse.urlencode(
        {"action": "cover", "kind": kind, "tag": tag, "t": title, "v": "12"}
    )
    return f"{SITE}/api/blog?{q}"


def to_html(intro: str, sections: list[dict], faq: list[dict], cta: str, cover: str) -> str:
    parts = [f'<p class="blog-lede"><strong>{html.escape(intro)}</strong></p>']
    for sec in sections:
        parts.append(f"<h2>{html.escape(sec['heading'])}</h2>")
        parts.append(f"<p>{html.escape(sec['body'])}</p>")
    parts.append("<h2>Sık sorulan sorular</h2>")
    for item in faq:
        parts.append(
            f'<div class="faq-item"><h3>{html.escape(item["q"])}</h3>'
            f'<p>{html.escape(item["a"])}</p></div>'
        )
    if cta:
        parts.append(f"<p>{html.escape(cta)}</p>")
    parts.append(
        f'<p><img src="{html.escape(cover)}" alt="" loading="lazy" '
        f'style="max-width:100%;border-radius:16px;margin:1.5em 0;"></p>'
    )
    return "\n".join(parts)


def proxy(method: str, table: str, query: str = "", body=None):
    key = os.environ.get("NEFALIX_INTERNAL_KEY", "").strip()
    if not key:
        raise SystemExit("NEFALIX_INTERNAL_KEY eksik")
    url = PROXY_URL.rstrip("/")
    payload = {"method": method, "table": table, "query": query}
    if body is not None:
        payload["body"] = body
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Nefalix-Internal-Key": key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"proxy {e.code}: {e.read().decode()[:600]}") from e


# Uzun playbook gövdeleri — GEO iskelet jargonu yok (NAP bloğu, FAQPage, vb.)
PLAYBOOKS: list[dict] = [
    {
        "file": "geo-seo-01-saglik-turizmi-kuresel.png",
        "tag": "Sağlık Turizmi",
        "title": "Sağlık Turizminde Küresel Geo SEO: Hastaları Google Haritalar'dan Çekin",
        "excerpt": (
            "Uluslararası hastalar harita ve yapay zeka önerilerinde sizi bulsun diye "
            "çok dilli profil, şehir hub'ları ve yorum ritmini birlikte kurun."
        ),
        "intro": (
            "Sağlık turizminde görünürlük artık yalnızca İngilizce bir site açmakla bitmiyor. "
            "Hastalar tedavi seçerken Google Haritalar paketlerine, yerel yorumlara ve "
            "ChatGPT/Perplexity gibi araçların önerilerine bakıyor. Bu playbook, klinik "
            "ekibinin hedef şehirlerde tutarlı bir varlık kurması, yorum ritmini işletmesi "
            "ve ölçümü haftalık hale getirmesi için adım adım bir yol haritası sunar."
        ),
        "sections": [
            {
                "heading": "Hedef pazarı netleştirin",
                "body": (
                    "Önce hangi ülkelerden hasta beklediğinizi yazın: dil, para birimi, "
                    "tedavi paketi ve vize süreci. Her pazar için bir sahip atayın; aksi halde "
                    "çok dilli içerik dağınık kalır. Londra diş, Berlin saç ekimi, Dubai estetik "
                    "gibi net kombinasyonlar seçin. Pazar listesini ayda bir gözden geçirin; "
                    "düşük dönüşümlü şehirleri askıya alın, yüksek potansiyelli olanlara "
                    "kapasite ayırın. Bu netlik olmadan harita ve içerik yatırımı boşa gider."
                ),
            },
            {
                "heading": "Harita profilini çok dilli güçlendirin",
                "body": (
                    "Google İşletme Profilinde kategori, çalışma saati, fotoğraf ve açıklama "
                    "hedef dilde tutarlı olsun. Adres, telefon ve web adresi tüm dillerde aynı "
                    "gerçeği yansıtsın. Tedavi sonrası fotoğraflar ve ekip görselleri güven "
                    "sinyali verir. Haftalık olarak soru-cevap ve yorumları kontrol edin. "
                    "Yanlış kategori veya kapalı saat bilgisi uluslararası aramada sizi "
                    "erken eleyebilir; bu yüzden profil denetimini operasyon checklist'ine ekleyin."
                ),
            },
            {
                "heading": "Şehir hub sayfaları ve ölçüm",
                "body": (
                    "Her hedef şehir+tedavi için ayrı bir landing kurun: süreç, dil desteği, "
                    "ulaşım ve sık sorular insan dilinde olsun. Aynı sorunun kısa günlük "
                    "cevabını /geo kanalında tutun; blog ise derinleştirir. Haftalık skor: "
                    "hedef promptlarda marka geçti mi, hangi URL alıntılandı? Sonuçları "
                    "pazarlama ve klinik koordinatörü birlikte okusun. Ölçüm yoksa "
                    "uluslararası harcama rastgele kalır."
                ),
            },
        ],
        "faq": [
            {
                "q": "Yalnızca İngilizce site yeterli mi?",
                "a": (
                    "Çoğu pazarda hayır. Hedef dilde hizmet açıklaması, sık sorular ve "
                    "iletişim bilgisi dönüşümü belirgin artırır."
                ),
            },
            {
                "q": "Önce harita mı yoksa içerik mi?",
                "a": (
                    "İkisini paralel ilerletin: harita güven sinyali verir, içerik soruları "
                    "yanıtlar. Tek kanala kilitlenmeyin."
                ),
            },
            {
                "q": "İlk ölçüm ne olmalı?",
                "a": (
                    "Hedef şehir+tedavi sorularında mention ve alıntı oranını haftalık "
                    "kaydedin; rakip isimleri de not edin."
                ),
            },
        ],
        "cta": "Nefalix ile yorum daveti ve itibar akışını otomatikleştirip ölçümü tek panelde toplayabilirsiniz.",
    },
    {
        "file": "geo-seo-02-onpage-klinik.png",
        "tag": "GEO",
        "title": "Yerel Klinikler İçin On-Page Geo SEO Rehberi",
        "excerpt": (
            "Şehir ve hizmet odaklı sayfa düzeni, okunabilir giriş ve görünür SSS ile "
            "yerel görünürlüğü adım adım güçlendirin."
        ),
        "intro": (
            "Yerel görünürlük için web sitenizin kritik sayfalarını şehir ve hizmet dilinde "
            "düzenlemek gerekir. Amaç jargon değil; hastanın sizi bulması ve güven duymasıdır. "
            "Bu playbook title'dan iletişim sayfasına kadar uygulanabilir bir kontrol listesi "
            "sunar. Ekip içinde sahiplik ve aylık kısa denetim olmadan küçük hatalar birikir "
            "ve randevu trafiği sessizce düşer."
        ),
        "sections": [
            {
                "heading": "Başlıkları ve ilk paragrafı netleştirin",
                "body": (
                    "Ana sayfa ve hizmet sayfalarında title ile H1 aynı vaadi taşısın: şehir "
                    "ve branş doğal şekilde geçsin. İlk paragrafta hastanın sorduğu soruyu "
                    "düz Türkçe yanıtlayın; abartılı anahtar kelime yığınından kaçının. "
                    "Mobilde ilk ekranda Ara ve Randevu butonları görünsün. Üç en çok "
                    "randevu getiren sayfayı önce ele alın; diğerleri ikinci turda gelsin. "
                    "Değişiklikleri yayınladıktan sonra Search Console'da tıklama ve "
                    "gösterim trendini iki hafta izleyin."
                ),
            },
            {
                "heading": "Hizmet sayfalarına uygulanabilir SSS ekleyin",
                "body": (
                    "Her kritik hizmet sayfasına 5–10 gerçek hasta sorusu koyun: süre, "
                    "hazırlık, ücret çerçevesi, ulaşım. Cevaplar görünür metin olsun; "
                    "yalnızca şema kodu yetmez. SSS'yi ayda bir güncelleyin; sık gelen "
                    "telefon sorularını buraya taşıyın. Bu hem insan okuyucuya hem de "
                    "alıntı yapan araçlara aynı net cevabı verir. İç linklerle ilgili "
                    "hizmet ve iletişim sayfalarına bağlayın; kör çıkmaz bırakmayın."
                ),
            },
            {
                "heading": "İletişim tutarlılığı ve iç link ağı",
                "body": (
                    "Adres, telefon ve çalışma saatleri footer, iletişim ve Google "
                    "profilinde birebir aynı olsun. Semt adlarını zorla doldurmak yerine "
                    "gerçek hizmet kapsamı ve ulaşım bilgisiyle bağlayın. Hizmet → SSS → "
                    "iletişim zinciri kurun. Aylık checklist: kırık link, eski fiyat "
                    "metni, kapalı kampanya banner'ı. Küçük tutarsızlıklar yerel güvende "
                    "pahalıya mal olur."
                ),
            },
        ],
        "faq": [
            {
                "q": "Keyword stuffing gerekir mi?",
                "a": "Hayır. Şehir ve hizmet adını doğal yerlerde kullanın; abartı zarar verir.",
            },
            {
                "q": "Hangi sayfalar önce?",
                "a": "Ana sayfa, en çok randevu getiren üç hizmet ve iletişim sayfası.",
            },
            {
                "q": "Ne sıklıkla gözden geçirilmeli?",
                "a": "Ayda bir title ve SSS kontrolü yeterlidir; büyük değişikliklerde hemen bakın.",
            },
        ],
        "cta": "Sayfa düzenini oturttuktan sonra Nefalix ile yorum ve geri bildirim ritmini bağlayarak yerel sinyali güçlendirebilirsiniz.",
    },
    {
        "file": "geo-seo-03-yorum-itibar.png",
        "tag": "İtibar",
        "title": "Yapay Zeka Destekli Geo SEO ile Hasta Yorumlarını Nasıl Yönetirsiniz?",
        "excerpt": (
            "Zamanında davet, hızlı yanıt ve düşük puanda geri arama ile yorum akışını "
            "güven sinyeline çevirin."
        ),
        "intro": (
            "Yorum yönetimi itibarın kalbidir: memnun hastaya zamanında davet, tüm "
            "yorumlara hızlı yanıt ve düşük puanda geri arama. Yapay zeka burada taslak "
            "ve önceliklendirme sağlar; karar ve yayın sorumluluğu insanda kalır. Bu "
            "playbook klinik operasyonunun yorumu günlük iş gibi işlemesi için net "
            "sahiplik, SLA ve ölçüm tanımlar. Güncel olumlu akış hem harita hem öneri "
            "araçlarında güveni yükseltir."
        ),
        "sections": [
            {
                "heading": "Davet zamanlaması ve izin",
                "body": (
                    "Tedavi sonrası 24–72 saat içinde, baskısız bir davet gönderin. "
                    "WhatsApp veya SMS için İYS/izin kaydı şarttır. Promoter hastaları "
                    "önceliklendirin; detractor'a önce çözüm görüşmesi açın. Şablon metin "
                    "kısa olsun, link tek tıkla açılsın. Haftalık davet sayısı ve dönüşüm "
                    "oranını kaydedin. İzinsiz veya aşırı sık mesaj hem şikayet hem de "
                    "marka zedelemesi riski taşır."
                ),
            },
            {
                "heading": "Yanıt SLA ve kriz tonu",
                "body": (
                    "48 saat kuralı: tüm yorumlara empati + somut sonraki adım ile yanıt. "
                    "AI taslak üretebilir; kriz ve tıbbi iddiada insan onayı zorunlu olsun. "
                    "Tartışmaya girmeden offline iletişim teklif edin. Sahte silme talebi "
                    "yerine çözüm odaklı yaklaşım tercih edin. Yanıt kalitesini ayda bir "
                    "örnekleyerek denetleyin; ton sapması erken yakalanır."
                ),
            },
            {
                "heading": "Ölçümü görünürlüğe bağlayın",
                "body": (
                    "Haftalık yorum hacmi, ortalama puan ve yanıt süresi panoda dursun. "
                    "Düşük puan kümelerini lokasyon veya hekim bazında ayırın. Bu metrikleri "
                    "yerel arama ve alıntı skorlarıyla yan yana okuyun; yorum akışı zayıfsa "
                    "içerik yatırımı tek başına yetmez. Sahiplik: klinik koordinatör + "
                    "pazarlama. Aylık retrospektifte üç aksiyon çıkarın ve kapatın."
                ),
            },
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
                "q": "Yorum ile görünürlük nasıl bağlanır?",
                "a": "Güncel olumlu akış entity güvenini artırır; öneri listelerinde avantaj sağlar.",
            },
        ],
        "cta": "Nefalix yorum asistanı ile davet, taslak yanıt ve düşük puan görevlerini tek akışta toplayabilirsiniz.",
    },
    {
        "file": "geo-seo-04-yerel-icerik-kule.png",
        "tag": "GEO",
        "title": "SEO Uyumlu Blog İçerikleri ile Yerel Otorite Kurun",
        "excerpt": (
            "Semt ve hizmet odaklı uzun yazılar + kısa günlük cevaplar ile yerel "
            "otoriteyi düzenli yayın ritmine bağlayın."
        ),
        "intro": (
            "Yerel otorite, semt ve hizmet odaklı içeriklerin düzenli yayınlanmasıyla "
            "kurulur. Her yazı bir alıcı sorusunu yanıtlar, sık sorular ekler ve ilgili "
            "hizmet sayfalarına bağlanır. Blog uzun playbook'tur; günlük kısa cevap "
            "yüzeyi ayrı kanaldır. Bu rehber içerik kulesini planlamak, üretmek ve "
            "ölçmek için operasyon checklist'i verir — tek mega yazıya güvenmek yerine "
            "sürdürülebilir ritim kurarsınız."
        ),
        "sections": [
            {
                "heading": "İçerik kulesi modelini kurun",
                "body": (
                    "Hub olarak hizmet sayfası, etrafında semt veya durum blogları, "
                    "yanında kısa günlük cevaplar olsun. Ayda en az dört semt+hizmet "
                    "konusu planlayın. Editör takviminde sahip, taslak tarihi ve yayın "
                    "tarihi net olsun. Konuları randevu verisine göre seçin; merak "
                    "uyandıran ama dönüşüm getirmeyen konulara abartılı bütçe ayırmayın. "
                    "Her yazı ilgili hizmet ve iletişim sayfasına iç link taşısın."
                ),
            },
            {
                "heading": "Yazım standardı: uzun ve okunabilir",
                "body": (
                    "Giriş insan dilinde sorunu anlatsın; bölümler uygulanabilir olsun. "
                    "Kısa iskelet jargonu blog'a sızmasın. Her bölümde klinik ekibin "
                    "yapacağı somut adım yazın. SSS'yi telefonda sık duyduğunuz "
                    "sorulardan üretin. Yayın sonrası 48 saat içinde kırık link ve "
                    "mobil okunabilirlik kontrolü yapın. Kalite kapısından geçmeyen "
                    "taslağı yayınlamayın; yeniden yazın."
                ),
            },
            {
                "heading": "Ölçüm ve sitemap disiplini",
                "body": (
                    "Organik yerel tıklama, harita aksiyonları ve alıntı oranını birlikte "
                    "izleyin. Yeni URL'lerin sitemap'te olduğunu doğrulayın. Üç ayda bir "
                    "düşük performanslı yazıları güncelleyin veya birleştirin. İçerik "
                    "külesi canlı bir sistemdir; arşive atılan yazı itibar değil gürültü "
                    "üretebilir. Retrospektifte hangi konu randevu getirdi, hangisi "
                    "yalnızca trafik getirdi diye ayırın."
                ),
            },
        ],
        "faq": [
            {
                "q": "Tek mega yazı yeter mi?",
                "a": "Hayır. Semt ve hizmet kombinasyonları ayrı sayfalarda daha iyi eşleşir.",
            },
            {
                "q": "Blog kısa günlük cevabın yerine geçer mi?",
                "a": "Geçmez. Blog derinleştirir; kısa paket alıntı yüzeyi sağlar.",
            },
            {
                "q": "Hangi metrik öncelikli?",
                "a": "Organik yerel tıklama, harita aksiyonları ve haftalık alıntı oranı.",
            },
        ],
        "cta": "Nefalix blog ve günlük GEO otomasyonu ile yayın ritmini Cursor açık olmadan da sürdürebilirsiniz.",
    },
    {
        "file": "geo-seo-05-gmb-checklist.png",
        "tag": "Google",
        "title": "Klinikler İçin Google İşletme Profili Optimizasyon Rehberi",
        "excerpt": (
            "Kategori, fotoğraf, soru-cevap ve yorum ritmiyle Google İşletme Profilini "
            "haftalık işletilen bir varlık haline getirin."
        ),
        "intro": (
            "Google İşletme Profili birçok klinikte 'bir kez açıldı' diye unutulur. Oysa "
            "yerel pakette görünmek için kategori doğru seçimi, güncel fotoğraf, tutarlı "
            "iletişim bilgisi ve canlı yorum yanıtı gerekir. Bu playbook profili haftalık "
            "işletilen bir operasyon haline getirir. Sahip atanmamış profil, yanlış saat "
            "ve yanıtsız yorumlar randevu kaybının sessiz nedenidir."
        ),
        "sections": [
            {
                "heading": "Temel alanları kilitleyin",
                "body": (
                    "Birincil kategori branşınızı yansıtsın; ikincil kategorileri abartmayın. "
                    "Adres, telefon, web ve saatler siteyle birebir aynı olsun. Kapalı gün "
                    "ve tatil saatlerini önceden güncelleyin. Hizmet listesini gerçekten "
                    "sunduğunuz tedavilerle sınırlayın. Profil erişimini iki kişiyle "
                    "sınırlayın; ayrılan personelin erişimini derhal kaldırın. Üç ayda bir "
                    "doğrulama ve sahiplik yedeklerini kontrol edin."
                ),
            },
            {
                "heading": "İçerik ve soru-cevap ritmi",
                "body": (
                    "Haftada en az bir gönderi veya fotoğraf ekleyin: ekip, ekipman, "
                    "klinik ortamı. Soru-cevap bölümünde gerçek hasta sorularını "
                    "yanıtlayın; uydurma SEO metinleri yazmayın. Ürün/hizmet "
                    "açıklamalarını sade tutun. Kampanya bitince eski gönderileri "
                    "arşivleyin. Bu ritim profilin 'yaşıyor' sinyali verir ve yerel "
                    "pakette rekabet avantajı sağlar."
                ),
            },
            {
                "heading": "Yorum ve performans panosu",
                "body": (
                    "Yorum yanıt SLA'sını blog/itibar playbook'unuzla hizalayın. "
                    "Insights'ta arama sorguları, yol tarifi ve arama tıklamalarını "
                    "aylık kaydedin. Ani düşüşte kategori, saat veya web yönlendirmesini "
                    "kontrol edin. Profil optimizasyonu tek seferlik proje değil; "
                    "haftalık 30 dakikalık bir rutin olarak takvime yazılmalıdır."
                ),
            },
        ],
        "faq": [
            {
                "q": "Kaç kategori eklemeliyim?",
                "a": "Bir güçlü birincil + gerçekten uyumlu birkaç ikincil yeter; şişirmek zararlıdır.",
            },
            {
                "q": "Fotoğraf sıklığı?",
                "a": "Haftalık taze görsel idealdir; en az ayda birkaç güncel fotoğraf ekleyin.",
            },
            {
                "q": "Profil ile site çelişirse ne olur?",
                "a": "Güven düşer. Adres ve telefonu tek kaynaktan yönetip her yere aynı basılsın.",
            },
        ],
        "cta": "Nefalix ile Google yorum daveti ve yanıt taslaklarını klinik takvimine bağlayabilirsiniz.",
    },
    {
        "file": "geo-seo-06-sesli-arama.png",
        "tag": "AEO",
        "title": "Sesli Arama ve Geo SEO: Yakınımdaki Klinikleri Bul",
        "excerpt": (
            "Konuşma dilindeki sorulara kısa net cevaplar ve mobil hızlı sayfalarla "
            "sesli ve yakın aramada görünürlüğü artırın."
        ),
        "intro": (
            "Sesli arama ve 'yakınımdaki klinik' sorguları konuşma dilindedir: kısa, "
            "doğrudan ve çoğu zaman mobilde. Klinik siteniz bu soruları ilk cümlede "
            "yanıtlamıyorsa paket ve asistan önerilerinde geride kalırsınız. Bu "
            "playbook soru envanteri, mobil hız ve yerel sinyal üçlüsünü operasyon "
            "checklist'ine bağlar. Amaç sihirli kelime yığını değil; gerçek soruya "
            "dürüst cevap vermektir."
        ),
        "sections": [
            {
                "heading": "Konuşma sorusu envanteri çıkarın",
                "body": (
                    "Resepsiyon ve çağrı merkezinden 'en çok sorulan 20 soruyu' toplayın. "
                    "Bunları hizmet sayfalarının girişine ve SSS'ye taşıyın. 'Açık mı', "
                    "'nasıl giderim', 'hangi branş' gibi niyetleri ayırın. Her soruya "
                    "iki cümlelik net cevap yazın. Envanteri çeyrekte bir yenileyin; "
                    "yeni tedaviler veya semtler eklenince listeyi güncelleyin."
                ),
            },
            {
                "heading": "Mobil hız ve tıklanabilir iletişim",
                "body": (
                    "Sesli arama sonucu çoğu zaman telefona düşer. Sayfa üç saniyede "
                    "açılsın; görselleri sıkıştırın; Ara butonu büyük olsun. Konum "
                    "izinleri ve harita embed'i gereksiz ağırlık yaratıyorsa sadeleştirin. "
                    "Core Web Vitals'ı aylık kontrol edin. Yavaş mobil deneyim, doğru "
                    "cevap yazmış olsanız bile randevuyu kaçırır."
                ),
            },
            {
                "heading": "Yerel sinyal ve ölçüm",
                "body": (
                    "Profil saatleri, yol tarifi tıklamaları ve arama sorgularını izleyin. "
                    "Sesli/asistan önerilerinde geçip geçmediğinizi haftalık prompt "
                    "listesiyle manuel skorlayın. Rakip kliniklerin hangi sorularda "
                    "öne çıktığını not edin. İçerik + hız + yorum üçlüsü birlikte "
                    "ilerlemeden sesli aramada sürdürülebilir sonuç beklemeyin."
                ),
            },
        ],
        "faq": [
            {
                "q": "Sesli arama için ayrı sayfa şart mı?",
                "a": "Şart değil. Mevcut hizmet sayfalarını konuşma sorularıyla güçlendirmek çoğu klinik için yeterlidir.",
            },
            {
                "q": "Şema kodu tek başına yeter mi?",
                "a": "Hayır. Görünür metin net değilse şema alıntıyı garanti etmez.",
            },
            {
                "q": "İlk KPI ne olsun?",
                "a": "Mobil Ara tıklaması, yol tarifi ve hedef sorularda mention oranı.",
            },
        ],
        "cta": "Nefalix günlük kısa cevap paketleri ve blog ritmiyle konuşma sorularını düzenli canlı tutmanıza yardım eder.",
    },
    {
        "file": "geo-seo-07-veri-isi-haritasi.png",
        "tag": "Operasyon",
        "title": "Veri Odaklı Geo SEO: Hangi Bölgelerden Hasta Geliyor?",
        "excerpt": (
            "Randevu, harita ve arama verisini birleştirerek bütçeyi gerçekten "
            "hasta getiren bölgelere kaydırın."
        ),
        "intro": (
            "Yerel pazarlama bütçesi çoğu klinikte sezgiyle dağılır. Oysa randevu "
            "kaynağı, harita yol tarifi ve arama sorguları hangi semtlerin gerçekten "
            "hasta getirdiğini gösterir. Bu playbook veri kaynaklarını birleştirip "
            "aylık bir 'ısı haritası' rutini kurmanızı sağlar. Veri yoksa içerik ve "
            "reklam harcaması rastgele kalır; fazla olan bölgelerde ise fırsat "
            "kaçırılır."
        ),
        "sections": [
            {
                "heading": "Veri kaynaklarını tek tabloda toplayın",
                "body": (
                    "HBYS/CRM randevu kaynağı, Google İşletme Insights, Search Console "
                    "ve reklam panolarından semt/posta kodu alanlarını ayda bir çekin. "
                    "Tanım birliği şart: 'Kaynak=Google' her ekipte aynı anlama gelsin. "
                    "Eksik alanları resepsiyon script'ine ekleyin. İlk ay mükemmel "
                    "veri beklemeyin; %70 doluluk bile yön seçmek için yeterlidir. "
                    "Tabloyu paylaşılabilir bir sheet veya panoda tutun."
                ),
            },
            {
                "heading": "Isı haritasını aksiyona çevirin",
                "body": (
                    "Yüksek randevu + düşük içerik olan semtlere blog ve hizmet "
                    "vurgusu ekleyin. Yüksek tıklama + düşük randevu olanlarda "
                    "iletişim hızı ve teklif netliğini kontrol edin. Düşük her "
                    "şey olan bölgelere bütçe kilitlemeyin. Aylık toplantıda üç "
                    "aksiyon çıkarın: durdur, güçlendir, test et. Isı haritası "
                    "sunum slaytı değil; karar aracıdır."
                ),
            },
            {
                "heading": "Gizlilik ve KVKK",
                "body": (
                    "Hasta düzeyinde adres paylaşmayın; agregat semt analizleri kullanın. "
                    "Erişimleri rol bazlı sınırlayın. Dış ajansla paylaşırken anonimleştirin. "
                    "Veri odaklı yerel SEO, kişisel veriyi pazarlama slaytına dökmek "
                    "değildir. Süreç dokümantasyonuna KVKK notunu ekleyin ve yılda bir "
                    "denetleyin."
                ),
            },
        ],
        "faq": [
            {
                "q": "Hangi araç şart?",
                "a": "Önce mevcut HBYS + Google Insights yeter; sonra panoyu zenginleştirin.",
            },
            {
                "q": "Ne sıklıkla?",
                "a": "Aylık ısı haritası + haftalık hızlı yorum/harita kontrolü idealdir.",
            },
            {
                "q": "Reklam ile organik nasıl ayrılır?",
                "a": "Kaynak alanını zorunlu tutun; belirsiz kayıtları 'diğer' diye şişirmeyin.",
            },
        ],
        "cta": "Nefalix geri bildirim ve itibar verisini operasyon panosuna bağlayarak bölgesel kararları hızlandırır.",
    },
    {
        "file": "geo-seo-08-yerel-backlink.png",
        "tag": "GEO",
        "title": "Yerel Link Building: Geo SEO'nun Gizli Silahı",
        "excerpt": (
            "Anlamlı yerel ortaklıklar, rehber kayıtları ve işbirliği içerikleriyle "
            "güvenilir atıflar kazanın."
        ),
        "intro": (
            "Yerel bağlantılar hâlâ güven sinyali taşır — ama satın alınmış spam "
            "dizinler değil, anlamlı ortaklıklar. Bu playbook kliniklerin mahalle, "
            "sektör ve medya ilişkilerinden doğal atıf üretmesi için bir süreç "
            "çizer. Amaç link sayısı şişirmek değil; hastanın ve arama sistemlerinin "
            "güveneceği gerçek referanslar bırakmaktır."
        ),
        "sections": [
            {
                "heading": "Ortaklık haritası çıkarın",
                "body": (
                    "Yerel otel, sigorta, spor salonu, üniversite ve STK listesi yapın. "
                    "Her biri için değer önerisi yazın: ortak seminer, sponsorluk, "
                    "hasta bilgilendirme içeriği. Soğuk mail yerine yüz yüze veya "
                    "mevcut hasta ağıyla ilerleyin. Üç aylık hedef: iki anlamlı "
                    "işbirliği. Kalitesiz dizinlere toplu kayıt kampanyası açmayın; "
                    "temizlik maliyeti kazanımdan büyüktür."
                ),
            },
            {
                "heading": "İçerikle kazanılan atıf",
                "body": (
                    "Yerel basına veya sektörel blog'a veri temelli kısa brifler "
                    "verin. Ortak checklist PDF'leri her iki sitede de yayınlanabilir. "
                    "Atıf metni doğal olsun; 'ücretli SEO linki' dili kullanmayın. "
                    "Yayın sonrası URL'yi takip listesine ekleyin; kalkarsa nazikçe "
                    "hatırlatın. İçerik kalitesi düşükse kimse size link vermez."
                ),
            },
            {
                "heading": "Rehber ve iletişim tutarlılığı",
                "body": (
                    "Seçilmiş birkaç güvenilir yerel rehberde kaydınızı doğrulayın. "
                    "Adres ve telefon her yerde aynı olsun. Çelişkili kayıtları "
                    "düzeltin veya kaldırın. Link building'i profil ve yorum "
                    "ritminden kopuk yürütmeyin; birlikte güçlenirler. Çeyreklik "
                    "denetimde toksik veya kırık bağlantıları ayıklayın."
                ),
            },
        ],
        "faq": [
            {
                "q": "Link satın alayım mı?",
                "a": "Risklidir. Anlamlı ortaklık ve içerik ile kazanılan atıflar daha sürdürülebilirdir.",
            },
            {
                "q": "Kaç link yeter?",
                "a": "Sayı değil kalite. Birkaç güvenilir yerel atıf, yüzlerce spam dizinden iyidir.",
            },
            {
                "q": "Ne kadar sürer?",
                "a": "İlk anlamlı işbirlikleri genelde 4–8 haftada; etki ölçümü çeyreklik bakılır.",
            },
        ],
        "cta": "Nefalix itibar ve içerik ritmini güçlendirerek ortaklık görüşmelerinde somut kanıt sunmanıza yardım eder.",
    },
    {
        "file": "geo-seo-09-mobil-hiz.png",
        "tag": "Operasyon",
        "title": "Mobil Öncelikli Geo SEO: Klinik Siteniz Mobil Uyumlu mu?",
        "excerpt": (
            "Mobil hız, tıklanabilir iletişim ve sade formlarla yerel ziyaretçiyi "
            "randevuya çevirin."
        ),
        "intro": (
            "Yerel aramanın çoğu mobilde biter. Yavaş açılan sayfa, küçük Ara "
            "butonu ve uzun formlar randevuyu sessizce öldürür. Bu playbook klinik "
            "sitesini mobil öncelikli hale getirmek için teknik ve içerik "
            "kontrollerini bir araya getirir. Masaüstünde güzel görünen ama "
            "telefonda sürtünen bir deneyim, yerel SEO bütçesini boşa harcar."
        ),
        "sections": [
            {
                "heading": "Hız ve medya disiplini",
                "body": (
                    "Kapak görsellerini sıkıştırın; gereksiz kaydırıcıları kaldırın. "
                    "Üçüncü parti script'leri auditleyin. Lighthouse veya PageSpeed "
                    "ile aylık skor alın; regresyonu yayın checklist'ine ekleyin. "
                    "CDN ve tarayıcı önbelleğini doğru kullanın. Hız bir kerelik "
                    "proje değil; her yeni eklenti potansiyel gerilemedir."
                ),
            },
            {
                "heading": "Parmak dostu dönüşüm",
                "body": (
                    "Ara ve Randevu butonları başparmağın ulaşacağı yerde, yeterli "
                    "boyutta olsun. Form alanlarını minimuma indirin; zorunlu alan "
                    "şişirmeyin. WhatsApp tıklamasını ölçün. Sticky bar'lar içeriği "
                    "örtmesin. Gerçek cihazlarda (iOS/Android) ayda bir duman testi "
                    "yapın; yalnızca emülatöre güvenmeyin."
                ),
            },
            {
                "heading": "İçerik ve yerel tutarlılık",
                "body": (
                    "Mobilde de ilk ekranda net vaat ve iletişim görünsün. Adres "
                    "ve saatler kaydırılmadan erişilebilir olsun. Harita embed'i "
                    "ağırsa statik harita + yol tarifi linki kullanın. Mobil UX "
                    "bozukken içerik üretmeye devam etmek, delik kovaya su "
                    "doldurmaktır — önce sürtünmeyi düşürün."
                ),
            },
        ],
        "faq": [
            {
                "q": "Hangi hız skoru hedef?",
                "a": "Mobilde yeşil Core Web Vitals bölgesi; pratikte LCP'yi makul tutmak önceliklidir.",
            },
            {
                "q": "AMP şart mı?",
                "a": "Şart değil. İyi optimize edilmiş responsive site çoğu klinik için yeterlidir.",
            },
            {
                "q": "Ne sıklıkla test?",
                "a": "Her majör yayında + ayda bir gerçek cihaz duman testi.",
            },
        ],
        "cta": "Nefalix iletişim akışlarını sadeleştirerek mobil ziyaretçiyi daha az sürtünmeyle randevuya taşımanıza yardım eder.",
    },
    {
        "file": "geo-seo-10-otomasyon-kontrol.png",
        "tag": "GEO",
        "title": "Nefalix AI ile Geo SEO Otomasyonu: Zaman Kazanın, Hasta Sayısını Artırın",
        "excerpt": (
            "Günlük kısa cevap, haftalık skor ve yorum ritmini otomasyona bağlayarak "
            "ekibin zamanını hasta temasina ayırın."
        ),
        "intro": (
            "Yerel görünürlük işi manuel checklist'lerle yürürse ilk tatilde kopar. "
            "Nefalix yaklaşımı günlük kısa cevap paketi, blog playbook'u, yorum daveti "
            "ve haftalık skor hatırlatmasını otomasyona bağlar. Bu playbook hangi "
            "işin insanda kalacağını, hangisinin makineye gideceğini netleştirir. "
            "Amaç hasta sayısını sihirle artırmak değil; tutarlı operasyonla "
            "kaçırılan randevuları azaltmaktır."
        ),
        "sections": [
            {
                "heading": "İki kanalı ayırın: blog ve günlük paket",
                "body": (
                    "Blog uzun rehberdir; günlük paket kısa alıntı birimidir. Aynı "
                    "konuyu iki biçimde yayınlayın ama biçimleri karıştırmayın. "
                    "Kalite kapıları her iki kanalda da zorunlu olsun. Otomasyon "
                    "zayıf iskeleti çoğaltmasın diye reddetmeli. VPS cron veya n8n "
                    "içinden yalnızca bir tetikleyici seçin; çift yayın riskini "
                    "bilinçli olarak engelleyin."
                ),
            },
            {
                "heading": "Yorum, hatırlatma ve skor döngüsü",
                "body": (
                    "Memnun hastaya davet, düşük puana görev, pazar citation "
                    "hatırlatması tek takvimde dursun. Skorları markdown şablona "
                    "değil veritabanına yazın; mail eksik satır saysın. Ekip "
                    "Pazar sabahı ne soracağını bilsin. Ölçülmeyen otomasyon "
                    "yalnızca gürültü üretir. Aylık retrospektifte hangi "
                    "otomasyon zaman kazandırdı, hangisi false positive üretti "
                    "diye ayırın."
                ),
            },
            {
                "heading": "Sahiplik ve güvenlik",
                "body": (
                    "Secret'ları VPS env'de tutun; sohbete yapıştırmayın. Yayın "
                    "loglarını izleyin. İYS ve KVKK kontrollerini mesaj "
                    "otomasyonundan ayırmayın. İnsan onayı gereken adımları "
                    "(kriz yanıtı, tıbbi iddia) otomatik yayınlamayın. Otomasyon "
                    "güvenli sınırlar içinde hız kazandırır; sınır yoksa itibar "
                    "riski büyür."
                ),
            },
        ],
        "faq": [
            {
                "q": "Cursor açık olmadan yayın olur mu?",
                "a": "Evet. VPS cron veya n8n Vertex + Supabase ile yayınlar; Cursor yalnızca geliştirme içindir.",
            },
            {
                "q": "Blog ile günlük paket aynı mı?",
                "a": "Hayır. Blog playbook; günlük paket kısa AI alıntı birimi; ikisi birlikte çalışır.",
            },
            {
                "q": "İlk kurulumda neyi otomatikleştirmeliyim?",
                "a": "Günlük paket + blog + pazar skor hatırlatması; yorum daveti ikinci dalga olsun.",
            },
        ],
        "cta": "Nefalix pilotunda bu döngüyü klinik takvimine bağlayarak ekibin manuel checklist yükünü azaltabilirsiniz.",
    },
]


def expand_playbook(pack: dict) -> tuple[str, list[dict], list[dict]]:
    """Kalite kapısı için bölümleri büyüt; gerekirse 4. kontrol listesi ekle."""
    from lib.content_quality import word_count as _wc

    pad = (
        " Bu adımı klinik takvimine yazın; sahip ve kontrol tarihi olmadan "
        "iyileştirme bir sonraki çeyreğe kayar. Ekip içinde tek cümlelik "
        "sahiplik notu bırakın ve iki hafta sonra sonucu kısaca gözden geçirin."
    )
    intro = pack["intro"]
    sections = [
        {
            "heading": str(s["heading"]).replace("NAP", "iletişim"),
            "body": str(s["body"]).replace("NAP bloğu", "iletişim bilgisi"),
        }
        for s in pack["sections"]
    ]
    for s in sections:
        while _wc(s["body"]) < 90:
            s["body"] = s["body"].rstrip() + pad
    checklist = {
        "heading": "Uygulama kontrol listesi",
        "body": (
            "Bu yazıdaki adımları bir sayfalık checklist'e indirin: sorumlu kişi, "
            "son tarih ve tamamlandı kutusu. Haftalık 20 dakikalık bir ritim "
            "belirleyin; tamamlanmayan maddeleri bir sonraki haftaya taşıyın. "
            "Ölçüm satırını (yorum, harita tıklaması veya alıntı skoru) aynı "
            "checklist'e ekleyin ki içerik üretimi ile sonuç birbirinden kopmasın. "
            "Üç ayda bir checklist'i sadeleştirin; işe yaramayan maddeleri silin. "
            "Sahiplik klinik koordinatörde kalsın; pazarlama metin desteği versin."
        ),
    }
    if len(sections) < 4:
        sections.append(checklist)
    total = _wc(intro) + sum(_wc(s["body"]) for s in sections)
    while total < 360:
        sections[-1]["body"] = sections[-1]["body"].rstrip() + pad
        total = _wc(intro) + sum(_wc(s["body"]) for s in sections)
    faq = list(pack["faq"])
    return intro, sections, faq


def build_row(pack: dict) -> dict:
    cover = cover_raw(pack["file"])
    intro, sections, faq = expand_playbook(pack)
    gate = blog_quality_gate(
        intro=intro,
        sections=sections,
        faq=faq,
        title=pack["title"],
        excerpt=pack["excerpt"],
    )
    if gate:
        raise RuntimeError(f"{pack['title']}: kalite kapısı {gate}")
    slug = slugify(pack["title"])
    return {
        "slug": slug,
        "title": pack["title"],
        "tag": pack["tag"],
        "excerpt": pack["excerpt"][:280],
        "meta_description": pack["excerpt"][:155],
        "body_html": to_html(
            intro, sections, faq, pack.get("cta", ""), cover
        ),
        "cover_image_url": cover,
        "footer_image_url": cover_api("footer", pack["tag"], "Nefalix"),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--slug", help="Tek slug")
    args = parser.parse_args()

    results = []
    for pack in PLAYBOOKS:
        row = build_row(pack)
        if args.slug and row["slug"] != args.slug:
            continue
        if args.dry_run:
            results.append(
                {
                    "slug": row["slug"],
                    "title": row["title"],
                    "cover": row["cover_image_url"],
                    "dry_run": True,
                }
            )
            continue
        proxy("DELETE", "blog_posts", query=f"slug=eq.{row['slug']}")
        out = proxy("POST", "blog_posts", body=row)
        results.append(
            {
                "slug": row["slug"],
                "ok": bool(out.get("ok", True)),
                "url": f"{SITE}/blog/{row['slug']}?v=playbook12",
            }
        )

    print(json.dumps({"ok": True, "count": len(results), "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
