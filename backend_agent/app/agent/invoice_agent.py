# app/agent/invoice_agent.py
from strands import Agent
from strands.models.ollama import OllamaModel  # Import OllamaModel class
from strands.types.exceptions import StructuredOutputException
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.tools.preprocess import clean_invoice_text
from agent_def import InvoiceSchema
from typing import Any
import asyncio

# Khởi tạo Ollama model provider object
ollama_model_provider = OllamaModel(
    host=OLLAMA_BASE_URL,  # Ollama server address
    model_id=OLLAMA_MODEL  # model muốn dùng (tùy)
)

# Định nghĩa Strands Agent với Ollama model provider và tools
# Agent sẽ tự động gọi tool clean_invoice_text để làm sạch text trước khi trích xuất
invoice_agent = Agent(
    model=ollama_model_provider, # Truyền object Ollama vào model parameter
    system_prompt=(
        "Bạn là một AI chuyên trích xuất dữ liệu từ hóa đơn với độ chính xác cao. "
        "QUY TRÌNH XỬ LÝ:\n"
        "1. Đầu tiên, sử dụng tool clean_invoice_text để làm sạch văn bản hóa đơn (loại bỏ ký tự lạ, chuẩn hóa format)\n"
        "2. Sau đó, đọc KỸ LƯỠNG toàn bộ văn bản đã được làm sạch và trích xuất TẤT CẢ thông tin có trong đó.\n\n"
        "QUY TẮC QUAN TRỌNG:\n"
        "1. ĐỌC TOÀN BỘ văn bản hóa đơn từ đầu đến cuối, không bỏ sót bất kỳ phần nào\n"
        "2. Tìm kiếm thông tin trong TẤT CẢ các phần: THÔNG TIN NGƯỜI BÁN, THÔNG TIN NGƯỜI MUA, CHI TIẾT SẢN PHẨM, và phần tính toán\n"
        "3. Nếu một trường có thông tin trong hóa đơn, BẮT BUỘC phải trích xuất, KHÔNG được để null\n"
        "4. Đối với thuế: Nếu hóa đơn ghi 'Thuế VAT (10%)' thì tax_rate = 10.0 và tax_amount = số tiền thuế tương ứng\n\n"
        "CÁC TRƯỜNG CẦN TRÍCH XUẤT:\n"
        "- invoice_number: Số hóa đơn (tìm trong dòng 'Số: ...')\n"
        "- date: Ngày phát hành (tìm trong dòng 'Ngày phát hành: ...')\n"
        "- seller_name: Tên người bán (tìm trong phần 'THÔNG TIN NGƯỜI BÁN')\n"
        "- seller_address: Địa chỉ người bán (tìm dòng 'Địa chỉ: ...' trong phần THÔNG TIN NGƯỜI BÁN)\n"
        "- seller_tax_code: Mã số thuế người bán (tìm dòng 'Mã số thuế: ...' trong phần THÔNG TIN NGƯỜI BÁN)\n"
        "- buyer_name: Tên người mua (tìm trong phần 'THÔNG TIN NGƯỜI MUA')\n"
        "- buyer_address: Địa chỉ người mua (tìm dòng 'Địa chỉ: ...' trong phần THÔNG TIN NGƯỜI MUA)\n"
        "- buyer_tax_code: Mã số thuế người mua (tìm dòng 'Mã số thuế: ...' trong phần THÔNG TIN NGƯỜI MUA)\n"
        "- items: Danh sách sản phẩm (tìm trong phần 'CHI TIẾT SẢN PHẨM')\n"
        "- subtotal: Tổng tiền trước thuế (tìm dòng 'Tổng tiền trước thuế: ...')\n"
        "- tax_rate: Thuế suất (tìm trong dòng 'Thuế VAT (...%)' - chuyển % thành số, ví dụ 10% = 10.0)\n"
        "- tax_amount: Số tiền thuế (tìm trong dòng 'Thuế VAT (...): ...')\n"
        "- total: Tổng cộng (tìm trong dòng 'TỔNG CỘNG: ...')\n"
        "- currency: Đơn vị tiền tệ (thường là VND)\n\n"
        "NHẮC LẠI: Đọc KỸ LƯỠNG và trích xuất TẤT CẢ thông tin có trong hóa đơn!"
    ),
    tools=[clean_invoice_text],  # Agent sẽ tự động gọi tool này để làm sạch text trước khi trích xuất
)

async def run_invoice_extraction(invoice_text: str) -> Any:
    """
    Gọi agent với structured output đúng chuẩn Strands SDK.
    
    QUAN TRỌNG: Function này là STATELESS - mỗi lần gọi là hoàn toàn độc lập.
    Mỗi request mới sẽ gọi agent một lần duy nhất (không có retry).
    
    Implementation theo Structured Output API của Strands:
    - Sử dụng invoke_async() với structured_output_model parameter (Recommended API)
    - Deprecated: agent.structured_output() - KHÔNG dùng nữa
    
    Reference: 
    - https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/structured-output/
    
    Args:
        invoice_text: Văn bản hóa đơn cần trích xuất
    
    Returns:
        dict: Dữ liệu hóa đơn đã được trích xuất và validate
    """
    # Gửi invoice_text thô vào agent
    # Agent sẽ tự động gọi tool clean_invoice_text trong agent loop để làm sạch text trước
    # Sau đó agent mới thực hiện structured output extraction
    user_message = f"""Trích xuất ĐẦY ĐỦ thông tin từ hóa đơn sau:

{invoice_text}

Hãy đọc KỸ LƯỠNG toàn bộ văn bản và trích xuất TẤT CẢ thông tin có trong đó, bao gồm:
- Thông tin người bán (tên, địa chỉ, mã số thuế)
- Thông tin người mua (tên, địa chỉ, mã số thuế)
- Chi tiết sản phẩm/dịch vụ
- Thông tin về thuế (tax_rate và tax_amount)
- Tổng tiền và các thông tin tính toán khác"""
    
    try:
        # Dùng invoke_async() với structured_output_model parameter (Recommended API)
        # Theo documentation: https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/structured-output/
        result = await invoice_agent.invoke_async(
            user_message,
            structured_output_model=InvoiceSchema
        )
        
        # Truy cập structured output qua result.structured_output (theo documentation)
        # result.structured_output là Pydantic model instance đã được validate
        return result.structured_output.model_dump()
        
    except StructuredOutputException as e:
        # StructuredOutputException được raise khi model không thể invoke structured output tool
        raise RuntimeError(
            f"Không thể trích xuất hóa đơn. "
            f"Nguyên nhân có thể do: model quá nhỏ, hóa đơn quá phức tạp, hoặc format không đúng. "
            f"Bạn có thể thử lại với request mới hoặc thử model lớn hơn. "
            f"Chi tiết lỗi: {str(e)}"
        )
    
    except Exception as e:
        # Các exception khác (network, validation, etc.)
        raise RuntimeError(
            f"Lỗi khi trích xuất hóa đơn: {str(e)}. "
            f"Bạn có thể thử lại với request mới. Mỗi request là độc lập."
        )
