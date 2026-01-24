# Ollama Strands Agent

Ứng dụng full-stack sử dụng **Strands Agent SDK** với **Ollama** (local LLM) để xây dựng AI agents cho chat và trích xuất hóa đơn.

## 🚀 Công nghệ

- **Backend:** Strands Agent SDK, FastAPI, Pydantic, Ollama
- **Frontend:** React, Vite
- **Infrastructure:** Docker & Docker Compose

## 📋 Yêu cầu

- Docker Desktop
- Tối thiểu 4GB RAM

## 🛠️ Cài đặt và chạy

### Bước 1: Clone repository
```bash
git clone https://github.com/NguyenNgocTrieuVy1404/Ollama_Strands_Agent.git
cd ollama_strands_agent
```

### Bước 2: Pull Ollama model (QUAN TRỌNG!)

**Cách 1: Pull model trước khi start (Khuyến nghị)**
```bash
# Start Ollama container
docker-compose up ollama -d

# Đợi Ollama khởi động (10-20 giây), sau đó pull model
docker exec -it ollama_strands ollama pull qwen2.5:3b
```

**Cách 2: Pull model sau khi start**
```bash
docker-compose up --build -d
docker exec -it ollama_strands ollama pull qwen2.5:3b
docker-compose restart backend
```

**Lưu ý:** Model được lưu trong Docker volume, chỉ cần pull một lần.

### Bước 3: Start services
```bash
docker-compose up --build
```

### Bước 4: Truy cập ứng dụng
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Ollama API:** http://localhost:11434

## ⚙️ Cấu hình

### Thay đổi model Ollama

Sửa trong `docker-compose.yml`:
```yaml
environment:
  - OLLAMA_MODEL=qwen2.5:3b  # Thay đổi model ở đây
```

Sau đó pull model mới và restart:
```bash
docker exec -it ollama_strands ollama pull <model-name>
docker-compose restart backend
```

## 🔧 Tính năng

- **Chat Agent:** Tương tác chat với AI (`POST /api/chat`)
- **Invoice Extraction:** Trích xuất thông tin hóa đơn với Structured Output (`POST /api/extract-invoice`)

**Lưu ý:** Sử dụng `agent.invoke_async(prompt, structured_output_model=Model)` - không dùng deprecated `structured_output()` method.

## 📝 Lưu ý quan trọng

### Strands Agent SDK
- Import: `from strands.models.ollama import OllamaModel`
- Khởi tạo: `OllamaModel(host=..., model_id=...)`
- Dùng `structured_output_model` parameter khi gọi agent

### Model Ollama
- Model `qwen2.5:3b` phù hợp máy yếu nhưng có thể thiếu một số trường optional
- Nếu cần độ chính xác cao hơn, dùng model lớn hơn (7b+)

## 🐛 Troubleshooting

**Model not found:**
```bash
docker exec -it ollama_strands ollama pull qwen2.5:3b
```

**Cannot connect to Ollama:**
- Kiểm tra container: `docker ps`
- Kiểm tra `OLLAMA_BASE_URL` trong `docker-compose.yml`

**Structured output failed:**
- Model có thể quá nhỏ, thử model lớn hơn
- Xem logs: `docker-compose logs backend`

## 📚 Tài liệu tham khảo

- [Strands Agent SDK](https://strandsagents.com/latest/documentation/docs/)
- [Strands Structured Output](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/structured-output/)
- [Ollama Documentation](https://ollama.ai/docs)
