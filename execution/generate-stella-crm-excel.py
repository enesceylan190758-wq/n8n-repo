#!/usr/bin/env python3
"""Nefalix CRM (Estesoft Stella kopyasi) — sayfa sayfa ekran envanteri Excel'i.

Her sheet Stella'daki bir modulu/ekrani dokumante eder (ekran goruntulerinden birebir).

Kaynak: Stella ekranlari 15.07.2026 + docs/nefalix-stella-crm-plan.md
Cikti:  docs/Nefalix_Stella_CRM_Plani.xlsx

Kullanim: python3 execution/generate-stella-crm-excel.py
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

OUT = Path(__file__).resolve().parent.parent / "docs" / "Nefalix_Stella_CRM_Plani.xlsx"
TODAY = date(2026, 7, 15)


class Sheet:
    def __init__(self, name: str, widths: list[float]):
        self.name = name
        self.widths = widths
        self.rows: list[list[dict]] = []

    def add_row(self, values: list[str], style: str = "text"):
        self.rows.append([{"value": v, "style": style} for v in values])


def col_name(idx: int) -> str:
    out = ""
    while idx:
        idx, rem = divmod(idx - 1, 26)
        out = chr(65 + rem) + out
    return out


def inline_cell(ref: str, value: str, style_id: int) -> str:
    safe = escape("" if value is None else str(value))
    return f'<c r="{ref}" t="inlineStr" s="{style_id}"><is><t xml:space="preserve">{safe}</t></is></c>'


def sheet_xml(sheet: Sheet) -> str:
    cols = "".join(
        f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>'
        for i, w in enumerate(sheet.widths, 1)
    )
    rows_xml = []
    for r_idx, row in enumerate(sheet.rows, 1):
        cells = []
        for c_idx, cell in enumerate(row, 1):
            ref = f"{col_name(c_idx)}{r_idx}"
            style_id = {"title": 1, "header": 2, "plain": 3, "text": 4, "accent": 5}.get(cell["style"], 4)
            cells.append(inline_cell(ref, cell["value"], style_id))
        rows_xml.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetViews><sheetView workbookViewId="0" showGridLines="0"/></sheetViews>
  <cols>{cols}</cols>
  <sheetData>
    {"".join(rows_xml)}
  </sheetData>
</worksheet>'''


def workbook_xml(sheets: list[Sheet]) -> str:
    entries = "".join(
        f'<sheet name="{escape(sheet.name)}" sheetId="{idx}" r:id="rId{idx}"/>'
        for idx, sheet in enumerate(sheets, 1)
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>{entries}</sheets>
</workbook>'''


def workbook_rels_xml(sheets: list[Sheet]) -> str:
    rels = "".join(
        f'<Relationship Id="rId{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{idx}.xml"/>'
        for idx, _ in enumerate(sheets, 1)
    )
    rels += '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {rels}
</Relationships>'''


def root_rels_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''


def content_types_xml(sheets: list[Sheet]) -> str:
    overrides = "".join(
        f'<Override PartName="/xl/worksheets/sheet{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for idx, _ in enumerate(sheets, 1)
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {overrides}
</Types>'''


def styles_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="4">
    <font><sz val="11"/><name val="Calibri"/><family val="2"/></font>
    <font><b/><sz val="16"/><color rgb="FF0E2A47"/><name val="Calibri"/><family val="2"/></font>
    <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/><family val="2"/></font>
    <font><b/><sz val="11"/><color rgb="FF0E2A47"/><name val="Calibri"/><family val="2"/></font>
  </fonts>
  <fills count="6">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFFFFFFF"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF0E2A47"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFF4F6F9"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFEAF1FB"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border>
      <left style="thin"><color rgb="FFE2E8F0"/></left>
      <right style="thin"><color rgb="FFE2E8F0"/></right>
      <top style="thin"><color rgb="FFE2E8F0"/></top>
      <bottom style="thin"><color rgb="FFE2E8F0"/></bottom>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="6">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"><alignment vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="2" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="2" borderId="1" xfId="0" applyBorder="1"><alignment wrapText="1" vertical="top"/></xf>
    <xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFill="1" applyBorder="1"><alignment wrapText="1" vertical="top"/></xf>
    <xf numFmtId="0" fontId="3" fillId="5" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment wrapText="1" vertical="top"/></xf>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''


def core_xml() -> str:
    iso = TODAY.isoformat()
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Nefalix Stella CRM Plani</dc:title>
  <dc:creator>Cursor</dc:creator>
  <cp:lastModifiedBy>Cursor</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{iso}T12:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{iso}T12:00:00Z</dcterms:modified>
</cp:coreProperties>'''


def app_xml(sheets: list[Sheet]) -> str:
    titles = "".join(f"<vt:lpstr>{escape(s.name)}</vt:lpstr>" for s in sheets)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Cursor</Application>
  <TitlesOfParts>
    <vt:vector size="{len(sheets)}" baseType="lpstr">{titles}</vt:vector>
  </TitlesOfParts>
</Properties>'''


# ---------------------------------------------------------------- CONTENT ---

def build_sheets() -> list[Sheet]:
    sheets: list[Sheet] = []

    # ================= 0. OZET =================
    s = Sheet("0-Özet", [28, 72])
    s.add_row(["NEFALİX CRM — ESTESOFT STELLA ENVANTERİ"], "title")
    s.add_row([f"Kaynak: Medident Stella ekran görüntüleri (medidentistanbul.stellamedi.com) | {TODAY.strftime('%d.%m.%Y')}"], "plain")
    s.add_row(["Her sayfa Stella'daki bir modülü/ekranı birebir dokümante eder. Nefalix kopyası bu envantere göre kurulacak."], "plain")
    s.add_row([""])
    s.add_row(["Sayfa", "İçerik"], "header")
    for row in [
        ["1-Üst Menü", "9 ana menü + tüm alt menüler (dropdown'lardan birebir)"],
        ["2-CRM Lead", "Lead Listesi ekranı: kolonlar, aksiyonlar, örnek veri"],
        ["3-Dinamik Arama", "Dinamik Arama ekranı: kolonlar, filtreler, örnek 11 satır"],
        ["4-Danışan Listesi", "Danışan Listesi: kolonlar + gerçek örnek satırlar"],
        ["5-Danışan Kartı", "Kart yapısı: header, sidebar (23 menü), 3 kolon, notlar"],
        ["6-Segmentler", "Ekranda görülen tüm segmentler + dinamik kuralı"],
        ["7-Randevu", "Takvim ekranı + randevu detay modal alanları"],
        ["8-Gelirler-Kasa", "Kasa özeti, gelir/gider detay panelleri, işlem tablosu"],
        ["9-Giderler", "Gider Kaydet formu + Giderler alt menüsü + kategoriler"],
        ["10-WhatsApp", "Yönetim paneli sekmeleri + hesap tablosu"],
        ["11-Raporlar", "Rapor index: 6 kategori, tüm rapor isimleri"],
        ["12-Sistem", "Sistem alt menüleri + Ayarlar sidebar + genel ayar toggle'ları"],
        ["13-Destek", "Destek menüsü"],
        ["14-Süreç", "Lead → atama → not → segment → dinamik döngüsü (operasyon)"],
        ["15-Nefalix Planı", "Faz planı + veri modeli + MVP kabul kriterleri"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["Not", "Detaylı ekran spec: docs/nefalix-stella-crm-plan.md · HTML mock: clinic-crm/index.html"], "accent")
    sheets.append(s)

    # ================= 1. UST MENU =================
    s = Sheet("1-Üst Menü", [16, 32, 56])
    s.add_row(["ÜST MENÜ ENVANTERİ"], "title")
    s.add_row(["Sıra: Ana sayfa · CRM · DANIŞAN · RANDEVU · GELİRLER · GİDERLER · WHATSAPP · RAPOR · SİSTEM · DESTEK"], "plain")
    s.add_row(["Global üst bar: logo · arama 'Ara (Medident İstanbul)' · WhatsApp · bildirim · ana sayfa · dil (EN/TR) · profil"], "plain")
    s.add_row([""])
    s.add_row(["Ana Menü", "Alt Menü", "Açıklama / Stella URL"], "header")
    for row in [
        ["CRM", "Yeni Lead", "Manuel lead açma"],
        ["CRM", "Lead Listesi", "/lead — ham lead havuzu"],
        ["CRM", "Salesline", "Pipeline görünümü"],
        ["CRM", "Dinamik Arama", "/dynamicSearch — günlük arama kuyruğu"],
        ["CRM", "Dinamik Arama - Havuz", "Ortak/atanmamış dinamik havuz"],
        ["CRM", "Lead Dönüşüm Geçmişi", "Lead → danışan dönüşüm logu"],
        ["CRM", "Lead Takibi", "Genel takip"],
        ["CRM", "CRM Ayarları", "Kaynak/segment/atama ayarları"],
        ["DANIŞAN", "Yeni Danışan", "Yeni hasta kartı"],
        ["DANIŞAN", "Danışan Listesi", "/customer — tüm kartlar"],
        ["DANIŞAN", "Yeni Teklif", "Teklif oluştur"],
        ["DANIŞAN", "Teklifler", "Teklif listesi"],
        ["DANIŞAN", "Notlar & Görevler", "Not/görev yönetimi"],
        ["DANIŞAN", "Şikayetler", "Şikayet kayıtları"],
        ["RANDEVU", "Yeni Randevu", "Randevu formu"],
        ["RANDEVU", "Takvim", "/appointment/calendar/general"],
        ["RANDEVU", "Randevu Listesi", "Tablo görünüm"],
        ["RANDEVU", "Etkinlikler", "Etkinlik kayıtları"],
        ["RANDEVU", "Transfer Takvimi", "Sağlık turizmi transferleri"],
        ["GELİRLER", "Yeni Satış", "Satış kaydı"],
        ["GELİRLER", "Kasa", "/accounting/summary — kasa özeti"],
        ["GELİRLER", "Satış Listesi", "Satışlar"],
        ["GELİRLER", "Bakiye Listesi", "Açık bakiyeler"],
        ["GELİRLER", "Banka Özet", "Banka özeti"],
        ["GELİRLER", "Faturalar", "Fatura listesi"],
        ["GELİRLER", "Gelirler", "Gelir kayıtları"],
        ["GİDERLER", "Gider Kaydet", "/menu/expense/new — gider formu"],
        ["GİDERLER", "Yeni Firma", "Tedarikçi/firma tanımı"],
        ["GİDERLER", "Firma Listesi", "Firma listesi"],
        ["GİDERLER", "Yeni Ödeme/Ürün Alımı", "Firma ödemesi / alım kaydı"],
        ["GİDERLER", "Firma Ödemeleri", "Firma ödeme listesi"],
        ["GİDERLER", "Ödenecekler", "Vadesi gelen ödemeler"],
        ["GİDERLER", "Onaylar", "Gider onay akışı"],
        ["GİDERLER", "Giderler", "Gider listesi"],
        ["WHATSAPP", "Whatsapp Yönetim Paneli", "/integrations/whatsappManagementPanel"],
        ["WHATSAPP", "Whatsapp Raporları", "Mesaj raporları"],
        ["WHATSAPP", "Meta Yönetim Paneli", "Resmi Meta API paneli"],
        ["RAPOR", "Tüm Raporlar", "/reporting/index — rapor kartları"],
        ["SİSTEM", "Yetki", "Rol/ekran yetkileri"],
        ["SİSTEM", "Ayarlar", "/management/generalSettings"],
        ["SİSTEM", "Güvenlik Ayarları", "Güvenlik"],
        ["SİSTEM", "Personel", "Kullanıcı/personel yönetimi"],
        ["SİSTEM", "Prim Ayarlamaları", "Prim kuralları"],
        ["SİSTEM", "Entegrasyonlar", "Webhook/harici sistem"],
        ["SİSTEM", "Api Yönetimi", "API key / Swagger"],
        ["SİSTEM", "Hizmet", "Hizmet tanımları"],
        ["SİSTEM", "Paket", "Paket tanımları"],
        ["SİSTEM", "Ürün", "Ürün tanımları"],
        ["SİSTEM", "Tanımlamalar", "Lookup'lar (segment, kaynak, oda...)"],
        ["SİSTEM", "Toplu Sms Gönderim Onayları", "Toplu SMS onayı"],
        ["DESTEK", "Kayıtlarım", "Destek ticket'larım"],
        ["DESTEK", "Yeni Destek Kaydı", "Yeni ticket"],
    ]:
        s.add_row(row, "text")
    sheets.append(s)

    # ================= 2. CRM LEAD =================
    s = Sheet("2-CRM Lead", [22, 78])
    s.add_row(["CRM → LEAD LİSTESİ"], "title")
    s.add_row(["Stella URL: /lead | Başlık: 'Leadler'"], "plain")
    s.add_row([""])
    s.add_row(["Öğe", "Detay"], "header")
    for row in [
        ["Üst aksiyonlar", "İşlemler (dropdown, sağ üst) · Arama kriterleri (açılır filtre) · Ara (yeşil buton) · Kolonları filtrele"],
        ["Tablo kolonları", "checkbox · Kayıt tarihi (örn. 08.07.2026 23:17) · Ülke (ikon) · Lead (ad) · Telefon · İşlemler"],
        ["Satır aksiyonları", "Aç/yönlendir (ok butonu) · satır menüsü (▾)"],
        ["Sıralama", "Kayıt tarihi azalan (en yeni üstte)"],
        ["Kaynaklar", "WhatsApp, web sitesi, forum, form — otomatik düşer; ayrıca manuel Yeni Lead"],
        ["Spam gerçeği", "Ekranda bot lead'ler görünüyor (Robertmeery, Jimmyfub) → Nefalix'te spam filtresi düşünülmeli"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["Örnek satır (ekrandan)", ""], "header")
    for row in [
        ["08.07.2026 23:17", "Robertmeery · 85627132716"],
        ["08.07.2026 12:32", "Jimmyfub · 82677364186"],
        ["08.07.2026 06:02", "Traveldam · 87523825156"],
        ["07.07.2026 18:07", "Robertmeery · 88515535336"],
        ["06.07.2026 18:44", "Jimmyfub · 86393222774"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["Akış", "Lead buradan satış temsilcisine yönlendirilir → danışan kartı açılır → not+segment → Dinamik Arama döngüsü"], "accent")
    sheets.append(s)

    # ================= 3. DINAMIK =================
    s = Sheet("3-Dinamik Arama", [20, 18, 28, 16, 22, 18, 18])
    s.add_row(["CRM → DİNAMİK ARAMA (sistemin kalbi)"], "title")
    s.add_row(["Stella URL: /dynamicSearch | Segmente göre günlük arama kuyruğu; temsilcinin günlük işi bu liste"], "plain")
    s.add_row([""])
    s.add_row(["Öğe", "Detay", "", "", "", "", ""], "header")
    for row in [
        ["Üst aksiyonlar", "İşlemler ▾ · Arama kriterleri · Sms gönder · E-Posta gönder · Ara", "", "", "", "", ""],
        ["Kolonlar", "Dosya no · Ülke · Danışan · Telefon · Segment · Satış temsilcisi · Referans kaynağı · Kayıt tarihi · Değişiklik tarihi · İşlemler", "", "", "", "", ""],
        ["Satır aksiyonları", "Yeşil not butonu · detay · yer imi/bayrak ikonları", "", "", "", "", ""],
        ["Kural", "Segment değişen kayıt segment süresine göre bu listeye düşer; 'Ulaşılamadı' her gün yeniden düşer", "", "", "", "", ""],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["Danışan", "Telefon", "Segment", "Temsilci", "Referans kaynağı", "Kayıt", "Değişiklik"], "header")
    for row in [
        ["ARİF", "+4917661857475", "★ Teklif Verildi", "Enes Ceylan", "WHATSAPP TR-medident", "11.06.2026 18:25", "11.06.2026 18:42"],
        ["Erkan Arici", "+4915217687365", "★ Teklif Verildi", "Enes Ceylan", "—", "19.05.2026 17:32", "22.05.2026 19:19"],
        ["Salih Okatan", "+491638114626", "● Ulaşılamadı Tekrar Aranacak", "Enes Ceylan", "—", "11.04.2026 15:42", "22.05.2026 18:43"],
        ["Hüseyin Gazi Halis", "+491775565951", "● Ulaşılamadı Tekrar Aranacak", "Enes Ceylan", "—", "11.04.2026 15:42", "22.05.2026 18:42"],
        ["duran-ap", "+491637213541", "Röntgen ve Fotoğraf Gönderecek", "Enes Ceylan", "WHATSAPP TR-medident", "09.04.2026 16:33", "22.05.2026 18:36"],
        ["medi-dent", "+491632265784", "★ Teklif Verildi", "Enes Ceylan", "WHATSAPP TR-medident", "14.04.2026 16:54", "22.05.2026 18:34"],
        ["Ilyas Carcar", "+491796873763", "Röntgen ve Fotoğraf Gönderecek", "Enes Ceylan", "—", "05.05.2026 17:51", "22.05.2026 18:33"],
        ["Nazik Balabanoğlu-medi", "+4917623883536", "● Ulaşılamadı Tekrar Aranacak", "Enes Ceylan", "WHATSAPP TR-medident", "16.04.2026 18:01", "22.05.2026 18:29"],
        ["Müge Deniz", "+4915126959368", "● Ulaşılamadı Tekrar Aranacak", "Enes Ceylan", "—", "16.04.2026 17:36", "22.05.2026 18:25"],
        ["medi-dent", "+491746610963", "● Ulaşılamadı Tekrar Aranacak", "Enes Ceylan", "WHATSAPP TR-medident", "14.04.2026 16:54", "22.05.2026 18:20"],
        ["medi-app", "+491726405712", "● Ulaşılamadı Tekrar Aranacak", "Enes Ceylan", "WHATSAPP TR-medident", "14.04.2026 16:54", "22.05.2026 19:19"],
    ]:
        s.add_row(row, "text")
    sheets.append(s)

    # ================= 4. DANISAN LISTESI =================
    s = Sheet("4-Danışan Listesi", [8, 20, 18, 26, 20, 22, 14, 16])
    s.add_row(["DANIŞAN → DANIŞAN LİSTESİ"], "title")
    s.add_row(["Stella URL: /customer | Üst aksiyonlar: İşlemler ▾ · Arama kriterleri · Sms gönder · E-Posta gönder · Ara · Kolonları filtrele"], "plain")
    s.add_row(["Kolonlar: checkbox · ID · durum ikonu (sarı nokta) · Ad · Ülke · Telefon · Segment · Satış Temsilcisi · Referans kaynağı · Değişiklik tarihi · Kayıt tarihi · İşlemler (WhatsApp yeşil · aç · menü)"], "plain")
    s.add_row([""])
    s.add_row(["ID", "Ad", "Telefon", "Segment", "Temsilci", "Referans kaynağı", "Değişiklik", "Kayıt"], "header")
    for row in [
        ["11143", "mediapp", "+4917680632460", "● Ulaşılamadı Tekrar Aranacak", "Abdülkadir Yaşar", "WHATSAPP TR-medident", "01.07.2026", "01.07.2026 19:57"],
        ["11142", "enes ceylan", "+905359288250", "—", "Enes Ceylan", "—", "—", "22.06.2026 16:15"],
        ["11141", "ARİF", "+4917661857475", "★ Teklif Verildi", "Enes Ceylan", "WHATSAPP TR-medident", "11.06.2026", "11.06.2026 18:25"],
        ["11140", "Ali çarkıt", "+491728668794", "⚡ YENİ DATA", "Enes Ceylan", "WHATSAPP TR-medident", "—", "05.06.2026 17:49"],
        ["11139", "Tokac, Müjğan", "+491785733878", "● Ulaşılamadı Tekrar Aranacak", "Abdülkadir Yaşar", "WHATSAPP TR-medident", "08.06.2026", "05.06.2026 17:49"],
        ["11138", "~HASRST", "+4915908484101", "● Ulaşılamadı Tekrar Aranacak", "Abdülkadir Yaşar", "WHATSAPP TR-medident", "05.06.2026", "05.06.2026 17:36"],
        ["11137", "Saadet BALIKCI", "+4917670781730", "● Ulaşılamadı Tekrar Aranacak", "Abdülkadir Yaşar", "WHATSAPP TR-medident", "05.06.2026", "05.06.2026 17:36"],
        ["11136", "sara", "+491796923828", "● Ulaşılamadı Tekrar Aranacak", "Abdülkadir Yaşar", "WHATSAPP TR-medident", "05.06.2026", "05.06.2026 17:36"],
        ["11135", "HASAN BİLDİK REFİ", "+4915204299233", "★ Teklif Verildi", "Abdülkadir Yaşar", "Hasta Referansı", "03.06.2026", "03.06.2026 15:50"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["Not", "'YENİ DATA' henüz aranmamış kayıt işareti; referans kaynağı 'Hasta Referansı' da olabilir (WhatsApp dışı)", "", "", "", "", "", ""], "accent")
    sheets.append(s)

    # ================= 5. DANISAN KARTI =================
    s = Sheet("5-Danışan Kartı", [24, 76])
    s.add_row(["DANIŞAN KARTI (customer detail)"], "title")
    s.add_row(["Stella URL: /customer/{uuid} | Örnekler: ARİF #11141, NURSEL DEMİRDAŞ #9386"], "plain")
    s.add_row([""])
    s.add_row(["Bölüm", "İçerik (ekrandan birebir)"], "header")
    for row in [
        ["Header", "Avatar · Ad + ülke bayrağı + onay rozeti · [# ID] · [telefon] · sağda Hızlı İşlemler menüsü"],
        ["Hızlı İşlemler menüsü", "Yeni Not/Görev · Yeni Teklif · Yeni Randevu · Yeni Satış"],
        ["Sol sidebar (23 menü)", "Detaylar · Düzenle · Formlar · Teklif · Randevu · Notlar · İşlem Kartları · Dosya & Fotoğraf · Satış & Tahsilat · Faturalar · Puan · Paket Takibi · İletişim · Tanılar · Transfer & Konaklama · Diyetisyen İzlem Formu · Obezite İzlem Formu · Reçete · Tıbbi Raporlar · Diş Tedavisi · Göz Muayeneleri · Alternatif Obezite İzlem Formu · Tahliller"],
        ["Orta kolon: İşlemler", "Avatar + 'Potansiyel Hasta' badge · Whatsapp sohbeti başlat · Düzenleme geçmişi · Medikal Kayıtları İndir · Dosya No Değiştir · Sil (kırmızı)"],
        ["Orta kolon: sayaçlar", "Randevu / Satış / Teklif sayıları + her birine '+ Yeni' butonu (örn. Nursel: 1 randevu, 1 teklif)"],
        ["Orta kolon: Etiketler", "Açılır etiket bölümü"],
        ["Bilgi: Kişisel", "E-Posta (örn. nursel-43@hotmail.de) · Kayıt tarihi"],
        ["Bilgi: Adres", "Ülke (Almanya) · Dil (German)"],
        ["Bilgi: Diğer", "Kayıt açan · Segment · Referans kaynağı · Satış temsilcisi · Lead Kayıt Tarihi · Kampanyası (örn. WM - Medident - Türkçe) · Reklam seti (örn. İnterest) · Reklamı (örn. Uykuda Diş Tedavi) · Düzenleyen · Değişiklik tarihi"],
        ["Sağ kolon: Hızlı Not", "Textarea 'Notunuzu giriniz' · tarih alanı (GG.AA.YYYY) · segment dropdown · yeşil Kaydet"],
        ["Not geçmişi", "Her not: metin · tarih-saat · yazan kişi · segment etiketi (★) · renk noktası; örn. 'iptal etti' 07.05.2025 Abdülkadir Yaşar → İptal"],
        ["Alt sekmeler", "İşlem Geçmişi · Formlar · Teklifler · Tanılar"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["ÖNEMLİ BULGU", "Meta/Facebook reklam izleme alanları var: Kampanyası + Reklam seti + Reklamı → lead hangi reklamdan geldi takibi. Nefalix'te de olmalı."], "accent")
    s.add_row(["ÖNEMLİ BULGU", "Not geçmişinde süreli segmentler görüldü: 'Kısa Vadede Düşünecek 1 Hafta', '2 Gün Sonra Aranacak' → dinamik düşme süresi segment bazlı değişebiliyor."], "accent")
    sheets.append(s)

    # ================= 6. SEGMENTLER =================
    s = Sheet("6-Segmentler", [32, 22, 46])
    s.add_row(["SEGMENT KATALOĞU"], "title")
    s.add_row(["Kaynak 1: Danışan kartı segment dropdown (ARİF ekranı) | Kaynak 2: Not geçmişi etiketleri (Nursel ekranı)"], "plain")
    s.add_row([""])
    s.add_row(["Segment (dropdown'dan)", "Dinamik Arama'da?", "Kural / Not"], "header")
    for row in [
        ["Mesajlaşılıyor", "EVET", "Görüşme sürüyor; takipte kalır"],
        ["Orta Vadede Düşünecek", "EVET", "Periyodik hatırlatma"],
        ["Otel Satış", "HAYIR", "Kapanış segmenti"],
        ["Potansiyel", "EVET", "Takip sürer"],
        ["Revizyon", "EVET", "İşlem revizyonu bekleniyor"],
        ["Röntgen ve Fotoğraf Gönderecek", "EVET", "Hasta belge gönderene kadar takip"],
        ["Satıldı", "HAYIR", "Satış kapandı; operasyona geçer"],
        ["Sıcak Alacak", "EVET", "Yüksek öncelik"],
        ["Süreci Biten", "HAYIR", "Arşiv"],
        ["Takip", "EVET", "Standart takip"],
        ["Tedaviye Uygun Değil", "HAYIR", "Kapalı"],
        ["Teklif Verildi", "EVET", "Cevap bekleniyor"],
        ["TEKRAR GELEN LEAD", "EVET", "Aynı kişi yeniden başvurdu; öncelikli"],
        ["Ulaşılamadı-Tekrar Aranacak", "EVET", "HER GÜN yeniden düşer (günlük reset)"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["Not geçmişinde görülen ek segmentler (dropdown scroll dışı)", "", ""], "header")
    for row in [
        ["İptal", "HAYIR", "Nursel kartında segment=İptal"],
        ["Kısa Vadede Düşünecek 1 Hafta", "EVET (1 hafta sonra)", "Süreli segment — dinamik düşme gecikmesi segment içinde"],
        ["2 Gün Sonra Aranacak", "EVET (2 gün sonra)", "Süreli segment"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["TASARIM KARARI", "Nefalix segment tablosuna 'dynamic_delay_days' alanı (0=ertesi gün, 2, 7...). Segment dışı durumlar: 'Potansiyel Hasta' (kart badge), 'YENİ DATA' (liste ikonu).", ""], "accent")
    sheets.append(s)

    # ================= 7. RANDEVU =================
    s = Sheet("7-Randevu", [24, 76])
    s.add_row(["RANDEVU → TAKVİM + DETAY MODAL"], "title")
    s.add_row(["Stella URL: /appointment/calendar/general | Aylık grid, renkli randevu blokları"], "plain")
    s.add_row([""])
    s.add_row(["Bölüm", "İçerik (ekrandan birebir)"], "header")
    for row in [
        ["Takvim üst bar", "Genel Takvim ▾ · tarih (15.07.2026 + takvim ikonu) · Takvim Gösterim Tipi ▾ · Renk kaynağı ▾ · İşlemler ▾"],
        ["Filtreler", "Randevu Durum (select) · Oda (select) · Personel (select)"],
        ["Gezinme", "‹ › oklar · Bugün · Yarın · sağda görünüm: Ay / Hafta / Gün / Ajanda"],
        ["Randevu bloğu", "Renkli şerit: saat + ad + hizmet kısaltması; yeşil=tamamlandı, turuncu=beklemede (örn. '17:00 Sevda Emel Korkmaz ( PORS')"],
        ["Modal: üst", "Durum select (Beklemede) · Hızlı Düzenle (mavi) · İşlemler ▾"],
        ["Modal: kişi", "Avatar · Ad Soyad (link → danışan kartı) · Dosya no (MDİ-135) · Telefon (+4915563072884)"],
        ["Modal: randevu", "Saat (17:00 - 18:30) · Hizmet (PORSELEN DİŞ KAPLAMA) · Personel (Enes Ceylan) · Oda (DENTALZONE Prova/Geçici Diş Randevusu) · Randevu Tipi (2. Aşama Hastası) · Not (serbest metin)"],
        ["Modal: audit", "Kayıt tarihi (10.06.2026 10:22) · Oluşturan · Değişiklik tarihi · Düzenleyen"],
        ["Modal: alt", "Kapat (yeşil buton)"],
        ["Form alanları", "Tarih · başlangıç saati · bitiş saati · danışan · danışman/personel · oda · hizmet · randevu durumu · randevu tipi · not"],
        ["Randevu durumları", "Beklemede · Geldi · Tamamlandı · İptal · Gelmedi (+ 'saati geçen beklemede otomatik tamamlandı' ayarı var)"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["NEFALİX BAĞLANTISI", "Randevu 'Tamamlandı' olayı mevcut Nefalix NPS/WhatsApp akışını tetikler (wf-08 / estesoft_integration.md)"], "accent")
    sheets.append(s)

    # ================= 8. GELIRLER / KASA =================
    s = Sheet("8-Gelirler-Kasa", [14, 20, 12, 42, 10, 8, 12])
    s.add_row(["GELİRLER → KASA (accounting/summary)"], "title")
    s.add_row(["Filtre: Arama kriterleri · Aramayı kaydet · Tarih aralığı (01.06.2026 - 30.06.2026) · Ara"], "plain")
    s.add_row([""])
    s.add_row(["Özet kartları (filtre sonrası üstte)", "", "", "", "", "", ""], "header")
    for row in [
        ["Gelir", "3.200 TRY / 26.390 EUR", "", "Çift para birimi gösterimi", "", "", ""],
        ["Gider", "-256.876 TRY / -5.750 EUR", "", "", "", "", ""],
        ["Net", "-253.676 TRY / 20.640 EUR", "", "", "", "", ""],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["Detay panelleri", "", "", "", "", "", ""], "header")
    s.add_row(["Gelir - Detaylar (yeşil panel)", "Ödeme Yöntemleri: Nakit 3.200 TRY / 26.390 EUR", "", "", "", "", ""], "text")
    s.add_row(["Gider - Detaylar (kırmızı panel)", "Ödeme Yöntemleri: Nakit · Gider Kalemleri Kategorisi: Klinik Giderleri -5.750 EUR · Maaş ve personel -200.213 TRY · Otel Konaklama ve Transfer -29.940 TRY · Rutin Şirket -26.723 TRY", "", "", "", "", ""], "text")
    s.add_row([""])
    s.add_row(["Tarih", "Danışan/Firma", "İşlem tipi", "Bilgi (kategori + not)", "Referans", "Yöntem", "Tutar"], "header")
    for row in [
        ["30.06.2026", "Bayram Acikel", "Para girişi", "Satış", "D6819", "Nakit", "4.840 EUR"],
        ["30.06.2026", "Refiyce Celik", "Para girişi", "Satış", "ZZ7JR", "Nakit", "3.500 EUR"],
        ["30.06.2026", "Refiyce Celik", "Para girişi", "Satış", "2CDY8", "Nakit", "600 EUR"],
        ["30.06.2026", "—", "Para çıkışı", "Cepten Harcamalar (Rutin Şirket) — NEFALIXAI HOSTING API VS", "—", "Nakit", "-5.583 TRY"],
        ["30.06.2026", "—", "Para çıkışı", "SGK ÖDEMESİ (Maaş ve personel) — SGK", "—", "Nakit", "-20.213 TRY"],
        ["30.06.2026", "—", "Para çıkışı", "Telefon Faturası (Rutin Şirket) — VODAFON", "—", "Nakit", "-3.500 TRY"],
        ["30.06.2026", "—", "Para çıkışı", "Cepten Harcamalar (Rutin Şirket) — KADİR CEPTEN GİDER", "—", "Nakit", "-11.140 TRY"],
        ["30.06.2026", "—", "Para çıkışı", "MUHASEBE ÜCRETİ (Rutin Şirket) — MUHASEBE", "—", "Nakit", "-3.000 TRY"],
        ["30.06.2026", "—", "Para çıkışı", "Nivrasyon Ödemesi (Rutin Şirket)", "—", "Nakit", "-3.500 TRY"],
        ["30.06.2026", "—", "Para çıkışı", "Dentalzone Ödemesi (Klinik Giderleri) — KLİNİK ÖDEMESİ", "—", "Nakit", "-5.750 EUR"],
        ["30.06.2026", "—", "Para çıkışı", "Maaş Ödemesi (Maaş ve personel) — ÖDENDİ", "—", "Nakit", "-180.000 TRY"],
        ["30.06.2026", "—", "Para çıkışı", "SEL TUR KONAKLAMA-TRANSFER (Otel Konaklama ve Transfer) — otel transfer", "—", "Nakit", "-29.940 TRY"],
        ["29.06.2026", "Yağmur nihat ketenci", "Para girişi", "Satış", "Z0S06", "Nakit", "2.000 EUR"],
        ["22.06.2026", "mustafa Şenlikci", "Para girişi", "Satış", "EKZMR", "Nakit", "9.000 EUR"],
        ["22.06.2026", "Ali bektaş ebru yam re", "Para girişi", "Satış", "Y5AH1", "Nakit", "3.200 TRY"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["Kolon notu", "Tam kolon listesi: Ödeme tarihi · Danışan/Firma · İşlem tipi · Bilgi · Referans kodu · Ödeme Yöntemi · Ödeme Aracı · Not · Tutar · İşlemler (düzenle; para çıkışında sil)", "", "", "", "", ""], "accent")
    sheets.append(s)

    # ================= 9. GIDERLER =================
    s = Sheet("9-Giderler", [30, 70])
    s.add_row(["GİDERLER → GİDER KAYDET"], "title")
    s.add_row(["Stella URL: /menu/expense/new | Sade tek kolon form"], "plain")
    s.add_row([""])
    s.add_row(["Form alanı", "Tip / Örnek"], "header")
    for row in [
        ["Kategori", "Select (boş başlar)"],
        ["Gider Kalemi", "Select — kategoriye bağlı alt kalem"],
        ["Fatura no/Ek Bilgi", "Text"],
        ["Gider tarihi", "Date (varsayılan bugün: 15.07.2026)"],
        ["Tutar", "Number (0,00) + para birimi select (TRY varsayılan, EUR...)"],
        ["Ödeme Yöntemi", "Select (Nakit varsayılan)"],
        ["Notlar", "Textarea"],
        ["Butonlar", "Vazgeç (turuncu) · Kaydet (yeşil)"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["Gider kategorileri (kasa ekranından)", ""], "header")
    for row in [
        ["Klinik Giderleri", "Örn. Dentalzone Ödemesi"],
        ["Maaş ve personel Giderleri", "Örn. Maaş Ödemesi, SGK Ödemesi"],
        ["Otel Konaklama ve Transfer Giderleri", "Örn. SEL TUR konaklama-transfer"],
        ["Rutin Şirket Giderleri", "Örn. Telefon, Muhasebe, Cepten Harcamalar, Hosting"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["Alt menü (tam liste)", "Gider Kaydet · Yeni Firma · Firma Listesi · Yeni Ödeme/Ürün Alımı · Firma Ödemeleri · Ödenecekler · Onaylar · Giderler"], "accent")
    s.add_row(["Ayar bağlantısı", "Sistem ayarlarında 'Gider & Firma ödemesi kaydederken onay mekanizması kullan' toggle'ı var"], "accent")
    sheets.append(s)

    # ================= 10. WHATSAPP =================
    s = Sheet("10-WhatsApp", [30, 70])
    s.add_row(["WHATSAPP → YÖNETİM PANELİ"], "title")
    s.add_row(["Stella URL: /integrations/whatsappManagementPanel"], "plain")
    s.add_row([""])
    s.add_row(["Öğe", "Detay"], "header")
    for row in [
        ["Sekmeler (6)", "Whatsapp hesapları · Template mesajlar · WhatsApp Template Tercihleri · Otomatik yanıtlayıcılar · Whatsapp otomatik atama kuralları · Ayarlar"],
        ["Hesap tablosu kolonları", "Ad · Telefon · Sağlayıcı · Varsayılan sender mı? · Durum · İşlemler"],
        ["Hesap ekleme", "Sağ üst yeşil 'Hesap Ekle' butonu"],
        ["Medident durumu", "Tablo boş — WhatsApp hesabı Stella'ya bağlanmamış; iletişim Nefalix/Evolution üstünden"],
        ["Otomatik atama", "Gelen WhatsApp mesajını temsilciye otomatik atama kuralları (lead dağıtımının otomasyonu)"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["NEFALİX AVANTAJI", "Evolution API + mevcut inbox/chatbot zaten canlı. Stella'nın hesap/template/otomatik-atama UX'ini kopyala; motor Nefalix'in kendi WhatsApp altyapısı. Referans kaynağı 'WHATSAPP TR-medident' formatı korunmalı."], "accent")
    sheets.append(s)

    # ================= 11. RAPORLAR =================
    s = Sheet("11-Raporlar", [24, 44, 32])
    s.add_row(["RAPOR → TÜM RAPORLAR (reporting/index)"], "title")
    s.add_row(["6 kart halinde rapor kategorileri; Sık Kullanılanlar yıldızla işaretleniyor"], "plain")
    s.add_row([""])
    s.add_row(["Kategori", "Rapor", "Nefalix MVP?"], "header")
    for row in [
        ["Sık Kullanılanlar", "Danışan Bağlılığı · Çapraz Satış · Satış · Tahsilat · Satış Fiyat Analizi", "Yıldızlama özelliği P2"],
        ["Finansal", "Satış Raporu", "EVET (MVP)"],
        ["Finansal", "Hizmet Satış Adetleri", "P2"],
        ["Finansal", "Ürün Satış Adetleri", "P2"],
        ["Finansal", "Paket Satış Adetleri", "P2"],
        ["Finansal", "Tahsilat Raporu", "EVET (MVP)"],
        ["Finansal", "Çapraz Satış Raporu", "P2"],
        ["Finansal", "Satış Fiyat Analizi", "P2"],
        ["Finansal", "Prim Raporu", "P3"],
        ["Finansal", "Kapora Raporu", "P3"],
        ["Finansal", "Teklif Raporu", "P2"],
        ["Danışan", "Danışan Bağlılığı Raporu", "P2"],
        ["Danışan", "Danışan Performans Raporu", "P2"],
        ["Danışan", "Referans Kaynağı Performans Raporu", "EVET (MVP) — hangi kanal lead getiriyor"],
        ["Danışan", "Referans Getiren Kişi Performans Raporu", "P2"],
        ["Danışan", "Puan Raporu", "P3"],
        ["Danışan", "Gelmeyen Danışanlar Raporu", "EVET (MVP)"],
        ["Danışan", "Transfer raporu", "P3 (turizm)"],
        ["Danışan", "Konaklama raporu", "P3 (turizm)"],
        ["Danışan", "Obezite İzlem Raporu", "MVP dışı"],
        ["Danışan", "Danışan Temsilci & Segment Raporu", "EVET (MVP) — temsilci performansı"],
        ["Randevu", "Yardımcı Personel Görev Raporu", "P3"],
        ["Sistem", "TTB İzlem Raporu", "MVP dışı"],
        ["Sistem", "Paket Takip Raporu", "P3"],
        ["Sistem", "Stok Raporu", "MVP dışı"],
        ["Form & Anket", "Doldurulan Form & Anket", "Nefalix NPS modülü zaten var"],
        ["Form & Anket", "Gönderilen Form & Anket", "Nefalix NPS modülü zaten var"],
        ["Form & Anket", "Form & Anket Analiz", "Nefalix NPS modülü zaten var"],
    ]:
        s.add_row(row, "text")
    sheets.append(s)

    # ================= 12. SISTEM =================
    s = Sheet("12-Sistem", [30, 70])
    s.add_row(["SİSTEM → AYARLAR VE YÖNETİM"], "title")
    s.add_row(["Stella URL: /management/generalSettings"], "plain")
    s.add_row([""])
    s.add_row(["Bölüm", "İçerik (ekrandan birebir)"], "header")
    for row in [
        ["Sistem alt menüleri (12)", "Yetki · Ayarlar · Güvenlik Ayarları · Personel · Prim Ayarlamaları · Entegrasyonlar · Api Yönetimi · Hizmet · Paket · Ürün · Tanımlamalar · Toplu Sms Gönderim Onayları"],
        ["Ayarlar sidebar (10)", "Genel Ayarlar · Danışan Kayıt Tercihleri · Tablet Kayıt Tercihleri · Sms Gönderim Tercihleri · WhatsApp Template Tercihleri · Anket Tercihleri · Form Tercihleri · Puan Modülü Tercihleri · Satış Modülü Tercihleri · Hedefler"],
        ["Genel: marka", "Logo yükleme · Renk (#8BA777) · Şablon (Mint)"],
        ["Toggle 1", "Saati geçen beklemede durumundaki randevular otomatik tamamlandı olsun mu? (KAPALI)"],
        ["Toggle 2", "Randevudan ödeme oluşturulduğunda randevu durumu otomatik güncellensin mi? (KAPALI)"],
        ["Toggle 3", "Aynı saate randevu oluşturulmasına izin verilsin mi? (AÇIK)"],
        ["Toggle 4", "Gider & Firma ödemesi kaydederken onay mekanizmasını kullan (KAPALI)"],
        ["Toggle 5", "İşlem kartını randevu tarihine göre sırala (KAPALI)"],
        ["Diğer ayar", "Randevu hatırlatma mesajı gönderim saati: 16:45"],
        ["Footer bilgisi", "Estesoft 2025 © v140726_01 · Benzersiz müşteri kodu: 3LC5"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["NEFALİX İÇİN", "Tanımlamalar ekranı kritik: segment, kaynak, oda, hizmet, randevu tipi lookuplarının hepsi buradan yönetiliyor. Nefalix'te tek 'Tanımlamalar' CRUD ekranı yeterli."], "accent")
    sheets.append(s)

    # ================= 13. DESTEK =================
    s = Sheet("13-Destek", [30, 70])
    s.add_row(["DESTEK"], "title")
    s.add_row([""])
    s.add_row(["Alt menü", "Açıklama"], "header")
    s.add_row(["Kayıtlarım", "Kullanıcının açtığı destek ticket'ları"], "text")
    s.add_row(["Yeni Destek Kaydı", "Yeni ticket formu"], "text")
    s.add_row([""])
    s.add_row(["Nefalix kararı", "P3 — MVP'de basit iletişim (WhatsApp/e-posta) yeterli; ticket sistemi sonra"], "accent")
    sheets.append(s)

    # ================= 14. SUREC =================
    s = Sheet("14-Süreç", [10, 30, 60])
    s.add_row(["KRİTİK İŞ SÜRECİ: LEAD → DİNAMİK ARAMA DÖNGÜSÜ"], "title")
    s.add_row(["Medident'in günlük operasyonu — Nefalix MVP bunu birebir kurmalı"], "plain")
    s.add_row([""])
    s.add_row(["Adım", "Aşama", "Detay"], "header")
    for row in [
        ["1", "Veri gelir", "WhatsApp / web / forum / form kaynaklı kayıt otomatik Lead Listesi'ne düşer (veya manuel Yeni Lead)"],
        ["2", "Dağıtım", "Yetkili kullanıcı lead'i satış temsilcisine yönlendirir (örn. Abdülkadir'e); WhatsApp otomatik atama kuralı da destekler"],
        ["3", "Arama + Not", "Temsilci arar; danışan kartında Hızlı Not girer"],
        ["4", "Segment seçimi", "Not kaydında segment seçilir (6-Segmentler sayfası; süreli segmentler dahil)"],
        ["5", "Dinamik listeye düşme", "Dinamik=EVET segmentler segmentin süresine göre (ertesi gün / 2 gün / 1 hafta) temsilcinin Dinamik Arama listesine düşer"],
        ["6", "Günlük döngü", "Temsilci her sabah dinamik listesini açar → arar → not + segment günceller"],
        ["7", "Ulaşılamadı kuralı", "Ulaşılamadı kaydı HER ertesi gün dinamikte yeniden görünür (günlük reset)"],
        ["8", "Dönüşüm", "Teklif Verildi → Satıldı akışı: randevu (takvim) + satış (kasa para girişi) + danışan operasyona geçer"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["", "Kural", "MVP kararı"], "header")
    for row in [
        ["", "Dinamiğe girenler", "Mesajlaşılıyor · Orta Vade · Potansiyel · Revizyon · Röntgen-Foto · Sıcak · Takip · Teklif Verildi · Tekrar Gelen · Ulaşılamadı · süreli segmentler"],
        ["", "Dinamiğe girmeyenler", "Otel Satış · Satıldı · Süreci Biten · Tedaviye Uygun Değil · İptal"],
        ["", "Düşme zamanı", "Segment süresine göre: varsayılan ertesi gün 00:00 (TR); süreli segmentlerde +2 gün / +7 gün"],
        ["", "Havuz vs kişisel", "Temsilciye atanmış → kişisel liste; atanmamış → Havuz"],
        ["", "Atama", "Tek temsilci; yeniden atama (reassign) mümkün"],
        ["", "Not zorunluluğu", "Segment değişiminde not zorunlu"],
    ]:
        s.add_row(row, "text")
    sheets.append(s)

    # ================= 15. NEFALIX PLANI =================
    s = Sheet("15-Nefalix Planı", [14, 32, 54])
    s.add_row(["NEFALİX UYGULAMA PLANI"], "title")
    s.add_row(["Fazlar + veri modeli + MVP kabul kriterleri"], "plain")
    s.add_row([""])
    s.add_row(["Faz", "Kapsam", "İçerik"], "header")
    for row in [
        ["Faz 0", "Temel iskelet", "Üst menü + yetki + personel · clinic_id bağlamı · Tanımlamalar (segment, kaynak, oda, hizmet)"],
        ["Faz 1", "CRM çekirdeği (P0)", "Lead ingest (WA/web/manuel) · Lead Listesi + atama · Not + segment · Dinamik Arama + Havuz + günlük rollover job · Danışan Listesi + Kartı"],
        ["Faz 2", "Randevu (P0)", "Takvim + Yeni Randevu + durumlar · kartından randevu · 'Tamamlandı' → Nefalix NPS/WhatsApp akışı"],
        ["Faz 3", "Kasa (P1)", "Gider kaydı + kategoriler · gelir/satış kaydı · Gelir-Gider-Net özet + detay paneller"],
        ["Faz 4", "WhatsApp panel (P1)", "Evolution hesap bağlama · template / otomatik yanıt / otomatik atama · inbox-lead eşlemesi"],
        ["Faz 5", "Rapor + sistem (P2)", "MVP raporları (satış, tahsilat, referans kaynağı, temsilci&segment, gelmeyen) · yetki matrisi"],
        ["Faz 6", "Destek + Salesline (P3)", "Ticket · pipeline · teklif modülü · prim"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["", "Veri modeli (Supabase taslak)", ""], "header")
    for row in [
        ["", "crm_leads", "id, clinic_id, name, phone, country, source, campaign, ad_set, ad_name, assigned_to, status, created_at"],
        ["", "crm_clients", "id, file_no, lead_id, name, phone, email, country, language, segment_id, rep_id, source_id, campaign/ad alanları, lead_at, updated_at"],
        ["", "crm_segments", "id, code, label, show_in_dynamic, dynamic_delay_days, sort"],
        ["", "crm_notes", "id, client_id, user_id, body, segment_id, follow_up_date, created_at"],
        ["", "crm_dynamic_queue", "id, client_id, user_id, due_date, segment_id, done_at"],
        ["", "crm_appointments", "id, client_id, start, end, room, staff, service, status, type, notes, created_by, updated_by"],
        ["", "crm_transactions", "id, type (in/out), amount, currency, method, category_id, item_id, ref_code, note, paid_at, client_id"],
        ["", "crm_expense_categories/items", "Kategori + kaleme bağlı iki seviye"],
        ["", "crm_whatsapp_accounts", "id, phone, provider, is_default, status"],
        ["", "Günlük job", "crm_dynamic_queue üretimi: segment.dynamic_delay_days'e göre due_date hesapla; Ulaşılamadı'yı her gün yenile"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["", "MVP kabul kriterleri", ""], "header")
    for row in [
        ["1", "Lead otomatik düşer", "Web/WA/form lead'i Lead Listesi'ne otomatik gelir (+kampanya/reklam alanları)"],
        ["2", "Atama çalışır", "Lead Abdülkadir'e atanabilir; yeniden atama mümkün"],
        ["3", "Not + segment", "Danışan kartından not + segment kaydedilir; not geçmişi segment etiketli"],
        ["4", "Dinamik reset", "Ulaşılamadı → ertesi gün; süreli segment → süresi kadar sonra dinamikte görünür"],
        ["5", "Dinamik döngü", "Dinamik listeden arama + segment güncelleme çalışır; Havuz ayrı görünür"],
        ["6", "Randevu", "Karttan ve takvimden randevu (tarih/saat/personel/oda/hizmet/durum/tip/not)"],
        ["7", "Gider", "Kategori + kalem + tarih + tutar (TRY/EUR) + yöntem + not"],
        ["8", "Kasa özet", "Tarih filtresi sonrası Gelir/Gider/Net + kategori bazlı gider detayı"],
        ["9", "WhatsApp", "Evolution hesabı bağlanıp lead ile eşleşir; referans kaynağı otomatik yazılır"],
        ["10", "Rapor", "Referans Kaynağı + Temsilci&Segment raporları çalışır"],
    ]:
        s.add_row(row, "text")
    s.add_row([""])
    s.add_row(["", "Açık sorular", ""], "header")
    for row in [
        ["1", "Lead atamasını kim yapar?", "AÇIK — varsayılan: yönetici + temsilci kendisi alabilir"],
        ["2", "Stella'dan veri migrate edilecek mi?", "AÇIK — varsayılan: pilot dönem çift kayıt, sonra migrate"],
        ["3", "Saha CRM (/crm) ile birleşir mi?", "AÇIK — varsayılan: ayrı kalır"],
        ["4", "Süreli segmentlerin tam listesi", "Stella Tanımlamalar ekranından teyit edilmeli (dropdown'da scroll ile kesilmiş olabilir)"],
    ]:
        s.add_row(row, "text")
    sheets.append(s)

    return sheets


def main():
    sheets = build_sheets()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml(sheets))
        zf.writestr("_rels/.rels", root_rels_xml())
        zf.writestr("docProps/core.xml", core_xml())
        zf.writestr("docProps/app.xml", app_xml(sheets))
        zf.writestr("xl/workbook.xml", workbook_xml(sheets))
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml(sheets))
        zf.writestr("xl/styles.xml", styles_xml())
        for idx, sheet in enumerate(sheets, 1):
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml(sheet))
    print(OUT)


if __name__ == "__main__":
    main()
