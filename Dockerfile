# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot bot

# Stage 2: Production
FROM python:3.11-slim as production

WORKDIR /

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

RUN rm -f /usr/lib/x86_64-linux-gnu/libmfxhw* /usr/lib/x86_64-linux-gnu/mfx/* && \
    useradd --create-home --shell /bin/sh zaws && \
    chown -R zaws:zaws .

USER zaws

COPY --from=builder /bot /bot

CMD ["python", "-m", "bot.main"]