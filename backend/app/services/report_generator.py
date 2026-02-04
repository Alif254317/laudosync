import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


# Cores do sistema
COLOR_GREEN = colors.HexColor("#27ae60")
COLOR_YELLOW = colors.HexColor("#f39c12")
COLOR_RED = colors.HexColor("#e74c3c")
COLOR_BLUE = colors.HexColor("#2196F3")
COLOR_PURPLE = colors.HexColor("#5C2D91")
COLOR_LIGHT_GRAY = colors.HexColor("#f5f5f5")
COLOR_DARK_GRAY = colors.HexColor("#333333")


def get_classification_color(classification: str) -> colors.Color:
    """Retorna a cor baseada na classificação."""
    mapping = {
        "CONCORDÂNCIA TOTAL": COLOR_GREEN,
        "CONCORDÂNCIA PARCIAL": COLOR_YELLOW,
        "DISCORDÂNCIA": COLOR_RED
    }
    return mapping.get(classification, colors.gray)


def generate_report_pdf(audit_data: dict) -> bytes:
    """
    Gera o PDF do relatório de auditoria.

    Args:
        audit_data: Dicionário com todos os dados da auditoria

    Returns:
        Bytes do PDF gerado
    """
    buffer = io.BytesIO()

    # Configuração do documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Estilos
    styles = getSampleStyleSheet()

    # Estilos customizados
    styles.add(ParagraphStyle(
        name='MainTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=COLOR_PURPLE,
        alignment=TA_CENTER,
        spaceAfter=20
    ))

    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=COLOR_BLUE,
        spaceBefore=15,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name='SmallText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.gray
    ))

    # Elementos do documento
    elements = []

    # Cabeçalho
    elements.append(Paragraph("ELO SYSTEM", styles['MainTitle']))
    elements.append(Paragraph("Relatório de Auditoria Comparativa de Laudos", styles['Heading2']))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=COLOR_PURPLE))
    elements.append(Spacer(1, 0.5*cm))

    # Data do relatório
    elements.append(Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        styles['SmallText']
    ))
    elements.append(Spacer(1, 0.5*cm))

    # Dados do paciente/exame
    elements.append(Paragraph("Dados do Exame", styles['SectionTitle']))

    patient_data = [
        ["Paciente:", audit_data.get("patient_name", "Não informado")],
        ["Tipo de Exame:", audit_data.get("exam_type", "Não informado")],
        ["Data do Exame:", audit_data.get("exam_date", "Não informada")],
    ]

    patient_table = Table(patient_data, colWidths=[4*cm, 12*cm])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 0.5*cm))

    # Status da classificação (destaque)
    classification = audit_data.get("classification", "")
    status_color = get_classification_color(classification)

    elements.append(Paragraph("Resultado da Análise", styles['SectionTitle']))

    status_table = Table(
        [[classification]],
        colWidths=[16*cm]
    )
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), status_color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 0.5*cm))

    # Resumo da análise
    summary = audit_data.get("analysis_summary", "")
    if summary:
        elements.append(Paragraph("Resumo", styles['SectionTitle']))
        elements.append(Paragraph(summary, styles['CustomBody']))
        elements.append(Spacer(1, 0.3*cm))

    # Alerta crítico (se houver)
    if audit_data.get("has_critical_alert"):
        elements.append(Spacer(1, 0.3*cm))

        alert_text = audit_data.get("critical_alert_text", "Alerta crítico detectado")
        alert_table = Table(
            [["⚠️ ALERTA CRÍTICO"], [alert_text]],
            colWidths=[16*cm]
        )
        alert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_RED),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#ffebee")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), COLOR_RED),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 2, COLOR_RED),
        ]))
        elements.append(alert_table)
        elements.append(Spacer(1, 0.5*cm))

    # Achados concordantes
    concordant = audit_data.get("concordant_findings", [])
    if concordant:
        elements.append(Paragraph("Achados Concordantes", styles['SectionTitle']))

        items = [ListItem(Paragraph(f"✓ {finding}", styles['CustomBody']))
                 for finding in concordant]
        elements.append(ListFlowable(items, bulletType='bullet', start=''))
        elements.append(Spacer(1, 0.3*cm))

    # Discrepâncias
    discrepancies = audit_data.get("discrepancies", [])
    if discrepancies:
        elements.append(Paragraph("Discrepâncias Identificadas", styles['SectionTitle']))

        for i, disc in enumerate(discrepancies, 1):
            severity = disc.get("severity", "baixa")
            severity_colors = {
                "baixa": COLOR_LIGHT_GRAY,
                "média": colors.HexColor("#fff3e0"),
                "alta": colors.HexColor("#fff8e1"),
                "crítica": colors.HexColor("#ffebee")
            }
            bg_color = severity_colors.get(severity, COLOR_LIGHT_GRAY)

            disc_data = [
                [f"Discrepância #{i}", f"Severidade: {severity.upper()}"],
                [f"Tipo: {disc.get('type', 'N/A')}", ""],
                ["Descrição:", disc.get("description", "")],
                ["Laudo Oficial diz:", disc.get("official_says", "N/A")],
                ["Laudo Auditor diz:", disc.get("auditor_says", "N/A")],
            ]

            disc_table = Table(disc_data, colWidths=[8*cm, 8*cm])
            disc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), COLOR_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 1), (-1, -1), bg_color),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 2), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('BOX', (0, 0), (-1, -1), 1, COLOR_BLUE),
                ('SPAN', (0, 2), (-1, 2)),
                ('SPAN', (0, 3), (-1, 3)),
                ('SPAN', (0, 4), (-1, 4)),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(disc_table)
            elements.append(Spacer(1, 0.3*cm))

    # Nota técnica
    technical_note = audit_data.get("technical_note")
    if technical_note:
        elements.append(Paragraph("Nota Técnica", styles['SectionTitle']))

        note_table = Table([[technical_note]], colWidths=[16*cm])
        note_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_LIGHT_GRAY),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Oblique'),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(note_table)
        elements.append(Spacer(1, 0.5*cm))

    # Rodapé
    elements.append(Spacer(1, 1*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.gray))
    elements.append(Spacer(1, 0.3*cm))

    footer_text = """
    <font size="8" color="gray">
    Este relatório foi gerado automaticamente pelo sistema ELO System - LaudoSync.<br/>
    A análise comparativa é realizada por inteligência artificial e deve ser validada por um médico qualificado.<br/>
    Este documento não substitui a avaliação médica profissional.
    </font>
    """
    elements.append(Paragraph(footer_text, styles['Normal']))

    # Gera o PDF
    doc.build(elements)

    buffer.seek(0)
    return buffer.getvalue()
