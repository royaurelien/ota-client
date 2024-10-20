FROM python:3.9-slim

ADD . /app
WORKDIR /app


RUN apt update && apt install cloc graphviz --yes
RUN pip install -e .

VOLUME [ "/data" ]

ENTRYPOINT [ "/app/entrypoint.sh" ]
