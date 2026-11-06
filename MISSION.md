# Mission: Cerbos

## Why
Đưa Cerbos vào dự án thật (backend Python + frontend Next.js) và cuối cùng thay thế policy engine tự viết trong repo `turynix`, nhánh `unitegroup`, bằng policy-as-code dễ kiểm thử, dễ audit.

## Success looks like
- Tự viết resource policy + derived roles kết hợp RBAC (role) và ABAC (điều kiện CEL trên thuộc tính) cho domain thật của turynix
- Gọi PDP từ FastAPI (`cerbos` Python SDK) và từ Next.js (`@cerbos/grpc` / `@cerbos/http`) để kiểm tra quyền
- Dùng query plan (`plan_resources`) để lọc danh sách ở tầng DB (vd adapter SQLAlchemy) thay vì check từng bản ghi
- Viết test policy (`cerbos compile` + test suite) và chạy trong CI
- Làm chủ đường đi "dashboard → Postgres store qua Admin API → PDP" để có một admin dashboard sửa quyền RBAC/ABAC gần realtime (repo `~/git_repos/cerbos_payloadcms_ui`), kể cả khi chạy nhiều replica
- Đánh giá được Cerbos Hub (bản trả phí) so với tự làm dashboard, và quyết định dùng hay không
- Lập được bản đồ: luật trong engine cũ → policy Cerbos tương ứng, và chuyển đổi dần không gây hồi quy

## Constraints
- Đã quen Docker, Python + FastAPI, RBAC/ABAC, Next.js: không dạy lại các nền tảng này
- Bắt đầu từ quickstart chính thức, dùng Python SDK
- Học qua nhiều buổi ngắn, có bài tập tự chấm

## Out of scope
- Dùng thật Cerbos Hub (mới chỉ đánh giá, chưa đăng ký)
- Query plan: để sau, khi phần dashboard đã vững
- Tự host production (HA, Kubernetes) cho tới khi policy đã vững
