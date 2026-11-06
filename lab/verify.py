"""Tự chấm bài: so kết quả thật từ Cerbos với kết quả mong đợi của từng bước.

Dùng:  uv run verify.py <bước>
Các bước: deny-all | owner | public | challenge | flagged
Dữ liệu (principal, album) lấy từ fixtures.py. File này chỉ chứa kết quả mong đợi.
"""
import sys

from fixtures import CERBOS_HOST, connect, BUGS, BUGS001, DAFFY002, DAFFY_FLAGGED, DAFFY_SECRET

D, A = False, True
# Mỗi bước: danh sách (resource, {action: mong đợi})
STAGES = {
    "deny-all":  [(BUGS001,  {"view:public": D, "comment": D}),
                  (DAFFY002, {"view:public": D, "comment": D})],
    "owner":     [(BUGS001,  {"view:public": A, "comment": A}),
                  (DAFFY002, {"view:public": D, "comment": D})],
    "public":    [(BUGS001,  {"view:public": A, "comment": A}),
                  (DAFFY002, {"view:public": A, "comment": D})],
    "challenge": [(BUGS001,  {"view:public": A, "comment": A}),
                  (DAFFY002, {"view:public": A, "comment": A}),
                  (DAFFY_SECRET, {"view:public": D, "comment": D})],
    # Bài 0002: album bị flagged vẫn xem được (public) nhưng KHÔNG ai ngoài chủ được comment.
    "flagged":   [(BUGS001,  {"view:public": A, "comment": A}),
                  (DAFFY002, {"view:public": A, "comment": A}),
                  (DAFFY_SECRET, {"view:public": D, "comment": D}),
                  (DAFFY_FLAGGED, {"view:public": A, "comment": D})],
}


def fmt(b: bool) -> str:
    return "ALLOW" if b else "deny"


def main() -> None:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in STAGES:
        sys.exit(f"Chọn một bước: {' | '.join(STAGES)}")
    ok = True
    with connect() as c:
        for res, expected in STAGES[stage]:
            for action, want in expected.items():
                got = c.is_allowed(action, BUGS, res)
                ok &= got == want
                mark = "✓" if got == want else "✗"
                print(f" {mark} {res.id:<13} {action:<12} mong đợi {fmt(want):<5}  thực tế {fmt(got)}")
    if CERBOS_HOST.endswith(":3592"):
        hint = "xem policy có lỗi không: ./logs.sh"
    else:  # PDP của lab pgstore (4592) hoặc replica (4594)
        hint = ("xem log: docker compose -f pgstore/docker-compose.yml logs; "
                "nếu là replica thì có thể đang dùng cache cũ: CERBOS_ADMIN_HOST=<host> uv run admin.py reload")
    print(f"\nĐẠT ✓  [{CERBOS_HOST}]" if ok else f"\nCHƯA ĐẠT ✗  [{CERBOS_HOST}]  (gợi ý: {hint})")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
