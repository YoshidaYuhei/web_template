#!/bin/bash
set -e

# テスト用データベースを作成
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE ${PACKAGE_NAME}_test;
    GRANT ALL PRIVILEGES ON DATABASE ${PACKAGE_NAME}_test TO $POSTGRES_USER;
EOSQL
