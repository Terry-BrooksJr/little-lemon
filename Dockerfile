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
    apt-get -y install doppler && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Expose Application Port 
EXPOSE 8080

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOPPLER_TOKEN=${DOPPLER_TOKEN}
ENV POSTGRES_CERT_FILE=/src/.postgresql/do-cert.crt
# Set up directories and permissions
RUN mkdir -p /src/api /src/.postgresql && \
    groupadd --system api_group && \
    useradd --home-dir /src/api --no-create-home -g api_group api

WORKDIR /src/api/

# Install dependencies
RUN pip install --upgrade pip
COPY --chown=api:api_group requirements.txt /src/
COPY --chown=api:api_group little_lemon/ /src/api
RUN wget https://cloud.digitalocean.com/fc4d1f0f-d3d2-42a4-8b81-2bc09967e1ad -O /src/.postgresql/do-cert.crt
# Set up Doppler directory permissions
RUN mkdir -p /src/api/.doppler && \
    chown api:api_group /src/api/.doppler && \
    chmod 775 /src/api/.doppler

RUN pip install  --no-cache-dir  -r /src/requirements.txt

USER api
CMD ["inv", "start", "-p 8080", "-w 2", "-t 2"]  