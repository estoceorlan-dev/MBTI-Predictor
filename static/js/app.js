const questionCards = Array.from(document.querySelectorAll("[data-question-card]"));
const progressCount = document.getElementById("progressCount");
const progressFill = document.getElementById("progressFill");
const submitHint = document.getElementById("submitHint");
const quizForm = document.getElementById("quizForm");

function updateQuestionCard(card) {
  const questionName = card.dataset.questionName;
  const checked = document.querySelector(`input[name="${questionName}"]:checked`);
  const status = card.querySelector("[data-status-text]");

  card.classList.remove("pending", "complete", "needs-attention");

  if (checked) {
    card.classList.add("complete");
    status.textContent = `Answered: ${checked.value}/5`;
  } else {
    card.classList.add("pending");
    status.textContent = "Waiting";
  }
}

function refreshProgress() {
  let answered = 0;

  questionCards.forEach((card) => {
    updateQuestionCard(card);
    const questionName = card.dataset.questionName;
    if (document.querySelector(`input[name="${questionName}"]:checked`)) {
      answered += 1;
    }
  });

  const total = questionCards.length;
  const percent = total ? Math.round((answered / total) * 100) : 0;

  if (progressCount) {
    progressCount.textContent = answered;
  }

  if (progressFill) {
    progressFill.style.width = `${percent}%`;
  }

  if (submitHint) {
    if (answered === total) {
      submitHint.textContent = "Everything is complete. You can reveal the prediction now.";
    } else {
      submitHint.textContent = `${total - answered} question${total - answered === 1 ? "" : "s"} left before the result can be validated.`;
    }
  }
}

if (quizForm && questionCards.length) {
  questionCards.forEach((card) => {
    const questionName = card.dataset.questionName;
    document.querySelectorAll(`input[name="${questionName}"]`).forEach((input) => {
      input.addEventListener("change", refreshProgress);
    });
  });

  quizForm.addEventListener("submit", (event) => {
    const firstIncomplete = questionCards.find((card) => {
      const questionName = card.dataset.questionName;
      return !document.querySelector(`input[name="${questionName}"]:checked`);
    });

    questionCards.forEach((card) => {
      const questionName = card.dataset.questionName;
      const hasAnswer = document.querySelector(`input[name="${questionName}"]:checked`);
      card.classList.toggle("needs-attention", !hasAnswer);
    });

    if (firstIncomplete) {
      event.preventDefault();
      firstIncomplete.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });

  refreshProgress();
}
