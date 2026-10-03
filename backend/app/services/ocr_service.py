import os
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}


def extract_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato não suportado: {ext}")

    if ext == ".pdf":
        return _extract_from_pdf(file_path)
    elif ext == ".docx":
        return _extract_from_docx(file_path)
    else:
        return _ocr_image(file_path)


def _extract_from_pdf(file_path: str) -> str:
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise ImportError(
            "pdf2image não instalado. Execute: pip install pdf2image"
        )

    try:
        import pytesseract
    except ImportError:
        raise ImportError(
            "pytesseract não instalado. Execute: pip install pytesseract"
        )

    logger.info("Convertendo PDF para imagens: %s", file_path)
    images = convert_from_path(file_path, dpi=300, fmt="jpeg")
    texto_total = []

    for i, img in enumerate(images):
        logger.info("Aplicando OCR na página %d/%d", i + 1, len(images))
        texto = pytesseract.image_to_string(img, lang="por")
        texto_total.append(texto)

    return "\n\n".join(texto_total)


def _extract_from_docx(file_path: str) -> str:
    try:
        from docx import Document
    except ImportError:
        raise ImportError(
            "python-docx não instalado. Execute: pip install python-docx"
        )

    logger.info("Extraindo texto de DOCX: %s", file_path)
    doc = Document(file_path)
    paragrafos = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragrafos)


def _ocr_image(file_path: str) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise ImportError(
            "pytesseract/Pillow não instalados. Execute: pip install pytesseract Pillow"
        )

    logger.info("Aplicando OCR em imagem: %s", file_path)
    img = Image.open(file_path)
    texto = pytesseract.image_to_string(img, lang="por")
    return texto
