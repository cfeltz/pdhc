FROM ubuntu:22.04

RUN apt-get update && apt-get upgrade -y \ 
    && apt-get install -y --no-install-recommends \
        python3.10 \
        python3.10-venv \
        python3-pip \
        ca-certificates \
        bash \
        ffmpeg \
        curl \
        wget

COPY . /opt/pdhc/
COPY etc/pdhc/ /etc/pdhc/

RUN python3.10 -m venv /opt/pdhc/venv 

ENV PATH="/opt/pdhc/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /opt/pdhc/requirements.txt \
    && pip install -e /opt/pdhc/ 

WORKDIR /opt/pdhc