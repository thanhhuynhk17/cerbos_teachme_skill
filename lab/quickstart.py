# Code Python của quickstart, logic giữ nguyên:
#   https://docs.cerbos.dev/cerbos/latest/quickstart.html  (tab "Python")
# Bản gốc không có comment. Các comment tiếng Việt do Claude thêm vào.
# File này CỐ Ý để độc lập (không import fixtures.py) để đối chiếu 1-1 với tài liệu.
# Dữ liệu dùng chung của lab nằm ở fixtures.py.
#
# Chạy (từ thư mục lab/, PDP phải đang chạy bằng ./up.sh):
#   uv run quickstart.py
#
# Việc của file: hỏi Cerbos "bugs_bunny có được view:public / comment
# trên 2 album này không?" rồi in nguyên câu trả lời dạng JSON.

import json

# CerbosClient: client HTTP gọi tới PDP.
# Principal, Resource, ResourceAction, ResourceList: các dataclass mô tả request.
from cerbos.sdk.client import CerbosClient
from cerbos.sdk.model import Principal, Resource, ResourceAction, ResourceList

# Chỉ dùng để giả lập cách một app FastAPI trả về 403 (xem khối try/except bên dưới).
from fastapi import HTTPException, status

# ── 1. PRINCIPAL: ai đang gọi ───────────────────────────────────────────
# Principal(id, roles, attr)
#   id    = "bugs_bunny" → trong CEL là request.principal.id
#   roles = ["user"]     → role tĩnh (RBAC), so với `roles:` trong rule
#   attr  = thuộc tính tuỳ ý (ABAC), trong CEL là request.principal.attr.*
#           (beta_tester chưa được policy nào dùng tới trong quickstart)
principal = Principal(
    "bugs_bunny",
    roles=["user"],
    attr={
        "beta_tester": True,
    },
)

# ── 2. ACTIONS: muốn làm gì ─────────────────────────────────────────────
# Action là chuỗi tuỳ anh đặt. Cerbos không định nghĩa sẵn "view" hay "comment".
# Chuỗi này chỉ cần khớp với `actions:` trong rule của policy.
actions = ["view:public", "comment"]

# ── 3. RESOURCES: tác động lên cái gì ───────────────────────────────────
# Resource(id, kind, attr)
#   kind = "album:object" → Cerbos tìm resource policy có `resource: "album:object"`
#   attr = dữ liệu do APP tự lấy từ DB rồi gửi kèm (Cerbos không đọc DB của anh)
#          → trong CEL là request.resource.attr.owner, .public, ...
# ResourceAction ghép 1 resource với danh sách action cần kiểm tra.
# ResourceList gom nhiều resource lại, để hỏi tất cả trong MỘT lần gọi.
resource_list = ResourceList(
    resources=[
        ResourceAction(
            Resource(
                "BUGS001",            # album của chính bugs_bunny, private
                "album:object",
                attr={
                    "owner": "bugs_bunny",
                    "public": False,
                    "flagged": False,
                },
            ),
            actions=actions,
        ),
        ResourceAction(
            Resource(
                "DAFFY002",           # album của daffy_duck, public
                "album:object",
                attr={
                    "owner": "daffy_duck",
                    "public": True,
                    "flagged": False,
                },
            ),
            actions=actions,
        ),
    ],
)

# ── 4. GỌI PDP ──────────────────────────────────────────────────────────
# Cổng 3592 là cổng HTTP. check_resources() POST tới /api/check/resources,
# tức cùng endpoint với lệnh curl trong bài học.
with CerbosClient(host="http://localhost:3592") as c:
    try:
        resp = c.check_resources(principal=principal, resources=resource_list)
        # LƯU Ý: raise_if_failed() chỉ ném lỗi khi BẢN THÂN LỜI GỌI thất bại
        # (HTTP status khác 200, ví dụ request sai định dạng).
        # Nó KHÔNG ném lỗi khi kết quả là EFFECT_DENY. Bị deny vẫn là một
        # câu trả lời hợp lệ, nằm trong resp.
        resp.raise_if_failed()
    except Exception:
        # Quickstart biến mọi lỗi gọi Cerbos thành 403 kiểu FastAPI.
        # Trong app thật, anh còn phải tự kiểm tra effect (DENY → 403).
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized"
        )

# ── 5. KẾT QUẢ ──────────────────────────────────────────────────────────
# resp.results: mỗi phần tử ứng với 1 resource, trong đó
#   "actions": {"view:public": "EFFECT_ALLOW" | "EFFECT_DENY", "comment": ...}
# Muốn đọc gọn hơn: resp.get_resource("BUGS001").is_allowed("comment") → bool
# (check.py dùng đúng cách này để in bảng).
print(json.dumps(resp.to_dict(), sort_keys=False, indent=4))
