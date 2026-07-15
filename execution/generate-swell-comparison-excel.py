#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

OUT = Path(__file__).resolve().parent.parent / "docs" / "Swell_vs_Nefalix_Karsilastirma.xlsx"
TODAY = date(2026, 7, 7)


class Sheet:
    def __init__(self, name: str, widths: list[float]):
        self.name = name
        self.widths = widths
        self.rows: list[list[dict]] = []

    def add_row(self, values: list[str], style: str = "text"):
        row = []
        for value in values:
            row.append({"value": value, "style": style})
        self.rows.append(row)


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
            style_id = {"title": 1, "header": 2, "plain": 3, "text": 4}.get(cell["style"], 4)
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
  <fonts count="3">
    <font><sz val="11"/><name val="Calibri"/><family val="2"/></font>
    <font><b/><sz val="16"/><color rgb="FF0F172A"/><name val="Calibri"/><family val="2"/></font>
    <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/><family val="2"/></font>
  </fonts>
  <fills count="5">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFFFFFFF"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF6366F1"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFF8FAFC"/><bgColor indexed="64"/></patternFill></fill>
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
  <cellXfs count="5">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"><alignment vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="2" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="2" borderId="1" xfId="0" applyBorder="1"><alignment wrapText="1" vertical="top"/></xf>
    <xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFill="1" applyBorder="1"><alignment wrapText="1" vertical="top"/></xf>
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
  <dc:title>Swell vs Nefalix Karsilastirma</dc:title>
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


def build_sheets() -> list[Sheet]:
    s1 = Sheet("Ozet", [22, 24, 24, 24])
    s1.add_row(["SWELL CX vs NEFALIX - KARSILASTIRMA"], "title")
    s1.add_row([f"Guncel arastirma ozeti | {TODAY.strftime('%d.%m.%Y')}"], "plain")
    s1.add_row([""])
    s1.add_row(["Hizli mesaj", "Nefalix'in ana farki", "Neden onemli", "Kullanim alani"], "header")
    for row in [
        ["WhatsApp-first", "Swell SMS-first; Nefalix WhatsApp-first", "TR hasta iletisiminde adoption daha yuksek", "Demo acilisi"],
        ["Yerel uyum", "KVKK + IYS + HBYS dili", "Saglikta satin alma ekibi icin guven sebebi", "Teklif / toplantı"],
        ["Gelir etkisi", "Recall + Sentinel + NPS ayni panel", "Sadece yorum degil, kayip hasta ve risk gorunurlugu", "Kapanis argumani"],
    ]:
        s1.add_row(row, "text")
    s1.add_row([""])
    s1.add_row(["Tema", "Swell", "Nefalix", "Not"], "header")
    for row in [
        ["Ana kanal", "SMS + email + webchat + Facebook", "WhatsApp + web chat", "TR'de WhatsApp davranisi daha guclu."],
        ["Hedef pazar", "DSO/MSO, multi-location healthcare", "TR klinikleri + buyume", "Swell daha enterprise; Nefalix daha yerel."],
        ["Uyumluluk", "HIPAA + SOC 2 Type II", "KVKK + IYS + HBYS", "Regulasyon dili farkli."],
        ["Negatif akisi", "Ticket + routing + AI response", "Yonetici alarmi + sikayet formu", "Nefalix saha aksiyonunu vurgulayabilir."],
        ["Ek moduller", "Listings, ticketing", "Recall, Sentinel", "Nefalix gelir geri kazanimi tarafinda ayrisiyor."],
    ]:
        s1.add_row(row, "text")

    s2 = Sheet("Ozellik Matrisi", [24, 18, 18, 38, 26])
    s2.add_row(["OZELLIK BAZLI KARSILASTIRMA"], "title")
    s2.add_row(["Canli urun + arastirma sentezi"], "plain")
    s2.add_row([""])
    s2.add_row(["Ozellik", "Swell", "Nefalix", "Detay", "Satista Mesaj"], "header")
    for row in [
        ["Review generation", "Var", "Var", "Her ikisi de ziyaret sonrasi yorum daveti gonderiyor.", "Nefalix: Google + WhatsApp yerel akis"],
        ["Google review AI", "Var", "Var", "Swell HIPAA taslak; Nefalix AI onay akisi.", "Yerel ton + insan onayi"],
        ["Patient NPS", "Var", "Var", "Swell custom surveys; Nefalix NPS -> Google/detractor karari.", "Nefalix karar agaci daha net"],
        ["Employee eNPS", "Var", "Var", "Iki platformda da ekip nabzi var.", "Ic operasyon gorunurlugu"],
        ["Ticketing", "Guclu", "Kismi", "Swell otomatik ticket + ekip atama sunuyor.", "Nefalix icin gelistirme alani"],
        ["Inbox", "SMS/webchat/Facebook", "WhatsApp/web", "Kanal farki buyuk.", "TR'de WhatsApp avantaji"],
        ["Listings management", "Var", "Yok", "Swell dizin yonetimi satiyor.", "Nefalix premium roadmap konusu olabilir"],
        ["Recall", "Belirgin degil", "Var", "Nefalix kayip hasta geri kazanimi modulu sunuyor.", "Gelir etkisi dogrudan"],
        ["Sentinel", "Sinirli gorunur", "Var", "Nefalix mention/itibar taramasini ayri ele aliyor.", "Sadece review degil, genis itibar"],
        ["HBYS/EHR entegrasyon", "100+ hazir", "Yerel adapter / Estesoft", "Swell entegrasyon sayisinda onde.", "Nefalix: yerel derinlik"],
        ["Compliance", "HIPAA/SOC2", "KVKK/IYS", "Pazara gore farkli guc.", "TR klinikleri icin KVKK daha ilgili"],
        ["Enterprise rollup", "Cok guclu", "Gelisiyor", "Bolge/marka/klinik/provider reporting Swell'de native.", "Nefalix buyuk grup roadmap anlatmali"],
    ]:
        s2.add_row(row, "text")

    s3 = Sheet("Konumlandirma", [18, 36, 36, 14])
    s3.add_row(["SATIS VE KONUMLANDIRMA"], "title")
    s3.add_row(["Nefalix nasil farklilasmali?"], "plain")
    s3.add_row([""])
    s3.add_row(["Baslik", "Nefalix'te Soylenecek", "Swell'e Gore Fark", "Oncelik"], "header")
    for row in [
        ["Ana mesaj", "Kliniginiz icin WhatsApp-first hasta deneyimi ve itibar paneli.", "Swell SMS-first; Nefalix TR hasta davranisina daha yakin.", "P0"],
        ["Yorum stratejisi", "Memnun hastayi Google'a yonlendir, mutsuz hastayi once iceride coz.", "Nefalix detractor akisini daha net satar.", "P0"],
        ["Operasyon", "Inbox, NPS, eNPS, Recall, Sentinel tek panelde.", "Swell review/PX guclu; Nefalix operasyon genisligiyle konusur.", "P0"],
        ["Uyumluluk", "KVKK, IYS ve HBYS gercegine uygun yerel kurgu.", "HIPAA yerine TR dili.", "P0"],
        ["Gelir etkisi", "Recall ve tekrar randevu firsatlarini da gorursunuz.", "Swell pazarlama + reputasyon; Nefalix gelir geri kazanimi anlatabilir.", "P1"],
        ["Enterprise zayiflik", "Cok subeli buyuk gruplarda raporlama yol haritamiz var.", "Swell bu alanda daha olgun.", "P1"],
        ["Teknik zayiflik", "Yerel entegrasyonlarimiz ozellestirilebilir.", "Swell hazir entegrasyon sayisinda onde.", "P1"],
    ]:
        s3.add_row(row, "text")

    s4 = Sheet("Itirazlar", [22, 38, 38, 18])
    s4.add_row(["ITIRAZLAR VE CEVAPLAR"], "title")
    s4.add_row(["Satis gorusmesinde kullanilabilecek kisa cevaplar"], "plain")
    s4.add_row([""])
    s4.add_row(["Itiraz", "Kisa cevap", "Acilim", "Ne gosterilir?"], "header")
    for row in [
        ["'Swell daha buyuk duruyor'", "Dogru; ABD enterprise urunu. Nefalix ise TR klinik is akisini daha dogru cozuyor.", "Onlarin gucu entegrasyon sayisi; bizim gucumuz WhatsApp + KVKK + yerel operasyon.", "Inbox, NPS ve Recall akisi"],
        ["'Biz SMS degil WhatsApp kullaniyoruz'", "Tam da bu yuzden Nefalix daha uygun.", "Hasta iletisim davranisi burada SMS degil WhatsApp.", "Canli dashboard + WhatsApp akisi"],
        ["'Negatif yorum gelirse ne oluyor?'", "Nefalix mutsuz hastayi direkt Google'a itmez; once iceride cozum akisi acilir.", "Bu, itibar riskini azaltir ve sikayeti operasyonel goreve cevirir.", "NPS / Sentinel ekrani"],
        ["'Bize sadece review tool lazim'", "Nefalix review tool'dan fazlasi: yorum + inbox + recall + ekip nabzi.", "Tek modulle baslayip sonra digerlerini acabilirsiniz.", "Paket ve moduller"],
        ["'Kurulum zor olur mu?'", "Yerel entegrasyonlarda daha hizli ilerliyoruz cunku akisi kuruma gore uyarlayabiliyoruz.", "Hazir 100+ entegrasyon yerine dogru 1-2 entegrasyonu derin yapma stratejisi.", "Pilot plan"],
    ]:
        s4.add_row(row, "text")

    s5 = Sheet("Kaynaklar", [8, 26, 74])
    s5.add_row(["KAYNAKLAR"], "title")
    s5.add_row(["Arastirma notlari"], "plain")
    s5.add_row([""])
    s5.add_row(["No", "Kaynak", "Ozet"], "header")
    for row in [
        ["1", "swellcx.com", "AI healthcare reputation management, patient experience, employee feedback, ticketing, EHR/PMS integrations, HIPAA/SOC2."],
        ["2", "swellcx.com/integrations", "Dentrix, Open Dental, athenahealth, eClinicalWorks dahil 100+ entegrasyon listesi."],
        ["3", "swellcx.com/patient-experience", "NPS, anket, patient journey feedback, provider/location bazli metrikler."],
        ["4", "swellcx.com/ticketing", "Dusuk NPS/negatif yorum -> otomatik ticket, ekip atama, ileti gecmisi."],
        ["5", "3. parti incelemeler", "Tahmini fiyat bandi ve pazar konumlandirmasi icin yardimci referans; resmi fiyat degil."],
    ]:
        s5.add_row(row, "text")
    return [s1, s2, s3, s4, s5]


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
