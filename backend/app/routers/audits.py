from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import date
from pydantic import BaseModel
import io

from app.services.pdf_extractor import extract_text_from_pdf, validate_pdf


class TextAuditRequest(BaseModel):
    official_text: str
    auditor_text: str
    patient_name: str = "Não informado"
    exam_type: str = "Não informado"
    exam_date: Optional[str] = None
from app.services.gemini_comparator import compare_reports
from app.services.supabase_client import (
    upload_pdf_to_storage, save_audit, get_audit, list_audits
)
from app.services.report_generator import generate_report_pdf

router = APIRouter(prefix="/api/audits", tags=["audits"])


@router.post("")
async def create_audit(
    official_pdf: UploadFile = File(..., description="PDF do Laudo Oficial"),
    auditor_pdf: UploadFile = File(..., description="PDF do Laudo Auditor"),
    patient_name: str = Form(default="Não informado"),
    exam_type: str = Form(default="Não informado"),
    exam_date: Optional[str] = Form(default=None)
):
    """
    Cria uma nova auditoria comparando dois laudos médicos.

    - Recebe 2 PDFs (oficial e auditor)
    - Extrai texto de ambos
    - Envia para IA comparar
    - Gera relatório PDF
    - Salva tudo no Supabase
    """

    # 1. Lê os arquivos
    official_bytes = await official_pdf.read()
    auditor_bytes = await auditor_pdf.read()

    # 2. Valida os PDFs
    is_valid, error = validate_pdf(official_bytes)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Laudo Oficial inválido: {error}")

    is_valid, error = validate_pdf(auditor_bytes)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Laudo Auditor inválido: {error}")

    # 3. Extrai texto dos PDFs
    official_text = extract_text_from_pdf(official_bytes)
    auditor_text = extract_text_from_pdf(auditor_bytes)

    if not official_text:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível extrair texto do Laudo Oficial. O PDF pode ser uma imagem escaneada."
        )

    if not auditor_text:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível extrair texto do Laudo Auditor. O PDF pode ser uma imagem escaneada."
        )

    # 4. Compara os laudos via Gemini
    comparison_result = compare_reports(
        official_text=official_text,
        auditor_text=auditor_text,
        patient_name=patient_name,
        exam_type=exam_type,
        exam_date=exam_date or "Não informada"
    )

    if not comparison_result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na análise: {comparison_result.get('error', 'Erro desconhecido')}"
        )

    analysis = comparison_result["data"]

    # 5. Faz upload dos PDFs para o Storage
    official_url = upload_pdf_to_storage(
        official_bytes,
        official_pdf.filename or "laudo_oficial.pdf",
        folder="oficiais"
    )

    auditor_url = upload_pdf_to_storage(
        auditor_bytes,
        auditor_pdf.filename or "laudo_auditor.pdf",
        folder="auditores"
    )

    # 6. Prepara dados da auditoria
    audit_data = {
        "patient_name": patient_name,
        "exam_type": exam_type,
        "exam_date": exam_date,
        "official_pdf_url": official_url,
        "auditor_pdf_url": auditor_url,
        "official_text": official_text,
        "auditor_text": auditor_text,
        "classification": analysis.get("classification"),
        "analysis_summary": analysis.get("summary"),
        "concordant_findings": analysis.get("concordant_findings", []),
        "discrepancies": analysis.get("discrepancies", []),
        "has_critical_alert": analysis.get("has_critical_alert", False),
        "critical_alert_text": analysis.get("critical_alert_text"),
        "technical_note": analysis.get("technical_note"),
    }

    # 7. Gera o relatório PDF
    report_bytes = generate_report_pdf(audit_data)

    # 8. Faz upload do relatório
    report_url = upload_pdf_to_storage(
        report_bytes,
        f"relatorio_{patient_name.replace(' ', '_')}.pdf",
        folder="relatorios"
    )
    audit_data["report_pdf_url"] = report_url

    # 9. Salva no banco de dados
    saved_audit = save_audit(audit_data)

    # 10. Retorna resultado
    return {
        "success": True,
        "audit_id": saved_audit["id"] if saved_audit else None,
        "classification": analysis.get("classification"),
        "summary": analysis.get("summary"),
        "concordant_findings": analysis.get("concordant_findings", []),
        "discrepancies": analysis.get("discrepancies", []),
        "has_critical_alert": analysis.get("has_critical_alert", False),
        "critical_alert_text": analysis.get("critical_alert_text"),
        "technical_note": analysis.get("technical_note"),
        "report_url": report_url,
        "extracted_texts": {
            "official": official_text[:500] + "..." if len(official_text) > 500 else official_text,
            "auditor": auditor_text[:500] + "..." if len(auditor_text) > 500 else auditor_text
        }
    }


@router.post("/text")
async def create_audit_from_text(request: TextAuditRequest):
    """
    Cria uma nova auditoria a partir de textos já extraídos.

    - Recebe 2 textos (oficial e auditor)
    - Envia para IA comparar
    - Gera relatório PDF
    - Salva tudo no Supabase
    """

    official_text = request.official_text.strip()
    auditor_text = request.auditor_text.strip()

    if len(official_text) < 10:
        raise HTTPException(status_code=400, detail="Texto do Laudo Oficial muito curto")

    if len(auditor_text) < 10:
        raise HTTPException(status_code=400, detail="Texto do Laudo Auditor muito curto")

    # Compara os laudos via Gemini
    comparison_result = compare_reports(
        official_text=official_text,
        auditor_text=auditor_text,
        patient_name=request.patient_name,
        exam_type=request.exam_type,
        exam_date=request.exam_date or "Não informada"
    )

    if not comparison_result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na análise: {comparison_result.get('error', 'Erro desconhecido')}"
        )

    analysis = comparison_result["data"]

    # Prepara dados da auditoria
    audit_data = {
        "patient_name": request.patient_name,
        "exam_type": request.exam_type,
        "exam_date": request.exam_date,
        "official_pdf_url": None,
        "auditor_pdf_url": None,
        "official_text": official_text,
        "auditor_text": auditor_text,
        "classification": analysis.get("classification"),
        "analysis_summary": analysis.get("summary"),
        "concordant_findings": analysis.get("concordant_findings", []),
        "discrepancies": analysis.get("discrepancies", []),
        "has_critical_alert": analysis.get("has_critical_alert", False),
        "critical_alert_text": analysis.get("critical_alert_text"),
        "technical_note": analysis.get("technical_note"),
    }

    # Gera o relatório PDF
    report_bytes = generate_report_pdf(audit_data)

    # Faz upload do relatório
    report_url = upload_pdf_to_storage(
        report_bytes,
        f"relatorio_{request.patient_name.replace(' ', '_')}.pdf",
        folder="relatorios"
    )
    audit_data["report_pdf_url"] = report_url

    # Salva no banco de dados
    saved_audit = save_audit(audit_data)

    # Retorna resultado
    return {
        "success": True,
        "audit_id": saved_audit["id"] if saved_audit else None,
        "classification": analysis.get("classification"),
        "summary": analysis.get("summary"),
        "concordant_findings": analysis.get("concordant_findings", []),
        "discrepancies": analysis.get("discrepancies", []),
        "has_critical_alert": analysis.get("has_critical_alert", False),
        "critical_alert_text": analysis.get("critical_alert_text"),
        "technical_note": analysis.get("technical_note"),
        "report_url": report_url,
        "extracted_texts": {
            "official": official_text[:500] + "..." if len(official_text) > 500 else official_text,
            "auditor": auditor_text[:500] + "..." if len(auditor_text) > 500 else auditor_text
        }
    }


@router.get("")
async def get_audits(limit: int = 50, offset: int = 0):
    """Lista todas as auditorias."""
    audits = list_audits(limit=limit, offset=offset)
    return {"audits": audits, "count": len(audits)}


@router.get("/{audit_id}")
async def get_audit_detail(audit_id: str):
    """Retorna detalhes de uma auditoria específica."""
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")
    return audit


@router.get("/{audit_id}/report")
async def download_report(audit_id: str):
    """Regenera e faz download do relatório PDF."""
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")

    # Regenera o PDF
    report_bytes = generate_report_pdf(audit)

    return StreamingResponse(
        io.BytesIO(report_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=relatorio_{audit_id}.pdf"
        }
    )
