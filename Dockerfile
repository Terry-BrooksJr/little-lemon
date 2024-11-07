FROM python:3.12.7-bullseye
LABEL maintainer="Terry Brooks, Jr."

# Install necessary dependencies and Doppler CLI
RUN apt update && apt upgrade -y && apt install -y \
    apt-transport-https \
    ca-certificates \
    apache2-utils \
    curl \
    gnupg \
    cron \
    libmagic1 \
    libssl-dev \
    libenchant-2-dev \
    make \
    git

# Install Doppler CLI
RUN curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | \
    gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | \
    tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler=3.69.0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Exopse Appliocation Port 
EXPOSE 8080

# Set environment variables2
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DOPPLER_TOKEN=${DOPPLER_TOKEN}

RUN mkdir -p /src/api
RUN mkdir -p /src/.postgresql
WORKDIR /src
# Create necessary groups and users
RUN groupadd --system api && \
    useradd -g celery api && \
    groupadd --system api && \
    useradd --home-dir /src/api --no-create-home -g nhhc nhhc_app

RUN pip install --upgrade pip
COPY --chown=api:api requirements.txt /src/

COPY --chown=api:api little-lemon/ /src/api
COPY --chown=api:api .postgresql/do-cert.crt /src/.postgresql
