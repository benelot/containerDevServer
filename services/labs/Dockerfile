FROM python:3.11-slim

ARG HUGO_VERSION=0.128.2

# System deps + Hugo binary
RUN apt-get update && apt-get install -y --no-install-recommends git wget ca-certificates && \
    ARCH=$(dpkg --print-architecture) && \
    wget -q -O /tmp/hugo.tar.gz \
        "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-${ARCH}.tar.gz" && \
    tar -xzf /tmp/hugo.tar.gz -C /usr/local/bin hugo && \
    rm /tmp/hugo.tar.gz && \
    apt-get purge -y wget && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app

# Download Hugo theme at build time so container starts offline-capable
RUN git clone --depth 1 --branch main \
        https://github.com/McShelby/hugo-theme-relearn \
        /app/themes/hugo-theme-relearn

# Copy site source (theme stays from above RUN layer)
COPY hugo.toml .
COPY content/    content/
COPY layouts/    layouts/
COPY static/     static/
COPY data/       data/
COPY scripts/    scripts/
COPY main.py     .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 3003

CMD ["./entrypoint.sh"]
