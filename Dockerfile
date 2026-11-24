FROM gurobi/optimizer:12.0.2

ENV SOLVER=gurobi

WORKDIR /app

# Add this line before your pip install commands
# glpk-utils provides the `glpsol` binary so users can pick GLPK as solver too
RUN apt-get update && apt-get install -y build-essential glpk-utils libglpk-dev

COPY urbs-env.txt .

RUN python -m venv urbs-env \
    && ./urbs-env/bin/pip install --upgrade pip \
    && ./urbs-env/bin/pip install -r urbs-env.txt \
    && ./urbs-env/bin/pip install flask waitress

RUN ./urbs-env/bin/pip install glpk

COPY urbs urbs
COPY runme.py .
COPY server.py .

CMD ["./urbs-env/bin/python", "-m", "waitress", "--port=5000", "server:app"]