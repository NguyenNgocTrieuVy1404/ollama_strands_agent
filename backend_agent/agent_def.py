# agent_def.py
# File này chứa các Pydantic schemas cho invoice extraction
from pydantic import BaseModel, Field
from typing import List, Optional

# ===== SCHEMAS CHO INVOICE EXTRACTION =====

class InvoiceItem(BaseModel):
    """Item trong hóa đơn"""
    name: str = Field(description="Tên sản phẩm/dịch vụ")
    quantity: float = Field(description="Số lượng")
    unit_price: float = Field(description="Đơn giá")
    total: float = Field(description="Thành tiền")


class InvoiceSchema(BaseModel):
    """Schema cho hóa đơn"""
    invoice_number: str = Field(description="Số hóa đơn (ví dụ: HD-2024-001)")
    date: str = Field(description="Ngày phát hành hóa đơn (ví dụ: 15/01/2024)")
    seller_name: str = Field(description="Tên người bán/công ty bán")
    seller_address: Optional[str] = Field(None, description="Địa chỉ người bán - trích xuất từ phần THÔNG TIN NGƯỜI BÁN")
    seller_tax_code: Optional[str] = Field(None, description="Mã số thuế người bán - trích xuất từ phần THÔNG TIN NGƯỜI BÁN")
    buyer_name: str = Field(description="Tên người mua/công ty mua")
    buyer_address: Optional[str] = Field(None, description="Địa chỉ người mua - trích xuất từ phần THÔNG TIN NGƯỜI MUA")
    buyer_tax_code: Optional[str] = Field(None, description="Mã số thuế người mua - trích xuất từ phần THÔNG TIN NGƯỜI MUA")
    items: List[InvoiceItem] = Field(description="Danh sách sản phẩm/dịch vụ trong hóa đơn")
    subtotal: float = Field(description="Tổng tiền trước thuế (không bao gồm thuế)")
    tax_rate: Optional[float] = Field(None, description="Thuế suất tính theo phần trăm (ví dụ: 10.0 cho 10%)")
    tax_amount: Optional[float] = Field(None, description="Số tiền thuế phải trả (ví dụ: 5610000)")
    total: float = Field(description="Tổng cộng cuối cùng (bao gồm cả thuế)")
    currency: str = Field(default="VND", description="Đơn vị tiền tệ (thường là VND)")
