FROM python:3.13-slim

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin camuser

COPY camera_server.py cctv_passwords.txt /app/

USER camuser

ENV CAMERA_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

EXPOSE 8081

CMD ["python3", "/app/camera_server.py"]
