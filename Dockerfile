FROM python:3.11-slim

WORKDIR /app

# 複製項目文件
COPY . .

# 安裝依賴
COPY dependencies.txt .
RUN pip install --no-cache-dir -r dependencies.txt

# 創建必要的目錄結構
RUN mkdir -p .streamlit

# 複製 Streamlit 配置文件
COPY .streamlit/config.toml .streamlit/

# 默認端口設置為 5000（與 Replit 相同）
EXPOSE 5000

# 啟動 Streamlit 應用
CMD ["streamlit", "run", "Home.py", "--server.port=5000", "--server.address=0.0.0.0"]