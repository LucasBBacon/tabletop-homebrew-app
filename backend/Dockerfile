FROM python:3.11-slim

WORKDIR /tabletop-homebrew-app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY .env /tabletop-homebrew-app/.env

ENV PYTHONPATH=/tabletop-homebrew-app
ENV ENV_FILE_PATH=/tabletop-homebrew-app/.env

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]