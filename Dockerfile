FROM python:3.12-slim
WORKDIR /app
COPY . /app
CMD ["python", "crypto_intel_agent_v2.py", "--per-page", "50"]
