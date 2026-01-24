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
invoice_agent = Agent(
    model=ollama_model_provider, # Truyền object Ollama vào model parameter
    system_prompt=(
        "Bạn là một AI chuyên trích xuất dữ liệu từ hóa đơn với độ chính xác cao. "
        "Nhiệm vụ của bạn là đọc KỸ LƯỠNG toàn bộ văn bản hóa đơn và trích xuất TẤT CẢ thông tin có trong đó.\n\n"
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
    tools=[clean_invoice_text],  # tool tự định nghĩa 
)

async def run_invoice_extraction(invoice_text: str, retry_count: int = 3) -> Any:
    """
    Gọi agent với structured output đúng chuẩn Strands SDK.
    
    Implementation theo Structured Output API của Strands:
    - Sử dụng invoke_async() với structured_output_model parameter (Recommended API)
    - Deprecated: agent.structured_output() - KHÔNG dùng nữa
    - Retry mechanism với improved prompt khi lỗi (tương tự code cũ)
    - Error information được feed back vào agent loop để model tự điều chỉnh
    
    Reference: 
    - https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/structured-output/
    - https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/agent-loop/
    
    Args:
        invoice_text: Văn bản hóa đơn cần trích xuất
        retry_count: Số lần retry nếu structured output thất bại (default: 3)
    
    Returns:
        dict: Dữ liệu hóa đơn đã được trích xuất và validate
    """
    last_error = None
    
    for attempt in range(retry_count):
        try:
            # Xây dựng prompt với error information từ lần trước (nếu có)
            # Điều này phù hợp với Agent Loop concept: feed error back vào loop
            if attempt > 0 and last_error:
                # Improved prompt với error context - model sẽ nhận được feedback
                # và tự điều chỉnh trong agent loop
                user_message = f"""{invoice_text}

[QUAN TRỌNG - LẦN TRƯỚC ĐÃ THIẾU THÔNG TIN]
Lỗi: {last_error}

BẠN PHẢI ĐỌC LẠI TOÀN BỘ HÓA ĐƠN VÀ TRÍCH XUẤT ĐẦY ĐỦ:
1. Tìm trong phần "THÔNG TIN NGƯỜI BÁN":
   - seller_address: Tìm dòng "Địa chỉ: ..." (KHÔNG được để null nếu có)
   - seller_tax_code: Tìm dòng "Mã số thuế: ..." (KHÔNG được để null nếu có)

2. Tìm trong phần "THÔNG TIN NGƯỜI MUA":
   - buyer_address: Tìm dòng "Địa chỉ: ..." (KHÔNG được để null nếu có)
   - buyer_tax_code: Tìm dòng "Mã số thuế: ..." (KHÔNG được để null nếu có)

3. Tìm trong phần tính toán:
   - tax_rate: Tìm dòng "Thuế VAT (...%)" → chuyển % thành số (ví dụ: 10% = 10.0)
   - tax_amount: Tìm dòng "Thuế VAT (...): ..." → lấy số tiền thuế

Hãy đọc KỸ LƯỠNG từng dòng và trích xuất TẤT CẢ thông tin có trong hóa đơn!"""
            else:
                # Prompt ban đầu với hướng dẫn rõ ràng
                user_message = f"""Trích xuất ĐẦY ĐỦ thông tin từ hóa đơn sau:

{invoice_text}

Hãy đọc KỸ LƯỠNG toàn bộ văn bản và trích xuất TẤT CẢ thông tin có trong đó, bao gồm:
- Thông tin người bán (tên, địa chỉ, mã số thuế)
- Thông tin người mua (tên, địa chỉ, mã số thuế)
- Chi tiết sản phẩm/dịch vụ
- Thông tin về thuế (tax_rate và tax_amount)
- Tổng tiền và các thông tin tính toán khác"""
            
            # Dùng invoke_async() với structured_output_model parameter (Recommended API)
            # Theo documentation: https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/structured-output/
            # Deprecated: agent.structured_output() - KHÔNG dùng nữa
            # Recommended: agent.invoke_async(prompt, structured_output_model=Model)
            result = await invoice_agent.invoke_async(
                user_message,
                structured_output_model=InvoiceSchema
            )
            
            # Truy cập structured output qua result.structured_output (theo documentation)
            # result.structured_output là Pydantic model instance đã được validate
            return result.structured_output.model_dump()
            
        except StructuredOutputException as e:
            # StructuredOutputException được raise khi model không thể invoke structured output tool
            # Theo Agent Loop: tool execution failure được feed back vào model
            last_error = f"Structured output tool failed: {str(e)}"
            
            if attempt < retry_count - 1:
                # Continue loop với improved context
                continue
            else:
                # Loop terminated - không thể recover sau retry_count lần
                raise RuntimeError(
                    f"Structured output failed sau {retry_count} lần thử trong agent loop. "
                    f"Lỗi cuối: {last_error}"
                )
        
        except Exception as e:
            # Các exception khác (network, validation, etc.)
            last_error = f"Unexpected error: {str(e)}"
            
            if attempt < retry_count - 1:
                # Continue loop với error context
                continue
            else:
                # Loop terminated
                raise RuntimeError(
                    f"Error extracting invoice sau {retry_count} lần thử trong agent loop. "
                    f"Lỗi cuối: {last_error}"
                )
    
    # Fallback (không nên đến đây)
    raise RuntimeError(
        f"Không thể extract invoice sau {retry_count} lần thử trong agent loop. "
        f"Lỗi cuối: {last_error}"
    )
