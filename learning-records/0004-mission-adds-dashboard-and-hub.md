# Mission mở rộng: dashboard sửa quyền realtime trên Postgres, đánh giá Cerbos Hub

Sau bài 0001, người học muốn bài tiếp theo đi vào chuỗi "policy YAML → Postgres (Admin API)", dựa trên repo của họ `~/git_repos/cerbos_payloadcms_ui` (UI ma trận kiểu Permit.io, Payload là nguồn sự thật, compile ra Cerbos), để có một admin dashboard sửa RBAC/ABAC gần realtime. Họ cũng muốn đánh giá Cerbos Hub trả phí. Query plan để sau. MISSION.md đã cập nhật theo yêu cầu trực tiếp của người học.

**Implications**: Bài 0002 dạy Postgres store + Admin API + cache giữa nhiều replica, có liên hệ với repo, và có một phần ngắn về Hub. Chi tiết nằm trong research/0001-postgres-store-admin-api-and-hub.md.
