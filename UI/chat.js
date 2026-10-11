// ============================================================
// NEXT-SKILL Scripted Q&A Chatbot with Pip
// ============================================================

// 1. Array of questions at the top of the file for easy editing
const questions = [
  {
    id: "study",
    prompt: "Okay, I'm Pip. I know nothing yet, so tell me about you. What are you studying right now?",
    summaryLabel: "Current studies",
    multiSelect: false,
    chips: ["BCA", "BSc IT / CS", "B.Tech"]
  },
  {
    id: "area",
    prompt: "Got it! Which area pulls you in most?",
    summaryLabel: "Area of interest",
    multiSelect: false,
    chips: ["Websites and apps", "Data and AI", "Databases and backend", "Design", "Security", "No idea yet"]
  },
  {
    id: "enjoyment",
    prompt: "Fair enough! What do you enjoy doing most?",
    summaryLabel: "Favorite activity",
    multiSelect: false,
    chips: ["Building things", "Digging into data", "Designing how it looks", "Explaining things to people"]
  },
  {
    id: "skills",
    prompt: "Which skills do you already have? Pick all that apply, then hit Done.",
    summaryLabel: "Current skills",
    multiSelect: true,
    chips: ["Python", "SQL", "Git and GitHub", "HTML/CSS/JS", "Statistics", "Communication"]
  },
  {
    id: "comfort",
    prompt: "Honest rating time: how comfortable are you with your strongest skill?",
    summaryLabel: "Skill comfort",
    multiSelect: false,
    chips: ["Just started", "Can build small things", "Can build real projects"]
  },
  {
    id: "goal",
    prompt: "Last one! What do you want in the next year?",
    summaryLabel: "Next year goal",
    multiSelect: false,
    chips: ["An internship", "My first job", "Freelance work", "Higher studies"]
  }
];

// Single object storing all answers across the 6 questions
const nextskillAnswers = {
  study: "",
  area: "",
  enjoyment: "",
  skills: [],
  comfort: "",
  goal: ""
};

// Index tracking current question (0 to 5)
let currentQuestionIndex = 0;

// Set tracking active multi-select choices for Question 4
let selectedSkills = new Set();

// Reusable SVG avatar of Pip the confused student
const pipAvatarSvg = `
<svg viewBox="0 0 100 100" width="40" height="40" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Pip avatar">
  <!-- Student face circle in Paper #EEF2F7 with Ink Navy #14213D outline -->
  <circle cx="50" cy="52" r="38" fill="#EEF2F7" stroke="#14213D" stroke-width="4"/>
  <!-- Sky shirt collar in #5BC0EB -->
  <path d="M 30 86 Q 50 78 70 86" stroke="#14213D" stroke-width="4" fill="#5BC0EB"/>
  <!-- Messy doodle hair -->
  <path d="M 18 48 C 15 15, 60 12, 85 30 C 88 52, 78 48, 78 48 C 72 24, 35 25, 24 50 Z" fill="#14213D"/>
  <path d="M 42 18 Q 45 6 54 12 Q 62 4 66 18" stroke="#14213D" stroke-width="4" stroke-linecap="round" fill="none"/>
  <!-- Confused eyebrows -->
  <path d="M 32 40 Q 40 34 47 40" stroke="#14213D" stroke-width="3" stroke-linecap="round" fill="none"/>
  <path d="M 57 42 L 70 47" stroke="#14213D" stroke-width="3" stroke-linecap="round" fill="none"/>
  <!-- Confused student eyes -->
  <circle cx="39" cy="49" r="3.5" fill="#14213D"/>
  <circle cx="64" cy="52" r="3.5" fill="#14213D"/>
  <!-- Wavy mouth -->
  <path d="M 40 68 Q 48 62 54 69 Q 60 74 65 67" stroke="#14213D" stroke-width="3" stroke-linecap="round" fill="none"/>
  <!-- Sweat drop in Sky #5BC0EB -->
  <path d="M 82 46 C 82 46, 86 54, 86 57 C 86 60, 83 62, 80 62 C 77 62, 75 60, 75 57 C 75 54, 82 46, 82 46 Z" fill="#5BC0EB" stroke="#14213D" stroke-width="2"/>
</svg>`;

// Cache main DOM elements
const messagesContainer = document.getElementById("chat-messages");
const trayContainer = document.getElementById("chat-tray");
const tallyCounter = document.getElementById("tally-counter");

// Update tally tracker lines in header (6 total, with stroke 5 in Cherry)
function updateTallyDisplay(count) {
  // Update text counter
  tallyCounter.textContent = `${count} / 6`;

  // Update stroke 1 through 6
  for (let i = 1; i <= 6; i++) {
    const stroke = document.getElementById(`tally-${i}`);
    if (!stroke) continue;

    if (i <= count) {
      if (i === 5) {
        stroke.classList.add("tally-active-cherry");
      } else {
        stroke.classList.add("tally-active");
      }
    } else {
      stroke.classList.remove("tally-active", "tally-active-cherry");
    }
  }
}

// Render Pip's typing sticky note for 600ms
function showTypingIndicator() {
  const typingRow = document.createElement("div");
  typingRow.className = "bot-row";
  typingRow.id = "typing-indicator";

  typingRow.innerHTML = `
    <div class="bot-avatar">${pipAvatarSvg}</div>
    <div class="bot-note typing-note">
      <span>Pip is scribbling</span>
      <span class="typing-dots">
        <span>.</span><span>.</span><span>.</span>
      </span>
    </div>
  `;

  messagesContainer.appendChild(typingRow);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Remove the typing indicator when message is ready
function removeTypingIndicator() {
  const indicator = document.getElementById("typing-indicator");
  if (indicator) {
    indicator.remove();
  }
}

// Append a sticky note from Pip to the chat stream
function appendBotMessage(text) {
  const row = document.createElement("div");
  row.className = "bot-row";

  row.innerHTML = `
    <div class="bot-avatar">${pipAvatarSvg}</div>
    <div class="bot-note">
      <span class="bot-name">Pip</span>
      ${text}
    </div>
  `;

  messagesContainer.appendChild(row);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Append user's yellow marker-highlighted note to the chat stream
function appendUserMessage(text) {
  const row = document.createElement("div");
  row.className = "user-row";

  row.innerHTML = `
    <div class="user-note">${escapeHtml(text)}</div>
  `;

  messagesContainer.appendChild(row);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Helper to prevent HTML injection in user inputs
function escapeHtml(str) {
  return str.replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[tag] || tag));
}

// Render the interactive chips and input for the current question
function renderQuestionInput(question) {
  // Clear any existing controls in tray
  trayContainer.innerHTML = "";

  const container = document.createElement("div");
  container.className = "chips-container";

  // Render question chips
  question.chips.forEach(chipText => {
    const chipBtn = document.createElement("button");
    chipBtn.type = "button";
    chipBtn.className = "answer-chip";
    chipBtn.textContent = chipText;

    if (question.multiSelect) {
      // Toggle selection for multi-select (Question 4)
      if (selectedSkills.has(chipText)) {
        chipBtn.classList.add("selected");
      }
      chipBtn.addEventListener("click", () => {
        if (selectedSkills.has(chipText)) {
          selectedSkills.delete(chipText);
          chipBtn.classList.remove("selected");
        } else {
          selectedSkills.add(chipText);
          chipBtn.classList.add("selected");
        }
      });
    } else {
      // Single select: directly submit answer
      chipBtn.addEventListener("click", () => {
        handleUserAnswer(question.id, chipText);
      });
    }

    container.appendChild(chipBtn);
  });

  // Always append a "Something else" chip for custom user text
  const customChip = document.createElement("button");
  customChip.type = "button";
  customChip.className = "answer-chip";
  customChip.textContent = "Something else";
  customChip.addEventListener("click", () => {
    showCustomTextInput(question);
  });
  container.appendChild(customChip);

  // If question is multi-select, append a "Done" button
  if (question.multiSelect) {
    const doneBtn = document.createElement("button");
    doneBtn.type = "button";
    doneBtn.className = "done-button";
    doneBtn.textContent = "Done";
    doneBtn.addEventListener("click", () => {
      const skillsArray = Array.from(selectedSkills);
      const answerValue = skillsArray.length > 0 ? skillsArray.join(", ") : "None yet";
      handleUserAnswer(question.id, answerValue, skillsArray);
    });
    container.appendChild(doneBtn);
  }

  trayContainer.appendChild(container);

  // Auto-focus the first chip for keyboard accessibility
  const firstChip = container.querySelector(".answer-chip");
  if (firstChip) {
    firstChip.focus();
  }
}

// Show text input when "Something else" is clicked
function showCustomTextInput(question) {
  trayContainer.innerHTML = "";

  const form = document.createElement("form");
  form.className = "custom-input-form";

  const input = document.createElement("input");
  input.type = "text";
  input.className = "custom-input";
  input.placeholder = "Type your answer here...";
  input.setAttribute("aria-label", "Custom answer");
  input.required = true;

  const submitBtn = document.createElement("button");
  submitBtn.type = "submit";
  submitBtn.className = "custom-submit-btn";
  submitBtn.textContent = question.multiSelect ? "Add skill" : "Send";

  form.appendChild(input);
  form.appendChild(submitBtn);

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const value = input.value.trim();
    if (!value) return;

    if (question.multiSelect) {
      // Add custom skill to set and return to chips view with Done button
      selectedSkills.add(value);
      renderQuestionInput(question);
    } else {
      handleUserAnswer(question.id, value);
    }
  });

  trayContainer.appendChild(form);
  input.focus();
}

// Process an answered question, update state and trigger next step
function handleUserAnswer(questionId, displayAnswer, rawValue) {
  // Clear controls during transition
  trayContainer.innerHTML = "";

  // Append user's yellow note to chat
  appendUserMessage(displayAnswer);

  // Store in answers object
  if (questionId === "skills") {
    nextskillAnswers.skills = rawValue || [displayAnswer];
  } else {
    nextskillAnswers[questionId] = displayAnswer;
  }

  // Save to sessionStorage and console.log
  sessionStorage.setItem("nextskillAnswers", JSON.stringify(nextskillAnswers));
  console.log("NEXT-SKILL Answers updated:", nextskillAnswers);

  // Advance question index and update tallies
  currentQuestionIndex++;
  updateTallyDisplay(currentQuestionIndex);

  // Ask next question or show end screen
  if (currentQuestionIndex < questions.length) {
    askQuestionWithDelay(currentQuestionIndex);
  } else {
    showEndScreen();
  }
}

// Display bot typing for 600ms before showing next question
function askQuestionWithDelay(index) {
  showTypingIndicator();

  setTimeout(() => {
    removeTypingIndicator();
    const question = questions[index];
    appendBotMessage(question.prompt);
    renderQuestionInput(question);
  }, 600);
}

// Render final screen: path coming soon + summary card + Start over button
function showEndScreen() {
  showTypingIndicator();

  setTimeout(() => {
    removeTypingIndicator();

    // Final bot sticky note message
    appendBotMessage("All 6 noted! Your personalized NEXT-SKILL path is coming soon 🚀 Here is the notebook summary we put together:");

    // Build the notebook summary card
    const summaryCard = document.createElement("div");
    summaryCard.className = "summary-card";

    let listHtml = "";
    questions.forEach(q => {
      const ans = nextskillAnswers[q.id];
      const formattedAns = Array.isArray(ans) ? ans.join(", ") : (ans || "Not answered");
      listHtml += `
        <li class="summary-item">
          <span class="summary-q">${q.summaryLabel}:</span>
          <span class="summary-a">${escapeHtml(formattedAns)}</span>
        </li>
      `;
    });

    summaryCard.innerHTML = `
      <h2 class="summary-heading">Your Skill Snapshot</h2>
      <p class="summary-sub">Saved to session. Pip is calculating your optimal roadmap...</p>
      <ul class="summary-list">
        ${listHtml}
      </ul>
      <button type="button" class="start-over-btn" id="start-over-btn">Start over</button>
    `;

    messagesContainer.appendChild(summaryCard);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Attach Start over handler
    const startOverBtn = document.getElementById("start-over-btn");
    if (startOverBtn) {
      startOverBtn.focus();
      startOverBtn.addEventListener("click", resetChat);
    }
  }, 600);
}

// Reset chat state, clear sessionStorage, and restart
function resetChat() {
  // Clear answers object
  nextskillAnswers.study = "";
  nextskillAnswers.area = "";
  nextskillAnswers.enjoyment = "";
  nextskillAnswers.skills = [];
  nextskillAnswers.comfort = "";
  nextskillAnswers.goal = "";

  selectedSkills.clear();
  currentQuestionIndex = 0;

  sessionStorage.removeItem("nextskillAnswers");
  console.log("NEXT-SKILL session reset");

  messagesContainer.innerHTML = "";
  trayContainer.innerHTML = "";
  updateTallyDisplay(0);

  askQuestionWithDelay(0);
}

// Initialize chat when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  updateTallyDisplay(0);
  askQuestionWithDelay(0);
});
