import React, { useState } from "react";

// API base URL - có thể thay đổi bằng environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const styles = {
  container: {
    maxWidth: "1200px",
    margin: "0 auto",
    padding: "20px",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif",
    backgroundColor: "#f5f5f5",
    minHeight: "100vh",
  },
  header: {
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    padding: "30px",
    borderRadius: "10px",
    marginBottom: "30px",
    boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
  },
  title: {
    margin: "0 0 10px 0",
    fontSize: "32px",
    fontWeight: "700",
  },
  subtitle: {
    margin: "0",
    fontSize: "16px",
    opacity: 0.9,
  },
  tabs: {
    display: "flex",
    gap: "10px",
    marginBottom: "20px",
  },
  tab: {
    padding: "12px 24px",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "16px",
    fontWeight: "600",
    transition: "all 0.3s",
    backgroundColor: "#fff",
    color: "#667eea",
    boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
  },
  tabActive: {
    backgroundColor: "#667eea",
    color: "white",
  },
  content: {
    backgroundColor: "white",
    borderRadius: "10px",
    padding: "30px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  },
  chatContainer: {
    display: "flex",
    flexDirection: "column",
    gap: "20px",
  },
  chatMessages: {
    maxHeight: "500px",
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: "15px",
    padding: "20px",
    backgroundColor: "#f9f9f9",
    borderRadius: "8px",
  },
  message: {
    padding: "15px",
    borderRadius: "10px",
    maxWidth: "80%",
  },
  userMessage: {
    backgroundColor: "#667eea",
    color: "white",
    alignSelf: "flex-end",
    marginLeft: "auto",
  },
  aiMessage: {
    backgroundColor: "#e8e8e8",
    color: "#333",
    alignSelf: "flex-start",
  },
  messageLabel: {
    fontSize: "12px",
    fontWeight: "600",
    marginBottom: "5px",
    opacity: 0.8,
  },
  messageText: {
    margin: "0",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
  inputGroup: {
    display: "flex",
    gap: "10px",
  },
  input: {
    flex: 1,
    padding: "12px 16px",
    border: "2px solid #e0e0e0",
    borderRadius: "8px",
    fontSize: "16px",
    outline: "none",
    transition: "border-color 0.3s",
  },
  inputFocus: {
    borderColor: "#667eea",
  },
  textarea: {
    flex: 1,
    padding: "12px 16px",
    border: "2px solid #e0e0e0",
    borderRadius: "8px",
    fontSize: "16px",
    outline: "none",
    transition: "border-color 0.3s",
    minHeight: "200px",
    fontFamily: "inherit",
    resize: "vertical",
  },
  button: {
    padding: "12px 24px",
    backgroundColor: "#667eea",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontSize: "16px",
    fontWeight: "600",
    cursor: "pointer",
    transition: "all 0.3s",
    boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
  },
  buttonHover: {
    backgroundColor: "#5568d3",
    transform: "translateY(-2px)",
    boxShadow: "0 4px 8px rgba(0,0,0,0.15)",
  },
  buttonDisabled: {
    backgroundColor: "#ccc",
    cursor: "not-allowed",
  },
  invoiceForm: {
    display: "flex",
    flexDirection: "column",
    gap: "20px",
  },
  resultContainer: {
    marginTop: "20px",
    padding: "20px",
    backgroundColor: "#f9f9f9",
    borderRadius: "8px",
    maxHeight: "600px",
    overflowY: "auto",
  },
  resultTitle: {
    margin: "0 0 15px 0",
    fontSize: "20px",
    fontWeight: "600",
    color: "#333",
  },
  resultJson: {
    backgroundColor: "#2d2d2d",
    color: "#f8f8f2",
    padding: "20px",
    borderRadius: "8px",
    fontSize: "14px",
    fontFamily: "'Courier New', monospace",
    overflowX: "auto",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
  error: {
    backgroundColor: "#fee",
    color: "#c33",
    padding: "15px",
    borderRadius: "8px",
    marginTop: "20px",
  },
  loading: {
    textAlign: "center",
    padding: "20px",
    color: "#667eea",
    fontSize: "16px",
  },
};

export default function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [msg, setMsg] = useState("");
  const [chat, setChat] = useState([]);
  const [invoiceText, setInvoiceText] = useState("");
  const [invoiceResult, setInvoiceResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendChat = async () => {
    if (!msg.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      });
      const d = await r.json();
      setChat([...chat, { u: msg, b: d.reply }]);
      setMsg("");
    } catch (err) {
      setError("Lỗi khi gửi tin nhắn: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const extractInvoice = async () => {
    if (!invoiceText.trim()) return;
    
    // QUAN TRỌNG: Clear tất cả state trước khi gửi request mới
    // Mỗi lần bấm button này = một request hoàn toàn mới, độc lập
    setError(null);
    setInvoiceResult(null);
    setLoading(true);
    
    try {
      const r = await fetch(`${API_BASE_URL}/api/extract-invoice`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ invoice_text: invoiceText }),
      });
      const d = await r.json();
      if (d.ok) {
        setInvoiceResult(d.data);
        setError(null); // Clear error nếu thành công
      } else {
        // Hiển thị error message từ backend (có thể kèm message hướng dẫn)
        const errorMsg = d.error || "Lỗi khi trích xuất hóa đơn";
        const helpMsg = d.message || "Bạn có thể thử lại bằng cách bấm nút 'Trích xuất Hóa đơn' lại.";
        setError(`${errorMsg}\n\n💡 ${helpMsg}`);
      }
    } catch (err) {
      setError(`Lỗi khi trích xuất hóa đơn: ${err.message}\n\n💡 Bạn có thể thử lại bằng cách bấm nút 'Trích xuất Hóa đơn' lại.`);
    } finally {
      setLoading(false);
    }
  };

  // Clear error và result khi switch tab
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === "invoice") {
      // Khi chuyển sang tab invoice, clear error và result cũ (nếu có)
      // Để user có thể bắt đầu lại từ đầu
      setError(null);
      setInvoiceResult(null);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>🤖 Ollama GenAI Agent</h1>
        <p style={styles.subtitle}>Trợ lý AI thông minh với Strand Agent & Invoice Extraction</p>
      </div>

      <div style={styles.tabs}>
        <button
          style={{ ...styles.tab, ...(activeTab === "chat" ? styles.tabActive : {}) }}
          onClick={() => handleTabChange("chat")}
        >
          💬 Chat với AI
        </button>
        <button
          style={{ ...styles.tab, ...(activeTab === "invoice" ? styles.tabActive : {}) }}
          onClick={() => handleTabChange("invoice")}
        >
          📄 Trích xuất Hóa đơn
        </button>
      </div>

      <div style={styles.content}>
        {activeTab === "chat" && (
          <div style={styles.chatContainer}>
            <div style={styles.chatMessages}>
              {chat.length === 0 && (
                <p style={{ textAlign: "center", color: "#999", margin: "20px 0" }}>
                  Chào mừng! Hãy bắt đầu cuộc trò chuyện với AI agent.
                </p>
              )}
              {chat.map((c, i) => (
                <div key={i}>
                  <div style={{ ...styles.message, ...styles.userMessage }}>
                    <div style={styles.messageLabel}>Bạn</div>
                    <p style={styles.messageText}>{c.u}</p>
                  </div>
                  <div style={{ ...styles.message, ...styles.aiMessage }}>
                    <div style={styles.messageLabel}>AI Agent</div>
                    <p style={styles.messageText}>{c.b}</p>
                  </div>
                </div>
              ))}
              {loading && activeTab === "chat" && (
                <div style={styles.loading}>Đang xử lý...</div>
              )}
            </div>
            <div style={styles.inputGroup}>
              <input
                style={styles.input}
                value={msg}
                onChange={(e) => setMsg(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && sendChat()}
                placeholder="Nhập tin nhắn của bạn..."
                disabled={loading}
              />
              <button
                style={{
                  ...styles.button,
                  ...(loading ? styles.buttonDisabled : {}),
                }}
                onClick={sendChat}
                disabled={loading}
              >
                Gửi
              </button>
            </div>
          </div>
        )}

        {activeTab === "invoice" && (
          <div style={styles.invoiceForm}>
            <h3 style={{ margin: "0 0 15px 0", color: "#333" }}>
              Nhập nội dung hóa đơn để trích xuất thông tin
            </h3>
            <textarea
              style={styles.textarea}
              value={invoiceText}
              onChange={(e) => setInvoiceText(e.target.value)}
              placeholder="Dán nội dung hóa đơn vào đây..."
              disabled={loading}
            />
            <button
              style={{
                ...styles.button,
                ...(loading ? styles.buttonDisabled : {}),
              }}
              onClick={extractInvoice}
              disabled={loading || !invoiceText.trim()}
            >
              {loading ? "Đang xử lý..." : "Trích xuất Hóa đơn"}
            </button>

            {error && (
              <div style={styles.error}>
                <div style={{ marginBottom: "10px", fontWeight: "600" }}>❌ Lỗi:</div>
                <div style={{ whiteSpace: "pre-wrap", marginBottom: "15px" }}>{error}</div>
                <button
                  style={{
                    ...styles.button,
                    backgroundColor: "#c33",
                    fontSize: "14px",
                    padding: "8px 16px",
                  }}
                  onClick={() => {
                    setError(null);
                    setInvoiceResult(null);
                  }}
                >
                  ✖️ Xóa thông báo lỗi
                </button>
              </div>
            )}

            {invoiceResult && (
              <div style={styles.resultContainer}>
                <h3 style={styles.resultTitle}>📋 Kết quả trích xuất:</h3>
                <pre style={styles.resultJson}>
                  {JSON.stringify(invoiceResult, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
