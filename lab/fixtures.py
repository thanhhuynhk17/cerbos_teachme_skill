"""NGUỒN DỮ LIỆU DUY NHẤT của lab: địa chỉ PDP, principal, actions, resources.

Mọi script (check.py, verify.py, ...) đều import từ đây. Muốn đổi dữ liệu
thì chỉ sửa ở file này.

Chạy trực tiếp để in request JSON (cùng body với quickstart) cho curl:
    uv run fixtures.py | curl -s "localhost:3592/api/check/resources?pretty" -d @-
"""
import json
import os
import sys

import httpx
from cerbos.sdk.client import CerbosClient

from cerbos.sdk.model import Principal, Resource, ResourceAction, ResourceList

# ── Địa chỉ PDP (cổng HTTP). Đổi bằng biến môi trường CERBOS_HOST nếu cần ──
CERBOS_HOST = os.environ.get("CERBOS_HOST", "http://localhost:3592")

# ── Bài 0002: PDP đọc policy từ Postgres (lab/pgstore), có Admin API ──
# Chạy check.py / verify.py với PDP này:  CERBOS_HOST=http://localhost:4592 uv run verify.py ...
PGSTORE_HOST = "http://localhost:4592"
ADMIN_HOST = os.environ.get("CERBOS_ADMIN_HOST", PGSTORE_HOST)
# Thông tin đăng nhập mặc định của Admin API khi không cấu hình (docs Admin API). Chỉ dùng cho lab.
ADMIN_USER, ADMIN_PASSWORD = "cerbos", "cerbosAdmin"

# ── Actions cần kiểm tra ────────────────────────────────────────────────
ACTIONS = ["view:public", "comment"]

# ── Principal: ai đang gọi ──────────────────────────────────────────────
BUGS = Principal("bugs_bunny", roles=["user"], attr={"beta_tester": True})

# ── Resources: các album ────────────────────────────────────────────────
def album(album_id: str, owner: str, public: bool, flagged: bool = False) -> Resource:
    return Resource(album_id, "album:object",
                    attr={"owner": owner, "public": public, "flagged": flagged})

BUGS001 = album("BUGS001", "bugs_bunny", public=False)    # của bugs_bunny, private
DAFFY002 = album("DAFFY002", "daffy_duck", public=True)   # của daffy_duck, public

# 2 album của request trong quickstart
QUICKSTART_ALBUMS = [BUGS001, DAFFY002]

# Album thêm cho bộ chấm thử thách: không thuộc bugs_bunny, không public.
# Dùng để bắt lỗi "mở quyền quá tay" (vd cho mọi user comment mọi album).
DAFFY_SECRET = album("DAFFY_SECRET", "daffy_duck", public=False)

# Bài 0002: album public nhưng bị gắn cờ (flagged) vì nội dung bị báo cáo.
DAFFY_FLAGGED = album("DAFFY_FLAGGED", "daffy_duck", public=True, flagged=True)


def connect() -> CerbosClient:
    """Tạo CerbosClient sau khi kiểm tra PDP đang chạy.
    PDP chưa chạy thì in hướng dẫn ngắn thay vì traceback httpx dài."""
    try:
        httpx.get(f"{CERBOS_HOST}/_cerbos/health", timeout=2).raise_for_status()
    except httpx.HTTPError as e:
        sys.exit(f"✗ Không kết nối được Cerbos PDP ở {CERBOS_HOST} ({type(e).__name__}).\n"
                 f"  PDP chưa chạy? Bật lại bằng:  ./up.sh   (kiểm tra: docker ps --filter name=cerbos)")
    return CerbosClient(host=CERBOS_HOST)


def quickstart_resource_list() -> ResourceList:
    """ResourceList: mỗi album trong quickstart kèm đủ ACTIONS."""
    return ResourceList(resources=[ResourceAction(r, actions=ACTIONS) for r in QUICKSTART_ALBUMS])


def quickstart_request_json(request_id: str = "quickstart") -> dict:
    """Body JSON cho POST /api/check/resources (dạng như ví dụ curl của quickstart)."""
    return {
        "requestId": request_id,
        "principal": {"id": BUGS.id, "roles": list(BUGS.roles), "attr": BUGS.attr},
        "resources": [
            {"actions": ACTIONS,
             "resource": {"kind": r.kind, "id": r.id, "attr": r.attr}}
            for r in QUICKSTART_ALBUMS
        ],
    }


if __name__ == "__main__":
    print(json.dumps(quickstart_request_json(), indent=2))
