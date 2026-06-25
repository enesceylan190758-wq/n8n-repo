#!/usr/bin/env python3
"""
Yönetici sunumu — sade dil, teknik terim yok.
Çıktı: docs/yonetici-sunum/ klasöründe CSV'ler → Google Sheets'e içe aktar.

Google Drive'a doğrudan yazmak için henüz bağlantı yok;
dosyaları Drive'a yükleyip "Dosya > İçe aktar > CSV" ile tek çalışma kitabında birleştirin.
"""
from __future__ import annotations

import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "yonetici-sunum"


def write_csv(name: str, headers: list[str], rows: list[list]):
    path = OUT / f"{name}.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    # ── 1. TEK SAYFA ÖZET ─────────────────────────────────────
    write_csv(
        "01_Ozet",
        ["Konu", "Açıklama (sade dil)"],
        [
            ["Bu proje ne?", "Diş kliniklerinin hasta mesajlarını, memnuniyetini ve internet yorumlarını tek yerden yönetmesini sağlayan bir program."],
            ["Kime satıyoruz?", "Önce diş klinikleri. İlk müşterimiz: Medident İstanbul."],
            ["Klinik ne kazanır?", "WhatsApp mesajı kaçmaz. Memnun hasta Google'a yönlendirilir. Kötü yorum erken görülür. Sekreter işi azalır."],
            ["Biz ne satıyoruz?", "Aylık abonelik + ilk kurulum ücreti. Yazılımı biz işletiyoruz; klinik sadece paneli kullanır."],
            ["Şu an durum", "Program kuruldu. Sunucu kimlik doğrulaması yüzünden geçici durdu — destek talebi açıldı."],
            ["12 ay hedef", "Medident günlük kullansın → 5–8 klinik para ödesin → aylık ~60–80 bin ₺ düzenli gelir."],
            ["Yıl 1 gerçek", "İlk yıl yatırım yılı; kâr beklenmez. Yıl 2'de kâra geçiş hedeflenir."],
            ["Önerilen fiyat", "Orta paket: ayda 7.990 ₺ + bir kerelik kurulum 14.900 ₺"],
            ["En büyük risk", "WhatsApp ve hasta verisi yasal kurallara (İYS, KVKK) uygun olmalı — hukuk desteği şart."],
        ],
    )

    # ── 2. PROGRAM NE YAPIYOR (modüller, jargon yok) ─────────
    write_csv(
        "02_Program_Ne_Yapiyor",
        ["Bölüm", "Klinikte ne işe yarar?", "Örnek", "Durum"],
        [
            ["Gelen kutusu", "WhatsApp mesajları tek listede. Yapay zeka taslak yanıt yazar; personel onaylayıp gönderir.", "Hasta: 'İmplant fiyatı?' → taslak hazır", "Kurulu — sunucu bekliyor"],
            ["Google yorumları", "Yeni yorum gelince analiz + cevap taslağı. Yönetici onaylar.", "4 yıldız yorum → nazik cevap önerisi", "Kurulu — ekran geliştirilecek"],
            ["Hasta memnuniyeti (NPS)", "Randevu sonrası puan istenir. Memnun hasta Google'a, memnun değilse şikâyet formuna yönlendirilir.", "9/10 → Google linki", "Kurulu"],
            ["İtibar takibi", "Şikâyetvar vb. mention'lar tek yerde; acil olanlar işaretlenir.", "Olumsuz haber → alarm", "Kurulu"],
            ["Geri çağırma", "Uzun süredir gelmeyen hastaya hatırlatma mesajı.", "6 ay gelmeyen hasta", "Kurulu"],
            ["Web sitesi sohbet", "Siteden yazan ziyaretçiye anında cevap.", "Gece gelen soru", "Bağlantı güncellenecek"],
            ["Yönetim paneli", "Tüm veriler tek ekranda: nefalixai.com/dashboard", "Sabah 10 dk kontrol", "Hazır"],
        ],
    )

    # ── 3. YOL HARİTASI (ay isimleri, faz kodu yok) ─────────
    write_csv(
        "03_Yol_Haritasi",
        ["Dönem", "Klinik ne görür?", "Biz ne yaparız?", "Ne kadar harcama?", "Bitti sayılır eğer…"],
        [
            ["Haziran 2026", "Panel tekrar açılır", "Sunucuyu ayağa kaldırırız", "Düşük", "Medident veriyi görür"],
            ["Temmuz", "WhatsApp yanıtı panelden", "Gelen kutusu iyileştirme", "Orta", "Haftada 5 gün panel kullanımı"],
            ["Ağustos–Eylül", "Google yorum onayı tek tık", "Onay ekranı + bildirim", "Orta", "Yorumların yarısı panelden"],
            ["Ekim–Aralık", "İlk ücretli müşteriler", "Satış, sözleşme, eğitim", "Yüksek", "5 klinik fatura ödüyor"],
            ["2027 ilk yarı", "Randevu sistemi bağlantısı", "Klinik programlarıyla entegrasyon", "Yüksek", "10+ klinik"],
        ],
    )

    # ── 4. MALİYETLER (sade) ─────────────────────────────────
    write_csv(
        "04_Aylik_Maliyetler",
        ["Gider kalemi", "Ne için?", "Ayda yaklaşık (₺)", "Zorunlu mu?"],
        [
            ["Türkiye sunucu", "Program 7/24 çalışsın, veri Türkiye'de kalsın", "170", "Evet"],
            ["İnternet sitesi barındırma", "nefalixai.com ve panel", "760", "Evet"],
            ["Yapay zeka kullanımı", "Taslak mesaj ve yorum analizi", "1.500", "Evet"],
            ["WhatsApp resmi hat (ileride)", "Yasal ticari mesaj", "2.000", "Satış başlayınca"],
            ["Hukuk / KVKK", "Sözleşme, aydınlatma metni", "2.500", "Evet"],
            ["İYS kayıt", "Ticari mesaj izin sistemi", "500", "Satış öncesi"],
            ["Yazılımcı (yarı zaman)", "Programı geliştirme", "45.000", "Önerilen"],
            ["Satışçı (yarı zaman)", "Klinik ziyareti, demo", "30.000", "5. müşteriden önce"],
            ["", "PİLOT TOPLAM (yazılımcı hariç)", "~6.000", ""],
            ["", "SATIŞA HAZIR TOPLAM (yazılımcı dahil)", "~82.000", ""],
        ],
    )

    # ── 5. FİYATLANDIRMA ─────────────────────────────────────
    write_csv(
        "05_Fiyat_Paketleri",
        ["Paket adı", "Kim alır?", "Ayda (₺)", "İlk kurulum (₺)", "Dahil olanlar (sade anlatım)"],
        [
            ["Başlangıç", "Tek hekim, küçük klinik", "4.990", "9.900", "WhatsApp kutusu + site sohbeti + basit rapor"],
            ["Profesyonel ★ önerilen", "Orta büyüklük klinik", "7.990", "14.900", "Her şey: yorum, memnuniyet, itibar, geri çağırma"],
            ["Kurumsal", "Birden fazla şube", "14.990", "29.900", "Profesyonel + öncelikli destek + randevu sistemi bağlantısı"],
            ["Özel anlaşma", "Büyük zincir / hastane", "Teklif", "Teklif", "İhtiyaca göre"],
        ],
    )

    write_csv(
        "05b_Neden_Bu_Fiyat",
        ["Soru", "Cevap (yöneticiye anlatım)"],
        [
            ["Klinik neden ödesin?", "Bir implant randevusu 15–30 bin ₺. Program ayda 8 bin ₺. Tek randevu 2 yılı öder."],
            ["Rakipler ne kadar?", "Basit WhatsApp programları 1.500–4.000 ₺. Biz daha kapsamlıyız; yapay zeka ve yorum yönetimi var."],
            ["Çok pahalı değil mi?", "Yurtdışı benzeri aylık 10–15 bin TL'nin üzerinde. Biz yerel ve KVKK uyumlu."],
            ["Kurulum ücreti neden?", "İlk hafta eğitim, ayar, WhatsApp bağlantısı 8–12 saat iş. Ciddi müşteri filtresi."],
            ["Yıllık ödeme indirimi?", "%15 indirim önerilir — 2 ay bedava gibi."],
        ],
    )

    # ── 6. GELİR SENARYOLARI ─────────────────────────────────
    write_csv(
        "06_Gelir_Senaryolari",
        ["Senaryo", "1 yıl sonunda kaç klinik?", "Ortalama aylık ücret", "Yıllık gelir (₺)", "Yorum"],
        [
            ["Kötü", "3", "5.990", "~216.000", "Satış yavaş"],
            ["Gerçekçi ★", "8", "7.490", "~718.000", "Medident referansı ile"],
            ["İyi", "15", "7.990", "~1.440.000", "İyi satış ekibi"],
            ["Çok iyi", "25", "8.490", "~2.550.000", "Agresif büyüme"],
        ],
    )

  # ── 7. RİSKLER (sade) ────────────────────────────────────
    write_csv(
        "07_Riskler",
        ["Risk", "Ne olabilir?", "Ne yapıyoruz?", "Önem"],
        [
            ["Sunucu kapalı", "Panel çalışmaz", "Türkiye sunucu + yedekleme", "Yüksek"],
            ["WhatsApp kapanması", "Mesaj gitmez", "Resmi iş ortağı hattına geçiş planı", "Yüksek"],
            ["Yasal uyumsuzluk", "Ceza, itibar kaybı", "Avukat + İYS + açık rıza metinleri", "Çok yüksek"],
            ["Klinik satın almaz", "Gelir olmaz", "Medident başarı hikâyesi + yüz yüze satış", "Orta"],
            ["Tek kişiye bağımlılık", "İş durur", "Dokümantasyon + yedek yazılımcı", "Yüksek"],
        ],
    )

    # ── 8. ONAY LİSTESİ (toplantıda işaretle) ───────────────
    write_csv(
        "08_Toplantida_Onay",
        ["#", "Karar", "Tahmini tutar", "Onay (EVET/HAYIR)", "Not"],
        [
            ["1", "Yıllık bütçe (~2,1 milyon ₺ yatırım yılı)", "2.100.000 ₺", "", "Gelir yıl 2'de"],
            ["2", "Hukuk / KVKK paketi", "25.000 ₺", "", "Satış öncesi şart"],
            ["3", "Yarı zamanlı yazılımcı", "45.000 ₺/ay", "", "Temmuz'dan"],
            ["4", "Fiyat listesi: 7.990 ₺/ay orta paket", "—", "", ""],
            ["5", "Medident'i referans gösterme izni", "—", "", "Case study için"],
            ["6", "İlk hedef: 5 ücretli klinik (Aralık)", "—", "", ""],
        ],
    )

    # ── 9. SORU CEVAP (yönetici sorar) ───────────────────────
    write_csv(
        "09_Soru_Cevap",
        ["Muhtemel soru", "Önerilen cevap (sunumda okuyun)"],
        [
            ["Bu teknik bir proje mi?", "Hayır — bu bir klinik işi. Teknoloji arka planda; ön planda randevu ve hasta memnuniyeti var."],
            ["Veriler nerede?", "Türkiye'deki sunucuda. Hasta bilgisi yurt dışına gitmemeli — bu yüzden Türkiye sunucu seçtik."],
            ["Yapay zeka teşhis koyar mı?", "Hayır. Sadece randevu, fiyat bilgisi, iletişim gibi idari konularda yardım eder."],
            ["Ne zaman para kazanırız?", "İlk ücretli müşteri Ekim–Kasım hedefi. Anlamlı gelir 8–10 klinikte başlar."],
            ["Rakip kim?", "Basit WhatsApp programları ve sekreterin defteri. Biz hepsini tek panelde topluyoruz."],
            ["Medident ne durumda?", "Kurulum bitti; sunucu askıda. Açılınca eğitim ve günlük kullanım başlayacak."],
            ["Kaç kişi lazım?", "Şimdi: 1 yazılımcı yarı zaman. 5 müşteriden sonra yarı zaman satış + destek."],
            ["Yatırımcı gerekir mi?", "500 bin ₺ nakit varsa 12–18 ay idare eder. Hızlı büyüme için 1–1,5 milyon ₺ eklenebilir."],
        ],
    )

    # ── 10. NASIL YAPACAĞIZ (teknik değil) ─────────────────
    write_csv(
        "10_Nasil_Yapacagiz",
        ["Adım", "Basit anlatım", "Benzeri"],
        [
            ["1", "Tüm bilgiler tek kasada toplanır (hasta mesajı, yorum, puan)", "Kliniğin dijital hafızası"],
            ["2", "Önce hazır otomasyon araçlarıyla hızlı çalışır hale getirdik", "Prototype — deneme modeli"],
            ["3", "Her parça hazır olunca kendi programımıza taşıyoruz", "Ev önce kirada, sonra mülk"],
            ["4", "Önce en çok kullanılan: gelen kutusu ve Google yorumu", "Önce vitrin, sonra depo"],
            ["5", "Her parça bitince klinikte test, sonra satışa aç", "Pilot → ürün"],
            ["6", "Eski otomasyon araçları tamamen kapanır (2027)", "Artık kendi evimiz"],
        ],
    )

    # ── 11. SUNUM AKIŞI (20 dk) ─────────────────────────────
    write_csv(
        "11_Sunum_Akisi_20dk",
        ["Dakika", "Ne söylenir?", "Hangi sayfa / slayt"],
        [
            ["0–2", "Problem: Klinikler mesaj kaçırıyor, yorumlara geç cevap veriyor", "01_Ozet"],
            ["2–5", "Çözüm: Tek panel, yapay zeka taslak, Türkiye sunucu", "02_Program"],
            ["5–8", "Canlı örnek: Medident, nefalixai.com/dashboard", "Demo"],
            ["8–11", "Fiyat: 7.990 ₺/ay — bir randevu bunu öder", "05_Fiyat"],
            ["11–14", "Maliyet ve yıl 1 gerçekçi beklenti", "04 + 06"],
            ["14–17", "Yol haritası: bu yaz yaz, sonbahar sat", "03_Yol"],
            ["17–19", "Riskler ve hukuk", "07_Riskler"],
            ["19–20", "Onay iste: bütçe, hukuk, fiyat", "08_Onay"],
        ],
    )

    # ── Talimat dosyası ──────────────────────────────────────
    readme = OUT / "GOOGLE_SHEETS_NASIL_YUKLENIR.txt"
    readme.write_text(
        """NEFALIX — YÖNETİCİ SUNUMU → GOOGLE SHEETS

1. drive.google.com → Yeni → Google E-Tablolar
2. Dosya → İçe aktar → Yükle
3. Bu klasördeki CSV dosyalarını TEK TEK içe aktarın
   (Her CSV = ayrı sekme olur; içe aktarırken "Yeni sayfa oluştur" seçin)
4. Sekme adlarını dosya adıyla aynı yapın (01_Ozet, 02_Program...)

ÖNERİLEN SIRALAMA:
  01_Ozet → toplantıda ilk açılan sayfa
  11_Sunum_Akisi_20dk → sunucu için rehber
  08_Toplantida_Onay → son slayt

GOOGLE DRIVE YETKİSİ:
  Şu an program otomatik Drive'a yazamıyor.
  Seçenekler:
  A) Bu CSV'leri yükleyin (5 dk, önerilen)
  B) Sheet'i "Düzenleyebilir" link ile paylaşın — manuel kopyalama
  C) İleride Google API bağlantısı eklenebilir

RENKLENDİRME (isteğe bağlı):
  - Başlık satırı: koyu yeşil arka plan, beyaz yazı
  - "Profesyonel ★" satırları: açık yeşil
  - Risk "Çok yüksek": açık kırmızı
""",
        encoding="utf-8",
    )

    files = sorted(OUT.glob("*.csv"))
    print(f"✓ {len(files)} CSV + talimat → {OUT}")
    for f in files:
        print(f"   {f.name}")


if __name__ == "__main__":
    main()
