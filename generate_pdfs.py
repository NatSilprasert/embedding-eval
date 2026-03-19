"""
Generates all 19 PDF documents for the RAG embedding evaluation:
  TechNest Thailand (3 PDFs) + 16 additional industry PDFs.

Usage:
  python generate_pdfs.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_REGULAR_URL = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
FONT_BOLD_URL    = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"

for fname, url in [("Sarabun-Regular.ttf", FONT_REGULAR_URL), ("Sarabun-Bold.ttf", FONT_BOLD_URL)]:
    if not os.path.exists(fname):
        print(f"Downloading {fname}...")
        urllib.request.urlretrieve(url, fname)

pdfmetrics.registerFont(TTFont("Sarabun", "Sarabun-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Sarabun-Bold", "Sarabun-Bold.ttf"))


PRIMARY_COLOR = colors.HexColor("#1A3C5E")
ACCENT_COLOR  = colors.HexColor("#F4A300")
LIGHT_BG      = colors.HexColor("#F0F4F8")
WHITE         = colors.white
DARK_TEXT     = colors.HexColor("#1F2937")

# ─── Styles ───────────────────────────────────────────────────────────────────
def make_styles():
    styles = getSampleStyleSheet()
    base = dict(fontName="Sarabun", leading=16)

    custom = {
        "Title":    ParagraphStyle("Title",    fontName="Sarabun-Bold", fontSize=24, textColor=PRIMARY_COLOR, spaceAfter=10, leading=30),
        "Subtitle": ParagraphStyle("Subtitle", fontName="Sarabun",      fontSize=14, textColor=ACCENT_COLOR,  spaceAfter=8),
        "H1":       ParagraphStyle("H1",       fontName="Sarabun-Bold", fontSize=16, textColor=PRIMARY_COLOR, spaceBefore=12, spaceAfter=6, leading=22),
        "H2":       ParagraphStyle("H2",       fontName="Sarabun-Bold", fontSize=13, textColor=PRIMARY_COLOR, spaceBefore=8,  spaceAfter=4, leading=18),
        "Body":     ParagraphStyle("Body",     fontName="Sarabun",      fontSize=10, textColor=DARK_TEXT,     spaceAfter=4,   leading=16),
        "BodyBold": ParagraphStyle("BodyBold", fontName="Sarabun-Bold", fontSize=10, textColor=DARK_TEXT,     spaceAfter=4,   leading=16),
        "Small":    ParagraphStyle("Small",    fontName="Sarabun",      fontSize=8,  textColor=DARK_TEXT,     spaceAfter=2,   leading=12),
        "Bullet":   ParagraphStyle("Bullet",   fontName="Sarabun",      fontSize=10, textColor=DARK_TEXT,     spaceAfter=3,   leading=15, leftIndent=15, bulletIndent=5),
        "Center":   ParagraphStyle("Center",   fontName="Sarabun",      fontSize=10, textColor=DARK_TEXT,     spaceAfter=4,   alignment=1, leading=16),
    }
    return custom

ST = make_styles()

# ─── Table helpers ────────────────────────────────────────────────────────────
def header_style(bg=PRIMARY_COLOR):
    return TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), bg),
        ("TEXTCOLOR",    (0,0), (-1,0), WHITE),
        ("FONTNAME",     (0,0), (-1,0), "Sarabun-Bold"),
        ("FONTSIZE",     (0,0), (-1,0), 9),
        ("ALIGN",        (0,0), (-1,0), "CENTER"),
        ("BOTTOMPADDING",(0,0), (-1,0), 6),
        ("TOPPADDING",   (0,0), (-1,0), 6),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, LIGHT_BG]),
        ("FONTNAME",     (0,1), (-1,-1), "Sarabun"),
        ("FONTSIZE",     (0,1), (-1,-1), 8),
        ("ALIGN",        (0,1), (-1,-1), "CENTER"),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("GRID",         (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ("TOPPADDING",   (0,1), (-1,-1), 4),
        ("BOTTOMPADDING",(0,1), (-1,-1), 4),
    ])

def wrap(text, style=None):
    return Paragraph(text, style or ST["Body"])

def page_num_canvas(canvas, doc):
    canvas.saveState()
    canvas.setFont("Sarabun", 8)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawString(2*cm, 1*cm, "TechNest Thailand")
    canvas.drawRightString(A4[0]-2*cm, 1*cm, f"Page {doc.page}")
    canvas.restoreState()


def page_footer(company_name):
    """Factory: returns a canvas callback that draws company name + page number."""
    def _footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Sarabun", 8)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawString(2*cm, 1*cm, company_name)
        canvas.drawRightString(A4[0]-2*cm, 1*cm, f"Page {doc.page}")
        canvas.restoreState()
    return _footer


def new_doc(path):
    return SimpleDocTemplate(path, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2.5*cm, bottomMargin=2*cm)


# PDF 1: technest_th.pdf — Thai Only
# ═══════════════════════════════════════════════════════════════════════════════
def build_thai_pdf(path: str):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)
    story = []

    # ── หน้า 1: ปก + สารบัญ ─────────────────────────────────────────────────
    story += [
        Spacer(1, 1.5*cm),
        Paragraph("TechNest Thailand", ST["Title"]),
        Paragraph("บริษัท เทคเนสท์ ไทยแลนด์ จำกัด", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1, 0.5*cm),
        Paragraph("TechNest Thailand ก่อตั้งขึ้นในปี 2562 มุ่งเน้นการจัดจำหน่ายอุปกรณ์ Smart Home คุณภาพสูงสำหรับตลาดประเทศไทย "
                  "ด้วยสินค้ากว่า 200 รายการ ครอบคลุมทั้งระบบแสงสว่าง ความปลอดภัย และระบบอัตโนมัติภายในบ้าน "
                  "บริษัทมุ่งมั่นนำเสนอเทคโนโลยีที่ทันสมัย ราคาเหมาะสม พร้อมบริการหลังการขายที่เป็นเลิศ", ST["Body"]),
        Spacer(1, 0.5*cm),
        Paragraph("สารบัญ", ST["H1"]),
    ]
    toc_data = [
        ["หัวข้อ", "หน้า"],
        ["แคตาล็อกสินค้า Smart Home", "2-3"],
        ["นโยบายคืนสินค้าและเปลี่ยนสินค้า", "4-5"],
        ["โปรโมชันและส่วนลด", "6-7"],
        ["นโยบายการจัดส่ง", "8-9"],
        ["FAQ ลูกค้า", "10-11"],
        ["ช่องทางติดต่อ + ข้อกำหนด", "12"],
    ]
    toc_table = Table(toc_data, colWidths=[13*cm, 3*cm])
    toc_table.setStyle(header_style())
    story += [toc_table, PageBreak()]

    # ── หน้า 2-3: แคตาล็อกสินค้า ────────────────────────────────────────────
    story += [Paragraph("แคตาล็อกสินค้า Smart Home", ST["H1"])]
    products = [
        ["รหัสสินค้า", "ชื่อสินค้า", "ราคาปกติ", "ราคาสมาชิก", "สต็อก", "รับประกัน"],
        ["TN-SH-2024-001", "TechNest Smart Bulb Pro X",    "890 THB",   "799 THB",   "450 pcs", "2 ปี"],
        ["TN-SH-2024-002", "TechNest Door Lock Ultra",     "5,490 THB", "4,899 THB", "120 pcs", "3 ปี"],
        ["TN-SH-2024-003", "TechNest Air Purifier S7",     "12,990 THB","11,500 THB","80 pcs",  "2 ปี"],
        ["TN-SH-2024-004", "TechNest CCTV 4K Dome",        "3,299 THB", "2,950 THB", "200 pcs", "1 ปี"],
        ["TN-SH-2024-005", "TechNest Smart Plug V3",       "490 THB",   "430 THB",   "1,200 pcs","1 ปี"],
        ["TN-SH-2024-006", "TechNest Hub Central Pro",     "7,800 THB", "6,990 THB", "60 pcs",  "3 ปี"],
        ["TN-SH-2024-007", "TechNest Sensor Motion 360",   "1,290 THB", "1,150 THB", "320 pcs", "1 ปี"],
        ["TN-SH-2024-008", "TechNest Robot Vacuum Z9",     "18,900 THB","16,800 THB","45 pcs",  "2 ปี"],
        ["TN-SH-2024-009", "TechNest Smart Curtain Kit",   "4,200 THB", "3,780 THB", "95 pcs",  "2 ปี"],
        ["TN-SH-2024-010", "TechNest LED Strip 5M",        "1,100 THB", "980 THB",   "800 pcs", "1 ปี"],
        ["TN-SH-2024-011", "TechNest Smart Doorbell HD",   "2,800 THB", "2,520 THB", "150 pcs", "2 ปี"],
        ["TN-SH-2024-012", "TechNest Water Leak Sensor",   "790 THB",   "710 THB",   "500 pcs", "1 ปี"],
    ]
    prod_table = Table(products, colWidths=[3.2*cm, 5.5*cm, 2.2*cm, 2.5*cm, 1.8*cm, 1.8*cm])
    prod_table.setStyle(header_style())
    story += [prod_table, Spacer(1, 0.3*cm)]

    story += [
        Paragraph("หมายเหตุ: ราคาสมาชิกสำหรับผู้ถือบัตร TechNest Plus เท่านั้น สต็อกอัปเดต ณ วันที่ 15 ตุลาคม 2567", ST["Small"]),
        Spacer(1, 0.3*cm),
        Paragraph("รายละเอียดสินค้าเด่น", ST["H2"]),
        Paragraph("TechNest Hub Central Pro (TN-SH-2024-006) — ศูนย์กลางควบคุมอุปกรณ์ Smart Home "
                  "รองรับโปรโตคอล Wi-Fi 2.4/5GHz, Zigbee 3.0, Z-Wave Plus และ Bluetooth 5.0 ในตัวเดียว "
                  "พร้อม Matter 1.2 support (FW-4.0.0) รองรับ Zigbee สูงสุด 200 อุปกรณ์ และ Z-Wave 100 อุปกรณ์ "
                  "ขนาด 120×120×28mm, พลังงาน DC 5V 2A, เวลาตอบสนอง API < 50ms บน LAN", ST["Body"]),
        Paragraph("TechNest Robot Vacuum Z9 (TN-SH-2024-008) — หุ่นยนต์ดูดฝุ่นแบรนด์พรีเมียม "
                  "แรงดูด 3,000Pa, แบตเตอรี่ 5,200mAh ทำงานต่อเนื่อง 120 นาที, ครอบคลุมพื้นที่ 250 ตร.ม. "
                  "ระบบ AI ตรวจจับสิ่งกีดขวาง v2.3 (FW-3.9.5) เสียงรบกวน 62dB(A) กรอง HEPA มาตรฐาน "
                  "เชื่อมต่อ Wi-Fi 2.4/5GHz รองรับ iOS 14+ และ Android 11+", ST["Body"]),
        Paragraph("TechNest Air Purifier S7 (TN-SH-2024-003) — เครื่องฟอกอากาศระดับพรีเมียม "
                  "CADR 350m³/h, กรอง HEPA 13 กำจัดฝุ่น PM2.5 ได้ 99.97%, เซ็นเซอร์ PM2.5 ความแม่นยำ ±10μg/m³ "
                  "ครอบคลุมพื้นที่ 45 ตร.ม., เสียง 22-52dB เปลี่ยนไส้กรองทุก 6 เดือน (Part: TN-APF-S7-H13) "
                  "เชื่อมต่อ Wi-Fi 2.4GHz กำลังไฟ 45W", ST["Body"]),
        PageBreak(),
    ]

    # ── หน้า 4-5: นโยบายคืนสินค้า ───────────────────────────────────────────
    story += [Paragraph("นโยบายคืนสินค้าและเปลี่ยนสินค้า", ST["H1"])]
    story += [
        Paragraph("ระยะเวลาและเงื่อนไขการคืนสินค้า", ST["H2"]),
        Paragraph("TechNest Thailand รับคืนสินค้าภายใน <b>15 วัน</b> นับจากวันที่ลูกค้าได้รับสินค้า "
                  "โดยสินค้าต้องอยู่ในสภาพสมบูรณ์ ไม่มีรอยแตก รอยขีดข่วน หรือความเสียหายจากการใช้งาน", ST["Body"]),
        Paragraph("เงื่อนไขสินค้าที่สามารถคืนได้:", ST["BodyBold"]),
        Paragraph("• สินค้าต้องอยู่ในสภาพสมบูรณ์ 100% ไม่มีรอยเปิดซีล", ST["Bullet"]),
        Paragraph("• ต้องมีกล่องบรรจุภัณฑ์และอุปกรณ์ครบถ้วน", ST["Bullet"]),
        Paragraph("• มีใบเสร็จรับเงินหรือหลักฐานการซื้อ", ST["Bullet"]),
        Paragraph("• ไม่เกิน 15 วันนับจากวันรับสินค้า", ST["Bullet"]),
        Spacer(1, 0.3*cm),
        Paragraph("สินค้าที่ไม่สามารถคืนได้:", ST["BodyBold"]),
        Paragraph("• TechNest Robot Vacuum Z9 (TN-SH-2024-008) และ TechNest Air Purifier S7 (TN-SH-2024-003) ที่เปิดใช้งานแล้ว", ST["Bullet"]),
        Paragraph("• สินค้าที่ซื้อในราคา Flash Sale หรือใช้โค้ด FLASH30OCT", ST["Bullet"]),
        Paragraph("• สินค้า Bundle ที่เปิดแพ็คเกจแล้ว", ST["Bullet"]),
        Spacer(1, 0.3*cm),
        Paragraph("ขั้นตอนการคืนสินค้า (5 ขั้นตอน)", ST["H2"]),
    ]
    steps = [
        ["ขั้นตอน", "รายละเอียด"],
        ["1. แจ้งคืนสินค้า", "ติดต่อผ่าน LINE @technest.th พร้อมแนบรูปถ่ายสินค้าและหลักฐานการซื้อ"],
        ["2. รอการยืนยัน", "ทีมงานจะตรวจสอบและตอบกลับภายใน 2 ชั่วโมงในวันทำการ (จ.-ศ. 09:00-18:00 น.)"],
        ["3. รับรหัส RMA", "เมื่ออนุมัติแล้ว ลูกค้าจะได้รับรหัส RMA (Return Merchandise Authorization) เช่น RMA-2024-TH-08821"],
        ["4. ส่งพัสดุคืน", "จ่าหน้าซองระบุรหัส RMA และส่งผ่านพาร์ทเนอร์โลจิสติกส์ที่กำหนด"],
        ["5. รอ Refund", "TechNest จะโอนเงินคืนภายใน 7 วันทำการหลังได้รับสินค้าคืนและตรวจสอบแล้ว"],
    ]
    steps_table = Table(steps, colWidths=[4*cm, 13*cm])
    steps_table.setStyle(header_style())
    story += [steps_table, PageBreak()]

    story += [
        Paragraph("ค่าธรรมเนียมการคืนสินค้าและเงื่อนไขเพิ่มเติม", ST["H1"]),
        Paragraph("ค่าธรรมเนียมการคืนสินค้า", ST["H2"]),
        Paragraph("• สินค้าราคาต่ำกว่า 500 THB: ผู้ซื้อรับผิดชอบค่าขนส่งคืนสินค้าทั้งหมด", ST["Bullet"]),
        Paragraph("• สินค้าราคา 500 THB ขึ้นไป: TechNest Thailand ออกค่าขนส่งคืนให้ทั้งหมด", ST["Bullet"]),
        Paragraph("• กรณีสินค้าชำรุดจากโรงงาน: TechNest รับผิดชอบค่าใช้จ่ายทั้งหมดและจัดส่งสินค้าทดแทนภายใน 3 วันทำการ", ST["Bullet"]),
        PageBreak(),
    ]

    # ── หน้า 6-7: โปรโมชัน ──────────────────────────────────────────────────
    story += [Paragraph("โปรโมชันและส่วนลด", ST["H1"])]
    story += [
        Paragraph("โปรแกรมสมาชิก TechNest Plus", ST["H2"]),
        Paragraph("ค่าสมาชิก: <b>299 THB/ปี</b> (ต่ออายุอัตโนมัติ ยกเว้นแจ้งยกเลิก 30 วันล่วงหน้า)", ST["Body"]),
        Paragraph("สิทธิประโยชน์สมาชิก TechNest Plus:", ST["BodyBold"]),
        Paragraph("1. ส่วนลดพิเศษ 15% ทุกออเดอร์ (ใช้กับโค้ด MEMBER15)", ST["Bullet"]),
        Paragraph("2. ฟรีค่าจัดส่งทุกออเดอร์ไม่มีขั้นต่ำ (ยกเว้นพื้นที่เกาะ)", ST["Bullet"]),
        Paragraph("3. การรับประกันสินค้าเพิ่มขึ้น 6 เดือนทุกรายการ", ST["Bullet"]),
        Paragraph("4. สิทธิ์เข้าถึง Early Access สินค้าใหม่ 48 ชั่วโมงก่อนเปิดขายทั่วไป", ST["Bullet"]),
        Paragraph("5. ช่องทาง Priority Support ตอบภายใน 30 นาที (09:00-21:00 น.)", ST["Bullet"]),
        Paragraph("6. แต้ม TechNest Point สะสม 2 เท่า (1 THB = 2 แต้ม)", ST["Bullet"]),
        Paragraph("7. เชิญเข้าร่วม TechNest Community Event ประจำปีฟรี", ST["Bullet"]),
        Paragraph("8. ส่วนลดซ่อมบำรุง 20% ที่ศูนย์บริการ TechNest Service Center ทุกสาขา", ST["Bullet"]),
        Spacer(1, 0.4*cm),
        Paragraph("รหัสโปรโมชันปัจจุบัน", ST["H2"]),
    ]
    promos = [
        ["รหัสโปรโมชัน", "ส่วนลด", "เงื่อนไข", "หมดอายุ", "Stack ได้"],
        ["FLASH30OCT", "30%", "เฉพาะสินค้า Smart Lighting (TN-SH-2024-001, 010)", "31 ต.ค. 2567", "ไม่ได้"],
        ["MEMBER15",   "15%", "สำหรับสมาชิก TechNest Plus ทุกออเดอร์", "ไม่มีวันหมด", "ได้บางรหัส"],
        ["BUNDLE2FREE","ฟรี Smart Plug V3", "ซื้อครบ 3 ชิ้นขึ้นไปในออเดอร์เดียว", "30 พ.ย. 2567", "ได้"],
        ["NEWUSER200", "200 THB", "ลูกค้าใหม่ ออเดอร์แรก ขั้นต่ำ 1,500 THB", "ไม่มีวันหมด", "ไม่ได้"],
    ]
    promo_table = Table(promos, colWidths=[3.5*cm, 3*cm, 5.5*cm, 3*cm, 2*cm])
    promo_table.setStyle(header_style())
    story += [promo_table, Spacer(1, 0.3*cm)]
    story += [
        Paragraph("หมายเหตุการ Stack โค้ด: MEMBER15 สามารถใช้ร่วมกับ BUNDLE2FREE ได้ "
                  "แต่ไม่สามารถใช้ร่วมกับ FLASH30OCT หรือ NEWUSER200 ได้ในออเดอร์เดียวกัน", ST["Small"]),
        PageBreak(),
    ]

    # ── หน้า 8-9: นโยบายการจัดส่ง ───────────────────────────────────────────
    story += [Paragraph("นโยบายการจัดส่งสินค้า", ST["H1"])]
    story += [
        Paragraph("โซนการจัดส่งและค่าบริการ", ST["H2"]),
    ]
    shipping = [
        ["โซน", "พื้นที่", "น้ำหนัก ≤1kg", "1-5kg", "5-10kg", "เวลาจัดส่ง"],
        ["Zone A", "กทม. และปริมณฑล", "30 THB", "60 THB", "100 THB", "1-2 วัน"],
        ["Zone B", "ต่างจังหวัด (ทั่วไทย)", "50 THB", "90 THB", "150 THB", "2-4 วัน"],
        ["Zone C", "เกาะ/พื้นที่ห่างไกล", "80 THB", "150 THB", "250 THB", "5-7 วัน"],
    ]
    ship_table = Table(shipping, colWidths=[2*cm, 5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    ship_table.setStyle(header_style())
    story += [ship_table, PageBreak()]

    story += [
        Paragraph("นโยบายการจัดส่งสินค้า (ต่อ)", ST["H1"]),
        Paragraph("เงื่อนไขพิเศษ", ST["H2"]),
        Paragraph("• ฟรีค่าจัดส่ง: ออเดอร์มูลค่า 1,500 THB ขึ้นไป (ยกเว้น Zone C เกาะ/พื้นที่ห่างไกล)", ST["Bullet"]),
        Paragraph("• บริการ Express 4 ชั่วโมง (เฉพาะกทม.): เพิ่มค่าบริการ 150 THB ต้องสั่งก่อน 14:00 น.", ST["Bullet"]),
        Paragraph("• สินค้าขนาดใหญ่ (Robot Vacuum, Air Purifier): อาจมีค่าบริการพิเศษเพิ่มเติม", ST["Bullet"]),
        Spacer(1, 0.3*cm),
        Paragraph("พาร์ทเนอร์โลจิสติกส์", ST["H2"]),
    ]
    carriers = [
        ["รหัส", "ผู้ให้บริการ", "จุดเด่น", "ตรวจสอบพัสดุ"],
        ["TN-JT", "J&T Express",    "ครอบคลุมทั่วประเทศ ราคาประหยัด", "jtexpress.co.th"],
        ["TN-FX", "Flash Express",  "จัดส่งเร็ว กทม.ส่งได้วันเดียว",  "flashexpress.co.th"],
        ["TN-KR", "Kerry Express",  "บริการ Premium บรรจุภัณฑ์แน่นหนา","kerryexpress.com"],
    ]
    carriers_table = Table(carriers, colWidths=[2*cm, 4*cm, 7*cm, 4*cm])
    carriers_table.setStyle(header_style())
    story += [carriers_table, PageBreak()]

    # ── หน้า 10-11: FAQ ──────────────────────────────────────────────────────
    story += [Paragraph("คำถามที่พบบ่อย (FAQ)", ST["H1"])]
    faqs = [
        ("สามารถเปลี่ยนที่อยู่จัดส่งหลังสั่งซื้อได้ไหม?",
         "ได้ภายใน 2 ชั่วโมงหลังยืนยันออเดอร์ ติดต่อ LINE @technest.th พร้อมแจ้งหมายเลขออเดอร์"),
        ("รับชำระเงินช่องทางใดบ้าง?",
         "บัตรเครดิต/เดบิต (Visa, Mastercard, JCB), PromptPay, โอนธนาคาร, TrueMoney Wallet, ผ่อน 0% 10 เดือน (บัตรเครดิตที่ร่วมรายการ)"),
        ("TechNest Smart Bulb Pro X ใช้กับหลอดไฟ E27 ได้ไหม?",
         "ได้ TN-SH-2024-001 ใช้ขั้ว E27 กำลังไฟ 9W ทดแทนหลอดไส้ 60W"),
        ("Hub Central Pro รองรับโปรโตคอลอะไรบ้าง?",
         "TN-SH-2024-006 รองรับ Wi-Fi 2.4/5GHz, Zigbee 3.0, Z-Wave Plus, Bluetooth 5.0 และ Matter 1.2 (อัปเดต FW-4.0.0)"),
        ("Robot Vacuum Z9 ทำความสะอาดพื้นที่ได้กี่ตารางเมตร?",
         "TN-SH-2024-008 ครอบคลุมพื้นที่สูงสุด 250 ตารางเมตรต่อการชาร์จหนึ่งครั้ง แบตเตอรี่ 5,200 mAh"),
        ("ถ้าสินค้าชำรุดภายในระยะรับประกัน ต้องทำอย่างไร?",
         "ติดต่อ LINE @technest.th แจ้งรหัสสินค้า รหัสรับประกัน และอธิบายปัญหา ทีมงานจะนัดหมายตรวจสอบภายใน 24 ชั่วโมง"),
        ("แอป TechNest Home ใช้ได้กับ iOS รุ่นใดขึ้นไป?",
         "iOS 14 ขึ้นไป (iPhone 6s หรือใหม่กว่า) และ Android 10 ขึ้นไป ดาวน์โหลดได้ที่ App Store และ Google Play"),
        ("โค้ด NEWUSER200 ใช้ได้กี่ครั้ง?",
         "ใช้ได้ครั้งเดียวต่อ 1 บัญชี สำหรับออเดอร์แรกที่มีมูลค่า 1,500 THB ขึ้นไปเท่านั้น"),
        ("สมัครสมาชิก TechNest Plus ได้ที่ไหน?",
         "สมัครได้ที่แอป TechNest Home > เมนูบัญชี > TechNest Plus หรือที่เว็บไซต์ technest.th/plus ค่าสมาชิก 299 THB/ปี"),
        ("Door Lock Ultra (TN-SH-2024-002) รองรับกุญแจสำรองแบบกลไกได้ไหม?",
         "ได้ รองรับกุญแจกลไกสำรอง (Physical Key Override) มาตรฐาน UL 437 ANSI Grade 2"),
        ("สั่งสินค้าแล้วจะรู้ได้อย่างไรว่าจัดส่งแล้ว?",
         "ระบบจะส่ง SMS และ LINE notification พร้อมหมายเลขพัสดุให้โดยอัตโนมัติเมื่อสินค้าออกจากคลัง"),
        ("Air Purifier S7 กรองฝุ่น PM2.5 ได้ไหม?",
         "ได้ TN-SH-2024-003 ใช้ระบบกรอง HEPA 13 กรองฝุ่น PM2.5 ได้ 99.97% ครอบคลุมพื้นที่ 45 ตารางเมตร"),
        ("สินค้า Flash Sale คืนไม่ได้จริงหรือ?",
         "จริง สินค้าที่ซื้อด้วยโค้ด FLASH30OCT หรือในช่วง Flash Sale ไม่รับคืนหรือเปลี่ยนทุกกรณี ยกเว้นสินค้าชำรุดจากโรงงาน"),
        ("ใช้ TechNest Smart Plug V3 กับเครื่องใช้ไฟฟ้ากี่วัตต์ได้?",
         "TN-SH-2024-005 รองรับกระแสไฟสูงสุด 16A (3,680W) ไม่แนะนำให้ใช้กับเครื่องทำความร้อนขนาดใหญ่"),
        ("แต้ม TechNest Point แลกอะไรได้บ้าง?",
         "แลกเป็นส่วนลดได้ 1,000 แต้ม = 10 THB, แลกของขวัญได้ในแอป > TechNest Rewards หรือใช้ชำระค่าซ่อมบำรุง"),
        ("Water Leak Sensor (TN-SH-2024-012) เชื่อมกับแอปอย่างไร?",
         "เปิดแอป TechNest Home > + เพิ่มอุปกรณ์ > เลือก Sensor > Water Leak Sensor กด pair button ที่อุปกรณ์ค้างไว้ 5 วินาที"),
        ("Refund จะโอนเงินคืนผ่านช่องทางไหน?",
         "โอนคืนผ่านช่องทางที่ชำระเงินเดิม บัตรเครดิตคืนภายใน 7-15 วันทำการ โอนธนาคาร/PromptPay คืนภายใน 7 วันทำการ"),
        ("Smart Curtain Kit ติดตั้งกับรางม่านแบบไหน?",
         "TN-SH-2024-009 รองรับรางม่านแบบ U-rail และ I-rail กว้างสูงสุด 6 เมตร น้ำหนักม่านสูงสุด 8 กิโลกรัม"),
        ("มีศูนย์บริการในต่างจังหวัดไหม?",
         "มีศูนย์บริการ TechNest Service Center ที่ เชียงใหม่ (นิมมานเหมินทร์ซอย 4), ขอนแก่น (Central Plaza), ภูเก็ต (Central Festival)"),
        ("CCTV 4K Dome (TN-SH-2024-004) บันทึกภาพไว้กี่วัน?",
         "บันทึกลง MicroSD สูงสุด 256GB (ประมาณ 30 วัน 1080p) หรือเชื่อมกับ TechNest Cloud Storage 299 THB/เดือน เก็บ 90 วัน"),
    ]
    for i, (q, a) in enumerate(faqs, 1):
        story += [
            Paragraph(f"Q{i}: {q}", ST["BodyBold"]),
            Paragraph(f"A: {a}", ST["Body"]),
            Spacer(1, 0.1*cm),
        ]
        if i == 10:
            story.append(PageBreak())
    story.append(PageBreak())

    # ── หน้า 12: ช่องทางติดต่อ ───────────────────────────────────────────────
    story += [
        Paragraph("ช่องทางติดต่อและข้อกำหนดการใช้งาน", ST["H1"]),
        Paragraph("ช่องทางติดต่อ TechNest Thailand", ST["H2"]),
    ]
    contacts = [
        ["ช่องทาง", "รายละเอียด", "เวลาทำการ"],
        ["LINE Official",  "@technest.th",                              "ทุกวัน 09:00-21:00 น."],
        ["โทรศัพท์",       "02-xxx-8899",                               "จ.-ศ. 09:00-18:00 น."],
        ["อีเมล",          "support@technest.th",                       "ตอบภายใน 4 ชั่วโมง (วันทำการ)"],
        ["เว็บไซต์",       "www.technest.th",                           "24/7"],
        ["Facebook",       "fb.com/TechNestThailand",                   "ทุกวัน 09:00-21:00 น."],
        ["ศูนย์บริการ กทม.","สยามพารากอน ชั้น 4 / เซ็นทรัลเวิลด์ ชั้น 2","จ.-อา. 10:00-22:00 น."],
    ]
    cont_table = Table(contacts, colWidths=[4*cm, 8*cm, 5*cm])
    cont_table.setStyle(header_style())
    story += [cont_table, Spacer(1, 0.5*cm)]
    story += [
        Paragraph("ข้อกำหนดและเงื่อนไขการใช้งาน", ST["H2"]),
        Paragraph("เนื้อหาในเอกสารฉบับนี้เป็นข้อมูลที่ถูกต้อง ณ วันที่ 15 ตุลาคม 2567 TechNest Thailand "
                  "ขอสงวนสิทธิ์ในการเปลี่ยนแปลงราคา นโยบาย และโปรโมชันโดยไม่ต้องแจ้งล่วงหน้า "
                  "ลูกค้าสามารถตรวจสอบข้อมูลล่าสุดได้ที่ www.technest.th หรือแอป TechNest Home เวอร์ชัน 4.2.1 ขึ้นไป", ST["Body"]),
        Paragraph("© 2567 TechNest Thailand Co., Ltd. All rights reserved. | เลขที่ทะเบียนบริษัท: 0105562089954", ST["Small"]),
    ]

    doc.build(story, onFirstPage=page_footer("TechNest Thailand"), onLaterPages=page_footer("TechNest Thailand"))
    print(f"  Created: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# PDF 2: technest_en.pdf — English Only
# ═══════════════════════════════════════════════════════════════════════════════
def build_english_pdf(path: str):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)
    story = []

    # Page 1: Cover + TOC
    story += [
        Spacer(1, 1.5*cm),
        Paragraph("TechNest Thailand", ST["Title"]),
        Paragraph("Product & Service Documentation — English Edition", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1, 0.5*cm),
        Paragraph("TechNest Thailand was established in 2019 as a premier smart home device distributor "
                  "serving the Thai market. With over 200 product lines spanning smart lighting, security, "
                  "and home automation, TechNest delivers cutting-edge technology at accessible price points "
                  "backed by industry-leading after-sales support.", ST["Body"]),
        Spacer(1, 0.5*cm),
        Paragraph("Table of Contents", ST["H1"]),
    ]
    toc = [
        ["Section", "Page"],
        ["Product Technical Specifications", "2-3"],
        ["Warranty Terms and Conditions", "4-5"],
        ["API and Integration Documentation", "6-7"],
        ["Shipping and Fulfillment Policy", "8-9"],
        ["Customer Support SLA and Escalation Matrix", "10-11"],
        ["Legal and Compliance", "12"],
    ]
    toc_t = Table(toc, colWidths=[13*cm, 3*cm])
    toc_t.setStyle(header_style())
    story += [toc_t, PageBreak()]

    # Page 2-3: Technical Specifications
    story += [Paragraph("Product Technical Specifications", ST["H1"])]
    specs = [
        ["SKU", "Product", "Connectivity", "Power", "Dimensions", "App", "Certs"],
        ["TN-SPEC-EN-2024-001", "Smart Bulb Pro X",
         "Wi-Fi 2.4GHz\nZigbee 3.0", "E27, 9W", "60×115mm", "iOS 14+\nAndroid 10+", "CE, FCC, RCM"],
        ["TN-SPEC-EN-2024-002", "Door Lock Ultra",
         "BT 5.2\nZ-Wave Plus", "4×AA / DC 6V", "72×33mm cylinder", "iOS 13+\nAndroid 9+", "UL 437\nANSI Grade 2"],
        ["TN-SPEC-EN-2024-003", "Air Purifier S7",
         "Wi-Fi 2.4GHz", "AC 220V, 45W", "330×330×580mm", "iOS 14+\nAndroid 10+", "CE, RoHS\nTIS 1195"],
        ["TN-SPEC-EN-2024-004", "CCTV 4K Dome",
         "Wi-Fi 2.4/5GHz\nEthernet PoE", "DC 12V / PoE", "Ø115×90mm", "iOS 13+\nAndroid 9+", "CE, FCC\nIP67"],
        ["TN-SPEC-EN-2024-005", "Smart Plug V3",
         "Wi-Fi 2.4GHz", "AC 220V, 16A max", "63×63×35mm", "iOS 14+\nAndroid 10+", "CE, TIS 2162"],
        ["TN-SPEC-EN-2024-006", "Hub Central Pro",
         "Wi-Fi/Zigbee\nZ-Wave/BLE", "DC 5V 2A", "120×120×28mm", "iOS 14+\nAndroid 10+", "CE, FCC"],
        ["TN-SPEC-EN-2024-008", "Robot Vacuum Z9",
         "Wi-Fi 2.4/5GHz", "5,200mAh Li-ion\n120min runtime", "350×96mm", "iOS 14+\nAndroid 11+", "CE, FCC\nRoHS"],
        ["TN-SPEC-EN-2024-009", "Smart Curtain Kit",
         "Zigbee 3.0\nBT 5.0", "DC 24V 2A", "Motor: 45×45×160mm", "iOS 14+\nAndroid 10+", "CE, RoHS"],
    ]
    specs_t = Table(specs, colWidths=[3.2*cm, 3.2*cm, 3*cm, 2.5*cm, 2.8*cm, 2.3*cm, 2*cm])
    specs_t.setStyle(header_style())
    story += [specs_t, Spacer(1, 0.3*cm)]
    story += [
        Paragraph("Additional Specifications", ST["H2"]),
        Paragraph("• Smart Bulb Pro X: Color temperature 2700K-6500K, luminous flux 800lm, dimmable 1-100%, "
                  "noise level <25dB, max coverage angle 270°, rated life 25,000 hours", ST["Bullet"]),
        Paragraph("• Robot Vacuum Z9: Suction power 3000Pa, noise level 62dB(A), obstacle detection using "
                  "AI model v2.3 (FW-3.9.5), max obstacle height 20mm, HEPA filter, self-emptying base optional", ST["Bullet"]),
        Paragraph("• Hub Central Pro: Supports up to 200 Zigbee devices, 100 Z-Wave devices, "
                  "Matter 1.2 certified (FW-4.0.0), local processing for automations, "
                  "API response time <50ms on LAN", ST["Bullet"]),
        Paragraph("• Air Purifier S7: CADR 350m³/h, HEPA 13 filter, PM2.5 sensor (±10μg/m³ accuracy), "
                  "noise 22-52dB, coverage 45m², filter replacement every 6 months (part TN-APF-S7-H13)", ST["Bullet"]),
        Spacer(1, 0.3*cm),
        Paragraph("Connectivity Summary by Protocol", ST["H2"]),
    ]
    proto = [
        ["Protocol", "Supported Products (SKU)", "Max Devices per Hub", "Frequency"],
        ["Wi-Fi 2.4GHz",  "All Wi-Fi products",                     "N/A (router dependent)", "2.412-2.472 GHz"],
        ["Wi-Fi 5GHz",    "Hub Pro, Robot Vacuum Z9",                "N/A",                    "5.180-5.825 GHz"],
        ["Zigbee 3.0",    "Hub Pro, Bulb, Curtain, Motion Sensor",   "200 per Hub",            "2.4GHz (ch 11-26)"],
        ["Z-Wave Plus",   "Hub Pro, Door Lock Ultra",                "100 per Hub",            "868/908/916 MHz"],
        ["Bluetooth 5.2", "Door Lock Ultra",                         "1 (direct pair)",        "2.4GHz"],
        ["Bluetooth 5.0", "Hub Pro, Curtain Kit",                    "10 (mesh)",              "2.4GHz"],
        ["Matter 1.2",    "Hub Pro (FW-4.0.0+)",                     "50 per fabric",          "Wi-Fi/Thread/BLE"],
    ]
    proto_t = Table(proto, colWidths=[3*cm, 5.5*cm, 4*cm, 4.5*cm])
    proto_t.setStyle(header_style())
    story += [proto_t, PageBreak()]

    # Page 4-5: Warranty
    story += [Paragraph("Warranty Terms and Conditions", ST["H1"])]
    story += [
        Paragraph("Standard Warranty Coverage by Product Category", ST["H2"]),
    ]
    warranty = [
        ["Category", "Products", "Warranty Period"],
        ["Smart Locks", "TN-SPEC-EN-2024-002 Door Lock Ultra", "3 Years"],
        ["Smart Hub", "TN-SPEC-EN-2024-006 Hub Central Pro", "3 Years"],
        ["Air Purifiers", "TN-SPEC-EN-2024-003 Air Purifier S7", "2 Years (motor: 5 years)"],
        ["Robot Vacuums", "TN-SPEC-EN-2024-008 Robot Vacuum Z9", "2 Years (battery: 1 year)"],
        ["Smart Bulbs/LED", "TN-SPEC-EN-2024-001, 010", "2 Years"],
        ["CCTV / Security", "TN-SPEC-EN-2024-004", "1 Year"],
        ["Sensors / Plugs", "TN-SPEC-EN-2024-005, 007, 012", "1 Year"],
        ["Curtain Kit", "TN-SPEC-EN-2024-009 Smart Curtain Kit", "2 Years"],
    ]
    w_t = Table(warranty, colWidths=[4*cm, 8*cm, 5*cm])
    w_t.setStyle(header_style())
    story += [w_t, PageBreak()]
    story += [
        Paragraph("Warranty Terms and Conditions (continued)", ST["H1"]),
        Paragraph("What Is Covered", ST["H2"]),
        Paragraph("• Manufacturing defects in materials and workmanship", ST["Bullet"]),
        Paragraph("• Electronic component failure under normal use conditions", ST["Bullet"]),
        Paragraph("• Motor failure in Robot Vacuum Z9 and Smart Curtain Kit (within warranty period)", ST["Bullet"]),
        Paragraph("• Battery capacity below 70% of rated capacity within 12 months of purchase", ST["Bullet"]),
        Spacer(1, 0.2*cm),
        Paragraph("What Is NOT Covered", ST["H2"]),
        Paragraph("• Physical damage from drops, impacts, or mishandling", ST["Bullet"]),
        Paragraph("• Water damage to devices not rated IPX4 or higher", ST["Bullet"]),
        Paragraph("• Unauthorized modifications or use of third-party firmware", ST["Bullet"]),
        Paragraph("• Use outside Thailand without written authorization from TechNest", ST["Bullet"]),
        Paragraph("• Cosmetic damage: scratches, dents, broken plastic from accidents", ST["Bullet"]),
        Spacer(1, 0.3*cm),
        Paragraph("Warranty Claim Process", ST["H2"]),
    ]
    claim_steps = [
        ["Step", "Action", "Timeline"],
        ["1", "Submit warranty claim online at technest.th/warranty or LINE @technest.th "
              "using Form WC-2024-TH (available on website)", "Day 0"],
        ["2", "TechNest support team reviews submission and confirms eligibility", "Within 4 business hours"],
        ["3", "Receive claim approval and RMA code (format: RMA-WC-2024-XXXXX)", "Day 1-2"],
        ["4", "Ship defective unit to designated service center with RMA code on package", "Day 2-5"],
        ["5", "TechNest inspects device and confirms warranty coverage", "Day 6-8"],
        ["6", "Repaired or replaced unit shipped back to customer", "Day 9-14"],
    ]
    claim_t = Table(claim_steps, colWidths=[1*cm, 12*cm, 4*cm])
    claim_t.setStyle(header_style())
    story += [claim_t, Spacer(1, 0.3*cm)]

    story += [
        Paragraph("Authorized Service Centers", ST["H2"]),
    ]
    centers = [
        ["Location", "Address", "Phone", "Hours"],
        ["Bangkok - Siam", "4th Floor Siam Paragon, Rama I Rd, Pathumwan", "02-610-9901", "Daily 10:00-22:00"],
        ["Bangkok - CW",   "2nd Floor CentralWorld, Ratchadamri Rd, Pathumwan", "02-610-9902", "Daily 10:00-22:00"],
        ["Bangkok - Lat Phrao","Seacon Square, Lat Phrao Rd, Wang Thong Lang", "02-610-9903", "Daily 10:00-21:00"],
        ["Chiang Mai",     "Nimman Rd Soi 4, Suthep, Mueang Chiang Mai 50200", "053-210-441", "Tue-Sun 10:00-20:00"],
        ["Khon Kaen",      "Central Plaza Khon Kaen, Srichan Rd", "043-380-221", "Daily 10:00-21:00"],
        ["Phuket",         "2nd Floor Central Festival Phuket, Wichitsongkram Rd", "076-510-331", "Daily 10:00-22:00"],
        ["Pattaya",        "Central Festival Pattaya Beach, Pattaya 2nd Rd", "038-421-551", "Daily 10:00-21:00"],
        ["Hat Yai",        "DiamondPlaza Hat Yai, Niphat Uthit 3 Rd", "074-290-661", "Tue-Sun 10:00-20:00"],
    ]
    c_t = Table(centers, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    c_t.setStyle(header_style())
    story += [c_t, Spacer(1, 0.3*cm)]

    story += [
        Paragraph("Extended Warranty — TechNest Care+", ST["H2"]),
        Paragraph("• TechNest Care+ 1-Year Extension: 299 THB — adds 12 months to standard warranty, "
                  "includes 1 free on-site visit for Bangkok customers", ST["Bullet"]),
        Paragraph("• TechNest Care+ 2-Year Extension: 499 THB — adds 24 months, "
                  "includes 2 free on-site visits and priority repair queue (3-day turnaround guaranteed)", ST["Bullet"]),
        Paragraph("• Care+ must be purchased within 30 days of product purchase. "
                  "Plan code for 1-year: CARE-1YR-2024; 2-year: CARE-2YR-2024", ST["Bullet"]),
        PageBreak(),
    ]

    # Page 6-7: API Documentation
    story += [Paragraph("API and Integration Documentation", ST["H1"])]
    story += [
        Paragraph("TechNest Open API v2.3", ST["H2"]),
        Paragraph("Base URL: https://api.technest.th/v2/", ST["BodyBold"]),
        Paragraph("The TechNest Open API allows third-party developers and enterprise customers to integrate "
                  "smart home device control, automation management, and webhook events into their own applications. "
                  "API is RESTful, returns JSON, and supports HTTPS only.", ST["Body"]),
        Spacer(1, 0.2*cm),
        Paragraph("Authentication", ST["H2"]),
        Paragraph("• OAuth 2.0 client credentials flow for server-to-server integration", ST["Bullet"]),
        Paragraph("• API Key authentication: include X-TechNest-Key: <your_api_key> in request headers", ST["Bullet"]),
        Paragraph("• Token endpoint: POST https://api.technest.th/v2/auth/token", ST["Bullet"]),
        Spacer(1, 0.2*cm),
        Paragraph("Rate Limits", ST["H2"]),
    ]
    rates = [
        ["Tier", "Requests/min", "Requests/day", "Price"],
        ["Free",       "100",   "10,000",  "Free (1 property)"],
        ["Pro",      "1,000",  "500,000",  "599 THB/month"],
        ["Enterprise","10,000","Unlimited","Contact sales@technest.th"],
    ]
    rates_t = Table(rates, colWidths=[4*cm, 4*cm, 4*cm, 5*cm])
    rates_t.setStyle(header_style())
    story += [rates_t, Spacer(1, 0.3*cm)]

    story += [
        Paragraph("Key Endpoints", ST["H2"]),
        Paragraph("GET /devices — List all devices in a property", ST["BodyBold"]),
        Paragraph('Response: {"devices": [{"id": "dev-TN-001", "sku": "TN-SH-2024-006", '
                  '"name": "Living Room Hub", "online": true, "firmware": "FW-4.2.1"}]}', ST["Small"]),
        Spacer(1, 0.1*cm),
        Paragraph("POST /scenes — Create a new scene", ST["BodyBold"]),
        Paragraph('Body: {"name": "Movie Mode", "actions": [{"device_id": "dev-TN-001", '
                  '"command": "set_brightness", "value": 30}]}', ST["Small"]),
        Spacer(1, 0.1*cm),
        Paragraph("POST /automations — Create automation rule", ST["BodyBold"]),
        Paragraph('Body: {"trigger": {"type": "time", "time": "22:00"}, '
                  '"condition": {"operator": "AND", "rules": []}, '
                  '"actions": [{"device_id": "dev-TN-002", "command": "lock"}]}', ST["Small"]),
        Spacer(1, 0.1*cm),
        Paragraph("POST /webhooks — Register webhook endpoint", ST["BodyBold"]),
        Paragraph('Body: {"url": "https://your-server.com/webhook", '
                  '"events": ["device.online", "device.state_change", "automation.triggered"], '
                  '"secret": "your_signing_secret"}', ST["Small"]),
        Spacer(1, 0.3*cm),
        Paragraph("SDK Availability", ST["H2"]),
        Paragraph("• JavaScript/Node.js: npm install technest-sdk@2.3.1", ST["Bullet"]),
        Paragraph("• Python: pip install technest-sdk==2.3.1", ST["Bullet"]),
        Paragraph("• Documentation: https://developers.technest.th/docs/v2", ST["Bullet"]),
        PageBreak(),
    ]

    # Page 8-9: International Shipping
    story += [Paragraph("Shipping and Fulfillment Policy", ST["H1"])]
    story += [
        Paragraph("Domestic Shipping (Thailand)", ST["H2"]),
    ]
    dom_ship = [
        ["Zone", "Area", "≤1kg", "1-5kg", "5-10kg", "Delivery Time", "Free Shipping"],
        ["Zone A", "Bangkok & Greater BKK", "30 THB", "60 THB",  "100 THB", "1-2 days",  "Orders ≥ 1,500 THB"],
        ["Zone B", "Upcountry Thailand",    "50 THB", "90 THB",  "150 THB", "2-4 days",  "Orders ≥ 1,500 THB"],
        ["Zone C", "Islands / Remote Areas","80 THB", "150 THB", "250 THB", "5-7 days",  "Not eligible"],
    ]
    ds_t = Table(dom_ship, colWidths=[2*cm, 4*cm, 1.8*cm, 1.8*cm, 2.2*cm, 2.5*cm, 3.7*cm])
    ds_t.setStyle(header_style())
    story += [ds_t, Spacer(1, 0.3*cm)]

    story += [
        Paragraph("International Shipping — Available Countries", ST["H2"]),
    ]
    intl = [
        ["Country", "Carrier", "Delivery", "Rate (≤1kg)", "Rate (1-5kg)"],
        ["Singapore",   "DHL Express / FedEx", "3-5 days",  "350 THB",  "650 THB"],
        ["Malaysia",    "DHL Express",          "4-6 days",  "320 THB",  "600 THB"],
        ["Indonesia",   "DHL Express",          "5-7 days",  "400 THB",  "750 THB"],
        ["Vietnam",     "Kerry Express Intl",   "5-7 days",  "380 THB",  "700 THB"],
        ["Philippines", "DHL Express",          "6-8 days",  "420 THB",  "800 THB"],
        ["Cambodia",    "Kerry Express Intl",   "5-7 days",  "360 THB",  "680 THB"],
        ["Myanmar",     "Kerry Express Intl",   "7-10 days", "380 THB",  "720 THB"],
        ["Laos",        "Kerry Express Intl",   "5-8 days",  "350 THB",  "660 THB"],
        ["Brunei",      "DHL Express",          "5-7 days",  "450 THB",  "850 THB"],
        ["Hong Kong",   "FedEx / DHL Express",  "3-5 days",  "380 THB",  "720 THB"],
        ["Taiwan",      "FedEx",                "4-6 days",  "400 THB",  "760 THB"],
        ["Japan",       "FedEx / EMS",          "4-6 days",  "500 THB",  "950 THB"],
    ]
    i_t = Table(intl, colWidths=[2.5*cm, 4*cm, 2.5*cm, 2.5*cm, 3*cm])
    i_t.setStyle(header_style())
    story += [i_t, Spacer(1, 0.3*cm)]
    story += [
        Paragraph("International Shipping Restrictions", ST["H2"]),
        Paragraph("• Door Lock Ultra (TN-SPEC-EN-2024-002): Requires export license — contact export@technest.th", ST["Bullet"]),
        Paragraph("• CCTV 4K Dome (TN-SPEC-EN-2024-004): Subject to country-specific import regulations", ST["Bullet"]),
        Paragraph("• All international buyers are responsible for customs duties and import taxes", ST["Bullet"]),
        Paragraph("• International returns: customer bears return shipping + 15% restocking fee (min. 150 THB)", ST["Bullet"]),
        PageBreak(),
    ]

    # Page 10-11: SLA
    story += [Paragraph("Customer Support SLA and Escalation Matrix", ST["H1"])]
    sla = [
        ["Channel", "Response Target", "Operating Hours", "Available To"],
        ["Live Chat (Website/App)", "< 3 minutes",  "Daily 09:00-21:00 ICT",  "All customers"],
        ["Email (support@technest.th)", "< 4 business hours","Mon-Fri 09:00-18:00","All customers"],
        ["Phone (02-xxx-8899)",     "< 2 min hold",  "Mon-Fri 09:00-18:00 ICT","All customers"],
        ["LINE @technest.th",       "< 30 minutes",  "Daily 09:00-21:00 ICT",  "TechNest Plus members"],
        ["Priority Hotline",        "< 5 minutes",   "Daily 08:00-22:00 ICT",  "Enterprise B2B only"],
    ]
    sla_t = Table(sla, colWidths=[4.5*cm, 3.5*cm, 4*cm, 5*cm])
    sla_t.setStyle(header_style())
    story += [sla_t, Spacer(1, 0.3*cm)]

    story += [
        Paragraph("Support Tiers", ST["H2"]),
    ]
    tiers = [
        ["Tier", "Who", "Benefits"],
        ["Standard",   "All customers (free)",           "Live chat, email, phone, 4-hour email SLA"],
        ["Plus",       "TechNest Plus members (299/yr)", "30-min LINE response, priority queue, extended warranty"],
        ["Enterprise", "B2B contracts (custom pricing)", "Dedicated account manager, 24/7 priority hotline, SLA guarantee"],
    ]
    tier_t = Table(tiers, colWidths=[2.5*cm, 5*cm, 9.5*cm])
    tier_t.setStyle(header_style())
    story += [tier_t, Spacer(1, 0.3*cm)]

    story += [
        Paragraph("Escalation Path", ST["H2"]),
        Paragraph("L1 (Chatbot/Self-service) → L2 (Support Agent) → L3 (Technical Specialist) → L4 (Engineering Team)", ST["Body"]),
        Spacer(1, 0.2*cm),
        Paragraph("Issue Type Codes", ST["H2"]),
    ]
    issue_codes = [
        ["Code", "Issue Type", "Default L2 Escalation Trigger"],
        ["ISSUE-CONN",  "Connectivity / Network",  "Not resolved after 2 troubleshooting attempts"],
        ["ISSUE-APP",   "App bugs / crashes",       "Reproducible crash or error code ERR-APP-404 to ERR-APP-412"],
        ["ISSUE-HW",    "Hardware defects",         "Immediate escalation — no self-service resolution"],
        ["ISSUE-BILL",  "Billing / payment",        "Amount dispute > 500 THB"],
        ["ISSUE-SHIP",  "Shipping / delivery",      "Package delayed > 3 days beyond estimated delivery"],
    ]
    ic_t = Table(issue_codes, colWidths=[3*cm, 5*cm, 9*cm])
    ic_t.setStyle(header_style())
    story += [ic_t, Spacer(1, 0.3*cm)]
    story += [
        Paragraph("Scheduled Maintenance Windows", ST["H2"]),
        Paragraph("• Regular maintenance: every 2nd Sunday of the month, 02:00-04:00 ICT", ST["Bullet"]),
        Paragraph("• Emergency maintenance: announced via LINE Official and website banner at least 1 hour prior", ST["Bullet"]),
        Paragraph("• During maintenance: API endpoints may return HTTP 503. Webhooks are queued and delivered post-maintenance.", ST["Bullet"]),
        Spacer(1, 0.3*cm),
        Paragraph("Enterprise B2B Support Addendum", ST["H2"]),
        Paragraph("Enterprise contracts (minimum commitment: 50 devices or 100,000 THB annual spend) include:", ST["Body"]),
        Paragraph("• Dedicated Customer Success Manager (CSM) assigned within 5 business days of contract signing", ST["Bullet"]),
        Paragraph("• Monthly business review (MBR) meeting via video call or on-site at TechNest HQ, CW Tower 23F", ST["Bullet"]),
        Paragraph("• Custom SLA agreement with financial penalties: > 4hr response = 5% monthly credit, > 8hr = 15% credit", ST["Bullet"]),
        Paragraph("• Sandbox environment access: api-sandbox.technest.th/v2/ for integration testing without rate limits", ST["Bullet"]),
        Paragraph("• Bulk firmware deployment tool: push FW updates to all managed devices simultaneously via Enterprise Portal", ST["Bullet"]),
        Paragraph("• White-label API reseller option: embed TechNest device control under your own brand (requires NDA)", ST["Bullet"]),
        Paragraph("• On-site installation service in Bangkok: 500 THB/device first 20 devices, 350 THB thereafter", ST["Bullet"]),
        PageBreak(),
    ]

    # Page 12: Legal
    story += [
        Paragraph("Legal and Compliance", ST["H1"]),
        Paragraph("Company Information", ST["H2"]),
        Paragraph("TechNest Thailand Co., Ltd. | Registration No. 0105562089954 | "
                  "Registered Capital: 50,000,000 THB | Established: January 15, 2019", ST["Body"]),
        Paragraph("Registered Office: 88/8 CW Tower, 23rd Floor, Ratchadaphisek Rd, Huay Kwang, Bangkok 10310", ST["Body"]),
        Spacer(1, 0.3*cm),
        Paragraph("Product Certifications and Compliance", ST["H2"]),
        Paragraph("All TechNest products are tested and certified for the Thai market. Key certifications include:", ST["Body"]),
        Paragraph("• NBTC Type Approval (National Broadcasting and Telecommunications Commission of Thailand) "
                  "for all Wi-Fi and Bluetooth devices", ST["Bullet"]),
        Paragraph("• TIS 2162-2548 for smart plugs and electrical devices", ST["Bullet"]),
        Paragraph("• CE marking for electromagnetic compatibility (EMC) and low voltage directive compliance", ST["Bullet"]),
        Paragraph("• FCC Part 15 for radio frequency equipment", ST["Bullet"]),
        Paragraph("• RoHS Directive compliance — all products free of hazardous substances", ST["Bullet"]),
        Spacer(1, 0.3*cm),
        Paragraph("Data Privacy", ST["H2"]),
        Paragraph("TechNest Thailand processes user data in compliance with Thailand's Personal Data Protection Act "
                  "(PDPA) B.E. 2562 (2019). Device usage data is stored on AWS ap-southeast-1 (Singapore). "
                  "Data retention: usage logs 90 days, account data until deletion request. "
                  "DPO contact: dpo@technest.th", ST["Body"]),
        Spacer(1, 0.3*cm),
        Paragraph("Limitation of Liability", ST["H2"]),
        Paragraph("TechNest Thailand's total liability for any claim shall not exceed the purchase price of the "
                  "affected product. TechNest is not liable for indirect, incidental, or consequential damages "
                  "arising from product use or service interruption.", ST["Body"]),
        Spacer(1, 0.3*cm),
        Paragraph("© 2024 TechNest Thailand Co., Ltd. All rights reserved. "
                  "Document version EN-2024-v3.2 | Last updated: October 15, 2024", ST["Small"]),
    ]

    doc.build(story, onFirstPage=page_footer("TechNest Thailand"), onLaterPages=page_footer("TechNest Thailand"))
    print(f"  Created: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# PDF 3: technest_mixed.pdf — Thai + English Interleaved
# ═══════════════════════════════════════════════════════════════════════════════
def build_mixed_pdf(path: str):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)
    story = []

    # หน้า 1: ปก
    story += [
        Spacer(1, 1.5*cm),
        Paragraph("TechNest Thailand", ST["Title"]),
        Paragraph("คู่มือ Support and Troubleshooting Guide", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Paragraph("Version 3.1.2 | Updated: ตุลาคม 2567", ST["Center"]),
        Spacer(1, 0.5*cm),
        Paragraph("เอกสารฉบับนี้เป็น official support guide สำหรับ TechNest Thailand ครอบคลุมการ setup, "
                  "troubleshooting, automation configuration และ firmware update history "
                  "สำหรับอุปกรณ์ทุกรุ่นในปี 2567 เนื้อหาเขียนในรูปแบบ Thai-English mixed เพื่อความสะดวก "
                  "ของ support team และลูกค้าที่คุ้นเคยกับ technical terminology ภาษาอังกฤษ", ST["Body"]),
        PageBreak(),
    ]

    # หน้า 2-3: Setup Guide Hub Central Pro
    story += [
        Paragraph("Setup Guide: TechNest Hub Central Pro (TN-SH-2024-006)", ST["H1"]),
        Paragraph("Network Requirements และการเตรียมความพร้อม", ST["H2"]),
        Paragraph("ก่อนเริ่ม setup TechNest Hub Central Pro ให้ตรวจสอบว่า home network ของคุณพร้อมดังนี้: "
                  "ต้องใช้ Wi-Fi 2.4GHz band (5GHz ก็รองรับแต่แนะนำ 2.4GHz สำหรับ compatibility ที่ดีกว่า) "
                  "ระบบ security ต้องเป็น WPA2 หรือ WPA3 เท่านั้น WEP ไม่รองรับ "
                  "และ router ต้องเปิด UPnP หรือกำหนด port forwarding สำหรับ port 8883 (MQTT over TLS)", ST["Body"]),
        Spacer(1, 0.2*cm),
        Paragraph("ขั้นตอนการ Setup ทีละขั้น", ST["H2"]),
        Paragraph("ขั้นที่ 1: ดาวน์โหลด TechNest Home app เวอร์ชัน 4.2.1 ขึ้นไป (available บน App Store "
                  "สำหรับ iOS 14+ และ Google Play สำหรับ Android 10+) ถ้าติดตั้งไว้แล้วให้ check for update ก่อน", ST["Body"]),
        Paragraph("ขั้นที่ 2: เสียบ power adapter DC 5V 2A เข้าที่ Hub แล้วรอจนกว่า LED indicator "
                  "ด้านบนจะกะพริบสีขาว 3 ครั้ง (boot sequence เสร็จสมบูรณ์ ใช้เวลาประมาณ 30 วินาที)", ST["Body"]),
        Paragraph("ขั้นที่ 3: เปิดแอป > กด + (Add Device) > เลือก Hub > Hub Central Pro "
                  "แอปจะเริ่ม scan สัญญาณ Bluetooth ให้กด Pair button ที่ด้านหลัง Hub "
                  "ค้างไว้ 3 วินาทีจนกว่า LED จะกะพริบสีฟ้าเร็ว (Pairing Mode) "
                  "ซึ่งใช้เวลาประมาณ 45 วินาทีในการเข้า Pairing Mode", ST["Body"]),
        Paragraph("ขั้นที่ 4: แอปจะให้กรอก Wi-Fi credentials (SSID และ password) "
                  "จากนั้น Hub จะเชื่อมต่อ Wi-Fi — LED จะเปลี่ยนเป็นสีเขียวนิ่ง (Connected) "
                  "ถ้า LED กะพริบสีแดงให้ดู error code section ด้านล่าง", ST["Body"]),
        Paragraph("ขั้นที่ 5: หลัง connect สำเร็จ Hub จะ download latest firmware อัตโนมัติ "
                  "(FW-4.2.1 ขนาดประมาณ 18MB) ระหว่าง update LED จะกะพริบสีส้ม ห้ามปิดไฟหรือถอดสายไฟ", ST["Body"]),
        Spacer(1, 0.2*cm),
        Paragraph("Error Codes และวิธีแก้ไข", ST["H2"]),
    ]
    errors = [
        ["Error Code", "ความหมาย", "วิธีแก้ไข"],
        ["ERR-HUB-001", "Wi-Fi connection timeout", "ตรวจสอบว่า SSID และ password ถูกต้อง และ Hub อยู่ในระยะสัญญาณ Wi-Fi"],
        ["ERR-HUB-002", "Bluetooth pairing failed", "รีสตาร์ท Hub โดยกด reset 10 วินาที แล้วลอง pair ใหม่"],
        ["ERR-HUB-003", "Server authentication error", "ตรวจสอบว่า account ยังใช้งานได้ ลอง logout แล้ว login ใหม่ในแอป"],
        ["ERR-HUB-004", "Firmware update failed", "ตรวจสอบ internet connection แล้วกด Manual Update ในแอป > Settings > Hub"],
        ["ERR-HUB-005", "Zigbee network congestion", "ลด จำนวนอุปกรณ์ใกล้เคียงที่ใช้ channel เดียวกัน แนะนำ Zigbee channel 25"],
        ["ERR-HUB-006", "Z-Wave inclusion failed", "วางอุปกรณ์ Z-Wave ไม่เกิน 3 เมตรจาก Hub ระหว่าง inclusion"],
        ["ERR-HUB-007", "Cloud sync error", "ข้อมูลไม่ sync ตรวจสอบ firewall ว่าเปิด port 443 และ 8883 แล้ว"],
        ["ERR-HUB-008", "Memory full (>200 Zigbee devices)", "ลบอุปกรณ์ที่ไม่ใช้งาน Zigbee จำกัด 200 devices ต่อ Hub"],
        ["ERR-HUB-009", "Factory reset required", "กด Reset button ค้าง 15 วินาที LED จะกะพริบแดง 5 ครั้งก่อน reset"],
    ]
    err_t = Table(errors, colWidths=[3*cm, 4*cm, 10*cm])
    err_t.setStyle(header_style())
    story += [err_t, Spacer(1, 0.3*cm)]

    story += [
        Paragraph("App Version Compatibility Matrix", ST["H2"]),
    ]
    app_compat = [
        ["Hub Firmware", "Min App Version (iOS)", "Min App Version (Android)", "Notable Changes"],
        ["FW-4.2.1", "App 4.2.1+", "App 4.2.1+", "Matter 1.2 UI, Zigbee re-pair fix"],
        ["FW-4.1.8", "App 4.1.5+", "App 4.1.5+", "Security patch, no new UI features"],
        ["FW-4.0.0", "App 4.0.0+", "App 4.0.0+", "Matter 1.2 support (requires app 4.0.0 minimum)"],
        ["FW-3.9.x", "App 3.8.0+", "App 3.8.0+", "Legacy — upgrade recommended"],
    ]
    ac_t = Table(app_compat, colWidths=[3*cm, 4*cm, 4.5*cm, 5.5*cm])
    ac_t.setStyle(header_style())
    story += [ac_t, PageBreak()]

    # หน้า 4-5: Automation
    story += [
        Paragraph("Automation and Scene Configuration", ST["H1"]),
        Paragraph("วิธีสร้าง Automation Rule ใน TechNest Home App", ST["H2"]),
        Paragraph("เปิดแอป TechNest Home > กด Automation (ไอคอน flash) > กด + (New Automation) "
                  "จากนั้นเลือก Trigger type ที่ต้องการ: time-based, sensor-based, หรือ location-based (geofencing) "
                  "โดย geofencing radius default คือ 200 เมตร สามารถปรับได้ระหว่าง 100-500 เมตร", ST["Body"]),
        Spacer(1, 0.2*cm),
        Paragraph("Trigger Types ที่รองรับ", ST["H2"]),
        Paragraph("• Time-based: ตั้งเวลาทำงานตามเวลาที่กำหนด รองรับ recurring schedule (ทุกวัน, วันธรรมดา, วันหยุด) "
                  "และ sunrise/sunset trigger (คำนวณตามพิกัด GPS อัตโนมัติ)", ST["Bullet"]),
        Paragraph("• Sensor-based: ทำงานเมื่อ sensor ตรวจจับ event เช่น Motion Sensor (TN-SH-2024-007) "
                  "detect motion, Door Lock state change, Water Leak Sensor alert", ST["Bullet"]),
        Paragraph("• Location-based (Geofencing): ทำงานเมื่อสมาชิกในบ้าน enter หรือ leave geofence "
                  "radius 200 เมตร default ใช้ GPS ของ smartphone ที่ติดตั้งแอป", ST["Bullet"]),
        Spacer(1, 0.2*cm),
        Paragraph("Condition Operators", ST["H2"]),
        Paragraph("ใน TechNest automation engine รองรับ logical operators 3 แบบ:", ST["Body"]),
        Paragraph("• AND: ทุก condition ต้องเป็น true พร้อมกัน ตัวอย่าง JSON: "
                  '{"operator": "AND", "conditions": [{"device": "motion-01", "state": "active"}, '
                  '{"time": "20:00-08:00"}]}', ST["Bullet"]),
        Paragraph("• OR: condition อย่างน้อยหนึ่งอันเป็น true ตัวอย่าง JSON: "
                  '{"operator": "OR", "conditions": [{"device": "door-01", "state": "unlocked"}, '
                  '{"device": "motion-01", "state": "active"}]}', ST["Bullet"]),
        Paragraph("• NOT: condition ต้อง false ใช้สำหรับ exclusion เช่น NOT (ช่วงเวลา 09:00-17:00) "
                  "คือทำงานเฉพาะนอกเวลาทำงาน", ST["Bullet"]),
        Spacer(1, 0.3*cm),
        Paragraph("5 ตัวอย่าง Automation Use Cases", ST["H2"]),
        Paragraph("Use Case 1 — 'Good Night Mode': เมื่อกด scene 'Good Night' เวลา 22:00 "
                  "Hub จะ lock Door Lock Ultra (TN-SH-2024-002) อัตโนมัติ + dim Smart Bulb Pro X "
                  "ทุกดวงในบ้านเหลือ 10% + ตั้ง Air Purifier S7 (TN-SH-2024-003) เป็น sleep mode (ความเร็วพัดลม 1)", ST["Body"]),
        Paragraph("Use Case 2 — 'Away from Home': เมื่อ geofencing ตรวจพบว่าทุก device ออกจาก radius 200m "
                  "ระบบจะ turn off LED Strip 5M (TN-SH-2024-010) และ Smart Plug V3 (TN-SH-2024-005) ทุกตัว "
                  "และส่ง notification แจ้งเตือน security camera เริ่ม recording", ST["Body"]),
        Paragraph("Use Case 3 — 'Water Leak Alert': เมื่อ Water Leak Sensor (TN-SH-2024-012) detect น้ำ "
                  "ระบบ trigger ทันที: ส่ง push notification, SMS, และ LINE message พร้อมรูปถ่ายจาก CCTV 4K Dome "
                  "ถ้า severity level สูง (water detected > 30 วินาที) จะโทรหา emergency contact อัตโนมัติ", ST["Body"]),
        Paragraph("Use Case 4 — 'Morning Routine': เมื่อถึงเวลา sunrise (คำนวณ GPS อัตโนมัติ) "
                  "Smart Curtain Kit (TN-SH-2024-009) จะเปิดอัตโนมัติ 100% + Smart Bulb Pro X "
                  "ค่อยๆ brighten จาก 0% ถึง 80% ใน 10 นาที (sunrise simulation) "
                  "เพื่อปลุกอย่างอ่อนโยนโดยไม่ต้องใช้นาฬิกาปลุก", ST["Body"]),
        Paragraph("Use Case 5 — 'Security Night Mode': เมื่อ Motion Sensor 360 (TN-SH-2024-007) "
                  "detect motion ระหว่างเวลา 23:00-06:00 AND Door Lock Ultra อยู่ใน locked state "
                  "ระบบจะ flash LED Strip สีแดง 3 ครั้ง + เปิด CCTV recording + ส่ง LINE alert "
                  "พร้อมรูปภาพ snapshot ให้เจ้าของบ้านทันที", ST["Body"]),
        PageBreak(),
    ]

    # หน้า 6-7: Troubleshooting
    story += [Paragraph("Troubleshooting Guide: Connectivity Issues", ST["H1"])]
    trouble = [
        ["ปัญหา (Thai)", "Possible Cause (English)", "วิธีแก้ไข (Thai)"],
        ["อุปกรณ์ offline บ่อย", "Wi-Fi signal too weak (<-70dBm)", "ย้าย Hub ให้ใกล้ router มากขึ้น หรือเพิ่ม Wi-Fi extender"],
        ["Zigbee device ไม่ respond", "Zigbee channel interference (2.4GHz overlap)", "เปลี่ยน Zigbee channel เป็น 25 (แนะนำสุด) หรือ 15, 20, 11 ตามลำดับ"],
        ["BLE pairing ล้มเหลว", "Bluetooth adapter busy or device too far", "วาง Hub และอุปกรณ์ให้ห่างกันไม่เกิน 5 เมตร ระหว่าง pairing"],
        ["API timeout บ่อย", "Rate limit exceeded (>100 req/min free tier)", "Upgrade เป็น Pro tier หรือ implement exponential backoff ใน code"],
        ["แอปล่มบ่อย ERR-APP-404", "App version incompatible with firmware", "Update app เป็นเวอร์ชันล่าสุด ดู compatibility matrix"],
        ["ERR-APP-405", "Session token expired", "Logout แล้ว login ใหม่ ถ้ายังเกิดให้ clear app cache"],
        ["ERR-APP-406", "Device not found in registry", "ลบอุปกรณ์ออกจากแอปแล้ว re-add ใหม่ตั้งแต่ต้น"],
        ["ERR-APP-407", "Automation rule conflict", "ตรวจสอบว่า automation rules ไม่ขัดแย้งกัน เช่น สั่ง on/off พร้อมกัน"],
        ["ERR-APP-408", "Scene load timeout", "ลด จำนวนอุปกรณ์ใน scene หรือแบ่ง scene ออกเป็นหลายอัน"],
        ["ERR-APP-409", "Webhook delivery failed", "ตรวจสอบว่า webhook endpoint ตอบ HTTP 200 ภายใน 5 วินาที"],
        ["ERR-APP-410", "Geofencing GPS unavailable", "ให้สิทธิ์ Location ให้แอปเป็น 'Always Allow' ใน device settings"],
        ["ERR-APP-411", "OTA update download error", "ตรวจสอบ internet speed (ต้องการอย่างน้อย 1 Mbps) แล้วลอง update ใหม่"],
        ["ERR-APP-412", "Matter pairing QR code invalid", "Scan QR code ใหม่ให้ชัดเจน หรือกรอก pairing code ด้วยตนเอง"],
        ["Robot Vacuum หลงทาง", "Map corrupted after firmware update", "ลบ map เก่าในแอป > Robot Vacuum > Map Management แล้วสร้าง map ใหม่"],
        ["CCTV ภาพกระตุก", "Insufficient bandwidth for 4K stream", "เปลี่ยนเป็น 1080p stream ในแอป หรือใช้ Ethernet แทน Wi-Fi"],
    ]
    tr_t = Table(trouble, colWidths=[4.5*cm, 5.5*cm, 7*cm])
    tr_t.setStyle(header_style())
    story += [tr_t, Spacer(1, 0.3*cm)]
    story += [
        Paragraph("การ Debug ขั้นสูงสำหรับ Developer", ST["H2"]),
        Paragraph("ถ้า Zigbee interference ยังคงอยู่หลังเปลี่ยน channel แล้ว ให้ใช้ TechNest Zigbee Analyzer "
                  "(เข้าถึงได้ผ่าน Enterprise Portal) เพื่อ scan spectral density ของ 2.4GHz band "
                  "และหา channel ที่ clear ที่สุด โดย recommended channels ตามลำดับคือ 25 > 20 > 15 > 11 "
                  "เพื่อหลีกเลี่ยง overlap กับ Wi-Fi channels 1, 6 และ 11", ST["Body"]),
        Paragraph("สำหรับ API timeout ให้ implement exponential backoff ตัวอย่าง Python: "
                  "retry_delay = min(2**attempt, 60) โดย attempt เริ่มจาก 0 "
                  "และ jitter ±10% เพื่อหลีกเลี่ยง thundering herd problem "
                  "Free tier limit คือ 100 req/min นับ per API key ไม่ใช่ per IP", ST["Body"]),
        Paragraph("BLE pairing failure บ่อยที่สุดเกิดจาก interference จาก Bluetooth device อื่นในบริเวณ "
                  "ให้ปิด Bluetooth บน devices อื่นชั่วคราวระหว่าง pairing หรือเปลี่ยน advertising channel "
                  "ใน Door Lock Ultra โดยกด config button ด้านใน lock 7 ครั้งเร็วๆ เพื่อเข้า advanced mode", ST["Body"]),
        PageBreak(),
    ]

    # หน้า 8-9: Bundle Recommendations
    story += [Paragraph("Product Bundle Recommendations", ST["H1"])]
    story += [
        Paragraph("TechNest นำเสนอ bundle packages ที่ออกแบบมาสำหรับ use case ต่างๆ "
                  "แต่ละ bundle มีส่วนลดพิเศษเมื่อเทียบกับการซื้อแยกชิ้น", ST["Body"]),
        Spacer(1, 0.2*cm),
    ]
    bundles = [
        ["Bundle Code", "รายการสินค้า", "ราคารวมเดี่ยว", "ราคา Bundle", "ประหยัด"],
        ["BUNDLE-HOME-STARTER-01",
         "Smart Bulb Pro X ×2 + Smart Plug V3 ×2 + Motion Sensor 360 ×1",
         "4,960 THB", "3,990 THB", "970 THB"],
        ["BUNDLE-SECURITY-PRO-02",
         "Door Lock Ultra ×1 + CCTV 4K Dome ×2 + Motion Sensor 360 ×2 + Smart Doorbell HD ×1",
         "16,977 THB", "13,500 THB", "3,477 THB"],
        ["BUNDLE-ENERGY-03",
         "Smart Plug V3 ×4 + LED Strip 5M ×2 + Water Leak Sensor ×2 + Hub Central Pro ×1",
         "13,140 THB", "10,500 THB", "2,640 THB"],
        ["BUNDLE-CONDO-04",
         "Hub Central Pro ×1 + Smart Curtain Kit ×1 + Smart Bulb Pro X ×3 + Smart Plug V3 ×2",
         "18,050 THB", "14,800 THB", "3,250 THB"],
        ["BUNDLE-OFFICE-05",
         "Hub Central Pro ×1 + CCTV 4K Dome ×4 + Door Lock Ultra ×2 + Motion Sensor 360 ×4",
         "38,756 THB", "30,500 THB", "8,256 THB"],
    ]
    b_t = Table(bundles, colWidths=[4*cm, 7*cm, 2.8*cm, 2.8*cm, 2.4*cm])
    b_t.setStyle(header_style())
    story += [b_t, PageBreak()]

    story += [
        Paragraph("Product Bundle Recommendations (ต่อ)", ST["H1"]),
        Paragraph("Compatibility Guide: Bundle กับประเภทที่พักอาศัย", ST["H2"]),
    ]
    compat = [
        ["Bundle", "คอนโด", "บ้านชั้นเดียว", "Office", "ทาวน์เฮาส์"],
        ["BUNDLE-HOME-STARTER-01", "แนะนำมาก", "เหมาะสม",   "ใช้ได้",     "เหมาะสม"],
        ["BUNDLE-SECURITY-PRO-02", "เหมาะสม",  "แนะนำมาก", "แนะนำมาก",  "แนะนำมาก"],
        ["BUNDLE-ENERGY-03",       "แนะนำมาก", "เหมาะสม",   "แนะนำมาก", "เหมาะสม"],
        ["BUNDLE-CONDO-04",        "แนะนำมาก", "ใช้ได้",    "ไม่แนะนำ",  "เหมาะสม"],
        ["BUNDLE-OFFICE-05",       "ไม่แนะนำ", "ใช้ได้",    "แนะนำมาก", "ใช้ได้"],
    ]
    c_t2 = Table(compat, colWidths=[5*cm, 3*cm, 3.5*cm, 3*cm, 3.5*cm])
    c_t2.setStyle(header_style())
    story += [c_t2, PageBreak()]

    # หน้า 10-11: Firmware History
    story += [Paragraph("Firmware Update History and Roadmap", ST["H1"])]
    fw = [
        ["Version", "Release Date", "Compatible Devices", "Key Changes (EN)", "หมายเหตุ (TH)"],
        ["FW-4.2.1", "15 ต.ค. 2567", "Hub Central Pro\nSmart Bulb Pro X",
         "Fixed Zigbee re-pairing bug\nImproved MQTT latency by 40%", "แก้บั๊กการ pair ซ้ำ"],
        ["FW-4.1.8", "02 ก.ย. 2567", "All devices",
         "Security patch CVE-2024-TN-0031", "แพตช์ความปลอดภัยด่วน"],
        ["FW-4.0.0", "01 ส.ค. 2567", "Hub Central Pro",
         "Added Matter 1.2 protocol support", "รองรับ Matter 1.2"],
        ["FW-3.9.5", "12 ก.ค. 2567", "Robot Vacuum Z9",
         "Improved obstacle detection AI model v2.3", "AI ตรวจจับสิ่งกีดขวางดีขึ้น"],
        ["FW-3.8.2", "05 มิ.ย. 2567", "Smart Curtain Kit",
         "Added sunrise/sunset auto-schedule", "ตั้งเวลาตามพระอาทิตย์"],
        ["FW-3.7.0", "20 เม.ย. 2567", "Hub Central Pro\nDoor Lock Ultra",
         "Added voice assistant integration\n(Google Home, Alexa)", "รองรับสั่งด้วยเสียง"],
        ["FW-3.6.1", "03 มี.ค. 2567", "All devices",
         "Fixed memory leak causing 12hr+ uptime crashes", "แก้บั๊กค้างหลัง 12 ชั่วโมง"],
        ["FW-3.5.0", "15 ม.ค. 2567", "CCTV 4K Dome",
         "Added AI person detection\nFalse alarm rate reduced by 65%", "AI แยกแยะคนได้แม่นขึ้น 65%"],
    ]
    fw_t = Table(fw, colWidths=[2.2*cm, 2.8*cm, 3.5*cm, 5.5*cm, 3*cm])
    fw_t.setStyle(header_style())
    story += [fw_t, PageBreak()]

    story += [
        Paragraph("Firmware Update History (ต่อ) — Upcoming Releases", ST["H1"]),
        Paragraph("Roadmap 2568 (2025)", ST["H2"]),
        Paragraph("• Q1 2568 (ม.ค.-มี.ค. 2568): Energy monitoring dashboard — real-time power consumption tracking "
                  "สำหรับ Smart Plug V3 และ Hub Central Pro แสดงผลใน TechNest Home app พร้อม cost estimation "
                  "ตามอัตราค่าไฟ MEA/PEA ของ Thailand", ST["Bullet"]),
        Paragraph("• Q2 2568 (เม.ย.-มิ.ย. 2568): Thread protocol support — เพิ่ม Thread border router "
                  "ใน Hub Central Pro firmware อัปเดต ทำให้รองรับอุปกรณ์ Thread-based ใหม่ๆ "
                  "ที่ออกมาพร้อม Matter 1.2 ecosystem", ST["Bullet"]),
        Paragraph("• Q3 2568 (ก.ค.-ก.ย. 2568): TechNest Home app v5.0 redesign — "
                  "UI ใหม่ทั้งหมด improved dashboard, AI-powered automation suggestions, "
                  "และ Energy insights รองรับ iOS 16+ และ Android 12+", ST["Bullet"]),
        PageBreak(),
    ]

    # หน้า 12: Contact (Mixed)
    story += [
        Paragraph("ช่องทางติดต่อและ Escalation (Contact and Escalation)", ST["H1"]),
        Paragraph("ช่องทาง Support หลัก", ST["H2"]),
    ]
    contacts_mixed = [
        ["Channel", "รายละเอียด", "Response Time"],
        ["LINE @technest.th",        "สำหรับ support ทั่วไปและ TechNest Plus members", "< 30 นาที (09:00-21:00)"],
        ["Live Chat (technest.th)",  "Real-time chat บนเว็บไซต์ — ใช้ chatbot L1 ก่อน", "< 3 นาที"],
        ["Email: support@technest.th","สำหรับ ISSUE-BILL และ warranty claim ที่ต้องการเอกสาร", "< 4 business hours"],
        ["Phone: 02-xxx-8899",       "สำหรับ ISSUE-HW urgent ที่ต้องการ immediate help", "< 2 นาที hold time"],
        ["GitHub: technest-th/sdk",  "Bug reports สำหรับ TechNest Open API และ SDK", "3-5 business days"],
    ]
    cm_t = Table(contacts_mixed, colWidths=[4.5*cm, 7*cm, 5.5*cm])
    cm_t.setStyle(header_style())
    story += [cm_t, Spacer(1, 0.4*cm)]

    story += [
        Paragraph("Escalation Matrix", ST["H2"]),
        Paragraph("L1 (Chatbot / Self-service FAQ) → ถ้าไม่แก้ได้ใน 10 นาที →", ST["Body"]),
        Paragraph("L2 (Support Agent / Human) → ถ้าต้องการ technical knowledge หรือ ISSUE-HW →", ST["Body"]),
        Paragraph("L3 (Technical Specialist) → ถ้าปัญหาซับซ้อนหรือเกี่ยวกับ firmware/API bug →", ST["Body"]),
        Paragraph("L4 (Engineering Team) → สำหรับ critical bug ที่กระทบผู้ใช้หลายราย หรือ CVE security issue", ST["Body"]),
        Spacer(1, 0.4*cm),
        Paragraph("© 2567 TechNest Thailand Co., Ltd. | เลขที่ทะเบียน: 0105562089954 | "
                  "Document: MIX-2024-v3.1.2 | Last updated: 15 ตุลาคม 2567", ST["Small"]),
    ]

    doc.build(story, onFirstPage=page_footer("TechNest Thailand"), onLaterPages=page_footer("TechNest Thailand"))
    print(f"  Created: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════


# E-COMMERCE SET 1: StyleHub Thailand (แฟชั่นออนไลน์)
# ═══════════════════════════════════════════════════════════════════════════════

def build_stylehub_th(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1, 1.5*cm),
        Paragraph("StyleHub Thailand", ST["Title"]),
        Paragraph("แพลตฟอร์มแฟชั่นออนไลน์ครบวงจร", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1, 0.5*cm),
        Paragraph("StyleHub Thailand ก่อตั้งในปี 2563 เป็นแพลตฟอร์มอีคอมเมิร์ซด้านแฟชั่นชั้นนำของไทย "
                  "รวบรวมแบรนด์ไทยและนานาชาติกว่า 500 แบรนด์ สินค้ากว่า 50,000 รายการ ครอบคลุมเสื้อผ้า "
                  "กระเป๋า รองเท้า เครื่องประดับ และ lifestyle products พร้อมระบบ try-before-you-buy "
                  "และ AI-powered size recommendation", ST["Body"]),
        Spacer(1, 0.5*cm),
        Paragraph("สารบัญ", ST["H1"]),
    ]
    toc = [["หัวข้อ","หน้า"],
           ["แคตาล็อกสินค้าและแบรนด์","2-3"],
           ["นโยบายการคืนสินค้าและ Refund","4-5"],
           ["โปรโมชันและโปรแกรมสมาชิก","6-7"],
           ["นโยบายการจัดส่ง","8-9"],
           ["คำถามที่พบบ่อย (FAQ)","10-11"],
           ["ช่องทางติดต่อและข้อกำหนด","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    # Page 2-3: สินค้า
    story += [Paragraph("แคตาล็อกสินค้าและแบรนด์พันธมิตร", ST["H1"])]
    products = [
        ["รหัสสินค้า","แบรนด์/ชื่อสินค้า","หมวดหมู่","ราคา (THB)","ราคาสมาชิก","สต็อก"],
        ["SH-2024-F001","LookBook Premium Dress","เสื้อผ้าสตรี","2,490","2,100","320 pcs"],
        ["SH-2024-F002","UrbanWear Streetwear Hoodie","เสื้อผ้าบุรุษ","1,890","1,600","450 pcs"],
        ["SH-2024-F003","LaMode Leather Tote Bag","กระเป๋า","4,990","4,200","180 pcs"],
        ["SH-2024-F004","StepUp Running Shoes V2","รองเท้า","3,290","2,800","600 pcs"],
        ["SH-2024-F005","GlowUp Skincare Set (5 items)","ความงาม","1,590","1,350","900 pcs"],
        ["SH-2024-F006","ChicStyle Silver Necklace","เครื่องประดับ","890","760","1,200 pcs"],
        ["SH-2024-F007","ActiveZone Sports Leggings","กีฬา","1,190","1,010","750 pcs"],
        ["SH-2024-F008","NaturalCraft Linen Shirt","เสื้อผ้าสตรี","1,490","1,270","510 pcs"],
        ["SH-2024-F009","MetroKid School Backpack","กระเป๋า","1,890","1,600","380 pcs"],
        ["SH-2024-F010","TrendWatch Analog Timepiece","นาฬิกา","5,990","5,100","200 pcs"],
    ]
    pt = Table(products, colWidths=[3*cm,5*cm,3*cm,2.5*cm,2.5*cm,2*cm])
    pt.setStyle(header_style())
    story += [pt, Spacer(1,0.3*cm)]
    story += [
        Paragraph("แบรนด์พันธมิตรคัดสรร", ST["H2"]),
        Paragraph("• LookBook — แบรนด์ fast fashion ไทย ออกคอลเล็กชันใหม่ทุกสัปดาห์ ราคา 500-5,000 THB", ST["Bullet"]),
        Paragraph("• UrbanWear — streetwear local brand รุ่นลิมิเต็ดเอดิชัน ผ้า 100% cotton organic", ST["Bullet"]),
        Paragraph("• LaMode — กระเป๋าหนังแท้ handcrafted ในไทย รับประกัน 2 ปี", ST["Bullet"]),
        Paragraph("• StepUp — รองเท้ากีฬาและลำลอง รองรับ wide foot ทุกไซส์ 36-46 EU", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("ระบบ AI Size Recommendation", ST["H2"]),
        Paragraph("StyleHub AI วิเคราะห์ประวัติการซื้อและรีวิวของลูกค้ากว่า 2 ล้านคน "
                  "แนะนำขนาดที่เหมาะสมด้วยความแม่นยำ 94.7% ลดอัตราการคืนสินค้าเพราะไซส์ไม่พอดีได้ 62% "
                  "เปิดใช้งานได้ที่แอป StyleHub > โปรไฟล์ > My Size Profile กรอกน้ำหนัก ส่วนสูง และวัดรอบอก/เอว/สะโพก", ST["Body"]),
        PageBreak(),
    ]

    # Page 4-5: นโยบายคืนสินค้า
    story += [Paragraph("นโยบายการคืนสินค้าและ Refund", ST["H1"])]
    story += [
        Paragraph("เงื่อนไขการคืนสินค้า", ST["H2"]),
        Paragraph("StyleHub รับคืนสินค้าภายใน <b>30 วัน</b> นับจากวันรับสินค้า สำหรับสินค้าทั่วไป "
                  "และ <b>7 วัน</b> สำหรับสินค้าลดราคา/Sale items", ST["Body"]),
        Paragraph("• สินค้าต้องไม่ผ่านการใช้งาน ป้ายแท็กยังติดครบ", ST["Bullet"]),
        Paragraph("• บรรจุภัณฑ์เดิมสมบูรณ์ ไม่มีรอยฉีกขาด", ST["Bullet"]),
        Paragraph("• มีหลักฐานการซื้อ (Order ID หรือใบเสร็จ)", ST["Bullet"]),
        Paragraph("• สินค้าชุดชั้นใน ว่ายน้ำ ต่างหู ไม่รับคืนทุกกรณีด้วยเหตุผลด้านสุขอนามัย", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("ขั้นตอนการคืนสินค้า", ST["H2"]),
    ]
    steps = [["ขั้นตอน","รายละเอียด","ระยะเวลา"],
             ["1. แจ้งคืน","เข้าแอป > คำสั่งซื้อ > เลือก Order > กด คืนสินค้า แนบรูปสินค้า","ทันที"],
             ["2. รอการอนุมัติ","ทีมงาน Review ภายใน 1 วันทำการ","1 วัน"],
             ["3. รับ Return Label","StyleHub ส่ง QR Code สำหรับส่งพัสดุผ่าน J&T / Kerry","หลังอนุมัติ"],
             ["4. ส่งสินค้า","นำ QR ไปที่จุดรับพัสดุ หรือนัดรับที่บ้าน (กทม. เท่านั้น)","ภายใน 5 วัน"],
             ["5. Refund","โอนเงินคืน/คืน Credit ภายใน 5-10 วันทำการ","5-10 วัน"]]
    st_t = Table(steps, colWidths=[3*cm,11*cm,3*cm])
    st_t.setStyle(header_style())
    story += [st_t, PageBreak()]

    story += [
        Paragraph("นโยบายการคืนสินค้า (ต่อ)", ST["H1"]),
        Paragraph("ช่องทาง Refund", ST["H2"]),
        Paragraph("• บัตรเครดิต/เดบิต: คืนเข้าบัตรภายใน 7-14 วันทำการ ขึ้นอยู่กับธนาคาร", ST["Bullet"]),
        Paragraph("• StyleHub Wallet: คืนภายใน 24 ชั่วโมง พร้อมโบนัส 5% เพิ่มพิเศษ", ST["Bullet"]),
        Paragraph("• โอนธนาคาร: ภายใน 5 วันทำการ กรอกเลขบัญชีในหน้าคืนสินค้า", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("Try-Before-You-Buy Program", ST["H2"]),
        Paragraph("สมาชิก StyleHub Prime สามารถสั่งสินค้าได้สูงสุด 3 ชิ้น ลองสวมใส่ 3 วัน "
                  "จากนั้นเลือกซื้อชิ้นที่ต้องการและคืนชิ้นที่ไม่ต้องการโดยไม่เสียค่าใช้จ่าย "
                  "ค่าธรรมเนียมโปรแกรม 59 THB/ครั้ง (ฟรีสำหรับสมาชิก Prime Gold ขึ้นไป)", ST["Body"]),
        PageBreak(),
    ]

    # Page 6-7: โปรโมชัน
    story += [Paragraph("โปรโมชันและโปรแกรมสมาชิก StyleHub", ST["H1"])]
    story += [
        Paragraph("ระดับสมาชิก StyleHub", ST["H2"]),
    ]
    tiers = [["ระดับ","ยอดซื้อสะสม/ปี","ส่วนลด","ฟรีจัดส่ง","Try-Before-You-Buy","Cashback"],
             ["Basic","0-4,999 THB","5%","ขั้นต่ำ 800 THB","ไม่รวม","1%"],
             ["Silver","5,000-19,999 THB","10%","ขั้นต่ำ 500 THB","2 ครั้ง/เดือน","2%"],
             ["Gold","20,000-49,999 THB","15%","ทุกออเดอร์","ไม่จำกัด","3%"],
             ["Prime","50,000+ THB","20%","ทุกออเดอร์+Express","ไม่จำกัด (ฟรีค่าธรรมเนียม)","5%"]]
    tier_t = Table(tiers, colWidths=[2.5*cm,4*cm,2.5*cm,3.5*cm,4.5*cm,2*cm])
    tier_t.setStyle(header_style())
    story += [tier_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("รหัสโปรโมชันปัจจุบัน", ST["H2"]),
    ]
    promos = [["รหัส","ส่วนลด","เงื่อนไข","หมดอายุ"],
              ["STYLE11","11%","ทุกออเดอร์ขั้นต่ำ 1,000 THB","11 พ.ย. 2567"],
              ["NEWSTYLE","150 THB","ลูกค้าใหม่ ออเดอร์แรก ขั้นต่ำ 500 THB","ไม่มีวันหมด"],
              ["FASHIONDAY","20%","หมวดเสื้อผ้าสตรี ทุกวันศุกร์","ทุกวันศุกร์"],
              ["FREESHIP99","ฟรีค่าจัดส่ง","ขั้นต่ำ 299 THB วันจันทร์-อาทิตย์","31 ธ.ค. 2567"],
              ["PAYDAY15","15%","ทุกวันที่ 25-28 ของเดือน","สิ้นเดือนนั้น"]]
    promo_t = Table(promos, colWidths=[3*cm,3*cm,7*cm,4*cm])
    promo_t.setStyle(header_style())
    story += [promo_t, PageBreak()]

    # Page 8-9: จัดส่ง
    story += [Paragraph("นโยบายการจัดส่งสินค้า", ST["H1"])]
    shipping = [["โซน","พื้นที่","ราคา","เวลาจัดส่ง","Free Shipping"],
                ["Zone A","กรุงเทพฯ และปริมณฑล","40 THB","1-2 วัน","ขั้นต่ำ 800 THB"],
                ["Zone B","ต่างจังหวัดทั่วไทย","60 THB","2-4 วัน","ขั้นต่ำ 800 THB"],
                ["Zone C","เกาะ/ห่างไกล","100 THB","5-7 วัน","ไม่มีสิทธิ์ฟรี"],
                ["Express กทม.","บริการ Same-day (กทม.)","150 THB เพิ่ม","ภายในวันเดียวกัน (สั่งก่อน 13:00 น.)","ไม่ลดค่าบริการ"]]
    sh_t = Table(shipping, colWidths=[2.5*cm,4.5*cm,2.5*cm,4*cm,4.5*cm])
    sh_t.setStyle(header_style())
    story += [sh_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("บรรจุภัณฑ์และการดูแลสิ่งแวดล้อม", ST["H2"]),
        Paragraph("StyleHub มุ่งมั่นลดผลกระทบต่อสิ่งแวดล้อม โดยใช้กล่องจาก recycled paper 100% "
                  "และซองพลาสติกชีวภาพที่ย่อยสลายได้ภายใน 180 วัน ลูกค้าสามารถเลือก "
                  "'Green Packaging' ที่หน้า Checkout เพื่อรับ 50 StylePoints พิเศษ", ST["Body"]),
        PageBreak(),
    ]

    # Page 10-11: FAQ
    story += [Paragraph("คำถามที่พบบ่อย (FAQ)", ST["H1"])]
    faqs = [
        ("ตรวจสอบสถานะการสั่งซื้อได้อย่างไร?",
         "เข้าแอป StyleHub > My Orders หรือกดลิงก์ในอีเมลยืนยันการสั่งซื้อ สามารถ track real-time ได้ตลอด 24 ชั่วโมง"),
        ("ไซส์สินค้าไม่ตรงกับที่สั่ง ทำอย่างไร?",
         "แจ้งคืนสินค้าในแอปภายใน 30 วัน StyleHub จะจัดส่งสินค้าไซส์ที่ถูกต้องให้ฟรี หรือ Refund เต็มจำนวน"),
        ("สามารถสั่งซื้อสินค้าหลาย seller ในออเดอร์เดียวได้ไหม?",
         "ได้ StyleHub รวม Cart ให้ชำระครั้งเดียว แต่สินค้าจะถูกแยกจัดส่งจากแต่ละ seller และมีหมายเลข tracking แยกกัน"),
        ("StyleHub Wallet คืออะไร?",
         "กระเป๋าเงินดิจิทัลในแอป ใช้ชำระค่าสินค้า รับ Cashback และ Refund ยอดเงินใน Wallet ไม่หมดอายุ"),
        ("สินค้าลดราคา (Sale) คืนได้ไหม?",
         "ได้ภายใน 7 วัน (ไม่ใช่ 30 วัน) สินค้าที่ซื้อในราคา Flash Sale หรือมีป้าย Final Sale ไม่รับคืนทุกกรณี"),
        ("แบรนด์บน StyleHub เป็นของแท้ทั้งหมดไหม?",
         "ใช่ StyleHub ตรวจสอบ seller ทุกราย สินค้าจาก Official Brand Stores มีตรา 'StyleHub Verified' สามารถตรวจสอบ QR Code ได้"),
        ("รับชำระเงินช่องทางใดบ้าง?",
         "บัตรเครดิต/เดบิต Visa/Mastercard, PromptPay, ผ่อน 0% 6 เดือน (บัตรร่วมรายการ), TrueMoney, Rabbit LINE Pay, StyleHub Wallet"),
        ("StyleHub Prime สมัครอย่างไร?",
         "ระดับ Prime เป็นอัตโนมัติเมื่อยอดซื้อสะสมครบ 50,000 THB/ปี ไม่ต้องสมัครเพิ่มเติม"),
        ("สินค้า Pre-order ต้องรอนานแค่ไหน?",
         "สินค้า Pre-order ระบุวันจัดส่งประมาณในหน้าสินค้า โดยทั่วไป 14-45 วัน สามารถยกเลิกได้ก่อนวันจัดส่ง"),
        ("มี StyleHub ในรูปแบบเว็บไซต์หรือเฉพาะแอป?",
         "มีทั้งเว็บไซต์ www.stylehub.th และแอปมือถือ iOS/Android โดยแอปมีฟีเจอร์ AR try-on และ AI Size Recommendation เพิ่มเติม"),
    ]
    for i, (q,a) in enumerate(faqs, 1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]),
                  Paragraph(f"A: {a}", ST["Body"]),
                  Spacer(1,0.1*cm)]
        if i == 5: story.append(PageBreak())
    story.append(PageBreak())

    # Page 12: ติดต่อ
    story += [Paragraph("ช่องทางติดต่อและข้อกำหนด", ST["H1"])]
    contacts = [["ช่องทาง","รายละเอียด","เวลาทำการ"],
                ["LINE Official","@stylehub.th","ทุกวัน 08:00-22:00 น."],
                ["อีเมล","support@stylehub.th","ตอบภายใน 2 ชั่วโมง (วันทำการ)"],
                ["โทรศัพท์","02-xxx-7788","จ.-ศ. 09:00-18:00 น."],
                ["เว็บไซต์","www.stylehub.th","24/7"],
                ["Instagram","@StyleHubThailand","สอบถามแบรนด์และสินค้าใหม่"]]
    ct = Table(contacts, colWidths=[4*cm,8*cm,5*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [
        Paragraph("© 2567 StyleHub Thailand Co., Ltd. | เลขทะเบียน: 0105563012345 | "
                  "อัปเดต ณ วันที่ 1 พฤศจิกายน 2567", ST["Small"]),
    ]
    doc.build(story, onFirstPage=page_footer("StyleHub Thailand"), onLaterPages=page_footer("StyleHub Thailand"))
    print(f"  Created: {path}")


def build_stylehub_en(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1, 1.5*cm),
        Paragraph("StyleHub Thailand", ST["Title"]),
        Paragraph("Premier Online Fashion Marketplace — English Edition", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1, 0.5*cm),
        Paragraph("StyleHub Thailand, established in 2020, is Thailand's leading fashion e-commerce platform "
                  "hosting 500+ local and international brands with over 50,000 SKUs across apparel, bags, "
                  "footwear, jewelry and lifestyle products. Our AI-powered size recommendation engine and "
                  "try-before-you-buy program set us apart in Southeast Asia's fashion retail landscape.", ST["Body"]),
        Spacer(1, 0.5*cm),
        Paragraph("Table of Contents", ST["H1"]),
    ]
    toc = [["Section","Page"],
           ["Product Catalog and Brand Partners","2-3"],
           ["Return & Refund Policy","4-5"],
           ["Membership Program and Promotions","6-7"],
           ["Shipping and Fulfillment","8-9"],
           ["FAQ — Customer Support","10-11"],
           ["Contact and Legal","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("Product Catalog and Brand Partners", ST["H1"])]
    products = [
        ["SKU","Brand / Product Name","Category","Price (THB)","Member Price","Stock"],
        ["SH-2024-F001","LookBook Premium Dress","Women's Apparel","2,490","2,100","320 pcs"],
        ["SH-2024-F002","UrbanWear Streetwear Hoodie","Men's Apparel","1,890","1,600","450 pcs"],
        ["SH-2024-F003","LaMode Leather Tote Bag","Bags & Accessories","4,990","4,200","180 pcs"],
        ["SH-2024-F004","StepUp Running Shoes V2","Footwear","3,290","2,800","600 pcs"],
        ["SH-2024-F005","GlowUp Skincare Set (5 pcs)","Beauty","1,590","1,350","900 pcs"],
        ["SH-2024-F006","ChicStyle Silver Necklace","Jewelry","890","760","1,200 pcs"],
        ["SH-2024-F007","ActiveZone Sports Leggings","Sportswear","1,190","1,010","750 pcs"],
        ["SH-2024-F008","NaturalCraft Linen Shirt","Women's Apparel","1,490","1,270","510 pcs"],
        ["SH-2024-F009","MetroKid School Backpack","Bags","1,890","1,600","380 pcs"],
        ["SH-2024-F010","TrendWatch Analog Timepiece","Watches","5,990","5,100","200 pcs"],
    ]
    pt = Table(products, colWidths=[3*cm,5*cm,3*cm,2.5*cm,2.5*cm,2*cm])
    pt.setStyle(header_style())
    story += [pt, Spacer(1,0.3*cm)]
    story += [
        Paragraph("AI Size Recommendation System", ST["H2"]),
        Paragraph("StyleHub AI analyzes purchase history and 2M+ customer reviews to recommend the correct "
                  "size with 94.7% accuracy, reducing size-related returns by 62%. Setup via "
                  "StyleHub app > Profile > My Size Profile. Enter weight, height, and measurements.", ST["Body"]),
        Paragraph("Seller Standards", ST["H2"]),
        Paragraph("• All sellers undergo identity verification and product authentication review before listing", ST["Bullet"]),
        Paragraph("• Official Brand Stores carry 'StyleHub Verified' badge with QR-code authenticity check", ST["Bullet"]),
        Paragraph("• Seller performance score (≥4.5/5.0) required to maintain Featured Seller status", ST["Bullet"]),
        Paragraph("• StyleHub arbitrates all buyer-seller disputes within 3 business days", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Return and Refund Policy", ST["H1"])]
    story += [
        Paragraph("Return Window", ST["H2"]),
        Paragraph("Standard items: <b>30 days</b> from delivery date. Sale/discounted items: <b>7 days</b>. "
                  "Flash Sale / Final Sale items: <b>no returns accepted</b> unless manufacturing defect.", ST["Body"]),
        Paragraph("Return Eligibility Requirements", ST["H2"]),
        Paragraph("• Item unused, original tags attached, undamaged packaging", ST["Bullet"]),
        Paragraph("• Proof of purchase (Order ID or receipt)", ST["Bullet"]),
        Paragraph("• Underwear, swimwear, earrings excluded for hygiene reasons", ST["Bullet"]),
    ]
    steps = [["Step","Action","Timeline"],
             ["1. Submit Request","In-app: My Orders > Select Order > Return Item. Attach photos.","Immediately"],
             ["2. Approval Review","Support team reviews within 1 business day","1 business day"],
             ["3. Return Label","StyleHub sends QR code for drop-off at J&T/Kerry partner points","After approval"],
             ["4. Ship Item","Drop off at partner point or schedule home pickup (BKK only)","Within 5 days"],
             ["5. Refund Issued","Refund to original payment method or StyleHub Wallet","5-10 business days"]]
    st_t = Table(steps, colWidths=[3*cm,11*cm,3*cm])
    st_t.setStyle(header_style())
    story += [st_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Refund Methods", ST["H2"]),
        Paragraph("• Credit/Debit Card: 7-14 business days (bank processing time)", ST["Bullet"]),
        Paragraph("• StyleHub Wallet: within 24 hours + 5% bonus credit", ST["Bullet"]),
        Paragraph("• Bank Transfer: 5 business days, provide account details in return form", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Membership Program and Promotions", ST["H1"])]
    tiers = [["Tier","Annual Spend","Discount","Free Shipping","Try-Before-You-Buy","Cashback"],
             ["Basic","THB 0-4,999","5%","Min. 800 THB","Not included","1%"],
             ["Silver","THB 5,000-19,999","10%","Min. 500 THB","2x/month","2%"],
             ["Gold","THB 20,000-49,999","15%","All orders","Unlimited","3%"],
             ["Prime","THB 50,000+","20%","All + Express","Unlimited (fee waived)","5%"]]
    tier_t = Table(tiers, colWidths=[2.5*cm,4*cm,2.5*cm,3.5*cm,4.5*cm,2*cm])
    tier_t.setStyle(header_style())
    story += [tier_t, Spacer(1,0.3*cm)]
    promos = [["Code","Discount","Conditions","Expiry"],
              ["STYLE11","11% off","All orders ≥ 1,000 THB","11 Nov 2024"],
              ["NEWSTYLE","150 THB off","New customers, first order ≥ 500 THB","No expiry"],
              ["FASHIONDAY","20% off","Women's apparel every Friday","Every Friday"],
              ["FREESHIP99","Free shipping","Orders ≥ 299 THB, any day","31 Dec 2024"],
              ["PAYDAY15","15% off","25th-28th of every month","End of month"]]
    promo_t = Table(promos, colWidths=[3*cm,3*cm,7*cm,4*cm])
    promo_t.setStyle(header_style())
    story += [promo_t, PageBreak()]

    story += [Paragraph("Shipping and Fulfillment", ST["H1"])]
    shipping = [["Zone","Area","Rate","Delivery","Free Threshold"],
                ["Zone A","Bangkok & Greater BKK","40 THB","1-2 days","800 THB"],
                ["Zone B","Upcountry Thailand","60 THB","2-4 days","800 THB"],
                ["Zone C","Islands / Remote","100 THB","5-7 days","Not eligible"],
                ["Same-day","Bangkok only (+150 THB)","190 THB total","Same day (order before 13:00)","Not discountable"]]
    sh_t = Table(shipping, colWidths=[2*cm,4.5*cm,2.5*cm,4*cm,4*cm])
    sh_t.setStyle(header_style())
    story += [sh_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Sustainable Packaging", ST["H2"]),
        Paragraph("StyleHub uses 100% recycled cardboard boxes and biodegradable poly bags (180-day degradation). "
                  "Select 'Green Packaging' at checkout to earn 50 bonus StylePoints.", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("Frequently Asked Questions", ST["H1"])]
    faqs = [
        ("How do I track my order?","Open StyleHub app > My Orders, or click the tracking link in your confirmation email. Real-time tracking is available 24/7."),
        ("What if the size doesn't fit?","Submit a return within 30 days. StyleHub will ship the correct size for free or issue a full refund."),
        ("Can I buy from multiple sellers in one order?","Yes. StyleHub consolidates checkout but ships separately per seller with individual tracking numbers."),
        ("What is StyleHub Wallet?","A digital wallet within the app for payments, cashback, and refunds. Balance never expires."),
        ("Can I return Sale items?","Yes, within 7 days (not 30). Flash Sale / Final Sale items are non-returnable unless defective."),
        ("Are all products genuine?","Yes. Every seller is verified. Products from Official Brand Stores carry a 'StyleHub Verified' badge with QR authentication."),
        ("What payment methods are accepted?","Visa/Mastercard credit/debit, PromptPay, 0% installment 6 months (participating cards), TrueMoney, Rabbit LINE Pay, StyleHub Wallet."),
        ("How do I reach Prime membership?","Prime status is automatically granted when cumulative annual spend reaches 50,000 THB. No separate application needed."),
        ("How long do Pre-order items take?","Estimated ship dates are shown on each product page, typically 14-45 days. Cancellation allowed before ship date."),
        ("Is there a website version?","Yes: www.stylehub.th. The mobile app (iOS/Android) additionally offers AR try-on and AI size recommendation."),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
        if i == 5: story.append(PageBreak())
    story.append(PageBreak())

    story += [Paragraph("Contact and Legal", ST["H1"])]
    contacts = [["Channel","Details","Hours"],
                ["LINE Official","@stylehub.th","Daily 08:00-22:00 ICT"],
                ["Email","support@stylehub.th","Response < 2 business hours"],
                ["Phone","02-xxx-7788","Mon-Fri 09:00-18:00 ICT"],
                ["Website","www.stylehub.th","24/7"],
                ["Instagram","@StyleHubThailand","Brand & new arrivals enquiries"]]
    ct = Table(contacts, colWidths=[4*cm,8*cm,5*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [
        Paragraph("© 2024 StyleHub Thailand Co., Ltd. | Reg. No. 0105563012345 | "
                  "Document SH-EN-2024-v1.2 | Updated: November 1, 2024", ST["Small"]),
    ]
    doc.build(story, onFirstPage=page_footer("StyleHub Thailand"), onLaterPages=page_footer("StyleHub Thailand"))
    print(f"  Created: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# E-COMMERCE SET 2: TechMart TH (ตลาดอิเล็กทรอนิกส์มือสองและใหม่)
# ═══════════════════════════════════════════════════════════════════════════════

def build_techmart_th(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("TechMart TH", ST["Title"]),
        Paragraph("ตลาดออนไลน์อิเล็กทรอนิกส์และสมาร์ทโฟน", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("TechMart TH ก่อตั้งปี 2561 เป็นแพลตฟอร์ม C2C และ B2C ด้านอิเล็กทรอนิกส์ "
                  "สมาร์ทโฟน แล็ปท็อป เครื่องใช้ไฟฟ้า ทั้งสินค้าใหม่และมือสอง มีผู้ใช้งาน 4.5 ล้านคน "
                  "และ seller กว่า 80,000 ร้าน ระบบตรวจสอบคุณภาพสินค้ามือสองด้วย AI grading", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("สารบัญ", ST["H1"]),
    ]
    toc = [["หัวข้อ","หน้า"],
           ["ประเภทสินค้าและนโยบาย Seller","2-3"],
           ["ระบบ Grading มือสอง","4"],
           ["ค่าธรรมเนียมและนโยบาย Seller","5-6"],
           ["นโยบายผู้ซื้อและการคุ้มครอง","7-8"],
           ["นโยบายการจัดส่ง","9-10"],
           ["FAQ และช่องทางติดต่อ","11-12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("ประเภทสินค้าและหมวดหมู่หลัก", ST["H1"])]
    cats = [["หมวดหมู่","สินค้าตัวอย่าง","ยอดขาย/เดือน","ค่าธรรมเนียม Seller"],
            ["สมาร์ทโฟน","iPhone 15, Samsung Galaxy S24, OPPO Reno","85,000 รายการ","3.5%"],
            ["แล็ปท็อป","MacBook Air M2, Dell XPS 15, Asus ROG","32,000 รายการ","3.0%"],
            ["หูฟัง","AirPods Pro 2, Sony WH-1000XM5, JBL","120,000 รายการ","4.0%"],
            ["กล้อง","Sony Alpha, Canon EOS R, DJI Drone","18,000 รายการ","3.5%"],
            ["เครื่องใช้ไฟฟ้า","ไมโครเวฟ ตู้เย็น เครื่องซักผ้า","41,000 รายการ","4.5%"],
            ["อะไหล่/อุปกรณ์เสริม","เคส ฟิล์ม สายชาร์จ","500,000 รายการ","5.0%"],
            ["Gaming","PS5, Xbox Series X, Nintendo Switch","22,000 รายการ","3.5%"],
            ["Smart Home","Smart TV, Projector, Speaker","55,000 รายการ","4.0%"]]
    ct = Table(cats, colWidths=[4*cm,7*cm,3*cm,3*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.3*cm)]
    story += [
        Paragraph("สินค้าเด่นประจำเดือนพฤศจิกายน 2567", ST["H2"]),
        Paragraph("• iPhone 15 Pro 256GB (มือสองเกรด A) — ราคาเฉลี่ยบนแพลตฟอร์ม 32,500 THB (ราคาใหม่ 41,900 THB)", ST["Bullet"]),
        Paragraph("• MacBook Air M2 13\" 8GB/256GB (มือสองเกรด A+) — เฉลี่ย 28,000 THB", ST["Bullet"]),
        Paragraph("• Sony WH-1000XM5 ใหม่ — เฉลี่ย 9,200 THB (ราคา official 10,990 THB)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("ระบบ TechMart Grading สินค้ามือสอง", ST["H1"])]
    story += [
        Paragraph("TechMart ใช้ระบบ AI-assisted grading ร่วมกับการตรวจสอบโดย technician "
                  "เพื่อประเมินสภาพสินค้ามือสองด้วยมาตรฐานเดียวกัน", ST["Body"]),
    ]
    grades = [["เกรด","ชื่อ","สภาพ","รับประกัน TechMart","ส่วนลดเทียบราคาใหม่"],
              ["A+","Like New","ไม่มีรอยใดๆ เหมือนใหม่ 100%","90 วัน","15-25%"],
              ["A","Excellent","รอยขีดข่วนเล็กน้อยมาก ไม่เห็นในระยะ 30 ซม.","90 วัน","25-35%"],
              ["B","Good","รอยขีดข่วนเล็กน้อยที่มองเห็นได้ แต่ไม่กระทบการใช้งาน","30 วัน","35-50%"],
              ["C","Fair","รอยขีดข่วนชัดเจน หน้าจออาจมีรอย แต่ฟังก์ชันสมบูรณ์","7 วัน","50-65%"],
              ["D","Parts Only","ชำรุดบางส่วน ขายเพื่อ repair/อะไหล่","ไม่มี","65%+"]]
    g_t = Table(grades, colWidths=[2*cm,3*cm,6*cm,3*cm,3*cm])
    g_t.setStyle(header_style())
    story += [g_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("กระบวนการ Grading", ST["H2"]),
        Paragraph("1. Seller ส่งสินค้าไปยัง TechMart Inspection Center (กทม./เชียงใหม่/ขอนแก่น/หาดใหญ่)", ST["Bullet"]),
        Paragraph("2. AI Scan ตรวจสอบหน้าจอ body ด้วย computer vision 48 จุด ใช้เวลา 3 นาที", ST["Bullet"]),
        Paragraph("3. Technician ตรวจสอบระบบไฟฟ้า battery health แบตเตอรี่ต้องไม่ต่ำกว่า 80%", ST["Bullet"]),
        Paragraph("4. ทดสอบฟังก์ชันทั้งหมด: กล้อง ลำโพง ไมค์ ปุ่มทุกปุ่ม พอร์ตชาร์จ", ST["Bullet"]),
        Paragraph("5. ออกใบรับรอง TechMart Certified Grade พร้อมรูปถ่าย 360 องศา", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("ค่าธรรมเนียมและนโยบาย Seller", ST["H1"])]
    fees = [["ประเภทค่าธรรมเนียม","อัตรา","เงื่อนไข"],
            ["Commission Fee","3.0-5.0%","คิดจากราคาขาย ตามหมวดหมู่สินค้า"],
            ["Payment Processing","1.5%","ทุกการชำระเงิน ทุกช่องทาง"],
            ["TechMart Mall (Official Store)","2.0% + 1,500 THB/เดือน","สำหรับ brand official store"],
            ["Featured Listing","200-500 THB/รายการ/สัปดาห์","เพิ่มการมองเห็น"],
            ["Inspection Service (มือสอง)","150-300 THB/ชิ้น","สำหรับสินค้ามูลค่าสูง optional"],
            ["Withdrawal Fee","ฟรี (โอน >5,000 THB)","<5,000 THB: 25 THB/ครั้ง"]]
    f_t = Table(fees, colWidths=[5*cm,4*cm,8*cm])
    f_t.setStyle(header_style())
    story += [f_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("กฎระเบียบ Seller", ST["H2"]),
        Paragraph("• Seller ต้องส่งสินค้าภายใน 2 วันทำการหลังได้รับคำสั่งซื้อ", ST["Bullet"]),
        Paragraph("• คะแนน Seller ต่ำกว่า 4.0/5.0 ติดต่อกัน 30 วัน จะถูก suspend ชั่วคราว", ST["Bullet"]),
        Paragraph("• สินค้าลอกเลียนแบบ/ของปลอม: บัญชีถูกปิดถาวรและแจ้งดำเนินการทางกฎหมาย", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("นโยบายผู้ซื้อและการคุ้มครอง TechMart Buyer Protect", ST["H1"])]
    story += [
        Paragraph("TechMart Buyer Protect คุ้มครองทุกการซื้อขายบนแพลตฟอร์มในกรณีต่อไปนี้:", ST["Body"]),
        Paragraph("• สินค้าไม่ได้รับภายใน 10 วันหลังยืนยันการจัดส่ง", ST["Bullet"]),
        Paragraph("• สินค้าได้รับแตกต่างจากคำอธิบายอย่างมีนัยสำคัญ", ST["Bullet"]),
        Paragraph("• สินค้าได้รับชำรุดจากการขนส่ง (แจ้งภายใน 48 ชั่วโมงหลังรับสินค้า)", ST["Bullet"]),
        Paragraph("• สินค้ามือสองเกรดไม่ตรงกับที่ระบุ (TechMart Certified เท่านั้น)", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("ขั้นตอนการยื่น Dispute", ST["H2"]),
        Paragraph("1. แอป TechMart > คำสั่งซื้อ > Dispute > แนบหลักฐาน (รูปภาพ/วิดีโอ)", ST["Bullet"]),
        Paragraph("2. Seller มีเวลา 48 ชั่วโมงตอบกลับ ถ้าไม่ตอบ TechMart อนุมัติ Refund อัตโนมัติ", ST["Bullet"]),
        Paragraph("3. ถ้าทั้งสองฝ่ายตกลงกันไม่ได้ TechMart Mediator ตัดสินภายใน 3 วันทำการ", ST["Bullet"]),
        Paragraph("4. Refund ผ่าน TechMart Wallet ภายใน 24 ชั่วโมง หรือคืนช่องทางเดิม 5-7 วัน", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("นโยบายการจัดส่งสินค้า", ST["H1"])]
    shipping = [["พาร์ทเนอร์","ประเภทสินค้า","อัตราค่าจัดส่ง","เวลาจัดส่ง"],
                ["J&T Express","ทั่วไป <5kg","ตามน้ำหนัก (40-150 THB)","2-4 วัน"],
                ["Kerry Express","สินค้ามูลค่าสูง","ตามน้ำหนัก (50-200 THB)","2-3 วัน"],
                ["Flash Express","กทม.เร่งด่วน","เพิ่ม 80 THB","ภายใน 4 ชม. (กทม.)"],
                ["TechMart Logistics","สินค้าขนาดใหญ่ (>10kg)","คำนวณพิเศษ","3-7 วัน"],
                ["SCG Express","ขนส่งเฟอร์นิเจอร์/เครื่องใช้ไฟฟ้าใหญ่","คำนวณตามขนาด","5-10 วัน"]]
    sh_t = Table(shipping, colWidths=[3.5*cm,4.5*cm,4*cm,5*cm])
    sh_t.setStyle(header_style())
    story += [sh_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("ประกันสินค้าระหว่างขนส่ง", ST["H2"]),
        Paragraph("สินค้าทุกชิ้นมีประกันขนส่งสูงสุด 5,000 THB โดยอัตโนมัติ สำหรับสินค้ามูลค่าสูงกว่า "
                  "5,000 THB สามารถซื้อประกันเพิ่มได้ที่ 0.5% ของมูลค่าสินค้า (ขั้นต่ำ 30 THB)", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("คำถามที่พบบ่อย (FAQ)", ST["H1"])]
    faqs = [
        ("สินค้ามือสองมีการรับประกันไหม?","TechMart Certified Grade A+ และ A มีรับประกัน 90 วัน Grade B รับประกัน 30 วัน Grade C รับประกัน 7 วัน Grade D ไม่มีรับประกัน"),
        ("ทำไม Seller บางรายส่งช้า?","แต่ละ Seller มีกำหนดส่งสินค้าภายใน 2 วันทำการ ถ้า Seller ส่งช้าเกิน 5 วัน ระบบจะยกเลิกออเดอร์และ Refund อัตโนมัติ"),
        ("Battery Health ต่ำกว่า 80% ขายได้ไหม?","ไม่ได้สำหรับสินค้า TechMart Certified อย่างไรก็ตาม Seller ทั่วไปสามารถขายได้แต่ต้องระบุข้อมูล Battery Health ครบถ้วน"),
        ("ชำระเงินผ่าน QR Code หรือบัตรเครดิตได้ไหม?","รับชำระ: PromptPay QR, บัตรเครดิต/เดบิต, TrueMoney, TechMart Wallet, ผ่อน 0% 10 เดือน (Kbank/SCB/KRUNGTHAI)"),
        ("สินค้าที่ซื้อไปแล้วเปลี่ยนรุ่นได้ไหม?","ไม่สามารถเปลี่ยนรุ่นได้ ต้องคืนสินค้าก่อน แล้วสั่งซื้อรุ่นใหม่"),
        ("Seller ส่งสินค้าที่ไม่ตรงสเปค ทำอย่างไร?","เปิด Dispute ในแอปภายใน 7 วัน แนบรูปภาพเปรียบเทียบ TechMart Buyer Protect จะคืนเงิน 100%"),
        ("TechMart Mall คืออะไร?","Official Brand Store บนแพลตฟอร์ม มีการตรวจสอบสินค้าแท้ มีป้าย Official สีน้ำเงิน มีประกันศูนย์บริการเต็มรูปแบบ"),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("ช่องทางติดต่อ TechMart TH", ST["H1"])]
    contacts = [["ช่องทาง","รายละเอียด","เวลาทำการ"],
                ["LINE","@techmart.th","ทุกวัน 08:00-22:00 น."],
                ["อีเมล","support@techmart.th","ตอบภายใน 3 ชั่วโมง"],
                ["โทรศัพท์","02-xxx-9900","จ.-ศ. 09:00-18:00 น."],
                ["Seller Support","seller@techmart.th","จ.-ศ. 09:00-17:00 น."],
                ["เว็บไซต์","www.techmart.th","24/7"]]
    ct = Table(contacts, colWidths=[4*cm,7*cm,6*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [Paragraph("© 2567 TechMart TH Co., Ltd. | เลขทะเบียน: 0105561098765 | อัปเดต 1 พ.ย. 2567", ST["Small"])]
    doc.build(story, onFirstPage=page_footer("TechMart TH"), onLaterPages=page_footer("TechMart TH"))
    print(f"  Created: {path}")


def build_techmart_en(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("TechMart TH", ST["Title"]),
        Paragraph("Thailand's Electronics & Smartphone Marketplace — English Edition", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("TechMart TH, founded in 2018, is Thailand's premier C2C and B2C electronics marketplace "
                  "covering smartphones, laptops, electronics, and accessories — both new and pre-owned. "
                  "With 4.5M users and 80,000+ sellers, TechMart's AI grading system sets the standard "
                  "for pre-owned device quality in Southeast Asia.", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("Table of Contents", ST["H1"]),
    ]
    toc = [["Section","Page"],
           ["Product Categories and Seller Policy","2-3"],
           ["TechMart Grading System","4"],
           ["Seller Fees and Regulations","5-6"],
           ["Buyer Protection Policy","7-8"],
           ["Shipping Policy","9-10"],
           ["FAQ and Contact","11-12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("Product Categories", ST["H1"])]
    cats = [["Category","Example Products","Monthly Volume","Seller Commission"],
            ["Smartphones","iPhone 15, Samsung S24, OPPO Reno","85,000 listings","3.5%"],
            ["Laptops","MacBook Air M2, Dell XPS 15, Asus ROG","32,000 listings","3.0%"],
            ["Headphones","AirPods Pro 2, Sony WH-1000XM5","120,000 listings","4.0%"],
            ["Cameras","Sony Alpha, Canon EOS R, DJI Drone","18,000 listings","3.5%"],
            ["Appliances","Microwave, Refrigerator, Washer","41,000 listings","4.5%"],
            ["Accessories","Cases, films, cables, chargers","500,000 listings","5.0%"],
            ["Gaming","PS5, Xbox Series X, Nintendo Switch","22,000 listings","3.5%"],
            ["Smart Home","Smart TV, Projector, Speaker","55,000 listings","4.0%"]]
    ct = Table(cats, colWidths=[4*cm,6*cm,3*cm,4*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Top Deals — November 2024", ST["H2"]),
        Paragraph("• iPhone 15 Pro 256GB (Pre-owned Grade A) — avg. THB 32,500 (new: THB 41,900)", ST["Bullet"]),
        Paragraph("• MacBook Air M2 13\" 8GB/256GB (Pre-owned Grade A+) — avg. THB 28,000", ST["Bullet"]),
        Paragraph("• Sony WH-1000XM5 (New) — avg. THB 9,200 (official retail: THB 10,990)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("TechMart Grading System (Pre-owned Devices)", ST["H1"])]
    story += [Paragraph("TechMart employs AI-assisted grading combined with certified technician inspection "
                        "to ensure consistent quality standards across all pre-owned listings.", ST["Body"])]
    grades = [["Grade","Label","Condition","TechMart Warranty","Discount vs New"],
              ["A+","Like New","No marks whatsoever, 100% like new","90 days","15-25%"],
              ["A","Excellent","Micro-scratches only, invisible at 30 cm","90 days","25-35%"],
              ["B","Good","Minor visible scratches, full functionality","30 days","35-50%"],
              ["C","Fair","Visible scratches, screen may have marks, fully functional","7 days","50-65%"],
              ["D","Parts Only","Partially defective, sold for repair/parts","None","65%+"]]
    g_t = Table(grades, colWidths=[2*cm,2.5*cm,6*cm,3*cm,3.5*cm])
    g_t.setStyle(header_style())
    story += [g_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Grading Process", ST["H2"]),
        Paragraph("1. Seller ships device to TechMart Inspection Center (Bangkok/Chiang Mai/Khon Kaen/Hat Yai)", ST["Bullet"]),
        Paragraph("2. AI scan inspects screen and body at 48 checkpoints via computer vision (3 min)", ST["Bullet"]),
        Paragraph("3. Technician checks electrical system; battery health must be ≥80%", ST["Bullet"]),
        Paragraph("4. Full functional test: camera, speakers, mic, buttons, charging port", ST["Bullet"]),
        Paragraph("5. TechMart Certified Grade certificate issued with 360° photo documentation", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Seller Fees and Regulations", ST["H1"])]
    fees = [["Fee Type","Rate","Notes"],
            ["Commission Fee","3.0-5.0%","Based on selling price, varies by category"],
            ["Payment Processing","1.5%","Applied to all transactions, all payment methods"],
            ["TechMart Mall (Official Store)","2.0% + THB 1,500/mo","For brand official stores only"],
            ["Featured Listing","THB 200-500/listing/week","Boosts search visibility"],
            ["Inspection Service (pre-owned)","THB 150-300/item","For high-value items, optional"],
            ["Withdrawal Fee","Free (>THB 5,000)","<THB 5,000: THB 25/transaction"]]
    f_t = Table(fees, colWidths=[5*cm,4*cm,8*cm])
    f_t.setStyle(header_style())
    story += [f_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Seller Rules", ST["H2"]),
        Paragraph("• Sellers must ship within 2 business days of order confirmation", ST["Bullet"]),
        Paragraph("• Seller score below 4.0/5.0 for 30 consecutive days triggers temporary suspension", ST["Bullet"]),
        Paragraph("• Counterfeit listings: permanent account ban and legal referral", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Buyer Protection — TechMart Buyer Protect", ST["H1"])]
    story += [
        Paragraph("TechMart Buyer Protect covers all platform transactions in these cases:", ST["Body"]),
        Paragraph("• Item not received within 10 days of confirmed dispatch", ST["Bullet"]),
        Paragraph("• Item significantly different from listing description", ST["Bullet"]),
        Paragraph("• Item arrived damaged in transit (report within 48 hours of delivery)", ST["Bullet"]),
        Paragraph("• TechMart Certified pre-owned item does not match stated grade", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("Dispute Process", ST["H2"]),
        Paragraph("1. TechMart app > Orders > Dispute > submit evidence (photos/video)", ST["Bullet"]),
        Paragraph("2. Seller has 48 hours to respond; no response triggers automatic refund", ST["Bullet"]),
        Paragraph("3. If unresolved, TechMart Mediator rules within 3 business days", ST["Bullet"]),
        Paragraph("4. Refund via TechMart Wallet within 24 hours, or original method in 5-7 days", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Shipping Policy", ST["H1"])]
    shipping = [["Partner","Item Type","Rate","Delivery Time"],
                ["J&T Express","General items <5kg","By weight (THB 40-150)","2-4 days"],
                ["Kerry Express","High-value items","By weight (THB 50-200)","2-3 days"],
                ["Flash Express","Bangkok urgent","+THB 80 surcharge","Within 4 hrs (BKK)"],
                ["TechMart Logistics","Large items >10kg","Custom quote","3-7 days"],
                ["SCG Express","Large appliances/furniture","Volume-based","5-10 days"]]
    sh_t = Table(shipping, colWidths=[3.5*cm,4.5*cm,4*cm,5*cm])
    sh_t.setStyle(header_style())
    story += [sh_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Shipping Insurance", ST["H2"]),
        Paragraph("All items include automatic shipping insurance up to THB 5,000. "
                  "For items valued above THB 5,000, additional coverage is available at 0.5% of item value (min. THB 30).", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("Frequently Asked Questions", ST["H1"])]
    faqs = [
        ("Do pre-owned items come with a warranty?","TechMart Certified Grade A+ and A: 90 days. Grade B: 30 days. Grade C: 7 days. Grade D: no warranty."),
        ("Why do some sellers ship late?","All sellers must ship within 2 business days. If a seller fails to ship within 5 days, the order is automatically cancelled and refunded."),
        ("Can a device with battery health below 80% be sold?","No for TechMart Certified listings. However, regular sellers may list such devices provided battery health is clearly disclosed."),
        ("What payment methods are accepted?","PromptPay QR, Visa/Mastercard credit/debit, TrueMoney, TechMart Wallet, 0% installment 10 months (Kbank/SCB/Krungthai)."),
        ("Can I exchange for a different model after purchase?","No. Return the item first, then place a new order for the desired model."),
        ("Seller sent the wrong spec — what do I do?","Open a Dispute in the app within 7 days with comparison photos. TechMart Buyer Protect will issue a 100% refund."),
        ("What is TechMart Mall?","Official Brand Stores verified for genuine products, marked with a blue Official badge, with full manufacturer warranty support."),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("Contact TechMart TH", ST["H1"])]
    contacts = [["Channel","Details","Hours"],
                ["LINE","@techmart.th","Daily 08:00-22:00 ICT"],
                ["Email","support@techmart.th","Response < 3 hours"],
                ["Phone","02-xxx-9900","Mon-Fri 09:00-18:00 ICT"],
                ["Seller Support","seller@techmart.th","Mon-Fri 09:00-17:00 ICT"],
                ["Website","www.techmart.th","24/7"]]
    ct = Table(contacts, colWidths=[4*cm,7*cm,6*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [Paragraph("© 2024 TechMart TH Co., Ltd. | Reg. No. 0105561098765 | Updated: Nov 1, 2024", ST["Small"])]
    doc.build(story, onFirstPage=page_footer("TechMart TH"), onLaterPages=page_footer("TechMart TH"))
    print(f"  Created: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# LEGAL: Krung Thai Legal Associates
# ═══════════════════════════════════════════════════════════════════════════════

def build_legal_th(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("กรุงไทยลีกัล แอสโซซิเอทส์", ST["Title"]),
        Paragraph("สำนักงานกฎหมายชั้นนำ — เอกสารบริการและข้อกำหนด", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("กรุงไทยลีกัล แอสโซซิเอทส์ ก่อตั้งปี 2540 เชี่ยวชาญด้านกฎหมายธุรกิจ อสังหาริมทรัพย์ "
                  "แรงงาน และการระงับข้อพิพาท ด้วยทีมทนายความกว่า 45 คน รับรองโดยสภาทนายความแห่งประเทศไทย "
                  "มีสาขาในกรุงเทพฯ เชียงใหม่ ระยอง และสงขลา", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("สารบัญ", ST["H1"]),
    ]
    toc = [["หัวข้อ","หน้า"],
           ["บริการกฎหมายและอัตราค่าบริการ","2-3"],
           ["เงื่อนไขการว่าจ้างทนายความ","4-5"],
           ["นโยบายการรักษาความลับ","6-7"],
           ["กระบวนการรับคดีและขั้นตอน","8-9"],
           ["FAQ กฎหมายทั่วไป","10-11"],
           ["ช่องทางติดต่อและสาขา","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("บริการกฎหมายและอัตราค่าบริการ", ST["H1"])]
    services = [["สาขากฎหมาย","บริการ","ค่าบริการเริ่มต้น","หมายเหตุ"],
                ["กฎหมายธุรกิจ","จดทะเบียนบริษัท/ร่างสัญญา/M&A","15,000 THB","ขึ้นอยู่กับความซับซ้อน"],
                ["อสังหาริมทรัพย์","โอนกรรมสิทธิ์/ตรวจสอบโฉนด/ซื้อขาย","8,000 THB","ต่อรายการ"],
                ["กฎหมายแรงงาน","คดีเลิกจ้าง/ร่างสัญญาจ้าง/นายจ้าง","12,000 THB","ต่อคดี"],
                ["ทรัพย์สินทางปัญญา","จดทะเบียนเครื่องหมายการค้า/ลิขสิทธิ์","10,000 THB","ต่อประเภท"],
                ["กฎหมายครอบครัว","หย่า/มรดก/ควบคุมดูแลบุตร","20,000 THB","ต่อคดี"],
                ["อนุญาโตตุลาการ","ไกล่เกลี่ย/อนุญาโตตุลาการ","25,000 THB","ต่อวัน"],
                ["กฎหมายอาญา","ต่อสู้คดีอาญา/ประกันตัว","35,000 THB","ขึ้นต้น"],
                ["กฎหมาย BOI/FDI","ขอใบอนุญาต BOI/FDI","30,000 THB","ต่อโครงการ"]]
    sv_t = Table(services, colWidths=[4*cm,5*cm,3.5*cm,4.5*cm])
    sv_t.setStyle(header_style())
    story += [sv_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("อัตราค่าบริการที่ปรึกษากฎหมาย", ST["H2"]),
        Paragraph("• ที่ปรึกษาด่วน (30 นาที): 1,500 THB — สำหรับปรึกษาทั่วไป ไม่รวมการดำเนินคดี", ST["Bullet"]),
        Paragraph("• ที่ปรึกษารายเดือน (Retainer): 15,000-50,000 THB/เดือน — ชั่วโมงที่ปรึกษา 10-40 ชั่วโมง", ST["Bullet"]),
        Paragraph("• ค่าธรรมเนียมชนะคดี (Contingency): 15-25% ของทุนทรัพย์ที่ได้ (เฉพาะบางประเภทคดี)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("เงื่อนไขการว่าจ้าง (Engagement Terms)", ST["H1"])]
    story += [
        Paragraph("1. การทำสัญญาจ้าง", ST["H2"]),
        Paragraph("ลูกค้าทุกรายต้องลงนาม Engagement Letter ก่อนเริ่มดำเนินการทางกฎหมาย โดยระบุ: "
                  "ขอบเขตงาน (Scope of Work), ค่าธรรมเนียม, เงื่อนไขการชำระเงิน และระยะเวลาสัญญา", ST["Body"]),
        Paragraph("2. การชำระค่าธรรมเนียม", ST["H2"]),
        Paragraph("• คดีใหม่: ชำระล่วงหน้า 50% เมื่อลงนาม Engagement Letter ส่วนที่เหลือเมื่อสิ้นสุดงาน", ST["Bullet"]),
        Paragraph("• งานที่ปรึกษา Retainer: ชำระรายเดือนล่วงหน้า ภายในวันที่ 5 ของแต่ละเดือน", ST["Bullet"]),
        Paragraph("• ค่าใช้จ่ายพิเศษ (ค่าคัดสำเนา ค่าธรรมเนียมศาล): เรียกเก็บแยกพร้อมใบเสร็จ", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("3. การยกเลิกสัญญา", ST["H2"]),
        Paragraph("• ลูกค้ายกเลิกก่อนเริ่มงาน: คืน 80% ของเงินมัดจำ", ST["Bullet"]),
        Paragraph("• ยกเลิกระหว่างดำเนินการ: คิดค่าบริการตามสัดส่วนงานที่ทำเสร็จแล้ว ไม่คืนเงินส่วนที่เกิน", ST["Bullet"]),
        Paragraph("• สำนักงานสงวนสิทธิ์ปฏิเสธหรือถอนตัวจากคดีที่มีผลประโยชน์ทับซ้อน", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("4. Conflict of Interest Policy", ST["H2"]),
        Paragraph("กรุงไทยลีกัลตรวจสอบ Conflict of Interest ทุกรายก่อนรับคดี "
                  "หากพบว่ามีผลประโยชน์ทับซ้อน สำนักงานจะแจ้งลูกค้าทันทีและแนะนำสำนักงานกฎหมายอื่น", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("นโยบายการรักษาความลับ (Confidentiality)", ST["H1"])]
    story += [
        Paragraph("หลักการ Attorney-Client Privilege", ST["H2"]),
        Paragraph("ข้อมูลทุกอย่างที่ลูกค้าเปิดเผยแก่ทนายความถือเป็น privileged communication "
                  "ซึ่งได้รับความคุ้มครองตามกฎหมายและจริยธรรมวิชาชีพ กรุงไทยลีกัลจะไม่เปิดเผยข้อมูล "
                  "ของลูกค้าต่อบุคคลภายนอกโดยเด็ดขาด ยกเว้นกรณีต่อไปนี้:", ST["Body"]),
        Paragraph("• ลูกค้าให้ความยินยอมเป็นลายลักษณ์อักษร", ST["Bullet"]),
        Paragraph("• คำสั่งศาลที่มีผลบังคับตามกฎหมาย", ST["Bullet"]),
        Paragraph("• กรณีที่จำเป็นเพื่อป้องกันอาชญากรรมที่กำลังจะเกิดขึ้นหรือความเสียหายร้ายแรง", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("การจัดเก็บข้อมูล", ST["H2"]),
        Paragraph("เอกสารลูกค้าจัดเก็บในระบบ Cloud ที่เข้ารหัส AES-256 บน AWS ap-southeast-1 "
                  "สิทธิ์เข้าถึงจำกัดเฉพาะทนายความที่รับผิดชอบคดีเท่านั้น เอกสารฟิสิคัลเก็บใน "
                  "safe ล็อคในห้องที่ควบคุมการเข้าถึง ระยะเก็บรักษา: 10 ปีหลังสิ้นสุดคดี", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("กระบวนการรับคดีและขั้นตอนการทำงาน", ST["H1"])]
    process = [["ขั้นตอน","รายละเอียด","ระยะเวลา"],
               ["1. ปรึกษาเบื้องต้น","นัดหมายทนายความ ประเมินคดี และรับคำแนะนำเบื้องต้น","30-60 นาที"],
               ["2. ตรวจสอบคดี","ทนายความวิเคราะห์ข้อเท็จจริงและกฎหมายที่เกี่ยวข้อง","1-3 วันทำการ"],
               ["3. เสนอราคา","ส่ง Proposal พร้อมค่าธรรมเนียมโดยละเอียด","1 วันทำการ"],
               ["4. ลงนาม Engagement Letter","ลูกค้าอนุมัติ ชำระมัดจำ และลงนามสัญญา","ทันที"],
               ["5. ดำเนินงาน","ทนายความดำเนินการตาม Scope ที่ตกลงกัน","ตามกำหนด"],
               ["6. รายงานความคืบหน้า","ส่ง Progress Report รายสัปดาห์หรือรายเดือน","สม่ำเสมอ"],
               ["7. สรุปและปิดงาน","รายงานสรุป ชำระค่าธรรมเนียมส่วนที่เหลือ","เมื่อเสร็จสิ้น"]]
    p_t = Table(process, colWidths=[3.5*cm,10.5*cm,3*cm])
    p_t.setStyle(header_style())
    story += [p_t, PageBreak()]

    story += [Paragraph("คำถามที่พบบ่อยเกี่ยวกับบริการกฎหมาย", ST["H1"])]
    faqs = [
        ("ต้องใช้เอกสารอะไรบ้างในการจดทะเบียนบริษัท?",
         "บัตรประชาชนผู้ถือหุ้นทุกคน ที่อยู่จดทะเบียน หนังสือบริคณห์สนธิ และรายชื่อกรรมการ ใช้เวลาประมาณ 3-5 วันทำการ"),
        ("ค่าธรรมเนียมทนายความสามารถเจรจาได้ไหม?",
         "ได้ในบางกรณี โดยเฉพาะคดีที่มีทุนทรัพย์สูง หรือลูกค้า Retainer ระยะยาว ทั้งนี้ขึ้นอยู่กับดุลพินิจของหุ้นส่วนที่รับผิดชอบ"),
        ("ถ้าแพ้คดีต้องจ่ายค่าทนายเพิ่มไหม?",
         "ขึ้นอยู่กับข้อตกลงในสัญญา โดยทั่วไปค่าทนายชำระตามการดำเนินงานจริง ไม่ใช่ผลคดี ยกเว้นคดี Contingency Fee"),
        ("สามารถเปลี่ยนทนายความที่รับผิดชอบคดีได้ไหม?",
         "ได้ โดยแจ้งเป็นลายลักษณ์อักษรถึงหุ้นส่วนของสำนักงาน ทีมงานจะจัดสรรทนายความใหม่ที่เหมาะสม"),
        ("กรุงไทยลีกัลรับคดีต่างประเทศได้ไหม?",
         "ได้ โดยร่วมกับพันธมิตรสำนักงานกฎหมายนานาชาติ เชี่ยวชาญด้าน Cross-border M&A, BOI/FDI และอนุญาโตตุลาการระหว่างประเทศ"),
        ("ปรึกษาทางออนไลน์ได้ไหม?",
         "ได้ รับนัดหมายผ่าน Zoom/Microsoft Teams สำหรับลูกค้าต่างจังหวัดหรือต่างประเทศ บางเรื่องต้องนัดพบเป็นการส่วนตัว"),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("ช่องทางติดต่อและสาขา", ST["H1"])]
    branches = [["สาขา","ที่อยู่","โทรศัพท์","เวลาทำการ"],
                ["กรุงเทพฯ (สำนักงานใหญ่)","อาคาร CRC Tower ชั้น 22 ถ.สีลม บางรัก กทม. 10500","02-xxx-2244","จ.-ศ. 08:30-17:30 น."],
                ["เชียงใหม่","อาคาร OFFICE ONE ชั้น 5 ถ.นิมมานเหมินทร์ เมือง เชียงใหม่","053-xxx-551","จ.-ศ. 09:00-17:00 น."],
                ["ระยอง","อาคาร Eastern Seaboard Center ถ.สุขุมวิท มาบตาพุด","038-xxx-771","จ.-ศ. 09:00-17:00 น."],
                ["สงขลา","อาคาร DiamondSQ ชั้น 3 ถ.นิพัทธ์อุทิศ 3 หาดใหญ่","074-xxx-991","จ.-ศ. 09:00-17:00 น."]]
    br_t = Table(branches, colWidths=[3.5*cm,7*cm,3*cm,3.5*cm])
    br_t.setStyle(header_style())
    story += [br_t, Spacer(1,0.4*cm)]
    story += [
        Paragraph("อีเมล: info@krungthai-legal.th | เว็บไซต์: www.krungthai-legal.th", ST["Body"]),
        Paragraph("© 2567 กรุงไทยลีกัล แอสโซซิเอทส์ | เลขทะเบียนสภาทนายความ: TLA-2540-0892 | อัปเดต 1 พ.ย. 2567", ST["Small"]),
    ]
    doc.build(story, onFirstPage=page_footer("กรุงไทยลีกัล แอสโซซิเอทส์"), onLaterPages=page_footer("กรุงไทยลีกัล แอสโซซิเอทส์"))
    print(f"  Created: {path}")


def build_legal_en(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("Krung Thai Legal Associates", ST["Title"]),
        Paragraph("Premier Thai Law Firm — Service Guide & Terms of Engagement", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("Krung Thai Legal Associates, established in 1997, specializes in corporate law, "
                  "real estate, labor law and dispute resolution. Our 45-attorney team is accredited "
                  "by the Lawyers Council of Thailand with offices in Bangkok, Chiang Mai, Rayong, and Songkhla.", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("Table of Contents", ST["H1"]),
    ]
    toc = [["Section","Page"],
           ["Legal Services and Fee Schedule","2-3"],
           ["Terms of Engagement","4-5"],
           ["Confidentiality Policy","6-7"],
           ["Case Intake Process","8-9"],
           ["General Legal FAQ","10-11"],
           ["Contact and Branch Offices","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("Legal Services and Fee Schedule", ST["H1"])]
    services = [["Practice Area","Services","Starting Fee","Notes"],
                ["Corporate Law","Company registration / contract drafting / M&A","THB 15,000","Complexity-dependent"],
                ["Real Estate","Title deed review / property transfer / purchase","THB 8,000","Per transaction"],
                ["Labor Law","Wrongful termination / employment contracts","THB 12,000","Per case"],
                ["IP Law","Trademark / copyright registration","THB 10,000","Per class"],
                ["Family Law","Divorce / inheritance / child custody","THB 20,000","Per case"],
                ["Arbitration","Mediation / international arbitration","THB 25,000","Per day"],
                ["Criminal Defense","Defense / bail applications","THB 35,000","Starting rate"],
                ["BOI / FDI","Investment promotion licenses","THB 30,000","Per project"]]
    sv_t = Table(services, colWidths=[4*cm,5.5*cm,3*cm,4.5*cm])
    sv_t.setStyle(header_style())
    story += [sv_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Consultation Fee Structure", ST["H2"]),
        Paragraph("• Express consultation (30 min): THB 1,500 — general advice, no litigation included", ST["Bullet"]),
        Paragraph("• Monthly retainer: THB 15,000-50,000/month — 10-40 consultation hours included", ST["Bullet"]),
        Paragraph("• Contingency fee: 15-25% of recovery amount (select case types only)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Terms of Engagement", ST["H1"])]
    story += [
        Paragraph("1. Engagement Letter", ST["H2"]),
        Paragraph("All clients must sign an Engagement Letter before work commences, specifying: "
                  "scope of work, fee schedule, payment terms, and contract duration.", ST["Body"]),
        Paragraph("2. Fee Payment", ST["H2"]),
        Paragraph("• New matters: 50% upfront upon signing Engagement Letter; balance upon completion", ST["Bullet"]),
        Paragraph("• Retainer: monthly in advance, due by the 5th of each month", ST["Bullet"]),
        Paragraph("• Disbursements (court fees, copying costs): billed separately with receipts", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("3. Termination", ST["H2"]),
        Paragraph("• Client cancels before work begins: 80% of retainer refunded", ST["Bullet"]),
        Paragraph("• Mid-matter cancellation: fees charged pro-rata for work completed; no refund of excess", ST["Bullet"]),
        Paragraph("• Firm reserves the right to decline or withdraw from matters with conflict of interest", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("4. Conflict of Interest Policy", ST["H2"]),
        Paragraph("Every new matter undergoes a conflict check before acceptance. If a conflict is identified, "
                  "the client is immediately informed and referred to an appropriate alternative firm.", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("Confidentiality Policy", ST["H1"])]
    story += [
        Paragraph("Attorney-Client Privilege", ST["H2"]),
        Paragraph("All client communications are protected under attorney-client privilege. "
                  "Krung Thai Legal will not disclose client information to third parties except:", ST["Body"]),
        Paragraph("• With the client's written consent", ST["Bullet"]),
        Paragraph("• Under a binding court order", ST["Bullet"]),
        Paragraph("• When necessary to prevent an imminent crime or serious harm", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("Data Storage", ST["H2"]),
        Paragraph("Client documents are stored in AES-256 encrypted cloud storage on AWS ap-southeast-1. "
                  "Access is restricted to the attorneys assigned to each matter. Physical documents are "
                  "held in a controlled-access secured safe. Retention period: 10 years after matter closure.", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("Case Intake Process", ST["H1"])]
    process = [["Step","Description","Timeline"],
               ["1. Initial Consultation","Meet attorney; assess matter and receive preliminary advice","30-60 min"],
               ["2. Case Analysis","Attorney analyzes facts and applicable law","1-3 business days"],
               ["3. Fee Proposal","Detailed proposal with fee schedule submitted","1 business day"],
               ["4. Sign Engagement Letter","Client approves, pays retainer, and signs contract","Immediate"],
               ["5. Work Execution","Attorneys execute tasks per agreed scope","Per schedule"],
               ["6. Progress Reporting","Weekly or monthly progress reports","Ongoing"],
               ["7. Closure","Summary report; final invoice settled","Upon completion"]]
    p_t = Table(process, colWidths=[3.5*cm,10.5*cm,3*cm])
    p_t.setStyle(header_style())
    story += [p_t, PageBreak()]

    story += [Paragraph("Frequently Asked Legal Questions", ST["H1"])]
    faqs = [
        ("What documents are required to register a company in Thailand?",
         "ID of all shareholders, registered address, Memorandum of Association, and list of directors. Timeline: 3-5 business days."),
        ("Are attorney fees negotiable?",
         "In some cases, particularly high-value matters or long-term retainer relationships, at the partner's discretion."),
        ("Do I still pay if I lose the case?",
         "Typically yes, as fees are based on work performed, not outcome. Contingency fee arrangements differ — discussed at engagement."),
        ("Can I request a different attorney?",
         "Yes. Submit a written request to the partner-in-charge; a suitable reassignment will be arranged."),
        ("Can Krung Thai Legal handle cross-border matters?",
         "Yes, through our international law firm network specializing in cross-border M&A, BOI/FDI and international arbitration."),
        ("Is online consultation available?",
         "Yes, via Zoom/Microsoft Teams for out-of-province or overseas clients. Some matters require in-person attendance."),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("Contact and Branch Offices", ST["H1"])]
    branches = [["Branch","Address","Phone","Hours"],
                ["Bangkok HQ","CRC Tower 22F, Silom Rd, Bang Rak, Bangkok 10500","02-xxx-2244","Mon-Fri 08:30-17:30"],
                ["Chiang Mai","OFFICE ONE Bldg 5F, Nimman Rd, Mueang, Chiang Mai","053-xxx-551","Mon-Fri 09:00-17:00"],
                ["Rayong","Eastern Seaboard Center, Sukhumvit Rd, Map Ta Phut","038-xxx-771","Mon-Fri 09:00-17:00"],
                ["Songkhla/Hat Yai","DiamondSQ Bldg 3F, Niphat Uthit 3 Rd, Hat Yai","074-xxx-991","Mon-Fri 09:00-17:00"]]
    br_t = Table(branches, colWidths=[3*cm,7*cm,3*cm,4*cm])
    br_t.setStyle(header_style())
    story += [br_t, Spacer(1,0.4*cm)]
    story += [
        Paragraph("Email: info@krungthai-legal.th | Website: www.krungthai-legal.th", ST["Body"]),
        Paragraph("© 2024 Krung Thai Legal Associates | Lawyers Council Reg. No. TLA-2540-0892 | "
                  "Document KTL-EN-2024-v2.0 | Updated: November 1, 2024", ST["Small"]),
    ]
    doc.build(story, onFirstPage=page_footer("Krung Thai Legal Associates"), onLaterPages=page_footer("Krung Thai Legal Associates"))
    print(f"  Created: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# INVESTMENT: Alpha Capital Thailand
# ═══════════════════════════════════════════════════════════════════════════════

def build_investment_th(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("แอลฟ่า แคปิทัล ไทยแลนด์", ST["Title"]),
        Paragraph("บริษัทหลักทรัพย์จัดการกองทุน — คู่มือผลิตภัณฑ์การลงทุน", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("แอลฟ่า แคปิทัล ไทยแลนด์ ก่อตั้งปี 2548 ได้รับใบอนุญาตบริษัทหลักทรัพย์จัดการกองทุน "
                  "จากสำนักงาน กลต. มีสินทรัพย์ภายใต้การจัดการ (AUM) กว่า 85,000 ล้านบาท "
                  "นำเสนอกองทุนรวม 28 กองทุน ครอบคลุมหุ้นไทย หุ้นต่างประเทศ ตราสารหนี้ และกองทุนผสม", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("สารบัญ", ST["H1"]),
    ]
    toc = [["หัวข้อ","หน้า"],
           ["ผลิตภัณฑ์กองทุนรวม","2-3"],
           ["การเปิดบัญชีและการสมัคร","4-5"],
           ["ค่าธรรมเนียมและนโยบายการลงทุน","6-7"],
           ["การเปิดเผยความเสี่ยง","8-9"],
           ["FAQ การลงทุน","10-11"],
           ["ช่องทางติดต่อและข้อกำหนด","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("ผลิตภัณฑ์กองทุนรวม", ST["H1"])]
    funds = [["รหัสกองทุน","ชื่อกองทุน","ประเภท","นโยบาย","ความเสี่ยง (1-8)","ผลตอบแทน YTD"],
             ["ALPHA-EQ-TH","Alpha Thailand Equity","หุ้นไทย","ลงทุน SET50 อย่างน้อย 80%","6","12.4%"],
             ["ALPHA-EQ-GL","Alpha Global Growth","หุ้นต่างประเทศ","หุ้น Global Tech & Growth","7","18.2%"],
             ["ALPHA-FI-TH","Alpha Fixed Income","ตราสารหนี้ไทย","พันธบัตรและหุ้นกู้ investment grade","4","3.8%"],
             ["ALPHA-MIXED-60","Alpha Balanced 60/40","กองทุนผสม","หุ้น 60% / ตราสารหนี้ 40%","5","8.1%"],
             ["ALPHA-REIT","Alpha Property Fund","REITs","REITs ไทยและ Asia","6","9.5%"],
             ["ALPHA-GOLD","Alpha Gold Fund","สินค้าโภคภัณฑ์","ทองคำ 100% (Physical + Futures)","5","7.3%"],
             ["ALPHA-STARTUP","Alpha Innovation Fund","Private Equity","Startup stage B/C ไทย-ASEAN","8","N/A (locked 5yr)"],
             ["ALPHA-ESG","Alpha ESG Leaders","หุ้นยั่งยืน","ESG Score สูงสุดใน SET100","6","11.2%"]]
    f_t = Table(funds, colWidths=[3*cm,4*cm,3*cm,4.5*cm,2.5*cm,2*cm])
    f_t.setStyle(header_style())
    story += [f_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("หมายเหตุ: ผลการดำเนินงานในอดีตไม่ได้เป็นสิ่งยืนยันผลการดำเนินงานในอนาคต "
                  "YTD คำนวณ ณ วันที่ 31 ตุลาคม 2567 ผลตอบแทนเป็น net return หลังหักค่าธรรมเนียมแล้ว", ST["Small"]),
        PageBreak(),
    ]

    story += [Paragraph("การเปิดบัญชีและขั้นตอนการสมัคร", ST["H1"])]
    story += [
        Paragraph("เอกสารที่จำเป็น", ST["H2"]),
        Paragraph("• บัตรประชาชนหรือพาสปอร์ต (ยังไม่หมดอายุ)", ST["Bullet"]),
        Paragraph("• หน้าสมุดบัญชีธนาคาร (สำหรับโอนเงินลงทุนและรับผลตอบแทน)", ST["Bullet"]),
        Paragraph("• แบบ Know Your Customer (KYC) และ Risk Profile Assessment", ST["Bullet"]),
        Paragraph("• FATCA/CRS Declaration (สำหรับนักลงทุนที่มีสถานะภาษีต่างประเทศ)", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("ขั้นตอนการสมัครออนไลน์", ST["H2"]),
    ]
    steps = [["ขั้นตอน","รายละเอียด","ระยะเวลา"],
             ["1. ดาวน์โหลดแอป","Alpha Capital App (iOS/Android) หรือเว็บไซต์","5 นาที"],
             ["2. กรอกข้อมูลส่วนตัว","ข้อมูลส่วนตัว, ที่อยู่, แหล่งที่มาของเงิน","10 นาที"],
             ["3. ยืนยันตัวตน","ถ่ายรูปบัตรประชาชนและ selfie ระบบ AI ตรวจสอบ","3 นาที"],
             ["4. ทำ Risk Assessment","ตอบ 15 คำถามเพื่อประเมิน Risk Profile","10 นาที"],
             ["5. เปิดบัญชี","ระบบอนุมัติ (อัตโนมัติหรือ manual 1 วันทำการ)","ทันที-1 วัน"],
             ["6. โอนเงินและลงทุน","โอนผ่าน PromptPay หรือ Net Banking ขั้นต่ำ 500 THB","ทันที"]]
    s_t = Table(steps, colWidths=[3*cm,11*cm,3*cm])
    s_t.setStyle(header_style())
    story += [s_t, PageBreak()]

    story += [Paragraph("ค่าธรรมเนียมและนโยบายการลงทุน", ST["H1"])]
    fees = [["ค่าธรรมเนียม","อัตรา","รายละเอียด"],
            ["ค่าธรรมเนียมซื้อ (Front-end Load)","0.00-1.50%","แตกต่างตามกองทุนและช่องทางการซื้อ"],
            ["ค่าธรรมเนียมขาย (Back-end Load)","0.00-0.50%","บางกองทุนเรียกเก็บหากขายก่อนกำหนด"],
            ["ค่าธรรมเนียมบริหารจัดการ (Management Fee)","0.50-2.00%/ปี","หักจาก NAV กองทุนอัตโนมัติ"],
            ["ค่าธรรมเนียมผู้ดูแลทรัพย์สิน","0.10-0.20%/ปี","รวมในค่าใช้จ่ายกองทุน (TER)"],
            ["ค่าธรรมเนียมการแปลงกองทุน (Switch)","0.50%","ระหว่างกองทุนภายใน Alpha Capital"]]
    f_t2 = Table(fees, colWidths=[5*cm,3*cm,9*cm])
    f_t2.setStyle(header_style())
    story += [f_t2, Spacer(1,0.3*cm)]
    story += [
        Paragraph("นโยบายการซื้อ-ขาย (Cut-off Time)", ST["H2"]),
        Paragraph("• กองทุนหุ้นไทย: Cut-off 14:00 น. วันทำการ รับ NAV วันทำการถัดไป", ST["Bullet"]),
        Paragraph("• กองทุนต่างประเทศ: Cut-off 13:00 น. รับ NAV ตามกำหนดตลาดต่างประเทศ (T+3-5)", ST["Bullet"]),
        Paragraph("• กองทุนตลาดเงิน: ซื้อ-ขายได้ทุกวัน Cut-off 14:30 น.", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("การเปิดเผยความเสี่ยง (Risk Disclosure)", ST["H1"])]
    risks = [["ระดับความเสี่ยง","คำอธิบาย","กองทุนที่เหมาะสม"],
             ["ระดับ 1-2 (ต่ำมาก)","กองทุนตลาดเงิน ผลตอบแทนใกล้เคียงดอกเบี้ย","ALPHA-MM (ตลาดเงิน)"],
             ["ระดับ 3-4 (ต่ำ-ปานกลาง)","ตราสารหนี้ความเสี่ยงต่ำ พันธบัตรรัฐบาล","ALPHA-FI-TH"],
             ["ระดับ 5-6 (ปานกลาง-สูง)","หุ้นผสม REITs ทองคำ","ALPHA-MIXED-60, ALPHA-REIT, ALPHA-GOLD"],
             ["ระดับ 7 (สูง)","หุ้นไทย หุ้นต่างประเทศ","ALPHA-EQ-TH, ALPHA-EQ-GL"],
             ["ระดับ 8 (สูงมาก)","Private Equity / Startup","ALPHA-STARTUP (ผู้ลงทุนสถาบัน/UHNW)"]]
    r_t = Table(risks, colWidths=[3.5*cm,7*cm,6.5*cm])
    r_t.setStyle(header_style())
    story += [r_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("คำเตือนความเสี่ยงสำคัญ", ST["H2"]),
        Paragraph("การลงทุนมีความเสี่ยง ผู้ลงทุนอาจได้รับเงินคืนน้อยกว่าเงินลงทุนเริ่มต้น "
                  "กองทุนที่ลงทุนในหลักทรัพย์ต่างประเทศมีความเสี่ยงจากอัตราแลกเปลี่ยน "
                  "กองทุน ALPHA-STARTUP มีสภาพคล่องต่ำ ไม่สามารถขายคืนได้ก่อนครบกำหนด 5 ปี "
                  "ผู้ลงทุนควรศึกษาหนังสือชี้ชวนก่อนตัดสินใจลงทุน", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("คำถามที่พบบ่อยด้านการลงทุน", ST["H1"])]
    faqs = [
        ("ลงทุนขั้นต่ำเท่าไหร่?","ขั้นต่ำ 500 THB สำหรับกองทุนทั่วไป (ยกเว้น ALPHA-STARTUP ขั้นต่ำ 500,000 THB สำหรับ Accredited Investor)"),
        ("ขายคืนกองทุนได้เมื่อไหร่?","กองทุนส่วนใหญ่ขายคืนได้ทุกวันทำการ Cut-off ตามกองทุน ยกเว้น ALPHA-STARTUP ล็อคระยะ 5 ปี"),
        ("กองทุน LTF/RMF หักลดหย่อนภาษีได้ไหม?","Alpha Capital มีกองทุน SSF (Super Savings Fund) และ RMF ที่ลดหย่อนภาษีได้ตามเงื่อนไข กลต."),
        ("ผลตอบแทนกองทุนมีการรับประกันไหม?","ไม่มี ผลการดำเนินงานในอดีตไม่รับประกันอนาคต กองทุนที่ระดับ 3-4 มีความเสี่ยงต่ำกว่าแต่ก็ไม่มีการรับประกัน"),
        ("ดูพอร์ตและ NAV ได้ที่ไหน?","แอป Alpha Capital ดูได้ real-time ทุกวัน NAV ประกาศ 18:00 น. ของวันทำการ (กองทุนไทย)"),
        ("เปลี่ยนกองทุน (Switch) ต้องทำอย่างไร?","แอป Alpha Capital > พอร์ตโฟลิโอ > กด Switch > เลือกกองทุนปลายทาง ค่าธรรมเนียม 0.5% (บางกองทุน 0%)"),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("ช่องทางติดต่อและข้อกำหนด", ST["H1"])]
    contacts = [["ช่องทาง","รายละเอียด","เวลาทำการ"],
                ["โทรศัพท์","02-xxx-6688","จ.-ศ. 08:30-17:00 น."],
                ["อีเมล","invest@alphacapital.th","ตอบภายใน 1 วันทำการ"],
                ["แอป/เว็บ","www.alphacapital.th","24/7 (ข้อมูลและธุรกรรม)"],
                ["LINE","@alphacapital.th","จ.-ศ. 08:30-17:00 น."],
                ["สำนักงาน","อาคาร Park Ventures ชั้น 18 ถ.วิทยุ ลุมพินี","จ.-ศ. 08:30-17:00 น."]]
    ct = Table(contacts, colWidths=[3*cm,8*cm,6*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [
        Paragraph("บริษัท แอลฟ่า แคปิทัล ไทยแลนด์ จำกัด | ใบอนุญาต กลต. เลขที่ ลจ.0045/2548 "
                  "| AUM 85,000 ล้านบาท | อัปเดต 1 พ.ย. 2567", ST["Small"]),
    ]
    doc.build(story, onFirstPage=page_footer("แอลฟ่า แคปิทัล ไทยแลนด์"), onLaterPages=page_footer("แอลฟ่า แคปิทัล ไทยแลนด์"))
    print(f"  Created: {path}")


def build_investment_en(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("Alpha Capital Thailand", ST["Title"]),
        Paragraph("Asset Management — Investment Products Guide", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("Alpha Capital Thailand, established in 2005, is a SEC-licensed asset management company "
                  "with THB 85 billion in Assets Under Management (AUM). We offer 28 mutual funds covering "
                  "Thai equities, global equities, fixed income, and balanced portfolios.", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("Table of Contents", ST["H1"]),
    ]
    toc = [["Section","Page"],
           ["Mutual Fund Products","2-3"],
           ["Account Opening and Onboarding","4-5"],
           ["Fee Schedule and Investment Policy","6-7"],
           ["Risk Disclosure","8-9"],
           ["Investment FAQ","10-11"],
           ["Contact and Regulatory Information","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("Mutual Fund Products", ST["H1"])]
    funds = [["Fund Code","Fund Name","Type","Policy","Risk Level (1-8)","YTD Return"],
             ["ALPHA-EQ-TH","Alpha Thailand Equity","Thai Equity","≥80% in SET50 universe","6","12.4%"],
             ["ALPHA-EQ-GL","Alpha Global Growth","Foreign Equity","Global Tech & Growth stocks","7","18.2%"],
             ["ALPHA-FI-TH","Alpha Fixed Income","Thai Fixed Income","Investment grade bonds","4","3.8%"],
             ["ALPHA-MIXED-60","Alpha Balanced 60/40","Mixed Fund","60% equity / 40% bonds","5","8.1%"],
             ["ALPHA-REIT","Alpha Property Fund","REITs","Thai & Asian REITs","6","9.5%"],
             ["ALPHA-GOLD","Alpha Gold Fund","Commodities","100% gold (physical + futures)","5","7.3%"],
             ["ALPHA-STARTUP","Alpha Innovation Fund","Private Equity","ASEAN startup stage B/C","8","N/A (5yr lock)"],
             ["ALPHA-ESG","Alpha ESG Leaders","Sustainable Equity","Top ESG scorers in SET100","6","11.2%"]]
    f_t = Table(funds, colWidths=[3*cm,4*cm,3*cm,4.5*cm,2.5*cm,2*cm])
    f_t.setStyle(header_style())
    story += [f_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Note: Past performance does not guarantee future results. YTD calculated as of October 31, 2024. "
                  "Returns shown are net of management fees.", ST["Small"]),
        PageBreak(),
    ]

    story += [Paragraph("Account Opening and Onboarding", ST["H1"])]
    story += [
        Paragraph("Required Documents", ST["H2"]),
        Paragraph("• National ID or passport (not expired)", ST["Bullet"]),
        Paragraph("• Bank account page (for fund transfers and redemption proceeds)", ST["Bullet"]),
        Paragraph("• Know Your Customer (KYC) form and Risk Profile Assessment", ST["Bullet"]),
        Paragraph("• FATCA/CRS declaration (for investors with overseas tax status)", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("Online Account Opening Steps", ST["H2"]),
    ]
    steps = [["Step","Description","Time"],
             ["1. Download App","Alpha Capital App (iOS/Android) or website","5 min"],
             ["2. Enter Details","Personal info, address, source of funds","10 min"],
             ["3. Identity Verification","Photo ID + selfie, AI-powered verification","3 min"],
             ["4. Risk Assessment","15-question Risk Profile Questionnaire","10 min"],
             ["5. Account Approval","Automatic or manual review (1 business day)","Immediate-1 day"],
             ["6. Fund & Invest","Transfer via PromptPay or Net Banking; min. THB 500","Immediate"]]
    s_t = Table(steps, colWidths=[3*cm,11*cm,3*cm])
    s_t.setStyle(header_style())
    story += [s_t, PageBreak()]

    story += [Paragraph("Fee Schedule and Investment Policy", ST["H1"])]
    fees = [["Fee Type","Rate","Notes"],
            ["Front-end Load (Subscription)","0.00-1.50%","Varies by fund and purchase channel"],
            ["Back-end Load (Redemption)","0.00-0.50%","Some funds charge if redeemed before minimum hold"],
            ["Management Fee","0.50-2.00%/yr","Deducted from NAV automatically"],
            ["Custodian Fee","0.10-0.20%/yr","Included in Total Expense Ratio (TER)"],
            ["Switch Fee","0.50%","Between funds within Alpha Capital"]]
    f_t2 = Table(fees, colWidths=[5*cm,3*cm,9*cm])
    f_t2.setStyle(header_style())
    story += [f_t2, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Cut-off Times", ST["H2"]),
        Paragraph("• Thai equity funds: cut-off 14:00 ICT on business days; NAV applied next business day", ST["Bullet"]),
        Paragraph("• Foreign funds: cut-off 13:00 ICT; NAV per foreign market schedule (T+3-5)", ST["Bullet"]),
        Paragraph("• Money market fund: daily cut-off 14:30 ICT", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Risk Disclosure", ST["H1"])]
    risks = [["Risk Level","Description","Suitable Funds"],
             ["Level 1-2 (Very Low)","Money market; near-deposit returns","ALPHA-MM (Money Market)"],
             ["Level 3-4 (Low-Moderate)","Low-risk bonds, government securities","ALPHA-FI-TH"],
             ["Level 5-6 (Moderate-High)","Balanced funds, REITs, gold","ALPHA-MIXED-60, ALPHA-REIT, ALPHA-GOLD"],
             ["Level 7 (High)","Thai and global equities","ALPHA-EQ-TH, ALPHA-EQ-GL"],
             ["Level 8 (Very High)","Private equity / Startup","ALPHA-STARTUP (Institutional/UHNW only)"]]
    r_t = Table(risks, colWidths=[3.5*cm,7*cm,6.5*cm])
    r_t.setStyle(header_style())
    story += [r_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Key Risk Warning", ST["H2"]),
        Paragraph("Investing involves risk. Investors may receive back less than their initial investment. "
                  "Foreign-invested funds carry currency exchange risk. ALPHA-STARTUP has low liquidity "
                  "and cannot be redeemed before the 5-year lock-up period. "
                  "Investors should study the fund prospectus before making investment decisions.", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("Investment FAQ", ST["H1"])]
    faqs = [
        ("What is the minimum investment?","THB 500 for most funds. Exception: ALPHA-STARTUP requires minimum THB 500,000 for Accredited Investors only."),
        ("When can I redeem my investment?","Most funds allow daily redemption on business days per cut-off times. ALPHA-STARTUP has a 5-year lock-up."),
        ("Are there tax-deductible investment funds?","Alpha Capital offers SSF (Super Savings Fund) and RMF eligible for personal income tax deductions per SEC conditions."),
        ("Are returns guaranteed?","No. Past performance does not guarantee future returns. Even lower-risk funds (levels 3-4) carry some risk."),
        ("How do I view my portfolio and NAV?","Via Alpha Capital app in real-time. NAV is published at 18:00 ICT each business day (Thai funds)."),
        ("How do I switch funds?","Alpha Capital app > Portfolio > Switch > Select destination fund. Switch fee: 0.5% (some funds: 0%)."),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("Contact and Regulatory Information", ST["H1"])]
    contacts = [["Channel","Details","Hours"],
                ["Phone","02-xxx-6688","Mon-Fri 08:30-17:00 ICT"],
                ["Email","invest@alphacapital.th","Response within 1 business day"],
                ["App / Web","www.alphacapital.th","24/7 (data and transactions)"],
                ["LINE","@alphacapital.th","Mon-Fri 08:30-17:00 ICT"],
                ["Office","Park Ventures Bldg 18F, Wireless Rd, Lumpini, Bangkok","Mon-Fri 08:30-17:00 ICT"]]
    ct = Table(contacts, colWidths=[3*cm,8*cm,6*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [
        Paragraph("Alpha Capital Thailand Co., Ltd. | SEC License No. ลจ.0045/2548 | AUM: THB 85 billion | "
                  "Document AC-EN-2024-v3.1 | Updated: November 1, 2024", ST["Small"]),
    ]
    doc.build(story, onFirstPage=page_footer("Alpha Capital Thailand"), onLaterPages=page_footer("Alpha Capital Thailand"))
    print(f"  Created: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# INSURANCE SET 1: ThaiLife Plus (ประกันชีวิต)
# ═══════════════════════════════════════════════════════════════════════════════

def build_insurance1_th(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("ไทยไลฟ์พลัส", ST["Title"]),
        Paragraph("บริษัทประกันชีวิต — คู่มือผลิตภัณฑ์และบริการ", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("ไทยไลฟ์พลัส ก่อตั้งปี 2518 เป็นบริษัทประกันชีวิตชั้นนำของไทย มีลูกค้ากว่า 3.2 ล้านราย "
                  "ผลิตภัณฑ์ครอบคลุมประกันชีวิต ประกันสุขภาพ ประกันอุบัติเหตุ และผลิตภัณฑ์ออมทรัพย์ "
                  "ได้รับอนุญาตจากสำนักงาน คปภ. เลขที่ 001/2518", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("สารบัญ", ST["H1"]),
    ]
    toc = [["หัวข้อ","หน้า"],
           ["แผนประกันชีวิตและสุขภาพ","2-3"],
           ["ตารางเบี้ยประกันและความคุ้มครอง","4-5"],
           ["ขั้นตอนการซื้อประกันและเอกสาร","6-7"],
           ["กระบวนการเรียกร้องสินไหม","8-9"],
           ["FAQ ประกันชีวิตและสุขภาพ","10-11"],
           ["ช่องทางติดต่อ","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("แผนประกันชีวิตและสุขภาพ", ST["H1"])]
    plans = [["รหัสแผน","ชื่อแผน","ประเภท","ทุนประกัน","เบี้ยเริ่มต้น/เดือน","ระยะเวลา"],
             ["TLP-LIFE-01","ไทยไลฟ์ 20 ปี ออมทรัพย์","ชีวิตสะสมทรัพย์","500,000 THB","1,250 THB","20 ปี"],
             ["TLP-LIFE-02","ไทยไลฟ์ ตลอดชีพ Pro","ชีวิตตลอดชีพ","1,000,000 THB","2,800 THB","ตลอดชีพ"],
             ["TLP-HEALTH-01","ไทยไลฟ์ เฮลท์ พรีเมียม","สุขภาพผู้ป่วยใน","500,000 THB/ปี","850 THB","1 ปี ต่ออายุได้"],
             ["TLP-HEALTH-02","ไทยไลฟ์ โรคร้ายแรง 36","โรคร้ายแรง","300,000 THB","600 THB","ถึงอายุ 80"],
             ["TLP-ACC-01","ไทยไลฟ์ อุบัติเหตุ 24 ชม.","อุบัติเหตุ PA","1,000,000 THB","300 THB/ปี","1 ปี ต่ออายุได้"],
             ["TLP-SAVING-01","ไทยไลฟ์ ออมสุข 10/15","ออมทรัพย์","ตามสัญญา","2,500 THB","10 ปี (รับ 15 ปี)"],
             ["TLP-UNIT-01","ไทยไลฟ์ ยูนิตลิงค์ Growth","Unit Linked","ขึ้นอยู่กับ NAV","3,000 THB","ตลอดชีพ"]]
    pl_t = Table(plans, colWidths=[3*cm,4*cm,3*cm,3*cm,2.5*cm,2.5*cm])
    pl_t.setStyle(header_style())
    story += [pl_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("สิทธิประโยชน์ทางภาษี", ST["H2"]),
        Paragraph("• เบี้ยประกันชีวิตลดหย่อนภาษีได้สูงสุด 100,000 THB/ปี (ประกันชีวิตระยะ ≥10 ปี)", ST["Bullet"]),
        Paragraph("• เบี้ยประกันสุขภาพลดหย่อนภาษีได้เพิ่มอีกสูงสุด 25,000 THB/ปี", ST["Bullet"]),
        Paragraph("• สินไหมมรณกรรมได้รับยกเว้นภาษีเงินได้ตามกฎหมาย", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("ตารางเบี้ยประกันและความคุ้มครอง (ตัวอย่าง)", ST["H1"])]
    story += [Paragraph("แผน TLP-HEALTH-01: ไทยไลฟ์ เฮลท์ พรีเมียม", ST["H2"])]
    health_table = [["อายุผู้เอาประกัน","ชาย (เบี้ย/ปี)","หญิง (เบี้ย/ปี)","วงเงินสูงสุด/ปี","ห้องผู้ป่วย/วัน"],
                    ["1-25 ปี","8,500 THB","7,900 THB","500,000 THB","3,500 THB"],
                    ["26-35 ปี","10,200 THB","9,400 THB","500,000 THB","3,500 THB"],
                    ["36-45 ปี","14,500 THB","13,200 THB","500,000 THB","3,500 THB"],
                    ["46-55 ปี","21,000 THB","18,900 THB","500,000 THB","3,500 THB"],
                    ["56-65 ปี","31,500 THB","28,700 THB","500,000 THB","3,500 THB"],
                    ["66-70 ปี","45,000 THB","41,200 THB","500,000 THB","3,500 THB"]]
    ht = Table(health_table, colWidths=[3.5*cm,3.5*cm,3.5*cm,3.5*cm,3*cm])
    ht.setStyle(header_style())
    story += [ht, Spacer(1,0.3*cm)]
    story += [
        Paragraph("ความคุ้มครองหลัก TLP-HEALTH-01", ST["H2"]),
        Paragraph("• ค่าห้องและค่าอาหาร: สูงสุด 3,500 THB/วัน ไม่จำกัดจำนวนวัน", ST["Bullet"]),
        Paragraph("• ค่าผ่าตัด: ตามตารางผ่าตัด สูงสุด 200,000 THB/ครั้ง", ST["Bullet"]),
        Paragraph("• ค่าห้อง ICU: สูงสุด 7,000 THB/วัน", ST["Bullet"]),
        Paragraph("• ผู้ป่วยนอก (OPD): 2,000 THB/ครั้ง สูงสุด 30 ครั้ง/ปี (แผน Premium เท่านั้น)", ST["Bullet"]),
        Paragraph("• ค่ารักษาอุบัติเหตุฉุกเฉิน: 20,000 THB/ครั้ง ไม่ต้องนอนโรงพยาบาล", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("ขั้นตอนการซื้อประกันและเอกสารที่ต้องใช้", ST["H1"])]
    story += [
        Paragraph("ช่องทางการซื้อประกัน", ST["H2"]),
        Paragraph("1. ตัวแทนประกันชีวิต (Agent): ติดต่อผ่านเว็บไซต์หรือโทรศัพท์ ตัวแทนมาพบถึงบ้าน", ST["Bullet"]),
        Paragraph("2. ออนไลน์ (Digital): เว็บไซต์ www.thailifeplus.th หรือแอป ThaiLife+ App", ST["Bullet"]),
        Paragraph("3. ธนาคารพาร์ทเนอร์: Bancassurance ผ่าน กสิกรไทย / SCB / กรุงไทย", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("เอกสารที่ต้องใช้", ST["H2"]),
        Paragraph("• บัตรประชาชนฉบับจริง (สำหรับสัญญาออนไลน์ใช้ภาพถ่าย)", ST["Bullet"]),
        Paragraph("• ผลการตรวจสุขภาพ (กรณีทุนประกันเกิน 3,000,000 THB หรืออายุ 50 ปีขึ้นไป)", ST["Bullet"]),
        Paragraph("• แบบฟอร์มใบคำขอประกันชีวิต (ตอบคำถามสุขภาพ 20 ข้อ)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("กระบวนการเรียกร้องสินไหม", ST["H1"])]
    claims = [["ประเภทสินไหม","ช่องทางแจ้ง","เอกสารสำคัญ","ระยะเวลาจ่าย"],
              ["มรณกรรม","โทร 02-xxx-5500 ภายใน 14 วัน","ใบมรณบัตร, สำเนาบัตรผู้รับประโยชน์","15 วันทำการ"],
              ["ผู้ป่วยใน (IPD)","แอปหรือเคาน์เตอร์โรงพยาบาลคู่สัญญา","ใบแจ้งหนี้โรงพยาบาล, OPD card","ทันที (cashless) / 7 วัน"],
              ["โรคร้ายแรง","อีเมล claim@thailifeplus.th พร้อมเอกสาร","รายงานแพทย์ยืนยันโรค","30 วันทำการ"],
              ["อุบัติเหตุ","แจ้งภายใน 30 วัน ผ่านแอปหรือโทรศัพท์","รายงานตำรวจ/แพทย์","10 วันทำการ"]]
    cl_t = Table(claims, colWidths=[3*cm,4*cm,5*cm,5*cm])
    cl_t.setStyle(header_style())
    story += [cl_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("โรงพยาบาลคู่สัญญา Cashless", ST["H2"]),
        Paragraph("ไทยไลฟ์พลัส มีโรงพยาบาลคู่สัญญากว่า 1,200 แห่งทั่วประเทศ ลูกค้าสามารถเข้ารับการรักษา "
                  "โดยไม่ต้องสำรองจ่าย โดยแสดงบัตรประกันสุขภาพ ThaiLife+ บัตรประชาชน และยืนยันตัวตน "
                  "ผ่าน OTP บนแอปมือถือ ตรวจสอบรายชื่อโรงพยาบาลได้ที่แอปหรือ www.thailifeplus.th/hospitals", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("คำถามที่พบบ่อย (FAQ)", ST["H1"])]
    faqs = [
        ("ซื้อประกันออนไลน์ปลอดภัยไหม?",
         "ปลอดภัย สัญญาประกันออนไลน์มีผลทางกฎหมายเช่นเดียวกับสัญญากระดาษ ทุกธุรกรรมเข้ารหัส TLS 1.3"),
        ("ถ้าแพ้ชนิดยาต้องแจ้งหรือไม่?",
         "ต้องระบุในแบบฟอร์มสุขภาพ การปิดบังข้อมูลสุขภาพสำคัญอาจเป็นเหตุให้บริษัทบอกเลิกสัญญาหรือปฏิเสธสินไหม"),
        ("เบี้ยประกันขึ้นทุกปีไหม?",
         "ขึ้นอยู่กับแผน แผนชีวิตสะสมทรัพย์และตลอดชีพเบี้ยคงที่ตลอดสัญญา แผนสุขภาพรายปีอาจปรับขึ้นตามอายุและสถิติการเรียกร้อง"),
        ("ยกเลิกกรมธรรม์ก่อนกำหนดได้ไหม?",
         "ได้ แต่จะได้รับมูลค่าเงินสดคืน (Cash Value) ซึ่งน้อยกว่าเบี้ยที่ชำระรวม โดยเฉพาะในปีแรกๆ"),
        ("สุขภาพไม่ดีมาก ยังสมัครได้ไหม?",
         "ขึ้นอยู่กับโรคและประวัติ อาจมีข้อยกเว้นโรคเดิม หรือ Loading (เบี้ยสูงกว่าปกติ) หรือปฏิเสธการรับประกัน"),
        ("ครอบคลุมการรักษาในต่างประเทศไหม?",
         "แผน TLP-HEALTH-01 คุ้มครองกรณีฉุกเฉินในต่างประเทศสูงสุด 50,000 THB/ครั้ง แผน Premium Plus คุ้มครองทั่วโลก"),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("ช่องทางติดต่อ ไทยไลฟ์พลัส", ST["H1"])]
    contacts = [["ช่องทาง","รายละเอียด","เวลาทำการ"],
                ["Call Center","02-xxx-5500","ทุกวัน 08:00-20:00 น."],
                ["อีเมล","service@thailifeplus.th","ตอบภายใน 1 วันทำการ"],
                ["แอป ThaiLife+","ดาวน์โหลด iOS/Android","24/7"],
                ["เว็บไซต์","www.thailifeplus.th","24/7"],
                ["LINE","@thailifeplus","ทุกวัน 08:00-20:00 น."],
                ["สำนักงานใหญ่","อาคาร Q-House Lumpini ชั้น 10 ถ.สาทร กทม.","จ.-ศ. 08:30-17:00 น."]]
    ct = Table(contacts, colWidths=[3*cm,7*cm,7*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [Paragraph("© 2567 บริษัท ไทยไลฟ์พลัส จำกัด (มหาชน) | ใบอนุญาต คปภ. เลขที่ 001/2518 | อัปเดต 1 พ.ย. 2567", ST["Small"])]
    doc.build(story, onFirstPage=page_footer("ไทยไลฟ์พลัส"), onLaterPages=page_footer("ไทยไลฟ์พลัส"))
    print(f"  Created: {path}")


def build_insurance1_en(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("ThaiLife Plus", ST["Title"]),
        Paragraph("Life Insurance Company — Products and Services Guide", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("ThaiLife Plus, established in 1975, is one of Thailand's leading life insurance companies "
                  "with 3.2 million policyholders. Our products cover life insurance, health insurance, "
                  "accident protection, and savings-linked plans. Licensed by the OIC (Office of Insurance Commission) "
                  "License No. 001/2518.", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("Table of Contents", ST["H1"]),
    ]
    toc = [["Section","Page"],
           ["Insurance Plans Overview","2-3"],
           ["Premium Tables and Coverage Details","4-5"],
           ["Application Process and Documents","6-7"],
           ["Claims Process","8-9"],
           ["FAQ — Life and Health Insurance","10-11"],
           ["Contact Information","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("Insurance Plans Overview", ST["H1"])]
    plans = [["Plan Code","Plan Name","Type","Sum Assured","Monthly Premium","Term"],
             ["TLP-LIFE-01","ThaiLife 20-Year Savings","Endowment","THB 500,000","THB 1,250","20 years"],
             ["TLP-LIFE-02","ThaiLife Whole Life Pro","Whole Life","THB 1,000,000","THB 2,800","Whole Life"],
             ["TLP-HEALTH-01","ThaiLife Health Premium","Inpatient Health","THB 500,000/yr","THB 850","Annual (renewable)"],
             ["TLP-HEALTH-02","ThaiLife Critical Illness 36","Critical Illness","THB 300,000","THB 600","To age 80"],
             ["TLP-ACC-01","ThaiLife 24hr PA","Personal Accident","THB 1,000,000","THB 300/yr","Annual (renewable)"],
             ["TLP-SAVING-01","ThaiLife Savings 10/15","Savings","Per policy schedule","THB 2,500","Pay 10, receive 15 yrs"],
             ["TLP-UNIT-01","ThaiLife Unit Linked Growth","Unit Linked","NAV-dependent","THB 3,000","Whole Life"]]
    pl_t = Table(plans, colWidths=[3*cm,4*cm,3*cm,3*cm,2.5*cm,2.5*cm])
    pl_t.setStyle(header_style())
    story += [pl_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Tax Benefits", ST["H2"]),
        Paragraph("• Life insurance premiums: deductible up to THB 100,000/yr (policy term ≥10 years)", ST["Bullet"]),
        Paragraph("• Health insurance premiums: additional deduction up to THB 25,000/yr", ST["Bullet"]),
        Paragraph("• Death benefits are exempt from personal income tax under Thai law", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Premium Tables and Coverage — TLP-HEALTH-01", ST["H1"])]
    health_table = [["Age","Male (Annual)","Female (Annual)","Max Annual Benefit","Room & Board/day"],
                    ["1-25","THB 8,500","THB 7,900","THB 500,000","THB 3,500"],
                    ["26-35","THB 10,200","THB 9,400","THB 500,000","THB 3,500"],
                    ["36-45","THB 14,500","THB 13,200","THB 500,000","THB 3,500"],
                    ["46-55","THB 21,000","THB 18,900","THB 500,000","THB 3,500"],
                    ["56-65","THB 31,500","THB 28,700","THB 500,000","THB 3,500"],
                    ["66-70","THB 45,000","THB 41,200","THB 500,000","THB 3,500"]]
    ht = Table(health_table, colWidths=[2.5*cm,3.5*cm,3.5*cm,4*cm,4*cm])
    ht.setStyle(header_style())
    story += [ht, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Key Coverage — TLP-HEALTH-01 Premium", ST["H2"]),
        Paragraph("• Room and board: up to THB 3,500/day, unlimited days", ST["Bullet"]),
        Paragraph("• Surgical fees: per surgical schedule, up to THB 200,000/procedure", ST["Bullet"]),
        Paragraph("• ICU room: up to THB 7,000/day", ST["Bullet"]),
        Paragraph("• Outpatient (OPD): THB 2,000/visit, up to 30 visits/year (Premium plan only)", ST["Bullet"]),
        Paragraph("• Emergency accident treatment: THB 20,000/incident, no hospitalization required", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Application Process and Required Documents", ST["H1"])]
    story += [
        Paragraph("Purchase Channels", ST["H2"]),
        Paragraph("1. Licensed Agent: contact via website or phone; agent visits at your convenience", ST["Bullet"]),
        Paragraph("2. Online (Digital): www.thailifeplus.th or ThaiLife+ App", ST["Bullet"]),
        Paragraph("3. Partner Banks: bancassurance via KBank / SCB / Krungthai Bank", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("Required Documents", ST["H2"]),
        Paragraph("• National ID or passport (copy for online; original for agent)", ST["Bullet"]),
        Paragraph("• Medical examination results (sum assured >THB 3M or applicant age ≥50)", ST["Bullet"]),
        Paragraph("• Life insurance application form (20 health declaration questions)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Claims Process", ST["H1"])]
    claims = [["Claim Type","Notification","Required Documents","Payment Timeline"],
              ["Death Benefit","Call 02-xxx-5500 within 14 days","Death certificate, beneficiary ID","15 business days"],
              ["Inpatient (IPD)","App or hospital cashless counter","Hospital invoice, OPD card","Immediate (cashless) / 7 days"],
              ["Critical Illness","Email claim@thailifeplus.th","Doctor's confirmed diagnosis report","30 business days"],
              ["Accident","Notify within 30 days via app or phone","Police/medical report","10 business days"]]
    cl_t = Table(claims, colWidths=[3*cm,4*cm,5*cm,5*cm])
    cl_t.setStyle(header_style())
    story += [cl_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Cashless Hospital Network", ST["H2"]),
        Paragraph("ThaiLife Plus has 1,200+ partner hospitals nationwide. Present your ThaiLife+ insurance card, "
                  "national ID, and confirm via OTP in the app to receive cashless treatment. "
                  "Find partner hospitals at the app or www.thailifeplus.th/hospitals.", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("Frequently Asked Questions", ST["H1"])]
    faqs = [
        ("Is buying insurance online safe?","Yes. Online policies are legally equivalent to paper contracts. All transactions are TLS 1.3 encrypted."),
        ("Do I need to disclose drug allergies?","Yes, on the health declaration form. Concealing material health information may result in policy cancellation or claim denial."),
        ("Do premiums increase annually?","Whole life and endowment plan premiums are fixed. Annual health plans may be adjusted based on age and claims experience."),
        ("Can I cancel the policy early?","Yes, but the cash surrender value returned will be less than total premiums paid, especially in early years."),
        ("Can I apply with a pre-existing condition?","Depends on the condition. The insurer may exclude the pre-existing condition, apply a loading, or decline coverage."),
        ("Does the plan cover overseas treatment?","TLP-HEALTH-01 covers emergency overseas treatment up to THB 50,000/incident. Premium Plus plan provides worldwide coverage."),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("Contact ThaiLife Plus", ST["H1"])]
    contacts = [["Channel","Details","Hours"],
                ["Call Center","02-xxx-5500","Daily 08:00-20:00 ICT"],
                ["Email","service@thailifeplus.th","Response within 1 business day"],
                ["App","ThaiLife+ (iOS/Android)","24/7"],
                ["Website","www.thailifeplus.th","24/7"],
                ["LINE","@thailifeplus","Daily 08:00-20:00 ICT"],
                ["Head Office","Q-House Lumpini 10F, Sathorn Rd, Bangkok","Mon-Fri 08:30-17:00"]]
    ct = Table(contacts, colWidths=[3*cm,7*cm,7*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [Paragraph("© 2024 ThaiLife Plus Plc. | OIC License No. 001/2518 | Document TLP-EN-2024-v4.0 | Updated: November 1, 2024", ST["Small"])]
    doc.build(story, onFirstPage=page_footer("ThaiLife Plus"), onLaterPages=page_footer("ThaiLife Plus"))
    print(f"  Created: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# INSURANCE SET 2: Shield Auto Insurance (ประกันรถยนต์)
# ═══════════════════════════════════════════════════════════════════════════════

def build_insurance2_th(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("ชิลด์ออโต้ ประกันภัย", ST["Title"]),
        Paragraph("บริษัทประกันภัยรถยนต์ — คู่มือผลิตภัณฑ์และบริการ", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("ชิลด์ออโต้ ประกันภัย ก่อตั้งปี 2555 เชี่ยวชาญด้านประกันรถยนต์ครบวงจร "
                  "มีลูกค้ากว่า 1.8 ล้านคัน อู่ซ่อมในเครือกว่า 2,500 แห่ง ทั่วประเทศไทย "
                  "บริการ 24 ชั่วโมง ทีมช่วยเหลือฉุกเฉิน Road Assistance พร้อมให้บริการทันที", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("สารบัญ", ST["H1"]),
    ]
    toc = [["หัวข้อ","หน้า"],
           ["แผนประกันรถยนต์และความคุ้มครอง","2-3"],
           ["ตารางเบี้ยประกันและการคำนวณ","4-5"],
           ["ขั้นตอนการซื้อและต่ออายุ","6-7"],
           ["กระบวนการเรียกร้องค่าสินไหม","8-9"],
           ["FAQ ประกันรถยนต์","10-11"],
           ["อู่ในเครือและช่องทางติดต่อ","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("แผนประกันรถยนต์และความคุ้มครอง", ST["H1"])]
    plans = [["แผน","ประเภท","ความเสียหายตนเอง","บุคคลภายนอก (ทรัพย์สิน)","บุคคลภายนอก (ร่างกาย)","ไฟไหม้/โจรกรรม","ภัยธรรมชาติ"],
             ["SHIELD-1+","ชั้น 1+","เต็มทุน","5,000,000 THB","10 ล้าน/ครั้ง","✓","✓"],
             ["SHIELD-1","ชั้น 1","เต็มทุน","3,000,000 THB","10 ล้าน/ครั้ง","✓","✗"],
             ["SHIELD-2+","ชั้น 2+","ไม่คุ้มครอง","3,000,000 THB","10 ล้าน/ครั้ง","✓","✗"],
             ["SHIELD-2","ชั้น 2","ไม่คุ้มครอง","1,000,000 THB","5 ล้าน/ครั้ง","✓","✗"],
             ["SHIELD-3+","ชั้น 3+","ไม่คุ้มครอง","1,000,000 THB","5 ล้าน/ครั้ง","✗","✗"],
             ["SHIELD-3","ชั้น 3 (พ.ร.บ.+)","ไม่คุ้มครอง","500,000 THB","5 ล้าน/ครั้ง","✗","✗"]]
    pl_t = Table(plans, colWidths=[2.5*cm,2*cm,2.5*cm,3*cm,3*cm,2.5*cm,2.5*cm])
    pl_t.setStyle(header_style())
    story += [pl_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("ความคุ้มครองเพิ่มเติม (Rider) ที่เลือกเพิ่มได้", ST["H2"]),
        Paragraph("• ความคุ้มครองน้ำท่วม: สูงสุด 30,000 THB (เพิ่มเบี้ย 1,500 THB/ปี)", ST["Bullet"]),
        Paragraph("• ประกันอุบัติเหตุส่วนบุคคลผู้ขับขี่: 500,000-1,000,000 THB", ST["Bullet"]),
        Paragraph("• ประกันตัวผู้ขับขี่ (Driver PA): 200,000-500,000 THB", ST["Bullet"]),
        Paragraph("• บริการรถยนต์ทดแทนระหว่างซ่อม: สูงสุด 7 วัน (เฉพาะแผน 1 และ 1+)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("ตารางเบี้ยประกันโดยประมาณ (รถเก๋ง ≤ 1500 cc อายุ ≤ 5 ปี)", ST["H1"])]
    premiums = [["แผน","ราคารถ (ล้าน THB)","เบี้ยประกัน/ปี (ไม่รวม VAT)","เบี้ยรวม VAT 7%"],
                ["SHIELD-1+","≤ 0.5","8,500 THB","9,095 THB"],
                ["SHIELD-1+","0.5-1.0","12,000 THB","12,840 THB"],
                ["SHIELD-1+","1.0-2.0","17,500 THB","18,725 THB"],
                ["SHIELD-1","≤ 0.5","7,200 THB","7,704 THB"],
                ["SHIELD-1","0.5-1.0","10,500 THB","11,235 THB"],
                ["SHIELD-2+","≤ 0.5","3,500 THB","3,745 THB"],
                ["SHIELD-2+","0.5-1.0","4,800 THB","5,136 THB"],
                ["SHIELD-3+","ทุกราคา","1,900 THB","2,033 THB"]]
    pr_t = Table(premiums, colWidths=[3*cm,4*cm,5*cm,5*cm])
    pr_t.setStyle(header_style())
    story += [pr_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("ปัจจัยที่ส่งผลต่อเบี้ยประกัน", ST["H2"]),
        Paragraph("• อายุรถ: รถอายุ 6-10 ปี เพิ่มเบี้ย 10-15% / อายุ 11-15 ปี เพิ่ม 20-30%", ST["Bullet"]),
        Paragraph("• ขนาดเครื่องยนต์: >1500cc เพิ่ม 5-15% ตามขนาด", ST["Bullet"]),
        Paragraph("• ประวัติการเรียกร้อง: ไม่เคยเคลม ลด 10% / เคลม 1 ครั้ง +5% / เคลม 2+ ครั้ง +15-25%", ST["Bullet"]),
        Paragraph("• อาชีพผู้ขับขี่: ส่งอาหาร/แกร็บ ต้องแจ้งเพิ่มเติม (เบี้ยพิเศษ)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("ขั้นตอนการซื้อและต่ออายุประกัน", ST["H1"])]
    story += [
        Paragraph("ช่องทางการซื้อ", ST["H2"]),
        Paragraph("1. ออนไลน์: www.shieldauto.th หรือแอป ShieldAuto — ใส่ทะเบียนรถ รับราคาทันที", ST["Bullet"]),
        Paragraph("2. โทรศัพท์: 02-xxx-4444 มีเจ้าหน้าที่ช่วยเลือกแผน", ST["Bullet"]),
        Paragraph("3. ตัวแทน/นายหน้า: ครอบคลุมทั่วประเทศ", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("เอกสารที่ต้องใช้", ST["H2"]),
        Paragraph("• สำเนาบัตรประชาชนหรือพาสปอร์ตผู้เอาประกัน", ST["Bullet"]),
        Paragraph("• เล่มทะเบียนรถ หรือ สำเนาคู่มือจดทะเบียนรถ", ST["Bullet"]),
        Paragraph("• รูปถ่ายรถ 4 ทิศ + เลขตัวถัง + เลขเครื่องยนต์ (สำหรับซื้อออนไลน์)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("กระบวนการเรียกร้องค่าสินไหมทดแทน", ST["H1"])]
    story += [
        Paragraph("ขั้นตอนเมื่อเกิดอุบัติเหตุ", ST["H2"]),
        Paragraph("1. โทรแจ้ง Shield Auto ทันที: 02-xxx-4444 หรือกด SOS ในแอป (บันทึกสถานที่อัตโนมัติ)", ST["Bullet"]),
        Paragraph("2. ทีม Surveyor ออกมาถึงที่เกิดเหตุภายใน 30-60 นาที (กทม.) / 60-120 นาที (ต่างจังหวัด)", ST["Bullet"]),
        Paragraph("3. Surveyor ถ่ายรูปความเสียหาย ออกใบ Accident Report และ Repair Authorization", ST["Bullet"]),
        Paragraph("4. เลือกอู่ในเครือ หรือแจ้งซ่อมอู่ตัวเอง (กรณีมีสิทธิ์ตามแผน)", ST["Bullet"]),
        Paragraph("5. ติดตามสถานะซ่อมได้ในแอป ShieldAuto (อัปเดต real-time)", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("ระยะเวลาการจ่ายสินไหม", ST["H2"]),
    ]
    timelines = [["ประเภท","เงื่อนไข","ระยะเวลา"],
                 ["ซ่อมอู่ในเครือ","บริษัทชำระให้อู่โดยตรง","ไม่ต้องสำรองจ่าย"],
                 ["ซ่อมอู่นอกเครือ","ลูกค้าสำรองจ่าย","บริษัทโอนคืนภายใน 15 วันทำการ"],
                 ["ค่าสินไหมกรณีรวม","กรณีรวมสมบูรณ์ รับทุนประกัน","30 วันทำการหลังตกลงราคา"],
                 ["ค่าสินไหมบุคคลภายนอก","ตกลงกับบุคคลภายนอกเสร็จ","15 วันทำการ"]]
    tl_t = Table(timelines, colWidths=[4*cm,9*cm,4*cm])
    tl_t.setStyle(header_style())
    story += [tl_t, PageBreak()]

    story += [Paragraph("คำถามที่พบบ่อย (FAQ)", ST["H1"])]
    faqs = [
        ("ถ้ารถถูกโจรกรรมต้องทำอย่างไร?","แจ้งความที่สถานีตำรวจและโทรแจ้ง Shield Auto ภายใน 24 ชั่วโมง บริษัทชดใช้มูลค่าตลาดรถ ณ วันเกิดเหตุ"),
        ("ประกันชั้น 1+ ต่างจากชั้น 1 อย่างไร?","SHIELD-1+ เพิ่มความคุ้มครองภัยธรรมชาติ (น้ำท่วม พายุ แผ่นดินไหว) ซึ่งชั้น 1 ปกติไม่คุ้มครอง"),
        ("ถ้าเมาแล้วขับ บริษัทจ่ายไหม?","ไม่จ่ายความเสียหายของรถตนเอง แต่ยังคุ้มครองบุคคลภายนอกตามกฎหมายประกันภัยภาคบังคับ"),
        ("ซ่อมอู่เองได้ไหม?","ได้เฉพาะแผน 1 และ 1+ บางเงื่อนไข ต้องแจ้ง Surveyor ตรวจสอบก่อนซ่อมทุกกรณี"),
        ("ต่ออายุประกันล่าช้าผลเป็นอย่างไร?","กรมธรรม์หมดอายุ ไม่มีความคุ้มครอง ถ้าเกิดอุบัติเหตุในช่วงขาด บริษัทไม่รับผิดชอบ"),
        ("ใช้แอปทำอะไรได้บ้าง?","ต่อประกัน ดูกรมธรรม์ แจ้งอุบัติเหตุ (SOS) ติดตามสถานะซ่อม ค้นหาอู่ในเครือ และเรียก Road Assistance"),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("อู่ในเครือและช่องทางติดต่อ", ST["H1"])]
    story += [
        Paragraph("อู่ในเครือ Shield Auto กว่า 2,500 แห่ง แบ่งเป็น:", ST["Body"]),
        Paragraph("• อู่มาตรฐาน A: รับรองมาตรฐาน ISO 9001 ทั่วประเทศ 1,200 แห่ง", ST["Bullet"]),
        Paragraph("• ศูนย์บริการแบรนด์: Toyota, Honda, Isuzu, Nissan, Ford ทุกสาขา", ST["Bullet"]),
        Paragraph("• อู่ดีลเลอร์อนุมัติ: 300 แห่งในกทม.และปริมณฑล", ST["Bullet"]),
        Spacer(1,0.3*cm),
    ]
    contacts = [["ช่องทาง","รายละเอียด","เวลาทำการ"],
                ["Call Center / SOS","02-xxx-4444","ตลอด 24 ชม. ทุกวัน"],
                ["อีเมล","claim@shieldauto.th","ตอบภายใน 2 ชั่วโมง (วันทำการ)"],
                ["แอป ShieldAuto","iOS/Android","24/7"],
                ["เว็บไซต์","www.shieldauto.th","24/7"],
                ["LINE","@shieldauto","ทุกวัน 07:00-22:00 น."]]
    ct = Table(contacts, colWidths=[3*cm,7*cm,7*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [Paragraph("© 2567 ชิลด์ออโต้ ประกันภัย จำกัด | ใบอนุญาต คปภ. เลขที่ 003/2555 | อัปเดต 1 พ.ย. 2567", ST["Small"])]
    doc.build(story, onFirstPage=page_footer("ชิลด์ออโต้ ประกันภัย"), onLaterPages=page_footer("ชิลด์ออโต้ ประกันภัย"))
    print(f"  Created: {path}")


def build_insurance2_en(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("Shield Auto Insurance", ST["Title"]),
        Paragraph("Motor Insurance Company — Products and Claims Guide", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("Shield Auto Insurance, established in 2012, is a specialist motor insurer with "
                  "1.8 million insured vehicles and 2,500+ affiliated repair shops nationwide. "
                  "We provide 24/7 road assistance and claims support across Thailand, "
                  "licensed by the OIC, License No. 003/2555.", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("Table of Contents", ST["H1"]),
    ]
    toc = [["Section","Page"],
           ["Motor Insurance Plans and Coverage","2-3"],
           ["Premium Tables and Rating Factors","4-5"],
           ["Purchase and Renewal Process","6-7"],
           ["Claims Process","8-9"],
           ["FAQ — Motor Insurance","10-11"],
           ["Affiliated Garages and Contact","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("Motor Insurance Plans and Coverage", ST["H1"])]
    plans = [["Plan","Class","Own Damage","3rd Party (Property)","3rd Party (Bodily)","Fire/Theft","Natural Disaster"],
             ["SHIELD-1+","Comprehensive+","Full sum insured","THB 5,000,000","THB 10M/incident","✓","✓"],
             ["SHIELD-1","Comprehensive","Full sum insured","THB 3,000,000","THB 10M/incident","✓","✗"],
             ["SHIELD-2+","Class 2+","Not covered","THB 3,000,000","THB 10M/incident","✓","✗"],
             ["SHIELD-2","Class 2","Not covered","THB 1,000,000","THB 5M/incident","✓","✗"],
             ["SHIELD-3+","Class 3+","Not covered","THB 1,000,000","THB 5M/incident","✗","✗"],
             ["SHIELD-3","Class 3 (Compulsory+)","Not covered","THB 500,000","THB 5M/incident","✗","✗"]]
    pl_t = Table(plans, colWidths=[2.5*cm,2.5*cm,3*cm,3*cm,3*cm,2*cm,2*cm])
    pl_t.setStyle(header_style())
    story += [pl_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Optional Add-on Riders", ST["H2"]),
        Paragraph("• Flood extension: up to THB 30,000 (additional premium THB 1,500/yr)", ST["Bullet"]),
        Paragraph("• Personal accident for driver: THB 500,000-1,000,000", ST["Bullet"]),
        Paragraph("• Driver PA extension: THB 200,000-500,000", ST["Bullet"]),
        Paragraph("• Replacement vehicle during repair: up to 7 days (Plans 1 and 1+ only)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Premium Table (Indicative) — Sedan ≤1500 cc, Age ≤5 yrs", ST["H1"])]
    premiums = [["Plan","Vehicle Value (THB M)","Annual Premium (ex-VAT)","Total incl. 7% VAT"],
                ["SHIELD-1+","≤ 0.5","THB 8,500","THB 9,095"],
                ["SHIELD-1+","0.5-1.0","THB 12,000","THB 12,840"],
                ["SHIELD-1+","1.0-2.0","THB 17,500","THB 18,725"],
                ["SHIELD-1","≤ 0.5","THB 7,200","THB 7,704"],
                ["SHIELD-1","0.5-1.0","THB 10,500","THB 11,235"],
                ["SHIELD-2+","≤ 0.5","THB 3,500","THB 3,745"],
                ["SHIELD-2+","0.5-1.0","THB 4,800","THB 5,136"],
                ["SHIELD-3+","Any value","THB 1,900","THB 2,033"]]
    pr_t = Table(premiums, colWidths=[3*cm,4*cm,5*cm,5*cm])
    pr_t.setStyle(header_style())
    story += [pr_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Key Rating Factors", ST["H2"]),
        Paragraph("• Vehicle age: 6-10 yrs +10-15%; 11-15 yrs +20-30%", ST["Bullet"]),
        Paragraph("• Engine size: >1500cc add 5-15% depending on displacement", ST["Bullet"]),
        Paragraph("• Claims history: no claims -10%; 1 claim +5%; 2+ claims +15-25%", ST["Bullet"]),
        Paragraph("• Occupation: food delivery / ride-hailing requires disclosure (special tariff applies)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Purchase and Renewal Process", ST["H1"])]
    story += [
        Paragraph("Purchase Channels", ST["H2"]),
        Paragraph("1. Online: www.shieldauto.th or ShieldAuto App — enter licence plate, get instant quote", ST["Bullet"]),
        Paragraph("2. Phone: 02-xxx-4444 — agent assists with plan selection", ST["Bullet"]),
        Paragraph("3. Authorised agents/brokers: nationwide coverage", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("Required Documents", ST["H2"]),
        Paragraph("• Copy of national ID or passport of insured", ST["Bullet"]),
        Paragraph("• Vehicle registration book or copy", ST["Bullet"]),
        Paragraph("• 4-angle vehicle photos + chassis number + engine number (for online purchase)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Claims Process", ST["H1"])]
    story += [
        Paragraph("Steps After an Accident", ST["H2"]),
        Paragraph("1. Call Shield Auto immediately: 02-xxx-4444 or tap SOS in-app (auto-logs location)", ST["Bullet"]),
        Paragraph("2. Surveyor dispatched: arrives within 30-60 min (BKK) / 60-120 min (upcountry)", ST["Bullet"]),
        Paragraph("3. Surveyor documents damage, issues Accident Report and Repair Authorization", ST["Bullet"]),
        Paragraph("4. Choose an affiliated garage, or use own garage if plan permits", ST["Bullet"]),
        Paragraph("5. Track repair status in real-time via the ShieldAuto app", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("Claims Payment Timeline", ST["H2"]),
    ]
    timelines = [["Type","Condition","Timeline"],
                 ["Affiliated garage repair","Company pays garage directly","No upfront payment required"],
                 ["Non-affiliated garage","Customer pays upfront","Company reimburses within 15 business days"],
                 ["Total loss claim","Total loss confirmed, agreed value","30 business days after settlement"],
                 ["Third-party property claim","Third party settlement confirmed","15 business days"]]
    tl_t = Table(timelines, colWidths=[4*cm,9*cm,4*cm])
    tl_t.setStyle(header_style())
    story += [tl_t, PageBreak()]

    story += [Paragraph("Frequently Asked Questions", ST["H1"])]
    faqs = [
        ("What to do if my car is stolen?","File a police report and notify Shield Auto within 24 hours. The insurer pays the market value of the vehicle at the time of theft."),
        ("What's the difference between 1+ and 1?","SHIELD-1+ adds natural disaster coverage (flood, storm, earthquake) which is excluded from standard SHIELD-1."),
        ("Does the policy cover drunk driving?","Own damage is NOT covered. However, third-party liability is still covered under the compulsory insurance law."),
        ("Can I use my own garage?","Yes, under plans 1 and 1+ subject to conditions. A surveyor must inspect before repairs begin in all cases."),
        ("What happens if I renew late?","The policy lapses and you have no coverage. Any accident during the lapsed period is not covered."),
        ("What can I do in the ShieldAuto app?","Renew insurance, view policy, report accidents (SOS), track repair status, find affiliated garages, and call road assistance."),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("Affiliated Garages and Contact", ST["H1"])]
    story += [
        Paragraph("Shield Auto's 2,500+ affiliated garages include:", ST["Body"]),
        Paragraph("• Grade A Standard Garages: ISO 9001 certified, 1,200 locations nationwide", ST["Bullet"]),
        Paragraph("• Brand Authorized Service Centers: Toyota, Honda, Isuzu, Nissan, Ford (all branches)", ST["Bullet"]),
        Paragraph("• Dealer-approved garages: 300 locations in Bangkok and Greater Bangkok", ST["Bullet"]),
        Spacer(1,0.3*cm),
    ]
    contacts = [["Channel","Details","Hours"],
                ["Call Center / SOS","02-xxx-4444","24/7, every day"],
                ["Email","claim@shieldauto.th","Response < 2 business hours"],
                ["App","ShieldAuto (iOS/Android)","24/7"],
                ["Website","www.shieldauto.th","24/7"],
                ["LINE","@shieldauto","Daily 07:00-22:00 ICT"]]
    ct = Table(contacts, colWidths=[3*cm,7*cm,7*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [Paragraph("© 2024 Shield Auto Insurance Co., Ltd. | OIC License No. 003/2555 | Document SA-EN-2024-v2.1 | Updated: November 1, 2024", ST["Small"])]
    doc.build(story, onFirstPage=page_footer("Shield Auto Insurance"), onLaterPages=page_footer("Shield Auto Insurance"))
    print(f"  Created: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# BANKING: NeoBank Thailand
# ═══════════════════════════════════════════════════════════════════════════════

def build_banking_th(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("นีโอแบงก์ ไทยแลนด์", ST["Title"]),
        Paragraph("ธนาคารดิจิทัล — คู่มือผลิตภัณฑ์และบริการ", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("นีโอแบงก์ ไทยแลนด์ ก่อตั้งปี 2564 ได้รับใบอนุญาตธนาคารพาณิชย์จากธนาคารแห่งประเทศไทย "
                  "เป็นธนาคารดิจิทัลล้วน (Fully Digital Bank) ไม่มีสาขา ให้บริการผ่านแอปมือถือ 100% "
                  "มีลูกค้ากว่า 2.1 ล้านคน ให้บริการบัญชีออมทรัพย์ สินเชื่อ บัตรเดบิต และการลงทุน", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("สารบัญ", ST["H1"]),
    ]
    toc = [["หัวข้อ","หน้า"],
           ["ประเภทบัญชีและผลิตภัณฑ์","2-3"],
           ["ค่าธรรมเนียมและอัตราดอกเบี้ย","4-5"],
           ["การเปิดบัญชีและ KYC","6-7"],
           ["นโยบายความปลอดภัยและความเป็นส่วนตัว","8-9"],
           ["FAQ การธนาคารดิจิทัล","10-11"],
           ["ช่องทางติดต่อและข้อกำหนด","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("ประเภทบัญชีและผลิตภัณฑ์", ST["H1"])]
    products = [["ผลิตภัณฑ์","รหัส","อัตราดอกเบี้ย/ปี","วงเงิน/เงื่อนไข","คุณสมบัติเด่น"],
                ["NeoSave ออมทรัพย์ดิจิทัล","NB-SAV-01","2.50% (ไม่มีขั้นต่ำ)","ไม่มีวงเงินสูงสุด","ฟรีโอนเงินไม่จำกัด 24/7"],
                ["NeoBoost ออมสูง","NB-SAV-02","3.50% (เงิน ≥50,000 THB)","ขั้นต่ำ 50,000 THB","ดอกเบี้ยสูง ถอนได้ทุกวัน"],
                ["NeoFixed ฝากประจำ 3 เดือน","NB-FIX-03M","3.80%","ขั้นต่ำ 10,000 THB","ดอกเบี้ยจ่ายเมื่อครบกำหนด"],
                ["NeoFixed ฝากประจำ 12 เดือน","NB-FIX-12M","4.50%","ขั้นต่ำ 10,000 THB","ดอกเบี้ยสูงสุด เบิกก่อนลด 50%"],
                ["NeoCash สินเชื่อส่วนบุคคล","NB-LOAN-01","อัตราดอกเบี้ย 15-25%/ปี","สูงสุด 500,000 THB","อนุมัติภายใน 1 ชั่วโมง"],
                ["NeoCard บัตรเดบิต","NB-CARD-01","N/A","วงเงินตามยอดในบัญชี","Cashback 0.5% ทุกการใช้จ่าย"],
                ["NeoInvest (กองทุน)","NB-INV-01","ตามกองทุน","ขั้นต่ำ 100 THB","ผ่านแอป พาร์ทเนอร์ กลต."]]
    pr_t = Table(products, colWidths=[3.5*cm,2.5*cm,2.5*cm,3.5*cm,5*cm])
    pr_t.setStyle(header_style())
    story += [pr_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("NeoCard บัตรเดบิต Virtual + Physical", ST["H2"]),
        Paragraph("• Virtual Card: รับทันทีเมื่อเปิดบัญชี ใช้ชำระออนไลน์/แอป Apple Pay/Google Pay", ST["Bullet"]),
        Paragraph("• Physical Card: สั่งผ่านแอป จัดส่งฟรีภายใน 3-5 วันทำการ", ST["Bullet"]),
        Paragraph("• Cashback 0.5% ทุกธุรกรรม สูงสุด 500 THB/เดือน", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("ค่าธรรมเนียมและอัตราดอกเบี้ย", ST["H1"])]
    fees = [["รายการ","ค่าธรรมเนียม","เงื่อนไข"],
            ["เปิดบัญชี","ฟรี","ไม่มีค่าธรรมเนียม"],
            ["โอนเงิน PromptPay","ฟรี ไม่จำกัดครั้ง","24/7 ทุกธนาคาร"],
            ["โอนเงินระหว่างธนาคาร (BAHTNET)","25 THB","สำหรับโอนมูลค่าสูง"],
            ["ค่ารักษาบัญชี","ฟรี","ไม่มีขั้นต่ำยอดคงเหลือ"],
            ["บัตร NeoCard (Physical)","ฟรี","สั่งผ่านแอปได้ 1 ใบฟรี"],
            ["ATM (เครือข่าย NeoATM)","ฟรี 10 ครั้ง/เดือน","ครั้งที่ 11+ ราคา 15 THB"],
            ["ATM ธนาคารอื่น","15 THB/ครั้ง","ทุกธนาคาร"],
            ["แปลงสกุลเงิน FX","Interbank rate + 0.8%","ผ่านแอป NeoXchange"],
            ["สินเชื่อส่วนบุคคล NeoCash","ดอกเบี้ย 15-25%/ปี","Flat rate, 12-60 เดือน"]]
    f_t = Table(fees, colWidths=[5*cm,4*cm,8*cm])
    f_t.setStyle(header_style())
    story += [f_t, PageBreak()]

    story += [Paragraph("การเปิดบัญชีและ KYC (Know Your Customer)", ST["H1"])]
    story += [
        Paragraph("เปิดบัญชีได้ใน 5 นาทีผ่านแอป NeoBank ไม่ต้องไปสาขา", ST["H2"]),
    ]
    steps = [["ขั้นตอน","รายละเอียด","ระยะเวลา"],
             ["1. ดาวน์โหลดแอป","NeoBank TH App — iOS 15+ / Android 10+","2 นาที"],
             ["2. กรอกข้อมูล","ชื่อ-นามสกุล เลขบัตรประชาชน วันเดือนปีเกิด เบอร์โทร อีเมล","3 นาที"],
             ["3. ยืนยันตัวตน eKYC","ถ่ายรูปบัตรประชาชน + selfie (ระบบ AI ตรวจ liveness)","2 นาที"],
             ["4. OTP Verification","รับ OTP ทาง SMS ยืนยันเบอร์มือถือ","1 นาที"],
             ["5. เปิดบัญชี","ระบบอนุมัติอัตโนมัติภายใน 60 วินาที","< 1 นาที"],
             ["6. รับเลขบัญชีและ Virtual Card","พร้อมใช้งานทันที","ทันที"]]
    s_t = Table(steps, colWidths=[3*cm,11*cm,3*cm])
    s_t.setStyle(header_style())
    story += [s_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("คุณสมบัติผู้เปิดบัญชี", ST["H2"]),
        Paragraph("• สัญชาติไทย อายุ 15 ปีขึ้นไป (อายุ 15-17 ปี ต้องมีผู้ปกครองลงนาม)", ST["Bullet"]),
        Paragraph("• บัตรประชาชนไทยที่ยังไม่หมดอายุ", ST["Bullet"]),
        Paragraph("• เบอร์โทรศัพท์มือถือที่ลงทะเบียนในนามตนเอง", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("นโยบายความปลอดภัยและความเป็นส่วนตัว", ST["H1"])]
    story += [
        Paragraph("มาตรการความปลอดภัย", ST["H2"]),
        Paragraph("• การเข้าสู่ระบบ: PIN 6 หลัก + Biometric (Face ID / Fingerprint) + Device Binding", ST["Bullet"]),
        Paragraph("• ธุรกรรมทุกรายการ: ยืนยันด้วย OTP ผ่าน SMS หรือแอปพิเศษสำหรับโอนเกิน 50,000 THB", ST["Bullet"]),
        Paragraph("• การเข้ารหัส: TLS 1.3 สำหรับทุกการสื่อสาร AES-256 สำหรับข้อมูลที่เก็บ", ST["Bullet"]),
        Paragraph("• Fraud Detection AI: ตรวจจับความผิดปกติ real-time และระงับบัญชีทันทีหากพบสัญญาณ", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("นโยบายข้อมูลส่วนบุคคล (PDPA)", ST["H2"]),
        Paragraph("นีโอแบงก์ประมวลผลข้อมูลส่วนบุคคลตามพระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 "
                  "ข้อมูลลูกค้าจัดเก็บในประเทศไทย บน AWS ap-southeast-1 (กรุงเทพฯ region) "
                  "ระยะเก็บรักษา: ข้อมูลธุรกรรม 5 ปี / ข้อมูลบัญชี 10 ปีหลังปิดบัญชี "
                  "ลูกค้าสามารถขอดูและลบข้อมูลได้ที่แอป > บัญชีของฉัน > ข้อมูลส่วนตัว > PDPA Request", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("คำถามที่พบบ่อย (FAQ)", ST["H1"])]
    faqs = [
        ("นีโอแบงก์ปลอดภัยเท่าธนาคารทั่วไปไหม?",
         "ใช่ ได้รับใบอนุญาตจาก ธปท. เงินฝากคุ้มครองโดยสถาบันคุ้มครองเงินฝาก (DPA) สูงสุด 1,000,000 THB/ราย"),
        ("ไม่มีสาขา ถ้ามีปัญหาต้องทำอย่างไร?",
         "ติดต่อผ่านแอป (Chat Support), อีเมล, โทรศัพท์ หรือ LINE ตอบ 24/7 ทุกช่องทาง"),
        ("โอนเงินต่างประเทศได้ไหม?",
         "ได้ผ่านฟีเจอร์ NeoXchange รองรับ 28 สกุลเงิน อัตราแลกเปลี่ยน Interbank + 0.8% ดีกว่าธนาคารทั่วไปเฉลี่ย 40%"),
        ("ขอสินเชื่อ NeoCash ต้องใช้หลักประกันไหม?",
         "ไม่ต้องใช้หลักประกัน (Unsecured Loan) ระบบประเมินจากประวัติการใช้บัญชีและ Credit Score"),
        ("บัตร NeoCard ใช้ในต่างประเทศได้ไหม?",
         "ได้ เป็น Visa Debit รับชำระทั่วโลก ค่าธรรมเนียม FX 0.8% ดีกว่าบัตรเดบิตธนาคารทั่วไป"),
        ("ดอกเบี้ย NeoBoost คิดอย่างไร?",
         "ดอกเบี้ยรายวัน คำนวณจากยอดเงินจริงแต่ละวัน จ่ายเข้าบัญชีทุกวันที่ 1 ของเดือน"),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("ช่องทางติดต่อและข้อกำหนด", ST["H1"])]
    contacts = [["ช่องทาง","รายละเอียด","เวลาทำการ"],
                ["แอป NeoBank Chat","แชทในแอป — ตอบทันที (AI + Human)","24/7"],
                ["Call Center","02-xxx-6600","24/7 ทุกวัน"],
                ["อีเมล","support@neobank.th","ตอบภายใน 2 ชั่วโมง"],
                ["LINE","@neobank.th","24/7"],
                ["เว็บไซต์","www.neobank.th","24/7"]]
    ct = Table(contacts, colWidths=[4*cm,7*cm,6*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [Paragraph("© 2567 นีโอแบงก์ ไทยแลนด์ จำกัด | ใบอนุญาตธนาคาร ธปท. เลขที่ DB-001/2564 | "
                        "เงินฝากคุ้มครอง DPA สูงสุด 1,000,000 THB | อัปเดต 1 พ.ย. 2567", ST["Small"])]
    doc.build(story, onFirstPage=page_footer("นีโอแบงก์ ไทยแลนด์"), onLaterPages=page_footer("นีโอแบงก์ ไทยแลนด์"))
    print(f"  Created: {path}")


def build_banking_en(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("NeoBank Thailand", ST["Title"]),
        Paragraph("Digital Bank — Products and Services Guide", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("NeoBank Thailand, established in 2021 and licensed by the Bank of Thailand, "
                  "is a fully digital bank with no physical branches. All services are delivered "
                  "via mobile app to our 2.1 million customers. Products include digital savings accounts, "
                  "personal loans, debit cards, and investment services.", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("Table of Contents", ST["H1"]),
    ]
    toc = [["Section","Page"],
           ["Account Types and Products","2-3"],
           ["Fee Schedule and Interest Rates","4-5"],
           ["Account Opening and eKYC","6-7"],
           ["Security and Privacy Policy","8-9"],
           ["FAQ — Digital Banking","10-11"],
           ["Contact and Terms","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("Account Types and Products", ST["H1"])]
    products = [["Product","Code","Interest Rate p.a.","Limit / Condition","Key Feature"],
                ["NeoSave Digital Savings","NB-SAV-01","2.50% (no minimum)","No max balance","Free unlimited transfers 24/7"],
                ["NeoBoost High-Yield Savings","NB-SAV-02","3.50% (≥THB 50,000)","Min. THB 50,000","High yield, withdraw anytime"],
                ["NeoFixed 3-Month Term","NB-FIX-03M","3.80%","Min. THB 10,000","Interest paid at maturity"],
                ["NeoFixed 12-Month Term","NB-FIX-12M","4.50%","Min. THB 10,000","Highest rate; early break: -50% interest"],
                ["NeoCash Personal Loan","NB-LOAN-01","15-25% p.a.","Up to THB 500,000","Approval within 1 hour"],
                ["NeoCard Debit Card","NB-CARD-01","N/A","Balance-linked limit","0.5% cashback on all spending"],
                ["NeoInvest (Mutual Funds)","NB-INV-01","Per fund performance","Min. THB 100","In-app, SEC-licensed partner"]]
    pr_t = Table(products, colWidths=[3.5*cm,2.5*cm,2.5*cm,3.5*cm,5*cm])
    pr_t.setStyle(header_style())
    story += [pr_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("NeoCard — Virtual + Physical Debit Card", ST["H2"]),
        Paragraph("• Virtual Card: issued instantly upon account opening; use online, Apple Pay, Google Pay", ST["Bullet"]),
        Paragraph("• Physical Card: order via app; free delivery in 3-5 business days", ST["Bullet"]),
        Paragraph("• 0.5% cashback on all transactions, up to THB 500/month", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Fee Schedule and Interest Rates", ST["H1"])]
    fees = [["Item","Fee","Conditions"],
            ["Account opening","Free","No fees"],
            ["PromptPay transfer","Free, unlimited","24/7, all banks"],
            ["Interbank transfer (BAHTNET)","THB 25","For large-value transfers"],
            ["Monthly account maintenance","Free","No minimum balance required"],
            ["NeoCard (Physical)","Free","1 free card per account"],
            ["NeoATM network withdrawal","Free 10x/month","11th+ at THB 15/transaction"],
            ["Other bank ATM","THB 15/transaction","All banks"],
            ["FX conversion (NeoXchange)","Interbank rate + 0.8%","In-app FX service"],
            ["NeoCash personal loan","15-25% p.a.","Flat rate, 12-60 month tenure"]]
    f_t = Table(fees, colWidths=[5*cm,4*cm,8*cm])
    f_t.setStyle(header_style())
    story += [f_t, PageBreak()]

    story += [Paragraph("Account Opening and eKYC", ST["H1"])]
    story += [Paragraph("Open an account in under 5 minutes, entirely through the NeoBank app — no branch visit required.", ST["H2"])]
    steps = [["Step","Description","Time"],
             ["1. Download App","NeoBank TH App — iOS 15+ / Android 10+","2 min"],
             ["2. Enter Details","Full name, national ID, date of birth, phone, email","3 min"],
             ["3. eKYC Verification","Photo of national ID + selfie (AI liveness check)","2 min"],
             ["4. OTP Verification","Receive OTP via SMS to verify mobile number","1 min"],
             ["5. Account Approval","Automated approval within 60 seconds","< 1 min"],
             ["6. Receive Account & Virtual Card","Instantly ready to use","Immediate"]]
    s_t = Table(steps, colWidths=[3*cm,11*cm,3*cm])
    s_t.setStyle(header_style())
    story += [s_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Eligibility Requirements", ST["H2"]),
        Paragraph("• Thai nationality, age 15 and above (ages 15-17 require guardian co-signature)", ST["Bullet"]),
        Paragraph("• Valid Thai national ID (not expired)", ST["Bullet"]),
        Paragraph("• Mobile number registered in the applicant's own name", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Security and Privacy Policy", ST["H1"])]
    story += [
        Paragraph("Security Measures", ST["H2"]),
        Paragraph("• Login: 6-digit PIN + biometric (Face ID/fingerprint) + device binding", ST["Bullet"]),
        Paragraph("• Every transaction: OTP confirmation via SMS or in-app for transfers >THB 50,000", ST["Bullet"]),
        Paragraph("• Encryption: TLS 1.3 for all communications; AES-256 for stored data", ST["Bullet"]),
        Paragraph("• AI fraud detection: real-time anomaly detection with immediate account freeze on suspicious activity", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("Personal Data Protection Act (PDPA) Compliance", ST["H2"]),
        Paragraph("NeoBank processes personal data in compliance with Thailand's PDPA B.E. 2562. "
                  "Customer data is stored in Thailand on AWS ap-southeast-1 (Bangkok region). "
                  "Retention: transaction data 5 years; account data 10 years after closure. "
                  "Customers can request data access or deletion via App > My Account > Privacy > PDPA Request.", ST["Body"]),
        PageBreak(),
    ]

    story += [Paragraph("Frequently Asked Questions", ST["H1"])]
    faqs = [
        ("Is NeoBank as safe as a traditional bank?","Yes. We are BOT-licensed and deposits are protected by the Deposit Protection Agency (DPA) up to THB 1,000,000 per depositor."),
        ("No branches — what if I need help?","Support available 24/7 via in-app chat (AI + human), phone, email, and LINE."),
        ("Can I transfer money internationally?","Yes, via NeoXchange supporting 28 currencies. FX rate: interbank + 0.8%, which is on average 40% better than traditional banks."),
        ("Does NeoCash require collateral?","No. It is an unsecured personal loan. Approval is based on account usage history and credit score."),
        ("Can I use NeoCard abroad?","Yes. NeoCard is a Visa Debit accepted worldwide. FX fee: 0.8%, competitive vs. standard bank debit cards."),
        ("How is NeoBoost interest calculated?","Interest accrues daily based on the actual daily balance and is credited to your account on the 1st of each month."),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("Contact and Terms", ST["H1"])]
    contacts = [["Channel","Details","Hours"],
                ["NeoBank App Chat","In-app chat (AI + Human)","24/7"],
                ["Call Center","02-xxx-6600","24/7"],
                ["Email","support@neobank.th","Response < 2 hours"],
                ["LINE","@neobank.th","24/7"],
                ["Website","www.neobank.th","24/7"]]
    ct = Table(contacts, colWidths=[4*cm,7*cm,6*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [Paragraph("© 2024 NeoBank Thailand Co., Ltd. | BOT Digital Bank License DB-001/2021 | "
                        "DPA Deposit Protection up to THB 1,000,000 | Document NB-EN-2024-v1.5 | Updated: November 1, 2024", ST["Small"])]
    doc.build(story, onFirstPage=page_footer("NeoBank Thailand"), onLaterPages=page_footer("NeoBank Thailand"))
    print(f"  Created: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# IT SERVICE: DataStream Solutions
# ═══════════════════════════════════════════════════════════════════════════════

def build_itservice_th(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("DataStream Solutions", ST["Title"]),
        Paragraph("บริษัท IT Consulting และ Managed Services — คู่มือบริการ", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("DataStream Solutions ก่อตั้งปี 2556 ให้บริการ IT Consulting, Managed Services, "
                  "Cloud Infrastructure, Cybersecurity และ Data Analytics แก่องค์กรในประเทศไทยและ ASEAN "
                  "ทีมผู้เชี่ยวชาญ 180 คน มีใบรับรอง AWS Premier Partner, Microsoft Gold Partner และ ISO 27001", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("สารบัญ", ST["H1"]),
    ]
    toc = [["หัวข้อ","หน้า"],
           ["แคตาล็อกบริการและราคา","2-3"],
           ["ระดับ SLA และข้อตกลงบริการ","4-5"],
           ["กระบวนการดำเนินโครงการ","6-7"],
           ["นโยบายความปลอดภัยและ Compliance","8-9"],
           ["FAQ IT Services","10-11"],
           ["ช่องทางติดต่อและทีมงาน","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("แคตาล็อกบริการและราคา", ST["H1"])]
    services = [["บริการ","รหัส","รายละเอียด","ราคาเริ่มต้น","Model"],
                ["Cloud Migration","DS-CLOUD-01","ย้ายระบบไปยัง AWS/Azure/GCP","150,000 THB","Fixed Price"],
                ["Managed Cloud (AWS/Azure)","DS-MCLOUD-01","ดูแลระบบ Cloud 24/7 + Optimization","25,000 THB/เดือน","Monthly"],
                ["Cybersecurity Assessment","DS-SEC-01","VAPT, Penetration Testing, ISO 27001 Readiness","80,000 THB","Per Assessment"],
                ["SOC as a Service","DS-SOC-01","Security Operations Center ตลอด 24 ชม.","45,000 THB/เดือน","Monthly"],
                ["Data Analytics Platform","DS-DATA-01","BI Dashboard, Data Lake, ETL Pipeline","200,000 THB","Project-based"],
                ["IT Consulting","DS-CONS-01","ที่ปรึกษา IT Architecture & Strategy","8,000 THB/วัน","Daily Rate"],
                ["Help Desk (Tier 1-3)","DS-HD-01","IT Support ผู้ใช้งาน ครอบคลุม 200 Users","35,000 THB/เดือน","Monthly"],
                ["Network Infrastructure","DS-NET-01","ออกแบบและติดตั้ง LAN/WAN/SD-WAN","120,000 THB","Fixed Price"]]
    sv_t = Table(services, colWidths=[3.5*cm,2.5*cm,5*cm,2.5*cm,3.5*cm])
    sv_t.setStyle(header_style())
    story += [sv_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("ความเชี่ยวชาญและใบรับรอง", ST["H2"]),
        Paragraph("• AWS Premier Consulting Partner: ได้รับการรับรองในระดับสูงสุดจาก AWS", ST["Bullet"]),
        Paragraph("• Microsoft Gold Partner: ด้าน Cloud Platform, Data Analytics, Security", ST["Bullet"]),
        Paragraph("• ISO/IEC 27001:2022: ระบบบริหารจัดการความมั่นคงปลอดภัยสารสนเทศ", ST["Bullet"]),
        Paragraph("• CISA/CISSP Certified Engineers: 12 คน / PMP Certified Project Managers: 8 คน", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("ระดับ SLA และข้อตกลงบริการ", ST["H1"])]
    sla = [["ระดับ SLA","บริการที่รวม","Response Time","Resolution Time (P1)","Uptime SLA","ราคา/เดือน"],
           ["Bronze","Help Desk + Monitoring","8 ชั่วโมง (วันทำการ)","24 ชั่วโมง","99.0%","35,000 THB"],
           ["Silver","Bronze + Backup + Patching","4 ชั่วโมง (วันทำการ)","8 ชั่วโมง","99.5%","60,000 THB"],
           ["Gold","Silver + SOC + DR Planning","2 ชั่วโมง (24/7)","4 ชั่วโมง","99.9%","95,000 THB"],
           ["Platinum","Gold + Dedicated Engineer + CAB","30 นาที (24/7)","2 ชั่วโมง","99.99%","180,000 THB"]]
    sla_t = Table(sla, colWidths=[2.5*cm,5*cm,3*cm,3*cm,2.5*cm,2*cm])
    sla_t.setStyle(header_style())
    story += [sla_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("นโยบาย SLA Breach Credit", ST["H2"]),
        Paragraph("• Uptime ต่ำกว่า SLA 0.1-0.5%: เครดิต 5% ของค่าบริการรายเดือน", ST["Bullet"]),
        Paragraph("• Uptime ต่ำกว่า SLA 0.5-1.0%: เครดิต 10% ของค่าบริการรายเดือน", ST["Bullet"]),
        Paragraph("• Uptime ต่ำกว่า SLA >1.0%: เครดิต 25% ของค่าบริการรายเดือน", ST["Bullet"]),
        Paragraph("• เครดิตสะสมได้สูงสุด 50% ของค่าบริการต่อเดือน และใช้หักจากใบแจ้งหนี้เดือนถัดไป", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("กระบวนการดำเนินโครงการ", ST["H1"])]
    story += [Paragraph("DataStream ใช้ Project Management แบบ PRINCE2 + Agile Hybrid ดังนี้:", ST["Body"])]
    process = [["ระยะ","รายละเอียด","Deliverable","ระยะเวลา"],
               ["1. Discovery","สำรวจและเก็บ Requirements ปัจจุบัน","AS-IS Report + Gap Analysis","1-2 สัปดาห์"],
               ["2. Design","ออกแบบสถาปัตยกรรมและแผนการดำเนินงาน","Architecture Design + Project Plan","1-2 สัปดาห์"],
               ["3. Build/Migrate","ดำเนินการตาม sprint 2-week intervals","Sprint Review per cycle","4-12 สัปดาห์"],
               ["4. Test & UAT","ทดสอบระบบ และ User Acceptance Testing","UAT Sign-off Document","1-2 สัปดาห์"],
               ["5. Go-live","Launch พร้อม Hypercare 2 สัปดาห์","Go-live Checklist","1 สัปดาห์"],
               ["6. Handover","ส่งมอบเอกสารและ Training ทีมลูกค้า","Technical Documentation + Training","1 สัปดาห์"]]
    p_t = Table(process, colWidths=[2.5*cm,7*cm,4*cm,3.5*cm])
    p_t.setStyle(header_style())
    story += [p_t, PageBreak()]

    story += [Paragraph("นโยบายความปลอดภัยและ Compliance", ST["H1"])]
    story += [
        Paragraph("ความปลอดภัยในการให้บริการ", ST["H2"]),
        Paragraph("• ข้อมูลลูกค้าถูกแยกจากกันโดยสิ้นเชิง (Strict Tenant Isolation)", ST["Bullet"]),
        Paragraph("• วิศวกรทุกคนต้องผ่านการตรวจสอบประวัติอาชญากรรมและลงนาม NDA", ST["Bullet"]),
        Paragraph("• การเข้าถึงระบบลูกค้า: ต้องได้รับ Approval ล่วงหน้า Privileged Access Management (PAM)", ST["Bullet"]),
        Paragraph("• Log การเข้าถึงทุกครั้ง เก็บบันทึกอย่างน้อย 1 ปี และพร้อม Audit ตลอดเวลา", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("Compliance ที่รองรับ", ST["H2"]),
        Paragraph("• ISO/IEC 27001:2022 — Information Security Management", ST["Bullet"]),
        Paragraph("• PDPA (พ.ร.บ.คุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562)", ST["Bullet"]),
        Paragraph("• BOT Cyber Resilience Assessment Framework (สำหรับลูกค้าสถาบันการเงิน)", ST["Bullet"]),
        Paragraph("• PCI DSS Level 1 (สำหรับโปรเจกต์ที่เกี่ยวข้องกับข้อมูลบัตรเครดิต)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("คำถามที่พบบ่อย (FAQ)", ST["H1"])]
    faqs = [
        ("DataStream รับโปรเจกต์ขนาดเล็กไหม?",
         "รับ ขั้นต่ำสำหรับโปรเจกต์ Fixed Price คือ 50,000 THB สำหรับบริการ Consulting รายวัน ไม่มีขั้นต่ำ"),
        ("ถ้าไม่พอใจผลงาน ทำอย่างไรได้บ้าง?",
         "มีกระบวนการ Escalation อย่างเป็นทางการ: Account Manager > Delivery Manager > CEO ภายใน 48 ชั่วโมง"),
        ("DataStream มีทีมในต่างจังหวัดไหม?",
         "มีทีมในกรุงเทพฯ (สำนักงานใหญ่) เชียงใหม่ และระยอง สำหรับพื้นที่อื่นส่ง Engineer On-site ได้"),
        ("ค่าบริการรวม License Software หรือไม่?",
         "ส่วนใหญ่ไม่รวม License Software (AWS, Microsoft, etc.) เนื่องจากอยู่ในชื่อลูกค้า DataStream ช่วย Negotiate ราคา Partner ได้"),
        ("ทำ Penetration Test บ่อยแค่ไหน?",
         "แนะนำปีละ 2 ครั้ง (ทุกครึ่งปี) สำหรับระบบ Production และหลัง Major Release ทุกครั้ง"),
        ("มีบริการ On-call หลังจาก Go-live ไหม?",
         "ใช่ ทุกโปรเจกต์มี Hypercare 2 สัปดาห์ฟรี หลังจากนั้นสามารถต่อสัญญา Managed Services ได้"),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("ช่องทางติดต่อและทีมงาน", ST["H1"])]
    contacts = [["ช่องทาง","รายละเอียด","เวลาทำการ"],
                ["โทรศัพท์","02-xxx-8833","จ.-ศ. 08:00-18:00 น."],
                ["Emergency Hotline","02-xxx-8800","24/7 (สำหรับลูกค้า Gold/Platinum)"],
                ["อีเมล","sales@datastream.th","ตอบภายใน 4 ชั่วโมง (วันทำการ)"],
                ["Support Ticket","support.datastream.th","24/7 (portal)"],
                ["เว็บไซต์","www.datastream.th","24/7"],
                ["LinkedIn","DataStream Solutions Thailand","ข่าวสารและ Case Studies"]]
    ct = Table(contacts, colWidths=[3.5*cm,7*cm,6.5*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [Paragraph("© 2567 DataStream Solutions (Thailand) Co., Ltd. | เลขทะเบียน: 0105556089123 | "
                        "AWS Premier Partner | Microsoft Gold Partner | ISO 27001:2022 | อัปเดต 1 พ.ย. 2567", ST["Small"])]
    doc.build(story, onFirstPage=page_footer("DataStream Solutions"), onLaterPages=page_footer("DataStream Solutions"))
    print(f"  Created: {path}")


def build_itservice_en(path: str):
    doc = new_doc(path)
    story = []

    story += [
        Spacer(1,1.5*cm),
        Paragraph("DataStream Solutions", ST["Title"]),
        Paragraph("IT Consulting & Managed Services — Service Guide", ST["Subtitle"]),
        HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=10),
        Spacer(1,0.5*cm),
        Paragraph("DataStream Solutions, founded in 2013, provides IT Consulting, Managed Services, "
                  "Cloud Infrastructure, Cybersecurity, and Data Analytics to organizations across "
                  "Thailand and ASEAN. Our 180-person team holds AWS Premier Partner, "
                  "Microsoft Gold Partner, and ISO 27001:2022 certifications.", ST["Body"]),
        Spacer(1,0.5*cm),
        Paragraph("Table of Contents", ST["H1"]),
    ]
    toc = [["Section","Page"],
           ["Service Catalog and Pricing","2-3"],
           ["SLA Tiers and Service Agreements","4-5"],
           ["Project Delivery Process","6-7"],
           ["Security and Compliance Policy","8-9"],
           ["FAQ — IT Services","10-11"],
           ["Contact and Team","12"]]
    t = Table(toc, colWidths=[13*cm,3*cm])
    t.setStyle(header_style())
    story += [t, PageBreak()]

    story += [Paragraph("Service Catalog and Pricing", ST["H1"])]
    services = [["Service","Code","Description","Starting Price","Engagement Model"],
                ["Cloud Migration","DS-CLOUD-01","Migrate workloads to AWS/Azure/GCP","THB 150,000","Fixed Price"],
                ["Managed Cloud","DS-MCLOUD-01","24/7 cloud ops + cost optimization","THB 25,000/mo","Monthly"],
                ["Cybersecurity Assessment","DS-SEC-01","VAPT, Pen Testing, ISO 27001 Readiness","THB 80,000","Per Assessment"],
                ["SOC as a Service","DS-SOC-01","24/7 Security Operations Center","THB 45,000/mo","Monthly"],
                ["Data Analytics Platform","DS-DATA-01","BI Dashboard, Data Lake, ETL Pipeline","THB 200,000","Project-based"],
                ["IT Consulting","DS-CONS-01","IT Architecture & Strategy Advisory","THB 8,000/day","Daily Rate"],
                ["Help Desk (Tier 1-3)","DS-HD-01","End-user IT support, 200 users covered","THB 35,000/mo","Monthly"],
                ["Network Infrastructure","DS-NET-01","Design & deploy LAN/WAN/SD-WAN","THB 120,000","Fixed Price"]]
    sv_t = Table(services, colWidths=[3.5*cm,2.5*cm,4.5*cm,2.5*cm,4*cm])
    sv_t.setStyle(header_style())
    story += [sv_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("Certifications and Expertise", ST["H2"]),
        Paragraph("• AWS Premier Consulting Partner: highest tier recognition from Amazon Web Services", ST["Bullet"]),
        Paragraph("• Microsoft Gold Partner: Cloud Platform, Data Analytics, Security specializations", ST["Bullet"]),
        Paragraph("• ISO/IEC 27001:2022: Information Security Management System certified", ST["Bullet"]),
        Paragraph("• 12 CISA/CISSP Certified Engineers; 8 PMP Certified Project Managers", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("SLA Tiers and Service Agreements", ST["H1"])]
    sla = [["SLA Tier","Included Services","Response Time","Resolution (P1)","Uptime SLA","Monthly Fee"],
           ["Bronze","Help Desk + Monitoring","8 hrs (business hrs)","24 hours","99.0%","THB 35,000"],
           ["Silver","Bronze + Backup + Patching","4 hrs (business hrs)","8 hours","99.5%","THB 60,000"],
           ["Gold","Silver + SOC + DR Planning","2 hrs (24/7)","4 hours","99.9%","THB 95,000"],
           ["Platinum","Gold + Dedicated Engineer + CAB","30 min (24/7)","2 hours","99.99%","THB 180,000"]]
    sla_t = Table(sla, colWidths=[2.5*cm,5*cm,3*cm,2.5*cm,2.5*cm,2.5*cm])
    sla_t.setStyle(header_style())
    story += [sla_t, Spacer(1,0.3*cm)]
    story += [
        Paragraph("SLA Breach Credit Policy", ST["H2"]),
        Paragraph("• Uptime below SLA by 0.1-0.5%: credit 5% of monthly fee", ST["Bullet"]),
        Paragraph("• Uptime below SLA by 0.5-1.0%: credit 10% of monthly fee", ST["Bullet"]),
        Paragraph("• Uptime below SLA by >1.0%: credit 25% of monthly fee", ST["Bullet"]),
        Paragraph("• Maximum cumulative credit: 50% of monthly fee; applied against next invoice", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Project Delivery Process", ST["H1"])]
    story += [Paragraph("DataStream uses a PRINCE2 + Agile Hybrid project management methodology:", ST["Body"])]
    process = [["Phase","Description","Deliverable","Duration"],
               ["1. Discovery","Survey current state, gather requirements","AS-IS Report + Gap Analysis","1-2 weeks"],
               ["2. Design","Architect solution and create project plan","Architecture Design + Project Plan","1-2 weeks"],
               ["3. Build/Migrate","Execute in 2-week sprint cycles","Sprint Review per cycle","4-12 weeks"],
               ["4. Test & UAT","System testing and User Acceptance Testing","UAT Sign-off Document","1-2 weeks"],
               ["5. Go-live","Launch with 2-week Hypercare period","Go-live Checklist","1 week"],
               ["6. Handover","Documentation delivery and client team training","Technical Docs + Training","1 week"]]
    p_t = Table(process, colWidths=[2.5*cm,7*cm,4*cm,3.5*cm])
    p_t.setStyle(header_style())
    story += [p_t, PageBreak()]

    story += [Paragraph("Security and Compliance Policy", ST["H1"])]
    story += [
        Paragraph("Service Security Practices", ST["H2"]),
        Paragraph("• Strict tenant isolation: all client data kept completely separate", ST["Bullet"]),
        Paragraph("• All engineers undergo background checks and sign NDA before client access", ST["Bullet"]),
        Paragraph("• Client system access requires advance approval via Privileged Access Management (PAM)", ST["Bullet"]),
        Paragraph("• All access sessions are logged; logs retained for minimum 1 year; audit-ready at all times", ST["Bullet"]),
        Spacer(1,0.3*cm),
        Paragraph("Compliance Frameworks Supported", ST["H2"]),
        Paragraph("• ISO/IEC 27001:2022 — Information Security Management", ST["Bullet"]),
        Paragraph("• Thailand PDPA B.E. 2562 — Personal Data Protection Act", ST["Bullet"]),
        Paragraph("• BOT Cyber Resilience Assessment Framework (for financial institution clients)", ST["Bullet"]),
        Paragraph("• PCI DSS Level 1 (for projects handling cardholder data)", ST["Bullet"]),
        PageBreak(),
    ]

    story += [Paragraph("Frequently Asked Questions", ST["H1"])]
    faqs = [
        ("Does DataStream take small projects?","Yes. Minimum project size for fixed-price engagements is THB 50,000. Consulting day rates have no minimum."),
        ("What if I'm not satisfied with the work?","A formal escalation process is in place: Account Manager → Delivery Manager → CEO, resolved within 48 hours."),
        ("Does DataStream have upcountry presence?","We have offices in Bangkok (HQ), Chiang Mai, and Rayong. On-site engineers can be dispatched elsewhere."),
        ("Are software license costs included?","Typically not — licenses are held in the client's name. DataStream can negotiate partner pricing on your behalf."),
        ("How often should penetration testing be done?","We recommend twice per year (every 6 months) for production systems and after every major release."),
        ("Is post-go-live support included?","Yes. Every project includes a 2-week free Hypercare period. Ongoing support is available via Managed Services contracts."),
    ]
    for i,(q,a) in enumerate(faqs,1):
        story += [Paragraph(f"Q{i}: {q}", ST["BodyBold"]), Paragraph(f"A: {a}", ST["Body"]), Spacer(1,0.1*cm)]
    story.append(PageBreak())

    story += [Paragraph("Contact and Team", ST["H1"])]
    contacts = [["Channel","Details","Hours"],
                ["Phone","02-xxx-8833","Mon-Fri 08:00-18:00 ICT"],
                ["Emergency Hotline","02-xxx-8800","24/7 (Gold/Platinum clients)"],
                ["Email","sales@datastream.th","Response < 4 hours (business days)"],
                ["Support Portal","support.datastream.th","24/7"],
                ["Website","www.datastream.th","24/7"],
                ["LinkedIn","DataStream Solutions Thailand","News and Case Studies"]]
    ct = Table(contacts, colWidths=[3.5*cm,7*cm,6.5*cm])
    ct.setStyle(header_style())
    story += [ct, Spacer(1,0.4*cm)]
    story += [Paragraph("© 2024 DataStream Solutions (Thailand) Co., Ltd. | Reg. No. 0105556089123 | "
                        "AWS Premier Partner | Microsoft Gold Partner | ISO 27001:2022 | Document DS-EN-2024-v2.3 | Updated: November 1, 2024", ST["Small"])]
    doc.build(story, onFirstPage=page_footer("DataStream Solutions"), onLaterPages=page_footer("DataStream Solutions"))
    print(f"  Created: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)

    print("Generating all PDF documents...\n")

    print("=== TechNest Thailand ===")
    build_thai_pdf("docs/technest_th.pdf")
    build_english_pdf("docs/technest_en.pdf")
    build_mixed_pdf("docs/technest_mixed.pdf")


    print("=== E-Commerce Set 1: StyleHub Thailand ===")
    build_stylehub_th("docs/stylehub_th.pdf")
    build_stylehub_en("docs/stylehub_en.pdf")

    print("=== E-Commerce Set 2: TechMart TH ===")
    build_techmart_th("docs/techmart_th.pdf")
    build_techmart_en("docs/techmart_en.pdf")

    print("=== Legal: Krung Thai Legal Associates ===")
    build_legal_th("docs/krungthai_legal_th.pdf")
    build_legal_en("docs/krungthai_legal_en.pdf")

    print("=== Investment: Alpha Capital Thailand ===")
    build_investment_th("docs/alphacapital_th.pdf")
    build_investment_en("docs/alphacapital_en.pdf")

    print("=== Insurance Set 1: ThaiLife Plus ===")
    build_insurance1_th("docs/thailife_th.pdf")
    build_insurance1_en("docs/thailife_en.pdf")

    print("=== Insurance Set 2: Shield Auto Insurance ===")
    build_insurance2_th("docs/shieldauto_th.pdf")
    build_insurance2_en("docs/shieldauto_en.pdf")

    print("=== Banking: NeoBank Thailand ===")
    build_banking_th("docs/neobank_th.pdf")
    build_banking_en("docs/neobank_en.pdf")

    print("=== IT Service: DataStream Solutions ===")
    build_itservice_th("docs/datastream_th.pdf")
    build_itservice_en("docs/datastream_en.pdf")

    print("\nAll 16 PDFs generated successfully!")
    for fname in [
        "stylehub_th.pdf","stylehub_en.pdf",
        "techmart_th.pdf","techmart_en.pdf",
        "krungthai_legal_th.pdf","krungthai_legal_en.pdf",
        "alphacapital_th.pdf","alphacapital_en.pdf",
        "thailife_th.pdf","thailife_en.pdf",
        "shieldauto_th.pdf","shieldauto_en.pdf",
        "neobank_th.pdf","neobank_en.pdf",
        "datastream_th.pdf","datastream_en.pdf",
    ]:
        fpath = f"docs/{fname}"
        if os.path.exists(fpath):
            size_kb = os.path.getsize(fpath) // 1024
            print(f"  {fpath}: {size_kb} KB")
