# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.agent.chat_agent import run_chat
from app.agent.invoice_agent import run_invoice_extraction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Strands-based GenAI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class InvoiceRequest(BaseModel):
    invoice_text: str

@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    """Chat endpoint sử dụng Strands Agent SDK"""
    try:
        reply = await run_chat(req.message)
        return {"ok": True, "reply": reply}
    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract-invoice")
async def api_extract(req: InvoiceRequest):
    """
    Invoice extraction endpoint sử dụng Strands Agent với Structured Output.
    
    LƯU Ý: Mỗi HTTP request là ĐỘC LẬP - không có state nào được giữ lại giữa các requests.
    Nếu request này fail, request tiếp theo sẽ bắt đầu lại từ đầu hoàn toàn mới.
    """
    try:
        # Mỗi lần gọi run_invoice_extraction() là một execution mới, độc lập
        data = await run_invoice_extraction(req.invoice_text)
        return {"ok": True, "data": data}
    except Exception as e:
        logger.exception("Invoice extraction error")
        # Trả về error message rõ ràng và cho biết có thể thử lại
        error_msg = str(e)
        # Rút gọn error message nếu quá dài
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        return {
            "ok": False, 
            "error": error_msg,
            "message": "Có thể thử lại bằng cách gửi request mới. Mỗi request là độc lập."
        }
