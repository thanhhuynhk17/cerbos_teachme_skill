# Research: Policy từ YAML sang Postgres, dashboard phân quyền realtime, và Cerbos Hub

Ngày 2026-11-04. Phiên bản: Cerbos PDP 0.57.0 (lab), 0.56.0 (repo `cerbos_payloadcms_ui`).
Ký hiệu: **[docs]** là đã đọc tài liệu chính thức; **[lab]** là đã tự chạy và kiểm chứng trong `lab/pgstore`; **[repo]** là đọc từ mã nguồn `~/git_repos/cerbos_payloadcms_ui`.

## 1. Policy có thể nằm ở đâu (storage driver)

Nguồn: [Storage block](https://docs.cerbos.dev/cerbos/latest/configuration/storage.html) [docs]

| Driver | Cách cập nhật policy | Ghi đè qua Admin API? |
|---|---|---|
| `disk` | sửa file; `watchForChanges: true` để tự nạp lại | Không |
| `git` | commit; PDP poll theo `updatePollInterval` | Không |
| `blob` (S3/GCS/Minio) | upload; poll theo `updatePollInterval` | Không |
| `postgres`, `mysql`, `sqlite3` | **Admin API** (`/admin/policy`) hoặc `cerbosctl put` | **Có** ("dynamic stores") |
| `hub` | Cerbos Hub build bundle rồi push xuống PDP | Không (quản lý trên Hub) |
| `overlay` | base + fallback (vd postgres + disk), có circuit breaker | Theo base driver |

Muốn có dashboard sửa quyền lúc đang chạy mà tự host, phải dùng một **mutable store** (Postgres/MySQL/SQLite) và **bật Admin API**.

## 2. Postgres driver

- Cerbos **không tự tạo bảng** trong Postgres (để giảm quyền DB của Cerbos). Phải chạy script SQL chính thức trước. Script tạo các bảng `policy`, `policy_dependency`, `policy_ancestor`, `policy_revision` (do trigger ghi lại mọi INSERT/UPDATE/DELETE), `attr_schema_defs`, và user `cerbos_user` với quyền tối thiểu. [docs]
- Cấu hình: `storage.driver: postgres`, `storage.postgres.url` (dùng `search_path=cerbos`). Ngoài ra có `connPool`, `connRetry`, `skipSchemaCheck`. URL dùng được biến môi trường `${PG_USER}`. [docs]
- Repo `cerbos_payloadcms_ui` dùng đúng script chính thức. Em đã so sánh, chỉ khác mật khẩu và tên database. [repo]
- Cột `definition` là `BYTEA`, nên không sửa policy trực tiếp bằng SQL; chỉ ghi qua Admin API. [lab]

## 3. Admin API

Nguồn: [Admin API](https://docs.cerbos.dev/cerbos/latest/api/admin_api.html), [cerbosctl](https://docs.cerbos.dev/cerbos/latest/cli/cerbosctl.html) [docs]

- Bật bằng `server.adminAPI.enabled: true`. Xác thực **bắt buộc**, chỉ có basic auth với **một** admin user. Không cấu hình thì mặc định là `cerbos` / `cerbosAdmin`. Docs khuyên luôn đổi mật khẩu và bật TLS. Docs ghi Admin API "still under development and might include breaking changes".
- Các endpoint chính:

| Việc | Endpoint |
|---|---|
| Thêm/cập nhật (1–100 policy mỗi lần) | `POST` hoặc `PUT /admin/policy` body `{"policies": [...]}` |
| Liệt kê | `GET /admin/policies` (`includeDisabled=true`, lọc `nameRegexp`/`scopeRegexp`/`versionRegexp`) |
| Lấy định nghĩa | `GET /admin/policy?id=...` |
| Inspect (actions, biến...) | `GET /admin/policies/inspect` |
| Disable / enable | `POST /admin/policy/disable?id=` và `/enable?id=` |
| Xoá hẳn | `POST /admin/policy/delete?id=` |
| ~~Xoá~~ (cũ) | `DELETE /admin/policy?id=` là **[DEPRECATED]** và thực chất là *disable* |
| Nạp lại store | `GET /admin/store/reload` (`?wait=true`) |
| Dọn lịch sử | `DELETE /admin/store/revisions` |
| Audit log | `GET /admin/auditlog/list/{KIND_ACCESS\|KIND_DECISION}` (khi bật audit) |

- CLI tương đương: `cerbosctl put policy`, `get rp`, `disable|enable|delete policy`, `store reload`, `store export`.
- Policy ID có dạng `resource.<kind, ":" đổi thành "_">.v<version>` và `derived_roles.<name>`, ví dụ `resource.album_object.vdefault`. [lab]

### Hành vi đã kiểm chứng trong lab [lab]

1. `POST /admin/policy` có hiệu lực **ngay**, không cần chờ như khi `disk` watch (khoảng 3 giây).
2. Disable resource policy thì mọi action của kind đó trở về DENY (mặc định từ chối). Enable lại thì quyền có lại ngay.
3. Xoá một derived roles đang được resource policy import sẽ bị từ chối với `HTTP 400 requiredByOtherPolicies`, nên không tạo ra được trạng thái hỏng.
4. Mỗi thao tác đều thêm một dòng vào `policy_revision`. Đây là audit trail miễn phí ở tầng DB.
5. **Nhiều PDP dùng chung một DB: PDP không nhận request ghi sẽ dùng policy cũ trong cache.** Em đã tái hiện: cập nhật qua PDP#1, `verify` trên PDP#2 vẫn ra kết quả cũ; gọi `/admin/store/reload` trên PDP#2 thì đúng lại.

## 4. "Realtime" khi có nhiều replica

Docs (mục Postgres driver) [docs]: cache của các policy đã compile chỉ được cập nhật trên **instance nhận request Admin API**. Các instance khác dùng chung DB sẽ không biết có thay đổi. Hai cách xử lý chính thức:

- Đặt `compile.cacheDuration` để cache tự hết hạn. Các instance sẽ *dần dần* nhất quán trong khoảng thời gian đó.
- Gọi `/admin/store/reload` trên **mọi** instance sau mỗi lần publish.

Đây đúng là câu hỏi ADR-0003 của repo để ngỏ ("How multiple replicas pick up new policies is unverified"). Giờ đã có câu trả lời và đã tái hiện được (mục 3.5).

## 5. Repo `cerbos_payloadcms_ui`: kiến trúc và lỗ hổng tìm thấy [repo]

Kiến trúc (CONTEXT.md, ADR-0001..0003):

```
Platform operator ──UI /matrix──► Payload (Postgres "payload") = NGUỒN SỰ THẬT
                                     │  takeSnapshot() → compile() (Policy Compiler)
                                     ▼
                         POST /admin/policy (basic auth, chỉ ở backend)
                                     ▼
                     Cerbos PDP ◄──► Postgres "cerbos" (mutable store)
Host app ──CheckResources──► Cerbos PDP
```

- Mô hình giống Permit.io: một Permission matrix dùng chung; tenant chỉ giới hạn việc gán role. Compiler luôn chèn điều kiện `tenantId` (ADR-0001). Đây là ABAC do compiler sinh ra; operator không xoá được.
- Publish là một Publication đánh số, không sửa được (rollback bằng cách publish lại bản cũ). Cerbos chỉ chứa artifact được sinh ra (ADR-0002).
- Cell mới có hai trạng thái Allow / Not granted. "Conditional" (ABAC do operator tự khai báo) mới ở mức kế hoạch.

Lỗ hổng/rủi ro, đối chiếu với docs và lab:

1. **Policy mồ côi khi xoá resource khỏi catalog.** `compile()` chỉ sinh policy cho các resource *đang có*, và `applyPolicies()` chỉ POST. Policy của resource đã xoá vẫn nằm trong store và vẫn ALLOW theo bản publish cuối. Rollback cũng gặp vấn đề tương tự. Cách sửa: khi publish, so danh sách `GET /admin/policies` với danh sách vừa compile, rồi disable hoặc delete phần thừa. (Suy ra từ mã nguồn, chưa chạy thử trên repo.)
2. **Replica**: mục 4. Khi chạy nhiều hơn một PDP, publish phải fan-out `/admin/store/reload`, hoặc đặt `compile.cacheDuration`.
3. **Test harness dùng `DELETE /admin/policy`** (`test/harness/cerbos.ts:34`), đã deprecated và chỉ *disable*. Vì vậy trong store dev có policy `invoice`/`plan`/`report` ở trạng thái disabled (em quan sát bằng `GET /admin/policies?includeDisabled=true`, chỉ đọc). Nên đổi sang `/admin/policy/delete`. Thêm nữa, dev và test đang dùng chung một PDP.
4. Admin API đang chạy qua HTTP thường với basic auth. Ổn cho dev; môi trường thật cần TLS, mật khẩu đủ mạnh, và chặn `/admin/*` ở tầng mạng.
5. Publish và lưu vào Payload không cùng một transaction. ADR-0002 đã biết điều này: Publication có `status: pending` → `applied`, cần cơ chế retry idempotent.

## 6. Cerbos Hub (trả phí)

Nguồn: [Hub docs](https://docs.cerbos.dev/cerbos-hub/), [Policy stores](https://docs.cerbos.dev/cerbos-hub/policy-stores), [Deployments](https://docs.cerbos.dev/cerbos-hub/deployments), [Audit log collection](https://docs.cerbos.dev/cerbos-hub/audit-log-collection), [Pricing](https://www.cerbos.dev/pricing), [cerbosctl hub store](https://docs.cerbos.dev/cerbos-hub/policy-stores-cli-binary.html) [docs]

- Hub là một **control plane tuỳ chọn** đặt trên PDP mã nguồn mở, cùng một binary PDP; chuyển sang Hub chỉ cần đổi cấu hình. PDP vẫn chạy trong hạ tầng của mình.
- **Policy stores**: nơi chứa file policy, nhận dữ liệu từ Git, CI, **Hub SDK/API** (docs gợi ý cho "per-tenant roles"), `cerbosctl hub store add-files/replace-files/...`, hoặc upload trên trình duyệt.
- **Deployments**: khi store thay đổi, Hub build (compile + chạy test policy) ra bundle, rồi **push** xuống mọi PDP gắn với deployment ("immediately"; docs không có số liệu độ trễ). Việc này giải quyết luôn vấn đề cache giữa các replica ở mục 4.
- **UI**: có Playground (trình soạn thảo kiểu IDE, cộng tác, có execution trace), cùng màn hình deployment với tab **Effect matrix** (Allow/Deny/Conditional theo role × action, ở chế độ *xem*), version history, rollback, freeze.
- **Không thấy** trên các trang đã đọc: trình chỉnh quyền kiểu no-code / form / ma trận *sửa được* cho operator (kiểu Permit.io). Hub là công cụ cho **developer viết policy**, không phải bảng điều khiển cho người vận hành sản phẩm.
- **Audit/decision logs** tập trung: lọc theo principal, resource, action, decision; export; masking dữ liệu nhạy cảm ngay tại PDP; lưu ở GCP europe-west6.
- **Giá** (trang pricing, 2026-11-04): Open source miễn phí. Hub có các gói: Proof of Concept $0 (100 MAP, 2 PDP, audit log 1 tuần), Development từ $25/tháng, Production từ $933/tháng (5.000 MAP), Enterprise theo thoả thuận (SSO, Hub tự host). Tính theo số *monthly active principals*.

### So sánh nhanh với hướng của repo

| Nhu cầu | Tự làm (Payload + Postgres + Admin API) | Cerbos Hub |
|---|---|---|
| Operator sửa ma trận quyền bằng UI | Có (đó là sản phẩm của repo) | Không có sẵn; Effect matrix chỉ để xem |
| Đưa thay đổi tới mọi PDP | Phải tự fan-out reload / cacheDuration | Push có sẵn |
| Test policy trước khi áp dụng | Phải tự làm (compile + test trong CI) | Build có chạy test |
| Audit quyết định | Tự bật audit, tự lưu | Có sẵn, có UI |
| Chi phí / phụ thuộc | Hạ tầng của mình | Theo MAP; phụ thuộc SaaS |

Hướng kết hợp đáng cân nhắc (**chưa thử**): giữ UI ma trận của repo, nhưng thay Postgres + Admin API bằng **Hub policy store API** làm đích publish. Khi đó Hub lo phần build/test/push và audit.

## Gaps

- Chưa đo độ trễ push của Hub; chưa đọc trang reliability/user-management của Hub.
- Chưa kiểm chứng trên repo thật lỗ hổng "policy mồ côi" (chỉ suy ra từ mã nguồn).
- Chưa thử `compile.cacheDuration` trong lab (mới thử cách reload).
