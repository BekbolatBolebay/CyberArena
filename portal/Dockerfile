FROM python:3.13-slim

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin arena

COPY server.py missions.py /app/
COPY static /app/static

RUN mkdir -p /app/data && chown -R arena:arena /app

USER arena

ENV ARENA_HOST=0.0.0.0
ENV ARENA_PORT=8000
ENV ARENA_DB_PATH=/app/data/arena.db
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python3", "/app/server.py"]
