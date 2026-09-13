# 使用官方 Python 3.12 Slim Image 作為基礎環境
FROM python:3.12-slim

# 設定 Container 內的工作目錄
WORKDIR /app

# 先複製 Python 套件清單
COPY requirements.txt .

# 安裝 Football AI Platform 需要的 Python Packages
RUN python -m pip install --no-cache-dir -r requirements.txt

# 將專案程式碼複製到 Container 的 /app
COPY . .

# 說明 FastAPI Application 使用 8000 Port
EXPOSE 8000

# Container 啟動時執行 FastAPI / Uvicorn
CMD ["python", "-m", "uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]

