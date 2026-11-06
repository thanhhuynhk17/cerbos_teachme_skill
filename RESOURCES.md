# Cerbos Resources

## Knowledge

- [Docs: Cerbos Quickstart](https://docs.cerbos.dev/cerbos/latest/quickstart.html)
  Nguồn chính của bài 0001: chạy PDP bằng Docker, derived role `owner`, policy `album:object`. Dùng khi: bắt đầu, hoặc cần lại request mẫu.
- [Docs: What is Cerbos](https://docs.cerbos.dev/cerbos/latest/what-is-cerbos)
  Mô hình PDP / PEP, vì sao tách phân quyền khỏi code. Dùng khi: giải thích kiến trúc cho team.
- [Docs: Resource policies](https://docs.cerbos.dev/cerbos/latest/policies/resource_policies)
  Spec đầy đủ của rules, actions, roles, wildcard. Dùng khi: viết hoặc debug resource policy.
- [Docs: How Cerbos evaluates requests](https://docs.cerbos.dev/cerbos/latest/policies/evaluation.html)
  Thứ tự đánh giá, rule khớp khi nào, deny thắng allow trong cùng role, mặc định deny. Dùng khi: cần dự đoán/giải thích vì sao ra ALLOW hay DENY.
- [Docs: Derived roles](https://docs.cerbos.dev/cerbos/latest/policies/derived_roles)
  Role động theo ngữ cảnh (owner, member...). Dùng khi: ánh xạ luật "chủ sở hữu / thành viên" từ engine cũ.
- [Docs: Conditions (CEL)](https://docs.cerbos.dev/cerbos/latest/policies/conditions)
  Biểu thức, biến `request.*` / `R` / `P`, `all`/`any`/`none`. Dùng khi: viết điều kiện ABAC.
- [Docs: Best practices](https://docs.cerbos.dev/cerbos/latest/policies/best_practices.html)
  Cách tổ chức policy. Dùng khi: thiết kế cấu trúc policy cho turynix.
- [Docs: Tutorial (Cerbforce)](https://docs.cerbos.dev/cerbos/latest/tutorial/00_intro)
  Tutorial nhiều bước, chính thức, đi sau quickstart. Dùng khi: cần luyện thêm sau các bài cơ bản.
- [Docs: API](https://docs.cerbos.dev/cerbos/latest/api/index.html)
  CheckResources, PlanResources, các endpoint. Dùng khi: tích hợp, query plan.
- [Docs: Query plan adapter cho SQLAlchemy](https://docs.cerbos.dev/cerbos/latest/recipes/query-plan-adapters/sqlalchemy.html)
  Biến query plan thành filter SQLAlchemy. Dùng khi: lọc danh sách theo quyền.
- [Docs: Storage drivers](https://docs.cerbos.dev/cerbos/latest/configuration/storage.html)
  Disk/Git/Blob/Postgres/MySQL/SQLite/Hub/Overlay; script schema Postgres; cache giữa nhiều replica. Dùng khi: chọn nơi lưu policy, cấu hình Postgres.
- [Docs: Admin API](https://docs.cerbos.dev/cerbos/latest/api/admin_api.html)
  Thêm/sửa/disable/xoá policy lúc chạy, store reload, audit log. Dùng khi: viết backend cho dashboard.
- [Docs: cerbosctl](https://docs.cerbos.dev/cerbos/latest/cli/cerbosctl.html)
  CLI cho Admin API (put/get/disable/delete/store reload). Dùng khi: thao tác tay, viết script.
- [Docs: Cerbos Hub](https://docs.cerbos.dev/cerbos-hub/), [Policy stores](https://docs.cerbos.dev/cerbos-hub/policy-stores), [Deployments](https://docs.cerbos.dev/cerbos-hub/deployments)
  Control plane trả phí: policy store API, build/test/push bundle xuống PDP, audit log tập trung. Dùng khi: đánh giá Hub so với tự làm.
- [Cerbos pricing](https://www.cerbos.dev/pricing)
  Các gói Hub và cách tính theo MAP. Dùng khi: ước lượng chi phí. Giá thay đổi được, nên kiểm tra lại trước khi quyết định.
- Repo của người học: `~/git_repos/cerbos_payloadcms_ui` (CONTEXT.md, docs/adr/, src/publishing/compile.ts, src/cerbos/admin.ts)
  Dashboard ma trận quyền: Payload → compile → Admin API → Postgres store. Dùng khi: lấy ví dụ thật cho các bài.
- [Research nội bộ: research/0001-postgres-store-admin-api-and-hub.md](research/0001-postgres-store-admin-api-and-hub.md)
  Tổng hợp có trích dẫn + kết quả kiểm chứng trong lab + lỗ hổng tìm thấy ở repo.
- [GitHub: cerbos/cerbos-sdk-python](https://github.com/cerbos/cerbos-sdk-python)
  Mã nguồn + README của SDK Python (đang dùng bản 0.16.1). Dùng khi: tra API client.
- [GitHub: cerbos/query-plan-adapters](https://github.com/cerbos/query-plan-adapters)
  Adapter query plan chính thức (SQLAlchemy, Prisma...). Dùng khi: đến phần query plan / Next.js + Prisma.
- [Playground: play.cerbos.dev](https://play.cerbos.dev)
  Thử policy trên trình duyệt, không cần cài. Dùng khi: thử nghiệm nhanh.

## Wisdom (Communities)

- [Cerbos Community Slack](http://go.cerbos.io/slack)
  Link chính thức từ quickstart; có đội ngũ Cerbos trả lời. Dùng khi: hỏi về thiết kế policy, cách migrate từ engine tự viết.

## Gaps
- Chưa đo độ trễ push của Cerbos Hub; chưa có nguồn về no-code editor cho operator trên Hub (có vẻ là không có).
- Chưa có nguồn chính về migrate từ engine phân quyền tự viết sang Cerbos (cần tìm case study / bài blog chính thức).
- Chưa xác minh tài liệu `@cerbos/grpc` / `@cerbos/http` cho Next.js.
