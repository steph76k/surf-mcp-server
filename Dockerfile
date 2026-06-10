FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen

COPY src ./src

EXPOSE 8000

CMD ["uv", "run", "python", "src/server.py"]
