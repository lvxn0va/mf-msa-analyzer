"""
Investment Brief PDF Generator - Narrative Format
Produces a detailed narrative report with reasoning and sources
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models import HeatMapItem

def generate_investment_brief_pdf(
    heat_map: List[HeatMapItem],
    deal_name: str,
    address: str,
    research_data: Optional[Dict[str, Any]],
    output_path: str
):
    """
    Generate the Investment Brief PDF (Narrative Format)

    Args:
        heat_map: List of 30 criterion evaluations
        deal_name: Name of the deal
        address: Property address
        research_data: Raw research data for appendix
        output_path: Where to save the PDF
    """
    # Create PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )

    # Container for PDF elements
    elements = []

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#555555'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )

    criterion_heading_style = ParagraphStyle(
        'CriterionHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=6,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        alignment=TA_JUSTIFY
    )

    # Cover Page
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("INVESTMENT BRIEF", title_style))
    elements.append(Paragraph(f"<b>{deal_name}</b>", subtitle_style))
    elements.append(Paragraph(address, subtitle_style))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        f"Analysis Date: {datetime.now().strftime('%B %d, %Y')}",
        subtitle_style
    ))
    elements.append(PageBreak())

    # Executive Summary
    elements.append(Paragraph("EXECUTIVE SUMMARY", section_heading_style))

    green_count = len([i for i in heat_map if i.status == 'GREEN'])
    yellow_count = len([i for i in heat_map if i.status == 'YELLOW'])
    red_count = len([i for i in heat_map if i.status == 'RED'])

    # Determine recommendation
    if red_count > 5:
        recommendation = "NO-GO"
        rec_color = "red"
        exec_summary = f"""
        This property at {address} has been evaluated against our 30-point investment criteria framework.
        The analysis reveals <font color="red"><b>{red_count} FAILING criteria</b></font>, which exceeds our
        institutional tolerance threshold. <b>We recommend PASSING on this opportunity.</b>
        """
    elif red_count > 2:
        recommendation = "CAUTION"
        rec_color = "orange"
        exec_summary = f"""
        This property at {address} has been evaluated against our 30-point investment criteria framework.
        The analysis reveals <font color="orange"><b>{red_count} concerning criteria</b></font> that require
        Investment Committee review. <b>Proceed with heightened scrutiny.</b>
        """
    else:
        recommendation = "PROCEED"
        rec_color = "green"
        exec_summary = f"""
        This property at {address} has been evaluated against our 30-point investment criteria framework.
        The analysis shows <font color="green"><b>strong fundamentals</b></font> with only {red_count}
        failing criteria. <b>We recommend proceeding to full due diligence.</b>
        """

    elements.append(Paragraph(exec_summary, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Score Summary Table
    score_data = [
        ['Status', 'Count', 'Percentage', 'Interpretation'],
        ['GREEN', str(green_count), f"{(green_count/30)*100:.1f}%", 'Meets or exceeds criteria'],
        ['YELLOW', str(yellow_count), f"{(yellow_count/30)*100:.1f}%", 'Marginal, requires review'],
        ['RED', str(red_count), f"{(red_count/30)*100:.1f}%", 'Fails to meet criteria']
    ]

    score_table = Table(score_data, colWidths=[1*inch, 0.8*inch, 1*inch, 3*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (-1, 1), colors.Color(0.2, 0.7, 0.3, alpha=0.2)),
        ('BACKGROUND', (0, 2), (-1, 2), colors.Color(1.0, 0.9, 0.2, alpha=0.2)),
        ('BACKGROUND', (0, 3), (-1, 3), colors.Color(0.9, 0.2, 0.2, alpha=0.2)),
    ]))

    elements.append(score_table)
    elements.append(PageBreak())

    # MSA-Level Analysis
    elements.append(Paragraph("MSA-LEVEL ANALYSIS (16 Criteria)", section_heading_style))
    elements.append(Paragraph(
        "The following criteria evaluate the broader metropolitan statistical area to assess "
        "regional economic health, demographic trends, and market fundamentals.",
        body_style
    ))

    msa_items = sorted(
        [item for item in heat_map if item.id.startswith('msa_')],
        key=lambda x: int(x.id.split('_')[1])
    )

    for item in msa_items:
        # Status indicator
        status_emoji = {
            'GREEN': '🟢',
            'YELLOW': '🟡',
            'RED': '🔴'
        }[item.status]

        override_indicator = " 📄" if item.override_applied else ""

        elements.append(Paragraph(
            f"{status_emoji} <b>{item.metric}</b>{override_indicator}",
            criterion_heading_style
        ))

        # Threshold and value
        elements.append(Paragraph(
            f"<b>Threshold:</b> {item.threshold} | <b>Actual:</b> {item.value}",
            body_style
        ))

        # Reasoning
        elements.append(Paragraph(
            f"<b>Analysis:</b> {item.reasoning}",
            body_style
        ))

        # Source
        elements.append(Paragraph(
            f"<i>Source: {item.source}</i>",
            body_style
        ))

        # Override note
        if item.override_applied:
            elements.append(Paragraph(
                f"<font color='blue'><b>Context Override Applied:</b> Data from user-uploaded "
                f"document '{item.override_document}' supersedes general market data.</font>",
                body_style
            ))

        elements.append(Spacer(1, 0.15*inch))

    elements.append(PageBreak())

    # Sub-Market Analysis
    elements.append(Paragraph("SUB-MARKET ANALYSIS (14 Criteria)", section_heading_style))
    elements.append(Paragraph(
        "The following criteria evaluate the immediate neighborhood and sub-market within "
        "1-3-5 mile radii to assess location quality, amenities, and competitive positioning.",
        body_style
    ))

    sub_items = sorted(
        [item for item in heat_map if item.id.startswith('sub_')],
        key=lambda x: int(x.id.split('_')[1])
    )

    for item in sub_items:
        # Status indicator
        status_emoji = {
            'GREEN': '🟢',
            'YELLOW': '🟡',
            'RED': '🔴'
        }[item.status]

        override_indicator = " 📄" if item.override_applied else ""

        elements.append(Paragraph(
            f"{status_emoji} <b>{item.metric}</b>{override_indicator}",
            criterion_heading_style
        ))

        # Threshold and value
        elements.append(Paragraph(
            f"<b>Threshold:</b> {item.threshold} | <b>Actual:</b> {item.value}",
            body_style
        ))

        # Reasoning
        elements.append(Paragraph(
            f"<b>Analysis:</b> {item.reasoning}",
            body_style
        ))

        # Source
        elements.append(Paragraph(
            f"<i>Source: {item.source}</i>",
            body_style
        ))

        # Override note
        if item.override_applied:
            elements.append(Paragraph(
                f"<font color='blue'><b>Context Override Applied:</b> Data from user-uploaded "
                f"document '{item.override_document}' supersedes general market data.</font>",
                body_style
            ))

        elements.append(Spacer(1, 0.15*inch))

    elements.append(PageBreak())

    # Final Recommendation
    elements.append(Paragraph("FINAL RECOMMENDATION", section_heading_style))

    if red_count > 5:
        final_rec_text = f"""
        Based on the comprehensive 30-point analysis, this property exhibits <b>{red_count} failing criteria</b>,
        which significantly exceeds our institutional risk tolerance. Multiple fundamental weaknesses across
        both MSA-level and sub-market metrics indicate structural challenges that cannot be easily mitigated.
        <br/><br/>
        <font color="red" size="14"><b>RECOMMENDATION: NO-GO</b></font>
        <br/><br/>
        We recommend <b>PASSING</b> on this opportunity and allocating capital to properties with stronger
        fundamental alignment to our investment thesis.
        """
    elif red_count > 2:
        final_rec_text = f"""
        Based on the comprehensive 30-point analysis, this property exhibits <b>{red_count} concerning criteria</b>
        alongside {green_count} passing metrics. While the property shows promise in several areas, the identified
        weaknesses require detailed Investment Committee review and risk mitigation planning.
        <br/><br/>
        <font color="orange" size="14"><b>RECOMMENDATION: CAUTION - PROCEED WITH SCRUTINY</b></font>
        <br/><br/>
        If the Committee determines that the RED-flagged risks can be mitigated through operational expertise,
        capital improvements, or favorable deal structure, proceed to full due diligence. Otherwise, pass.
        """
    else:
        final_rec_text = f"""
        Based on the comprehensive 30-point analysis, this property demonstrates <b>strong fundamental alignment</b>
        with our investment criteria, achieving {green_count} GREEN ratings across both MSA and sub-market metrics.
        The limited weaknesses ({red_count} RED flags) appear manageable and do not present systemic risk.
        <br/><br/>
        <font color="green" size="14"><b>RECOMMENDATION: PROCEED TO FULL DUE DILIGENCE</b></font>
        <br/><br/>
        We recommend advancing this opportunity to Phase II due diligence, including physical inspection,
        financial underwriting, and legal review.
        """

    elements.append(Paragraph(final_rec_text, body_style))
    elements.append(Spacer(1, 0.3*inch))

    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_JUSTIFY
    )

    elements.append(Paragraph(
        "<b>DISCLAIMER:</b> This analysis is generated by AI-powered research tools and should be used "
        "as a preliminary screening mechanism only. All data points must be independently verified during "
        "formal due diligence. This report does not constitute investment advice. All investment decisions "
        "remain the responsibility of the Investment Committee.",
        disclaimer_style
    ))

    # Build PDF
    doc.build(elements)
