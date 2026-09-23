FROM python:3.11-slim

RUN pip install --no-cache-dir evidently \
    && rm -rf /root/.cache/pip

WORKDIR /workspace

EXPOSE 8000

ENTRYPOINT ["evidently", "ui"]
CMD ["--workspace", "/workspace", "--host", "0.0.0.0", "--port", "8000"]
