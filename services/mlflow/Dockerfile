FROM python:3.11-slim

ARG MLFLOW_VERSION=2.16.0

RUN pip install --no-cache-dir \
    "mlflow[extras]==${MLFLOW_VERSION}" \
    boto3 \
    psycopg2-binary \
    && rm -rf /root/.cache/pip

WORKDIR /mlflow
EXPOSE 5000

ENTRYPOINT ["mlflow"]
CMD ["server", "--host", "0.0.0.0", "--port", "5000"]
