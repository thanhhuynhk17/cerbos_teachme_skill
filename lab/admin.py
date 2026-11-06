"""CLI nhỏ gọi Cerbos Admin API qua HTTP (bài 0002). Dùng httpx, cùng cách repo
cerbos_payloadcms_ui gọi trong src/cerbos/admin.ts.

  uv run admin.py put <file|thư-mục> ...   POST /admin/policy        (thêm/cập nhật)
  uv run admin.py list [--all]             GET  /admin/policies      (--all: gồm cả policy bị disable)
  uv run admin.py get <id> ...             GET  /admin/policy?id=
  uv run admin.py disable <id> ...         POST /admin/policy/disable?id=
  uv run admin.py enable <id> ...          POST /admin/policy/enable?id=
  uv run admin.py delete <id> ...          POST /admin/policy/delete?id=
  uv run admin.py reload                   GET  /admin/store/reload?wait=true

Docs: https://docs.cerbos.dev/cerbos/latest/api/admin_api.html
Địa chỉ + tài khoản lấy từ fixtures.py (ADMIN_HOST, ADMIN_USER, ADMIN_PASSWORD).
"""
import json
import sys
from pathlib import Path

import httpx
import yaml

from fixtures import ADMIN_HOST, ADMIN_PASSWORD, ADMIN_USER


def client() -> httpx.Client:
    return httpx.Client(base_url=ADMIN_HOST, auth=(ADMIN_USER, ADMIN_PASSWORD), timeout=10)


def load_policies(paths: list[str]) -> list[dict]:
    """Đọc file YAML policy (1 policy / file) thành dict để gửi dạng JSON."""
    files: list[Path] = []
    for p in map(Path, paths):
        files += sorted(p.glob("*.y*ml")) if p.is_dir() else [p]
    return [yaml.safe_load(f.read_text()) for f in files]


def show(resp: httpx.Response) -> None:
    try:
        body = json.dumps(resp.json(), indent=2, ensure_ascii=False)
    except ValueError:
        body = resp.text
    print(f"HTTP {resp.status_code}\n{body}")
    if resp.is_error:
        sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    ids = [("id", i) for i in args]
    try:
        with client() as c:
            if cmd == "put":
                show(c.post("/admin/policy", json={"policies": load_policies(args)}))
            elif cmd == "list":
                show(c.get("/admin/policies", params={"includeDisabled": "true"} if "--all" in args else None))
            elif cmd == "get":
                show(c.get("/admin/policy", params=ids))
            elif cmd in ("disable", "enable", "delete"):
                show(c.post(f"/admin/policy/{cmd}", params=ids))
            elif cmd == "reload":
                show(c.get("/admin/store/reload", params={"wait": "true"}))
            else:
                sys.exit(__doc__)
    except httpx.ConnectError:
        sys.exit(f"✗ Không kết nối được Admin API ở {ADMIN_HOST}. Đã chạy ./pgstore/up.sh chưa?")


if __name__ == "__main__":
    main()
