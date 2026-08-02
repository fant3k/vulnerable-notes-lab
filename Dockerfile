FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VNL_HOST=0.0.0.0 \
    VNL_PORT=8090 \
    VNL_DATA_DIR=/app/data

WORKDIR /app

RUN useradd --create-home --uid 10001 labuser

COPY --chown=labuser:labuser app.py ./
COPY --chown=labuser:labuser vuln_notes ./vuln_notes
RUN mkdir -p /app/data/uploads && chown -R labuser:labuser /app/data

USER labuser

EXPOSE 8090
HEALTHCHECK --interval=10s --timeout=2s --start-period=3s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8090/health', timeout=1)"

CMD ["python3", "app.py"]

