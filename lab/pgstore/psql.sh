#!/usr/bin/env bash
# Mở psql vào schema cerbos của lab. Ví dụ:
#   ./pgstore/psql.sh -c "select id, kind, name, version, disabled from policy;"
cd "$(dirname "$0")"
docker compose exec -T postgres psql -U postgres -d postgres -v ON_ERROR_STOP=1 \
  -c "set search_path to cerbos" "$@"
