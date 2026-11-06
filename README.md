# cerbos_teachme_skill

Workspace tự học [Cerbos](https://www.cerbos.dev/) (authorization: RBAC, ABAC, policy) bằng Python.
Bài học là trang HTML mở trên trình duyệt. Lab chạy Cerbos PDP trong Docker, có script tự chấm từng bước.
Workspace được tạo và dẫn dắt bằng skill **teach** của [mattpocock/skills](https://github.com/mattpocock/skills) trong Claude Code.

## Trước khi học: gọi skill teach

Mở Claude Code ngay trong thư mục này, rồi **gọi skill teach trước khi làm bất cứ gì**:

```text
/mattpocock-skills:teach
```

Skill sẽ đọc `MISSION.md`, `NOTES.md` và `learning-records/` để biết anh đang học tới đâu, rồi tiếp tục từ đó:
giải thích chỗ chưa rõ, chấm câu trả lời trong `answers/`, soạn bài tiếp theo. Không gọi skill thì Claude chỉ thấy
một thư mục code, không biết đây là một khoá học có trạng thái.

Chưa có plugin thì cài trong Claude Code:

```text
/plugin marketplace add mattpocock/skills
/plugin install mattpocock-skills@mattpocock
```

## Cần cài

| Công cụ | Dùng để | Cài |
|---|---|---|
| Docker | Chạy Cerbos PDP (`ghcr.io/cerbos/cerbos:0.57.0`) và Postgres của bài 0002 | https://docs.docker.com/get-docker/ |
| uv | Quản lý Python và thư viện (`cerbos` SDK, `fastapi`, `pyyaml`). Không dùng `pip` hay `venv` tay | Chưa có uv thì xem [tài liệu cài đặt của Astral](https://docs.astral.sh/uv/getting-started/installation/) |
| Claude Code | Giáo viên: chạy skill teach | https://docs.claude.com/en/docs/claude-code |

## Bắt đầu

```bash
git clone https://github.com/thanhhuynhk17/cerbos_teachme_skill.git
cd cerbos_teachme_skill
uv sync                      # tạo .venv từ uv.lock
uv run serve.py              # phục vụ bài học tại http://localhost:8901
```

Mở http://localhost:8901/lessons/0001-first-policy-quickstart.html (máy khác trong mạng thì thay `localhost` bằng IP máy chạy).
Mỗi câu dự đoán có ô trả lời và nút **Nộp**. Bài nộp được ghi vào `answers/<bài>.json`, nên trình duyệt nào nộp cũng được,
và Claude đọc từ đó để chấm.

Lab của từng bài chạy trong `lab/`. Bài học hướng dẫn từng lệnh, ví dụ:

```bash
cd lab
./up.sh                      # bật PDP ở cổng 3592, đọc lab/policies/
uv run check.py              # in bảng ALLOW/deny
uv run verify.py owner       # tự chấm một bước
./down.sh
```

## Bài học

| Bài | Nội dung | Lab |
|---|---|---|
| [0001](lessons/0001-first-policy-quickstart.html) | Quickstart: request, deny mặc định, derived role, RBAC kèm điều kiện CEL | `lab/up.sh` (cổng 3592) |
| [0002](lessons/0002-postgres-store-admin-api.html) | Lưu policy trong Postgres, sửa qua Admin API, bẫy cache khi có nhiều PDP, Cerbos Hub | `lab/pgstore/up.sh` (cổng 4592, replica 4594, Postgres 54341) |

Tra nhanh: [cheat sheet](reference/cerbos-cheatsheet.html). Tài liệu đã đọc: [RESOURCES.md](RESOURCES.md).

## Cấu trúc

```text
MISSION.md          vì sao học, thế nào là xong
NOTES.md            sở thích của người học, quy ước cho Claude
RESOURCES.md        nguồn tài liệu đáng tin
learning-records/   đã học được gì, nhầm chỗ nào (Claude dùng để chọn bài tiếp theo)
lessons/            bài học HTML
reference/          cheat sheet
research/           ghi chép research có trích dẫn
assets/             CSS, quiz, ô dự đoán, gửi bài nộp (dùng chung cho mọi bài)
serve.py            web server: phục vụ bài học và nhận bài nộp
lab/
  fixtures.py       nơi DUY NHẤT khai báo dữ liệu request (principal, album, actions)
  check.py          in bảng kết quả
  verify.py         tự chấm theo từng bước
  admin.py          CLI gọi Admin API (bài 0002)
  quickstart.py     code Python của tài liệu quickstart, để đối chiếu
  policies/         nơi tự viết policy, bắt đầu RỖNG
  solutions/        lời giải tham khảo, chỉ mở sau khi tự làm xong
  pgstore/          Postgres + Cerbos có Admin API (bài 0002)
```

Git không theo dõi `answers/` (bài nộp) và file trong `lab/policies/` (policy đang làm), để người clone về
bắt đầu bài 0001 từ "chưa có policy nào". Bài sau cần policy của bài trước mà `policies/` còn rỗng thì:
`cp lab/solutions/0001/*.yaml lab/policies/`.

Mật khẩu trong `lab/pgstore/` (`cerbos_lab_pw`, `cerbosAdmin`) là giá trị mặc định cho lab chạy trên máy, không dùng cho môi trường thật.
