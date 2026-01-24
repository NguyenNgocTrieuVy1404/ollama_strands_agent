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
        data = await run_invoice_extraction(req.invoice_text)
        return {"ok": True, "data": data}
    except ValueError as e:
        # Lỗi do input của người dùng (quá ngắn, không đúng format, hoặc model không trích xuất được)
        logger.warning(f"User input error: {str(e)}")
        return {
            "ok": False,
            "error_type": "VALIDATION_ERROR",
            "message": str(e)
        }
    except Exception as e:
        logger.exception("System error during invoice extraction")
        return {
            "ok": False,
            "error_type": "SYSTEM_ERROR",
            "message": "Có lỗi xảy ra trong quá trình xử lý hệ thống. Vui lòng thử lại sau."
        }
