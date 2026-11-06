"""Gửi request của quickstart (dữ liệu ở fixtures.py) và in kết quả thành bảng.

Chạy:  uv run check.py
"""
from fixtures import connect, ACTIONS, BUGS, QUICKSTART_ALBUMS, quickstart_resource_list

with connect() as c:
    resp = c.check_resources(principal=BUGS, resources=quickstart_resource_list())
    resp.raise_if_failed()  # chỉ lỗi khi lời gọi hỏng, không phải khi bị DENY

print(f"principal: {BUGS.id} roles={BUGS.roles}\n")
print(f"{'album':<10} " + " ".join(f"{a:<13}" for a in ACTIONS))
for r in QUICKSTART_ALBUMS:
    result = resp.get_resource(r.id)
    cells = ["ALLOW" if result.is_allowed(a) else "deny" for a in ACTIONS]
    print(f"{r.id:<10} " + " ".join(f"{x:<13}" for x in cells))
