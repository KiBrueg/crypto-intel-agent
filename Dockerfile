FROM python:3.12-slim
ENV PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app
EXPOSE 8765
CMD ["python", "web_dashboard.py", "--host", "0.0.0.0", "--port", "8765"]
