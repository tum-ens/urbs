FROM python:3.12-slim

WORKDIR /app

COPY urbs-env.txt .
RUN python -m venv urbs-env

RUN python -m venv urbs-env \
    && ./urbs-env/bin/pip install --upgrade pip \
    && ./urbs-env/bin/pip install -r urbs-env.txt \
    && ./urbs-env/bin/pip install flask waitress


RUN apt-get update && apt-get install -y \
    gcc libglpk-dev glpk-utils
RUN ./urbs-env/bin/pip install glpk

COPY urbs urbs
COPY runme.py .
COPY server.py .

CMD ["./urbs-env/bin/python", "-m", "waitress", "--port=5000", "server:app"]