FROM python:3.11-slim

WORKDIR /app

# 安装 ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY notion_uploader.py .

CMD ["python", "notion_uploader.py"]
