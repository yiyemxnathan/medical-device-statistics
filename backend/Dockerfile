FROM python:3.12-slim

WORKDIR /app/backend

COPY pyproject.toml ./
COPY app ./app
COPY tests ./tests

RUN python -m pip install --no-cache-dir -e ".[test]"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
