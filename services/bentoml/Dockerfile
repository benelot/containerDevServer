FROM python:3.11-slim

RUN pip install --no-cache-dir \
    bentoml \
    mlflow \
    torch --index-url https://download.pytorch.org/whl/cpu \
    boto3 \
    numpy

WORKDIR /app
COPY service.py .

EXPOSE 3000

CMD ["bentoml", "serve", "service:svc", "--host", "0.0.0.0", "--port", "3000"]
