"""Web server cho workspace học: phục vụ lessons/reference/assets và nhận bài nộp.

Chạy (từ gốc workspace):   uv run serve.py            # cổng 8901
                          uv run serve.py 8902       # cổng khác

API:
  GET  /api/answers?lesson=<tên-bài>   → các câu trả lời đã nộp (JSON)
  POST /api/answers                    → nộp 1 câu trả lời
       body: {"lesson": "...", "id": "...", "kind": "predict|quiz",
              "question": "...", "answer": "...", "correct": true|false|null}

Bài nộp được ghi vào answers/<tên-bài>.json, mỗi câu hỏi một khoá `id`.
Nộp lại thì ghi đè bản mới nhất, các lần nộp cũ giữ trong "history".
"""
import json
import re
import sys
from datetime import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
ANSWERS = ROOT / "answers"
LESSON_RE = re.compile(r"^[0-9]{4}-[a-z0-9-]+$")  # vd 0001-first-policy-quickstart
MAX_BODY = 64 * 1024


def answers_file(lesson: str) -> Path | None:
    return ANSWERS / f"{lesson}.json" if LESSON_RE.match(lesson) else None


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


class Handler(SimpleHTTPRequestHandler):
    def _json(self, code: int, payload) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path != "/api/answers":
            return super().do_GET()
        path = answers_file(parse_qs(url.query).get("lesson", [""])[0])
        if path is None:
            return self._json(400, {"error": "lesson không hợp lệ"})
        self._json(200, load(path).get("answers", {}))

    def do_POST(self):
        if urlparse(self.path).path != "/api/answers":
            return self._json(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length") or 0)
        if not 0 < length <= MAX_BODY:
            return self._json(413, {"error": "body rỗng hoặc quá lớn"})
        try:
            data = json.loads(self.rfile.read(length))
            lesson, qid = str(data["lesson"]), str(data["id"])
        except (ValueError, KeyError, TypeError):
            return self._json(400, {"error": "JSON không hợp lệ"})
        path = answers_file(lesson)
        if path is None or not re.match(r"^[a-z0-9-]{1,64}$", qid):
            return self._json(400, {"error": "lesson hoặc id không hợp lệ"})

        entry = {
            "kind": str(data.get("kind", "predict")),
            "question": str(data.get("question", ""))[:2000],
            "answer": str(data.get("answer", ""))[:20000],
            "correct": data.get("correct") if isinstance(data.get("correct"), bool) else None,
            "submitted_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        ANSWERS.mkdir(exist_ok=True)
        doc = load(path)
        doc.setdefault("lesson", lesson)
        answers = doc.setdefault("answers", {})
        if qid in answers:
            entry["history"] = answers[qid].pop("history", []) + [answers[qid]]
        answers[qid] = entry
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
        self._json(200, {"ok": True, "submitted_at": entry["submitted_at"]})

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")  # luôn thấy bản bài học mới nhất
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8901
    server = ThreadingHTTPServer(("0.0.0.0", port), partial(Handler, directory=str(ROOT)))
    print(f"Đang phục vụ {ROOT} tại http://0.0.0.0:{port}  (bài nộp → {ANSWERS}/)")
    server.serve_forever()
