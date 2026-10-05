import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable
)
from backend.config import REPORTS_FOLDER

BRAND_VIOLET = colors.HexColor("#8b5cf6")
BRAND_VIOLET_DARK = colors.HexColor("#6d28d9")
BRAND_INK = colors.HexColor("#0a0916")
BRAND_SURFACE = colors.HexColor("#f5f3ff")
BRAND_BORDER = colors.HexColor("#e2e0f0")
BRAND_MUTED = colors.HexColor("#6b7280")
BRAND_SUCCESS = colors.HexColor("#22c55e")
BRAND_DANGER = colors.HexColor("#ef4444")
BRAND_WARN = colors.HexColor("#f59e0b")


def _risk_color(level):
    l = (level or "").lower()
    if "critical" in l: return colors.HexColor("#dc2626")
    if "high" in l: return BRAND_DANGER
    if "medium" in l or "moderate" in l: return BRAND_WARN
    return BRAND_SUCCESS


def _header(canvas, doc):
    w, h = A4
    canvas.saveState()
    canvas.setFillColor(BRAND_VIOLET)
    canvas.rect(0, h - 22 * mm, w, 22 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawString(18 * mm, h - 14 * mm, "DamageGenX")
    canvas.setFont("Helvetica", 8)
    canvas.drawString(18 * mm, h - 18.5 * mm, "Multi-Vehicle Damage Assessment Platform")
    canvas.drawRightString(w - 18 * mm, h - 14 * mm,
                           f"Generated {datetime.utcnow().strftime('%d %b %Y · %H:%M UTC')}")
    canvas.setFillColor(BRAND_MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(18 * mm, 12 * mm,
                      "DamageGenX v1.0 · Deep Learning + IoT Vehicle Inspection")
    canvas.drawRightString(w - 18 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _cover(canvas, doc):
    w, h = A4
    canvas.saveState()
    canvas.setFillColor(BRAND_VIOLET)
    canvas.rect(0, 0, w, 6 * mm, fill=1, stroke=0)
    canvas.restoreState()


def _slug():
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def save_json_report(payload):
    path = os.path.join(REPORTS_FOLDER, f"DamageGenX_report_{_slug()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    return path


def _styles():
    s = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=s["Title"], fontName="Helvetica-Bold",
                                fontSize=26, textColor=BRAND_INK),
        "h1": ParagraphStyle("h1", parent=s["Heading1"], fontName="Helvetica-Bold",
                             fontSize=15, textColor=BRAND_VIOLET_DARK,
                             spaceBefore=12, spaceAfter=8),
        "h2": ParagraphStyle("h2", parent=s["Heading2"], fontName="Helvetica-Bold",
                             fontSize=11, textColor=BRAND_INK, spaceBefore=8, spaceAfter=6),
        "body": ParagraphStyle("b", parent=s["BodyText"], fontName="Helvetica",
                               fontSize=9.5, leading=13, textColor=BRAND_INK),
        "muted": ParagraphStyle("m", parent=s["BodyText"], fontName="Helvetica",
                                fontSize=8.5, textColor=BRAND_MUTED),
        "cell": ParagraphStyle("c", parent=s["BodyText"], fontName="Helvetica",
                               fontSize=9.5, textColor=BRAND_INK),
        "cellk": ParagraphStyle("ck", parent=s["BodyText"], fontName="Helvetica-Bold",
                                fontSize=9.5, textColor=BRAND_INK),
    }


def _kv(rows, styles):
    data = [[Paragraph(k, styles["cellk"]), Paragraph(str(v), styles["cell"])]
            for k, v in rows]
    t = Table(data, colWidths=(60 * mm, 100 * mm), hAlign="LEFT")
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BRAND_SURFACE]),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, BRAND_BORDER),
        ("BOX", (0, 0), (-1, -1), 0.5, BRAND_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def generate_pdf_report(payload):
    iid = payload.get("inspection_id") or f"INS-{_slug()[-6:]}"
    fname = f"DamageGenX_{iid}_{_slug()}.pdf"
    path = os.path.join(REPORTS_FOLDER, fname)

    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=30 * mm, bottomMargin=22 * mm)
    styles = _styles()
    story = []

    # Cover
    story.append(Spacer(1, 25 * mm))
    story.append(Paragraph("DAMAGEGENX", ParagraphStyle(
        "cb", fontName="Helvetica-Bold", fontSize=34, textColor=BRAND_VIOLET)))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Multi-Vehicle Damage Assessment Platform", styles["muted"]))
    story.append(Spacer(1, 25 * mm))
    story.append(Paragraph("Vehicle Inspection Report", ParagraphStyle(
        "ct", fontName="Helvetica-Bold", fontSize=24, textColor=BRAND_INK)))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "Deep Learning · IoT Sensor Fusion · Hidden-Damage Risk Prediction",
        styles["muted"]))
    story.append(Spacer(1, 35 * mm))
    story.append(_kv([
        ["Inspection ID", iid],
        ["Generated on", datetime.utcnow().strftime("%d %b %Y · %H:%M UTC")],
        ["Vehicle Type", payload.get("vehicle_type", "car_sedan").replace("_", " ").title()],
        ["Prepared by", payload.get("inspector_name", "DamageGenX System")],
    ], styles))
    story.append(PageBreak())

    # 1. Damage Summary
    story.append(Paragraph("1. Damage Summary", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=BRAND_VIOLET_DARK,
                            spaceBefore=2, spaceAfter=10))
    fusion = payload.get("fusion", {}) or {}
    views = payload.get("views", {}) or {}
    sev_score = payload.get("severity_score", 0)
    sev_label = payload.get("severity_label", "—")
    story.append(_kv([
        ("Dominant Damage", str(fusion.get("dominant_damage", "—")).replace("_", " ").title()),
        ("Fused Severity", f"{sev_score}/100 · {sev_label}"),
        ("Total Detections", str(len(fusion.get("fused_detections", [])))),
        ("Views Analyzed", f"{len(views)} / 5"),
        ("Vehicle Type", str(payload.get("vehicle_type", "car_sedan")).replace("_", " ").title()),
        ("Primary Component", str(payload.get("component", "—")).replace("_", " ").title()),
    ], styles))

    # 2. IoT Sensor
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("2. IoT Sensor Data", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=BRAND_VIOLET_DARK,
                            spaceBefore=2, spaceAfter=10))
    sensor = payload.get("sensor", {}) or {}
    story.append(_kv([
        ("Impact Force", f"{sensor.get('impact_g', 0)} G"),
        ("Rotation", f"{sensor.get('rotation_dps', 0)} °/s"),
        ("GPS Latitude", str(sensor.get("location", {}).get("lat", "—"))),
        ("GPS Longitude", str(sensor.get("location", {}).get("lon", "—"))),
    ], styles))

    # 3. Hidden Risk
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("3. Hidden-Damage Risk", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=BRAND_VIOLET_DARK,
                            spaceBefore=2, spaceAfter=10))
    hidden = payload.get("hidden_damage", {}) or {}
    level = (hidden.get("risk_level") or "—").upper()
    pct = int(round((hidden.get("risk_score") or 0) * 100))
    badge = Table([[Paragraph(f"<b>{level}</b>", ParagraphStyle(
        "bg", fontName="Helvetica-Bold", fontSize=13, textColor=colors.white))]],
        colWidths=(50 * mm,), rowHeights=(10 * mm,))
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _risk_color(level)),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(badge)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f"<b>Risk Score:</b> {pct}%", styles["body"]))
    story.append(Paragraph(f"<b>Recommendation:</b> {hidden.get('inspection_recommendation', '—')}",
                           styles["body"]))
    story.append(Paragraph(
        "Note: Hidden-damage output is a risk estimate, not a direct detection of internal damage.",
        styles["muted"]))

    # 4. Repair + Cost
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("4. Repair Recommendation & Cost", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=BRAND_VIOLET_DARK,
                            spaceBefore=2, spaceAfter=10))
    repair = payload.get("repair", {}) or {}
    cost = payload.get("cost", {}) or {}
    story.append(_kv([
        ("Recommended Action", str(repair.get("action", "—")).upper()),
        ("Component", str(payload.get("component", "—")).replace("_", " ").title()),
        ("Description", str(repair.get("description", "—"))),
        ("Priority", str(repair.get("severity", "—")).title()),
    ], styles))
    story.append(Spacer(1, 3 * mm))
    curr = cost.get("currency", "INR")
    story.append(Paragraph(
        f"<b>Estimated Cost Range:</b> {curr} {cost.get('cost_min', 0):,} – {cost.get('cost_max', 0):,}",
        ParagraphStyle("big", fontName="Helvetica-Bold", fontSize=13,
                       textColor=BRAND_VIOLET_DARK)))

    # 5. Annotated Images
    story.append(PageBreak())
    story.append(Paragraph("5. Annotated Views", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=BRAND_VIOLET_DARK,
                            spaceBefore=2, spaceAfter=10))
    ann = payload.get("annotated_images", {}) or {}
    cells, row = [], []
    for view, path in ann.items():
        if not os.path.exists(path):
            continue
        try:
            img = Image(path, width=75 * mm, height=55 * mm, kind="proportional")
        except Exception:
            continue
        cell = Table([[img], [Paragraph(f"<b>{view.title()}</b>", styles["muted"])]],
                     colWidths=(75 * mm,))
        cell.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 0.4, BRAND_BORDER),
            ("BACKGROUND", (0, 1), (0, 1), BRAND_SURFACE),
        ]))
        row.append(cell)
        if len(row) == 2:
            cells.append(row); row = []
    if row: cells.append(row)
    if cells:
        t = Table(cells, colWidths=(80 * mm, 80 * mm), hAlign="LEFT")
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(t)

    # 6. Evidence
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("6. Evidence Integrity", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=BRAND_VIOLET_DARK,
                            spaceBefore=2, spaceAfter=10))
    rows = []
    for view, r in views.items():
        ev = r.get("evidence") or {}
        if ev:
            rows.append((view.title(),
                         f"{ev.get('evidence_id','—')} · sha256:{str(ev.get('sha256',''))[:16]}…"))
    if rows:
        story.append(_kv(rows, styles))
    else:
        story.append(Paragraph("No evidence hashes recorded.", styles["muted"]))

    # Disclaimer
    story.append(Spacer(1, 10 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BRAND_BORDER))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Disclaimer", styles["h2"]))
    story.append(Paragraph(
        "This report is generated by DamageGenX, an AI-assisted vehicle inspection platform. "
        "Detected damage, severity estimation, hidden-damage risk, and cost estimates are "
        "algorithmic outputs and may not be fully accurate. This document does not replace "
        "professional mechanical inspection or a formal repair quotation.",
        styles["muted"]))

    doc.build(story, onFirstPage=_cover, onLaterPages=_header)
    return path