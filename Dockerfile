# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /bot

# Install git
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvloop

COPY bot bot

# Stage 2: Production
FROM python:3.11-slim as production

WORKDIR /bot

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY --from=builder /bot /bot

CMD ["python", "-m", "bot.main"]