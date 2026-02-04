import uuid
from datetime import datetime
from typing import Optional
from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_KEY, STORAGE_BUCKET


def get_supabase_client() -> Client:
    """Retorna uma instância do cliente Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_pdf_to_storage(
    pdf_bytes: bytes,
    filename: str,
    folder: str = "uploads"
) -> Optional[str]:
    """
    Faz upload de um PDF para o Supabase Storage.

    Args:
        pdf_bytes: Conteúdo do arquivo em bytes
        filename: Nome do arquivo
        folder: Pasta dentro do bucket

    Returns:
        URL pública do arquivo ou None em caso de erro
    """
    client = get_supabase_client()

    # Gera nome único para evitar colisões
    unique_filename = f"{folder}/{uuid.uuid4()}_{filename}"

    try:
        # Upload do arquivo
        result = client.storage.from_(STORAGE_BUCKET).upload(
            unique_filename,
            pdf_bytes,
            file_options={"content-type": "application/pdf"}
        )

        # Gera URL pública
        public_url = client.storage.from_(STORAGE_BUCKET).get_public_url(unique_filename)
        return public_url

    except Exception as e:
        print(f"Erro no upload para Supabase Storage: {e}")
        return None


def save_audit(audit_data: dict) -> Optional[dict]:
    """
    Salva uma auditoria no banco de dados.

    Args:
        audit_data: Dicionário com dados da auditoria

    Returns:
        Registro salvo ou None em caso de erro
    """
    client = get_supabase_client()

    # Prepara os dados
    record = {
        "id": str(uuid.uuid4()),
        "patient_name": audit_data.get("patient_name", ""),
        "exam_type": audit_data.get("exam_type", ""),
        "exam_date": audit_data.get("exam_date"),
        "official_pdf_url": audit_data.get("official_pdf_url"),
        "auditor_pdf_url": audit_data.get("auditor_pdf_url"),
        "official_text": audit_data.get("official_text", ""),
        "auditor_text": audit_data.get("auditor_text", ""),
        "classification": audit_data.get("classification"),
        "analysis_summary": audit_data.get("analysis_summary"),
        "concordant_findings": audit_data.get("concordant_findings", []),
        "discrepancies": audit_data.get("discrepancies", []),
        "has_critical_alert": audit_data.get("has_critical_alert", False),
        "critical_alert_text": audit_data.get("critical_alert_text"),
        "technical_note": audit_data.get("technical_note"),
        "report_pdf_url": audit_data.get("report_pdf_url"),
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        result = client.table("audits").insert(record).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao salvar auditoria: {e}")
        return None


def get_audit(audit_id: str) -> Optional[dict]:
    """
    Busca uma auditoria pelo ID.

    Args:
        audit_id: UUID da auditoria

    Returns:
        Dados da auditoria ou None se não encontrada
    """
    client = get_supabase_client()

    try:
        result = client.table("audits").select("*").eq("id", audit_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao buscar auditoria: {e}")
        return None


def list_audits(limit: int = 50, offset: int = 0) -> list:
    """
    Lista auditorias com paginação.

    Args:
        limit: Número máximo de registros
        offset: Offset para paginação

    Returns:
        Lista de auditorias
    """
    client = get_supabase_client()

    try:
        result = (
            client.table("audits")
            .select("*")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"Erro ao listar auditorias: {e}")
        return []
