# app/agent/chat_agent.py
from strands import Agent
from strands.models.ollama import OllamaModel  # Import OllamaModel class
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
import asyncio

# Khởi tạo Ollama model provider object
ollama_model_provider = OllamaModel(
    host=OLLAMA_BASE_URL,  # Ollama server address
    model_id=OLLAMA_MODEL  # Specify which model to use
)

# Cấu hình cố định cho Chat Agent
CHAT_SYSTEM_PROMPT = "Bạn là trợ lý AI thân thiện. Trả lời ngắn gọn, rõ ràng, không lan man."

async def run_chat(message: str) -> str:
    """
    Gọi agent với invoke_async() method (async) đúng chuẩn Strands SDK.
    
    LƯU Ý QUAN TRỌNG VỀ CONCURRENCY: Khởi tạo Agent mới cho mỗi request để hỗ trợ 
    xử lý đồng thời (Concurrency), tránh lỗi 'Agent is already processing'.
    """
    
    # Khởi tạo Agent mới cho mỗi request để hỗ trợ Concurrency
    chat_agent = Agent(
        model=ollama_model_provider, 
        system_prompt=CHAT_SYSTEM_PROMPT
    )

    # Dùng invoke_async() cho các agent call bất đồng bộ
    result = await chat_agent.invoke_async(message)
    
    # Lấy text từ result
    if hasattr(result, 'last_message'):
        return result.last_message.content.text
    elif hasattr(result, 'output'):
        return result.output
    else:
        return str(result)
