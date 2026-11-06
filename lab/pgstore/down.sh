#!/usr/bin/env bash
# Tắt lab 0002. Thêm --reset để xoá luôn dữ liệu Postgres (policy trong DB mất hết).
cd "$(dirname "$0")"
if [ "$1" = "--reset" ]; then docker compose down -v; else docker compose down; fi
