"""Generate printable client templates -> assets/downloads/*.pdf

    pip install reportlab && python3 _tools/make_pdfs.py

Letter (US/Canada) and A4 (UK/Australia/elsewhere), portrait.
While app_store_id in _config.yml is empty the footer only says "Free template from myclientbook.app".
After release, set app_store_id (and app_store_pt) and run this again: each page gets a small QR code
to the App Store (ct=pdf-record-card).
"""
import pathlib, re
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "downloads"

INK = HexColor("#141414")
MUTED = HexColor("#6b6e76")
LINE = HexColor("#d8d6d0")
ACCENT = HexColor("#4a6fea")
SOFT = HexColor("#f3f2ee")

config = (ROOT / "_config.yml").read_text()
APP_ID = re.search(r'^app_store_id:\s*"(\d*)"', config, re.M).group(1)
PT = re.search(r'^app_store_pt:\s*"(\d*)"', config, re.M).group(1)


def store_url(ct):
    url = f"https://apps.apple.com/app/apple-store/id{APP_ID}"
    return url + (f"?pt={PT}&ct={ct}&mt=8" if PT else "")


def qr(c, url, x, y, size):
    w = QrCodeWidget(url, barLevel="M")
    x0, y0, x1, y1 = w.getBounds()
    d = Drawing(size, size, transform=[size / (x1 - x0), 0, 0, size / (y1 - y0), 0, 0])
    d.add(w)
    renderPDF.draw(d, c, x, y)


def footer(c, W, M, ct):
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(M, 22, "Free template from myclientbook.app")
    if APP_ID:
        qs = 34
        qr(c, store_url(ct), W - M - qs, 10, qs)
        c.drawRightString(W - M - qs - 6, 27, "Keep client cards on your phone —")
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(W - M - qs - 6, 17, "Client Book for iPhone")


def title(c, W, H, M, text, sub):
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(M, H - M - 16, text)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9.5)
    c.drawString(M, H - M - 32, sub)


def section(c, M, W, y, text):
    """Section label with a thin accent rule. Returns the y below it."""
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(M, y, text.upper())
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.8)
    c.line(M + c.stringWidth(text.upper(), "Helvetica-Bold", 9) + 8, y + 3, W - M, y + 3)
    return y - 22


def field(c, x, y, w, label, h=22):
    """Label above a write-in line."""
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(x, y, label)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.7)
    c.line(x, y - h + 6, x + w, y - h + 6)


def box(c, x, y, w, h, label):
    """Label above an open writing box (y = top)."""
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(x, y, label)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.7)
    c.roundRect(x, y - h - 4, w, h, 5, stroke=1, fill=0)


def checks(c, x, y, label, options):
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(x, y, label)
    x += c.stringWidth(label, "Helvetica", 8) + 10
    c.setFillColor(INK)
    c.setFont("Helvetica", 9)
    for o in options:
        c.setStrokeColor(MUTED)
        c.setLineWidth(0.7)
        c.rect(x, y - 1, 8, 8, stroke=1, fill=0)
        c.drawString(x + 12, y, o)
        x += 12 + c.stringWidth(o, "Helvetica", 9) + 16


def card_page(c, size):
    W, H = size
    M = 40
    G = 18  # gap between columns
    title(c, W, H, M, "Client Record Card",
          "Keep one card per client. Update it at every visit and keep it somewhere private.")
    y = H - M - 70
    col = (W - 2 * M - G) / 2

    y = section(c, M, W, y, "Client details")
    field(c, M, y, W - 2 * M, "Full name")
    y -= 34
    field(c, M, y, col, "Phone")
    field(c, M + col + G, y, col, "Email")
    y -= 34
    field(c, M, y, col, "Birthday")
    field(c, M + col + G, y, col, "First visit")
    y -= 34
    field(c, M, y, W - 2 * M, "Address")
    y -= 32
    checks(c, M, y, "Preferred contact", ["Call", "Text", "Email"])
    checks(c, M + col + G, y, "OK to send reminders", ["Yes", "No"])
    y -= 26
    field(c, M, y, W - 2 * M, "How did you hear about us?")
    y -= 44

    y = section(c, M, W, y, "Health & safety")
    field(c, M, y, W - 2 * M, "Allergies or sensitivities (products, latex, fragrance…)")
    y -= 34
    field(c, M, y, W - 2 * M, "Health notes relevant to treatments (skin or scalp conditions, medication, pregnancy…)")
    y -= 34
    field(c, M, y, col * 0.62, "Patch test date")
    field(c, M + col * 0.62 + G, y, col * 0.75, "Product")
    field(c, M + col * 1.37 + 2 * G, y, W - 2 * M - col * 1.37 - 2 * G, "Result")
    y -= 44

    y = section(c, M, W, y, "Preferences")
    field(c, M, y, W - 2 * M, "Usual services")
    y -= 34
    field(c, M, y, W - 2 * M, "Products, colors, shapes or styles they like")
    y -= 34
    field(c, M, y, W - 2 * M, "Things to avoid")
    y -= 40
    box(c, M, y, W - 2 * M, 72, "Notes (personality, family, what you talked about — anything that helps next time)")
    y -= 104

    c.setFillColor(MUTED)
    c.setFont("Helvetica-Oblique", 8.5)
    c.drawString(M, y, "I confirm the information above is correct and I'll let you know if anything changes.")
    y -= 30
    field(c, M, y, col, "Client signature")
    field(c, M + col + G, y, col * 0.55, "Date")
    footer(c, W, M, "pdf-record-card")


def log_page(c, size):
    W, H = size
    M = 40
    title(c, W, H, M, "Visit Log", "One row per visit: what you did, what you used and what to remember next time.")
    y = H - M - 62
    field(c, M, y, (W - 2 * M) * 0.6, "Client name")
    y -= 38
    cols = [("Date", 0.12), ("Service", 0.22), ("Products / formula", 0.30), ("Price", 0.10), ("Notes for next time", 0.26)]
    tw = W - 2 * M
    rh = 30
    bottom = 50
    rows = int((y - 20 - bottom) // rh)
    # header
    c.setFillColor(SOFT)
    c.roundRect(M, y - 18, tw, 22, 4, stroke=0, fill=1)
    x = M
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8.5)
    for name, frac in cols:
        c.drawString(x + 6, y - 11, name)
        x += tw * frac
    y -= 18
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    top = y
    for r in range(rows + 1):
        c.line(M, y - r * rh, M + tw, y - r * rh)
    x = M
    for name, frac in cols[:-1]:
        x += tw * frac
        c.line(x, top, x, top - rows * rh)
    footer(c, W, M, "pdf-record-card")


def make(size, name):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    c = canvas.Canvas(str(path), pagesize=size)
    c.setTitle("Client Record Card — free printable template")
    c.setAuthor("Client Book · myclientbook.app")
    c.setSubject("Client record card and visit log for hair, nail, lash, beauty and wellness pros")
    card_page(c, size)
    c.showPage()
    log_page(c, size)
    c.showPage()
    c.save()
    print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    make(letter, "client-record-card-letter.pdf")
    make(A4, "client-record-card-a4.pdf")
