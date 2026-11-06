// Reusable predict-then-reveal component with an answer box.
// Markup:  <details class="predict" data-id="a-deny-all"><summary>Câu hỏi</summary> …đáp án… </details>
// Every details.predict (except .hint) becomes: question, textarea,
// "Nộp câu trả lời" (sends it to answers/<lesson>.json via LessonAnswers),
// and "Xem đáp án", enabled only after the answer has been submitted, so the
// prediction is recorded before the learner sees the solution.
// Drafts are also kept in localStorage (per browser) when available.
// Requires assets/answers.js loaded first.
(function () {
  const A = window.LessonAnswers;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch {} },
  };
  const fmtTime = (iso) => new Date(iso).toLocaleString("vi-VN", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "2-digit" });

  document.querySelectorAll("details.predict:not(.hint)").forEach((d, i) => {
    const id = d.dataset.id || `predict-${i + 1}`;
    const key = `cerbos-predict:${A.lesson}:${id}`;
    const summary = d.querySelector("summary");

    const box = document.createElement("div");
    box.className = "predict-box";
    const q = document.createElement("div");
    q.className = "predict-q";
    q.innerHTML = summary.innerHTML;
    const ta = document.createElement("textarea");
    ta.rows = 4;
    ta.placeholder = "Câu trả lời của anh: dự đoán gì, và vì sao (theo bước nào)?";
    ta.value = store.get(key) || "";

    const actions = document.createElement("div");
    actions.className = "predict-actions";
    const submit = document.createElement("button");
    submit.type = "button";
    submit.textContent = "Nộp câu trả lời";
    const reveal = document.createElement("button");
    reveal.type = "button";
    reveal.textContent = "Xem đáp án";
    const status = document.createElement("span");
    status.className = "predict-status";
    actions.append(submit, reveal, status);

    const answer = document.createElement("div");
    answer.className = "predict-answer";
    answer.hidden = true;
    [...d.childNodes].forEach((n) => { if (n !== summary) answer.appendChild(n); });

    let submitted = null; // text last accepted by the server
    const sync = () => {
      const text = ta.value.trim();
      submit.disabled = text === "" || text === submitted;
      reveal.disabled = submitted === null && answer.hidden;
      if (submitted === null) status.textContent = A.offline ? "Mở bài qua server (uv run serve.py) để nộp" : "Chưa nộp";
      else if (text !== submitted) status.textContent = "Có chỉnh sửa chưa nộp";
    };

    ta.addEventListener("input", () => { store.set(key, ta.value); sync(); });
    submit.addEventListener("click", () => {
      const text = ta.value.trim();
      submit.disabled = true;
      status.textContent = "Đang nộp…";
      A.submit({ id, kind: "predict", question: q.textContent.trim(), answer: text })
        .then((r) => { submitted = text; status.textContent = `Đã nộp ✓ ${fmtTime(r.submitted_at)}`; sync(); })
        .catch((e) => { status.textContent = `Nộp lỗi: ${e.message}. Server có đang chạy không?`; sync(); });
    });
    reveal.addEventListener("click", () => {
      answer.hidden = !answer.hidden;
      reveal.textContent = answer.hidden ? "Xem đáp án" : "Ẩn đáp án";
      sync();
    });

    box.append(q, ta, actions, answer);
    d.replaceWith(box);
    sync();

    // Pull answers already submitted (from any browser) from the server.
    A.load().then((all) => {
      const saved = all[id];
      if (!saved) return;
      submitted = saved.answer;
      if (!ta.value.trim()) ta.value = saved.answer;
      status.textContent = `Đã nộp ✓ ${fmtTime(saved.submitted_at)}`;
      sync();
    }).catch(() => {});
  });
})();
