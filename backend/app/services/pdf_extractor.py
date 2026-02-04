import io
import pdfplumber
from typing import Optional

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extrai texto de um arquivo PDF.
    Usa pdfplumber para PDFs nativos (texto selecionável).
    Se o texto extraído for muito curto, tenta OCR como fallback.
    """
    text = ""

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Erro ao extrair texto com pdfplumber: {e}")
        return ""

    # Se o texto extraído for muito curto, pode ser um PDF escaneado
    # Nesse caso, tentamos OCR (requer tesseract instalado)
    if len(text.strip()) < 50:
        text = _try_ocr_extraction(pdf_bytes)

    return text.strip()


def _try_ocr_extraction(pdf_bytes: bytes) -> str:
    """
    Tenta extrair texto usando OCR (Tesseract).
    Requer pytesseract e tesseract-ocr instalados no sistema.
    """
    try:
        import pytesseract
        from PIL import Image
        from pdf2image import convert_from_bytes

        # Converte PDF para imagens
        images = convert_from_bytes(pdf_bytes)

        text = ""
        for image in images:
            page_text = pytesseract.image_to_string(image, lang='por')
            text += page_text + "\n"

        return text.strip()
    except ImportError:
        print("OCR não disponível: pdf2image ou pytesseract não instalado")
        return ""
    except Exception as e:
        print(f"Erro no OCR: {e}")
        return ""


def validate_pdf(pdf_bytes: bytes) -> tuple[bool, Optional[str]]:
    """
    Valida se o arquivo é um PDF válido.
    Retorna (True, None) se válido, (False, mensagem_erro) se inválido.
    """
    # Verifica magic bytes do PDF
    if not pdf_bytes.startswith(b'%PDF'):
        return False, "Arquivo não é um PDF válido"

    # Tenta abrir com pdfplumber para validação adicional
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if len(pdf.pages) == 0:
                return False, "PDF não contém páginas"
    except Exception as e:
        return False, f"Erro ao processar PDF: {str(e)}"

    return True, None
