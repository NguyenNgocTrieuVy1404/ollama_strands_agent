# app/tools/preprocess.py
import re
from strands import tool

@tool
def clean_invoice_text(text: str) -> str:
    """
    Tool pure-Python để làm sạch text OCR.
    Đây KHÔNG gọi LLM.
    """
    if not text:
        return text
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = text.replace("­", "")  # soft hyphen artifacts
    return text.strip()
