from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from app.config import get_settings

def generate_contract_pdf(output_path: str, title: str, meta: dict, terms: str | None = None):
    settings = get_settings()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph(settings.company_name, styles["Title"]), Paragraph(title, styles["Heading2"]), Paragraph(datetime.now().strftime("%d/%m/%Y %H:%M"), styles["Normal"]), Spacer(1, 12)]
    rows = [[str(k), str(v or "-")] for k, v in meta.items()]
    t = Table(rows, colWidths=[130, 350])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),colors.HexColor("#111827")),("TEXTCOLOR",(0,0),(0,-1),colors.white),("GRID",(0,0),(-1,-1),0.25,colors.grey),("PADDING",(0,0),(-1,-1),7)]))
    story += [t, Spacer(1, 18), Paragraph("Condiciones", styles["Heading3"]), Paragraph((terms or "El cliente recibe los equipos en buen estado y acepta responder por pérdidas, roturas o faltantes.").replace("\\n","<br/>"), styles["Normal"]), Spacer(1, 50)]
    sig = Table([["Firma empresa", "Firma cliente"], ["", ""]], colWidths=[230,230], rowHeights=[20,60])
    sig.setStyle(TableStyle([("LINEABOVE",(0,1),(0,1),1,colors.black),("LINEABOVE",(1,1),(1,1),1,colors.black),("ALIGN",(0,0),(-1,-1),"CENTER")]))
    story.append(sig)
    doc.build(story)
