import json
import google.generativeai as genai
from typing import Optional
from app.config import GEMINI_API_KEY
from app.prompts.comparison import SYSTEM_PROMPT, USER_MESSAGE_TEMPLATE


def configure_gemini():
    """Configura a API do Gemini com a chave."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY não configurada")
    genai.configure(api_key=GEMINI_API_KEY)


def compare_reports(
    official_text: str,
    auditor_text: str,
    patient_name: str = "Não informado",
    exam_type: str = "Não informado",
    exam_date: str = "Não informada"
) -> dict:
    """
    Compara dois laudos médicos usando Gemini API.

    Args:
        official_text: Texto do laudo oficial
        auditor_text: Texto do laudo do auditor
        patient_name: Nome do paciente
        exam_type: Tipo do exame
        exam_date: Data do exame

    Returns:
        dict com resultado da comparação
    """
    configure_gemini()

    # Monta a mensagem do usuário
    user_message = USER_MESSAGE_TEMPLATE.format(
        patient_name=patient_name,
        exam_type=exam_type,
        exam_date=exam_date,
        official_text=official_text,
        auditor_text=auditor_text
    )

    # Configura o modelo
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT
    )

    # Configuração de geração
    generation_config = {
        "temperature": 0.1,  # Baixa temperatura para respostas consistentes
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 4096,
    }

    try:
        response = model.generate_content(
            user_message,
            generation_config=generation_config
        )

        # Extrai o texto da resposta
        response_text = response.text.strip()

        # Remove possíveis marcadores de código markdown
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        # Parse do JSON
        result = json.loads(response_text.strip())

        # Valida campos obrigatórios
        required_fields = ["classification", "summary", "concordant_findings", "discrepancies"]
        for field in required_fields:
            if field not in result:
                result[field] = [] if field in ["concordant_findings", "discrepancies"] else ""

        # Garante valores padrão para campos opcionais
        result.setdefault("has_critical_alert", False)
        result.setdefault("critical_alert_text", None)
        result.setdefault("technical_note", None)

        return {
            "success": True,
            "data": result,
            "raw_response": response_text
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Erro ao parsear resposta da IA: {str(e)}",
            "raw_response": response_text if 'response_text' in locals() else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro na chamada da API Gemini: {str(e)}",
            "raw_response": None
        }


def get_classification_color(classification: str) -> str:
    """Retorna a cor hexadecimal baseada na classificação."""
    colors = {
        "CONCORDÂNCIA TOTAL": "#27ae60",
        "CONCORDÂNCIA PARCIAL": "#f39c12",
        "DISCORDÂNCIA": "#e74c3c"
    }
    return colors.get(classification, "#95a5a6")
