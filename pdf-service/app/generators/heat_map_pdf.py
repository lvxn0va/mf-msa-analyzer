"""
Heat Map PDF Generator - Grid Format
Produces a visual "traffic light" grid showing all 30 criteria at a glance
"""
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import List
from datetime import datetime

from app.models import HeatMapItem

# Status color mapping
STATUS_COLORS = {
    "GREEN": colors.Color(0.2, 0.7, 0.3, alpha=0.3),  # Light green
    "YELLOW": colors.Color(1.0, 0.9, 0.2, alpha=0.3),  # Light yellow
    "RED": colors.Color(0.9, 0.2, 0.2, alpha=0.3)  # Light red
}

def generate_heat_map_pdf(
    heat_map: List[HeatMapItem],
    deal_name: str,
    address: str,
    output_path: str
):
    """
    Generate the Heat Map PDF (Grid Format)

    Args:
        heat_map: List of 30 criterion evaluations
        deal_name: Name of the deal
        address: Property address
        output_path: Where to save the PDF
    """
    # Create PDF with landscape orientation for better grid display
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch
    )

    # Container for PDF elements
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#555555'),
        spaceAfter=20,
        alignment=TA_CENTER
    )

    # Header
    elements.append(Paragraph("INVESTMENT DECISION HEAT MAP", title_style))
    elements.append(Paragraph(f"<b>{deal_name}</b> | {address}", subtitle_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))

    # Separate MSA and Sub-Market criteria
    msa_items = [item for item in heat_map if item.id.startswith('msa_')]
    sub_items = [item for item in heat_map if item.id.startswith('sub_')]

    # MSA Criteria Table
    elements.append(Paragraph("<b>MSA-LEVEL CRITERIA (16 Points)</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))

    msa_table_data = [
        ['#', 'Metric', 'Threshold', 'Actual Value', 'Status', 'Source']
    ]

    for item in sorted(msa_items, key=lambda x: int(x.id.split('_')[1])):
        msa_table_data.append([
            item.id.replace('msa_', 'M'),
            Paragraph(item.metric, styles['Normal']),
            Paragraph(item.threshold, styles['Normal']),
            Paragraph(item.value, styles['Normal']),
            Paragraph(f"<b>{item.status}</b>", styles['Normal']),
            Paragraph(item.source[:50] + '...' if len(item.source) > 50 else item.source, styles['Normal'])
        ])

    msa_table = Table(msa_table_data, colWidths=[0.4*inch, 1.8*inch, 1.5*inch, 1.5*inch, 0.8*inch, 2*inch])

    # Apply styling to MSA table
    msa_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    # Color-code rows by status
    for i, item in enumerate(sorted(msa_items, key=lambda x: int(x.id.split('_')[1])), start=1):
        msa_table_style.add('BACKGROUND', (0, i), (-1, i), STATUS_COLORS[item.status])

    msa_table.setStyle(msa_table_style)
    elements.append(msa_table)
    elements.append(PageBreak())

    # Sub-Market Criteria Table
    elements.append(Paragraph("<b>SUB-MARKET CRITERIA (14 Points)</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))

    sub_table_data = [
        ['#', 'Metric', 'Threshold', 'Actual Value', 'Status', 'Source']
    ]

    for item in sorted(sub_items, key=lambda x: int(x.id.split('_')[1])):
        # Add override indicator
        metric_text = item.metric
        if item.override_applied:
            metric_text += " 📄"  # Document emoji for override

        sub_table_data.append([
            item.id.replace('sub_', 'S'),
            Paragraph(metric_text, styles['Normal']),
            Paragraph(item.threshold, styles['Normal']),
            Paragraph(item.value, styles['Normal']),
            Paragraph(f"<b>{item.status}</b>", styles['Normal']),
            Paragraph(item.source[:50] + '...' if len(item.source) > 50 else item.source, styles['Normal'])
        ])

    sub_table = Table(sub_table_data, colWidths=[0.4*inch, 1.8*inch, 1.5*inch, 1.5*inch, 0.8*inch, 2*inch])

    # Apply styling to Sub-Market table
    sub_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    # Color-code rows by status
    for i, item in enumerate(sorted(sub_items, key=lambda x: int(x.id.split('_')[1])), start=1):
        sub_table_style.add('BACKGROUND', (0, i), (-1, i), STATUS_COLORS[item.status])

    sub_table.setStyle(sub_table_style)
    elements.append(sub_table)
    elements.append(Spacer(1, 0.3*inch))

    # Summary Statistics
    green_count = len([i for i in heat_map if i.status == 'GREEN'])
    yellow_count = len([i for i in heat_map if i.status == 'YELLOW'])
    red_count = len([i for i in heat_map if i.status == 'RED'])
    override_count = len([i for i in heat_map if i.override_applied])

    summary_data = [
        ['Summary', 'Count', 'Percentage'],
        ['GREEN (Pass)', str(green_count), f"{(green_count/30)*100:.1f}%"],
        ['YELLOW (Caution)', str(yellow_count), f"{(yellow_count/30)*100:.1f}%"],
        ['RED (Fail)', str(red_count), f"{(red_count/30)*100:.1f}%"],
        ['Context Overrides', str(override_count), f"{(override_count/30)*100:.1f}%"]
    ]

    summary_table = Table(summary_data, colWidths=[2*inch, 1*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, 1), STATUS_COLORS['GREEN']),
        ('BACKGROUND', (0, 2), (-1, 2), STATUS_COLORS['YELLOW']),
        ('BACKGROUND', (0, 3), (-1, 3), STATUS_COLORS['RED']),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 0.2*inch))

    # Recommendation
    if red_count > 5:
        recommendation = "NO-GO"
        rec_color = colors.red
    elif red_count > 2:
        recommendation = "CAUTION - Requires Committee Review"
        rec_color = colors.orange
    else:
        recommendation = "PROCEED to Full Due Diligence"
        rec_color = colors.green

    rec_style = ParagraphStyle(
        'Recommendation',
        parent=styles['Normal'],
        fontSize=14,
        textColor=rec_color,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    elements.append(Paragraph(f"<b>RECOMMENDATION: {recommendation}</b>", rec_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("📄 = Metric uses user-uploaded context document override", styles['Normal']))

    # Build PDF
    doc.build(elements)
