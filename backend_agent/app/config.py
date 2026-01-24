# app/config.py
import os

# ===== OLLAMA CONFIG (Ollama local - FREE) =====
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
