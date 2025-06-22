FROM postgres:15

RUN apt-get update && \
    apt-get install -y postgresql-server-dev-15 build-essential git && \
    git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git /tmp/pgvector && \
    cd /tmp/pgvector && make && make install && \
    rm -rf /tmp/pgvector && \
    apt-get remove --purge -y build-essential git && \
    apt-get autoremove -y && \
    apt-get clean
