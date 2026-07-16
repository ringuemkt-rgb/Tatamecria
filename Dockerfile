FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
RUN pip install --no-cache-dir ".[api,dashboard]"
EXPOSE 8000 8501
CMD ["uvicorn", "neurojitsu.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
