#!/usr/bin/env bash
# Khởi động Cerbos PDP (đúng lệnh trong quickstart, mount ./policies)
set -e
cd "$(dirname "$0")"
docker rm -f cerbos >/dev/null 2>&1 || true
docker run --rm --name cerbos -d \
  -v "$(pwd)/policies:/policies" \
  -p 3592:3592 -p 3593:3593 \
  ghcr.io/cerbos/cerbos:0.57.0
for i in $(seq 1 20); do
  curl -sf localhost:3592/_cerbos/health >/dev/null && { echo "Cerbos đã sẵn sàng: http://localhost:3592"; exit 0; }
  sleep 0.5
done
echo "Cerbos chưa lên, xem: docker logs cerbos"; exit 1
