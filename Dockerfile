FROM python:3.7-alpine

RUN apk --no-cache add \
    build-base=0.5-r1 libffi-dev=3.2.1-r6 \
    snappy=1.1.7-r1 snappy-dev=1.1.7-r1

# Setting Novosibirsk time-zone
ENV TZ=Asia/Novosibirsk
# hadolint ignore=DL3018
RUN apk --no-cache add tzdata && \
    cp "/usr/share/zoneinfo/$TZ" /etc/localtime && \
    echo "$TZ" > /etc/timezone

WORKDIR /tools_news

# Installing Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessery .py files
COPY tools_news tools_news
COPY worker.py worker.py

# Create a directory for logging 
RUN mkdir logs

# Copying config files
RUN mkdir config
COPY deploy/logging.yaml config/logging.yaml
COPY deploy/tools_news.yaml config/tools_news.yaml
RUN touch ./.env

CMD ["python", "worker.py"]
