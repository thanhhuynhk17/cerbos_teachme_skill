#!/usr/bin/env bash
# Bật Postgres + Cerbos (storage: postgres, Admin API bật) cho bài 0002.
set -e
cd "$(dirname "$0")"
docker compose up -d --wait
echo "Cerbos (Postgres store) sẵn sàng: http://localhost:4592   Postgres: localhost:54341"
