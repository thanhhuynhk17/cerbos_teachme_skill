// Shared client for the workspace answer API (served by ../serve.py).
// Load BEFORE predict.js / quiz.js. Exposes window.LessonAnswers:
//   lesson            – current lesson name, e.g. "0001-first-policy-quickstart"
//   load()            – Promise<{id: entry}> of answers already submitted
//   submit(entry)     – Promise<{ok, submitted_at}>; entry = {id, kind, question, answer, correct?}
// When the page is opened as file:// (no server) both reject, and the
// components show a hint to open the lesson through `uv run serve.py`.
(function () {
  const lesson = location.pathname.split("/").pop().replace(/\.html$/, "");
  const api = "/api/answers";
  const offline = location.protocol === "file:";
  const fail = () => Promise.reject(new Error("offline"));
  let cache = null;
  window.LessonAnswers = {
    lesson,
    offline,
    load() {
      if (offline) return fail();
      cache = cache || fetch(`${api}?lesson=${encodeURIComponent(lesson)}`)
        .then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.status))));
      return cache;
    },
    submit(entry) {
      if (offline) return fail();
      return fetch(api, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lesson, ...entry }),
      }).then((r) => r.json().then((j) => (r.ok ? j : Promise.reject(new Error(j.error || r.status)))));
    },
  };
})();
