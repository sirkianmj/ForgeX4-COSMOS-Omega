FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make libc6-dev linux-libc-dev libseccomp-dev pkg-config \
    libexpat1-dev zlib1g-dev libpcre2-dev libsqlite3-dev \
    libxml2-dev libyaml-dev libpng-dev libjpeg62-turbo-dev \
    libarchive-dev libssl-dev liblua5.4-dev \
    python3 python3-yaml python3-jinja2 python3-lxml python3-markdown \
    python3-flask gunicorn \
    nginx-light lighttpd redis-server memcached \
    git poppler-utils ghostscript imagemagick \
    sqlite3 jq tar gzip bzip2 xz-utils unzip curl file gawk \
    bc patch diffutils findutils sed perl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/cosmos_sandbox
COPY cosmos_enforcer.c /opt/cosmos_sandbox/cosmos_enforcer.c
COPY sandbox_daemon.py /opt/cosmos_sandbox/sandbox_daemon.py

RUN gcc -O2 -Wall -Wextra -o /usr/local/bin/cosmos_enforcer /opt/cosmos_sandbox/cosmos_enforcer.c -lseccomp

EXPOSE 8787
CMD ["python3", "/opt/cosmos_sandbox/sandbox_daemon.py"]
