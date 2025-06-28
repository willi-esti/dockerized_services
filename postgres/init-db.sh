#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE planka;
    CREATE DATABASE wiki;
    CREATE ROLE wikijs WITH LOGIN PASSWORD 'wikijs';
    GRANT ALL PRIVILEGES ON DATABASE wiki TO wikijs;
EOSQL
# Not needed we use postgres user for planka
#    CREATE ROLE planka WITH LOGIN PASSWORD 'planka';
#    GRANT ALL PRIVILEGES ON DATABASE planka TO planka;
