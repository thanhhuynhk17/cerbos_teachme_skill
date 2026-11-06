// Reusable quiz component.
// Markup: <div class="quiz" data-id="q1" data-answer="2"><div class="q">…</div>
//           <button>…</button>×N <div class="why">…</div></div>
// data-answer is the 1-based index of the correct button.
// Optional <p class="score" id="quiz-score"></p> shows the first-try score.
// The FIRST choice of each question is submitted via LessonAnswers (if
// assets/answers.js is loaded), so it lands in answers/<lesson>.json.
(function () {
  const A = window.LessonAnswers;
  const quizzes = document.querySelectorAll(".quiz");
  let firstTry = 0, answered = 0;
  const score = document.getElementById("quiz-score");
  const render = () => { if (score) score.textContent = `Đúng ngay lần đầu: ${firstTry}/${answered} (tổng ${quizzes.length} câu)`; };
  quizzes.forEach((quiz, qi) => {
    const answer = Number(quiz.dataset.answer);
    const id = quiz.dataset.id || `quiz-${qi + 1}`;
    let tried = false;
    quiz.querySelectorAll("button").forEach((btn, i) => {
      btn.type = "button";
      btn.addEventListener("click", () => {
        if (quiz.classList.contains("done")) return;
        const correct = i + 1 === answer;
        btn.classList.add(correct ? "right" : "wrong");
        if (!tried) {
          tried = true; answered++; if (correct) firstTry++; render();
          if (A) A.submit({ id, kind: "quiz", question: quiz.querySelector(".q").textContent.trim(),
                            answer: btn.textContent.trim(), correct }).catch(() => {});
        }
        if (correct) quiz.classList.add("done");
      });
    });
  });
  render();
})();
