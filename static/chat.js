// ============================================================
// NEXT-SKILL Scripted Q&A Chatbot with Pip
// ============================================================
// Array of 6 questions at the top of the file for easy editing
const questions = [
  // Question 1: Current studies
  {
    // Unique identifier for question 1
    id: "study",
    // Pip's question prompt text
    prompt: "Okay, I'm Pip. I know nothing yet, so tell me about you. What are you studying right now?",
    // Label used in final summary
    summaryLabel: "Current studies",
    // Single-choice question flag
    multiSelect: false,
    // Available answer choices
    chips: ["BCA", "BSc IT / CS", "B.Tech"]
  },
  // Question 2: Tech area of interest
  {
    // Unique identifier for question 2
    id: "area",
    // Pip's question prompt text
    prompt: "Got it! Which area pulls you in most?",
    // Label used in final summary
    summaryLabel: "Area of interest",
    // Single-choice question flag
    multiSelect: false,
    // Available answer choices
    chips: ["Websites and apps", "Data and AI", "Databases and backend", "Design", "Security", "No idea yet"]
  },
  // Question 3: Favorite activity
  {
    // Unique identifier for question 3
    id: "enjoyment",
    // Pip's question prompt text
    prompt: "Fair enough! What do you enjoy doing most?",
    // Label used in final summary
    summaryLabel: "Favorite activity",
    // Single-choice question flag
    multiSelect: false,
    // Available answer choices
    chips: ["Building things", "Digging into data", "Designing how it looks", "Explaining things to people"]
  },
  // Question 4: Current skills
  {
    // Unique identifier for question 4
    id: "skills",
    // Pip's question prompt text
    prompt: "Which skills do you already have? Pick all that apply, then hit Done.",
    // Label used in final summary
    summaryLabel: "Current skills",
    // Multi-choice question flag
    multiSelect: true,
    // Available answer choices
    chips: ["Python", "SQL", "Git and GitHub", "HTML/CSS/JS", "Statistics", "Communication"]
  },
  // Question 5: Comfort level
  {
    // Unique identifier for question 5
    id: "comfort",
    // Pip's question prompt text
    prompt: "Honest rating time: how comfortable are you with your strongest skill?",
    // Label used in final summary
    summaryLabel: "Skill comfort",
    // Single-choice question flag
    multiSelect: false,
    // Available answer choices
    chips: ["Just started", "Can build small things", "Can build real projects"]
  },
  // Question 6: Next year goal
  {
    // Unique identifier for question 6
    id: "goal",
    // Pip's question prompt text
    prompt: "Last one! What do you want in the next year?",
    // Label used in final summary
    summaryLabel: "Next year goal",
    // Single-choice question flag
    multiSelect: false,
    // Available answer choices
    chips: ["An internship", "My first job", "Freelance work", "Higher studies"]
  }
];
// Single object storing all answers across the 6 questions
const nextskillAnswers = {
  // Store study field
  study: "",
  // Store interest area
  area: "",
  // Store favorite activity
  enjoyment: "",
  // Store skills array
  skills: [],
  // Store skill comfort level
  comfort: "",
  // Store next year goal
  goal: ""
};
// Index tracking current question (0 to 5)
let currentQuestionIndex = 0;
// Set tracking active multi-select choices for Question 4
let selectedSkills = new Set();
// Static SVG markup string for Pip the confused student avatar
const pipAvatarSvg = `<svg viewBox="0 0 100 100" width="40" height="40" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Pip avatar"><circle cx="50" cy="52" r="38" fill="#EEF2F7" stroke="#14213D" stroke-width="4"/><path d="M 30 86 Q 50 78 70 86" stroke="#14213D" stroke-width="4" fill="#5BC0EB"/><path d="M 18 48 C 15 15, 60 12, 85 30 C 88 52, 78 48, 78 48 C 72 24, 35 25, 24 50 Z" fill="#14213D"/><path d="M 42 18 Q 45 6 54 12 Q 62 4 66 18" stroke="#14213D" stroke-width="4" stroke-linecap="round" fill="none"/><path d="M 32 40 Q 40 34 47 40" stroke="#14213D" stroke-width="3" stroke-linecap="round" fill="none"/><path d="M 57 42 L 70 47" stroke="#14213D" stroke-width="3" stroke-linecap="round" fill="none"/><circle cx="39" cy="49" r="3.5" fill="#14213D"/><circle cx="64" cy="52" r="3.5" fill="#14213D"/><path d="M 40 68 Q 48 62 54 69 Q 60 74 65 67" stroke="#14213D" stroke-width="3" stroke-linecap="round" fill="none"/><path d="M 82 46 C 82 46, 86 54, 86 57 C 86 60, 83 62, 80 62 C 77 62, 75 60, 75 57 C 75 54, 82 46, 82 46 Z" fill="#5BC0EB" stroke="#14213D" stroke-width="2"/></svg>`;
// Function to safely create Pip avatar DOM element without innerHTML
function createPipAvatar() {
  // Initialize DOMParser to parse static SVG XML safely
  const parser = new DOMParser();
  // Parse static SVG string into XML document
  const doc = parser.parseFromString(pipAvatarSvg, "image/svg+xml");
  // Import and return parsed SVG node
  return document.importNode(doc.documentElement, true);
}
// Cache main message stream DOM element
const messagesContainer = document.getElementById("chat-messages");
// Cache bottom interaction tray DOM element
const trayContainer = document.getElementById("chat-tray");
// Cache tally counter text DOM element
const tallyCounter = document.getElementById("tally-counter");
// Update tally tracker lines in header (6 total, with stroke 5 in Cherry)
function updateTallyDisplay(count) {
  // Set human-readable counter text using textContent
  tallyCounter.textContent = `${count} / 6`;
  // Loop through tally strokes 1 to 6
  for (let i = 1; i <= 6; i++) {
    // Select stroke element by ID
    const stroke = document.getElementById(`tally-${i}`);
    // Guard against missing stroke element
    if (!stroke) continue;
    // Activate stroke if count reached
    if (i <= count) {
      // Stroke 5 uses cherry cross-strike
      if (i === 5) {
        // Add cherry class
        stroke.classList.add("tally-active-cherry");
      // Other strokes use ink navy
      } else {
        // Add active ink class
        stroke.classList.add("tally-active");
      }
    // Deactivate stroke if count not reached
    } else {
      // Remove all active classes
      stroke.classList.remove("tally-active", "tally-active-cherry");
    }
  }
}
// Render Pip's typing sticky note with custom message
function showTypingIndicator(statusMessage = "Pip is scribbling") {
  // Create row wrapper
  const typingRow = document.createElement("div");
  // Set class for row
  typingRow.className = "bot-row";
  // Set identifier for indicator
  typingRow.id = "typing-indicator";
  // Create avatar wrapper
  const avatarWrapper = document.createElement("div");
  // Set avatar class
  avatarWrapper.className = "bot-avatar";
  // Append Pip avatar SVG
  avatarWrapper.appendChild(createPipAvatar());
  // Create note container
  const note = document.createElement("div");
  // Set note classes
  note.className = "bot-note typing-note";
  // Create status text span
  const textSpan = document.createElement("span");
  // Set status text safely using textContent
  textSpan.textContent = statusMessage;
  // Create animated dots container
  const dotsSpan = document.createElement("span");
  // Set dots class
  dotsSpan.className = "typing-dots";
  // Create first dot
  const dot1 = document.createElement("span");
  // Set first dot text safely using textContent
  dot1.textContent = ".";
  // Create second dot
  const dot2 = document.createElement("span");
  // Set second dot text safely using textContent
  dot2.textContent = ".";
  // Create third dot
  const dot3 = document.createElement("span");
  // Set third dot text safely using textContent
  dot3.textContent = ".";
  // Append dots to container
  dotsSpan.appendChild(dot1);
  // Append second dot
  dotsSpan.appendChild(dot2);
  // Append third dot
  dotsSpan.appendChild(dot3);
  // Append status text to note
  note.appendChild(textSpan);
  // Append dots to note
  note.appendChild(dotsSpan);
  // Append avatar to row
  typingRow.appendChild(avatarWrapper);
  // Append note to row
  typingRow.appendChild(note);
  // Append row to chat stream
  messagesContainer.appendChild(typingRow);
  // Scroll message stream to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
// Remove the typing indicator when message arrives
function removeTypingIndicator() {
  // Find typing indicator element
  const indicator = document.getElementById("typing-indicator");
  // Remove indicator if found
  if (indicator) {
    // Remove from DOM
    indicator.remove();
  }
}
// Append a sticky note from Pip using textContent
function appendBotMessage(text) {
  // Create bot row
  const row = document.createElement("div");
  // Set row class
  row.className = "bot-row";
  // Create avatar wrapper
  const avatar = document.createElement("div");
  // Set avatar class
  avatar.className = "bot-avatar";
  // Append Pip avatar
  avatar.appendChild(createPipAvatar());
  // Create note container
  const note = document.createElement("div");
  // Set note class
  note.className = "bot-note";
  // Create name tag
  const name = document.createElement("span");
  // Set name class
  name.className = "bot-name";
  // Set name text content safely
  name.textContent = "Pip";
  // Create message text element
  const messageBody = document.createElement("div");
  // Insert text safely using textContent
  messageBody.textContent = text;
  // Append name tag to note
  note.appendChild(name);
  // Append message body to note
  note.appendChild(messageBody);
  // Append avatar to row
  row.appendChild(avatar);
  // Append note to row
  row.appendChild(note);
  // Append row to message stream
  messagesContainer.appendChild(row);
  // Scroll message stream to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
// Append user's yellow marker-highlighted note using textContent
function appendUserMessage(text) {
  // Create user row
  const row = document.createElement("div");
  // Set row class
  row.className = "user-row";
  // Create user note container
  const note = document.createElement("div");
  // Set user note class
  note.className = "user-note";
  // Insert user text safely using textContent
  note.textContent = text;
  // Append note to row
  row.appendChild(note);
  // Append row to message stream
  messagesContainer.appendChild(row);
  // Scroll message stream to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
// Render interactive chips and input for current question
function renderQuestionInput(question) {
  // Clear any existing controls in tray
  trayContainer.replaceChildren();
  // Create chips container
  const container = document.createElement("div");
  // Set container class
  container.className = "chips-container";
  // Render question chips
  question.chips.forEach(chipText => {
    // Create button element
    const chipBtn = document.createElement("button");
    // Set button type
    chipBtn.type = "button";
    // Set chip class
    chipBtn.className = "answer-chip";
    // Set chip label safely using textContent
    chipBtn.textContent = chipText;
    // Branch for multi-select question
    if (question.multiSelect) {
      // Apply selected state if already chosen
      if (selectedSkills.has(chipText)) {
        // Add selected class
        chipBtn.classList.add("selected");
      }
      // Toggle selection on click
      chipBtn.addEventListener("click", () => {
        // Deselect if already present
        if (selectedSkills.has(chipText)) {
          // Remove from set
          selectedSkills.delete(chipText);
          // Remove active class
          chipBtn.classList.remove("selected");
        // Select if not present
        } else {
          // Add to set
          selectedSkills.add(chipText);
          // Add active class
          chipBtn.classList.add("selected");
        }
      });
    // Branch for single-select question
    } else {
      // Submit answer directly on click
      chipBtn.addEventListener("click", () => {
        // Handle answer submission
        handleUserAnswer(question.id, chipText);
      });
    }
    // Append chip to container
    container.appendChild(chipBtn);
  });
  // Create Something else chip
  const customChip = document.createElement("button");
  // Set button type
  customChip.type = "button";
  // Set chip class
  customChip.className = "answer-chip";
  // Set custom chip label safely using textContent
  customChip.textContent = "Something else";
  // Show input field on click
  customChip.addEventListener("click", () => {
    // Display custom text input form
    showCustomTextInput(question);
  });
  // Append custom chip to container
  container.appendChild(customChip);
  // Append Done button for multi-select questions
  if (question.multiSelect) {
    // Create Done button
    const doneBtn = document.createElement("button");
    // Set button type
    doneBtn.type = "button";
    // Set button class
    doneBtn.className = "done-button";
    // Set button label safely using textContent
    doneBtn.textContent = "Done";
    // Handle Done submission
    doneBtn.addEventListener("click", () => {
      // Convert set to array
      const skillsArray = Array.from(selectedSkills);
      // Format display string
      const answerValue = skillsArray.length > 0 ? skillsArray.join(", ") : "None yet";
      // Handle answer submission
      handleUserAnswer(question.id, answerValue, skillsArray);
    });
    // Append Done button
    container.appendChild(doneBtn);
  }
  // Append chips container to tray
  trayContainer.appendChild(container);
  // Auto-focus first chip for keyboard accessibility
  const firstChip = container.querySelector(".answer-chip");
  // Check if first chip exists
  if (firstChip) {
    // Focus first chip
    firstChip.focus();
  }
}
// Show custom text input when Something else is selected
function showCustomTextInput(question) {
  // Clear tray container
  trayContainer.replaceChildren();
  // Create form element
  const form = document.createElement("form");
  // Set form class
  form.className = "custom-input-form";
  // Create text input element
  const input = document.createElement("input");
  // Set input type
  input.type = "text";
  // Set input class
  input.className = "custom-input";
  // Set placeholder
  input.placeholder = "Type your answer here...";
  // Set accessible label
  input.setAttribute("aria-label", "Custom answer");
  // Require value
  input.required = true;
  // Create submit button
  const submitBtn = document.createElement("button");
  // Set button type
  submitBtn.type = "submit";
  // Set button class
  submitBtn.className = "custom-submit-btn";
  // Set button label safely using textContent
  submitBtn.textContent = question.multiSelect ? "Add skill" : "Send";
  // Append input to form
  form.appendChild(input);
  // Append submit button to form
  form.appendChild(submitBtn);
  // Handle form submission
  form.addEventListener("submit", (e) => {
    // Prevent default page reload
    e.preventDefault();
    // Trim input value
    const value = input.value.trim();
    // Guard against empty input
    if (!value) return;
    // Handle multi-select skill addition
    if (question.multiSelect) {
      // Add custom skill to set
      selectedSkills.add(value);
      // Re-render chips showing added skill
      renderQuestionInput(question);
    // Handle single-select submission
    } else {
      // Submit custom answer
      handleUserAnswer(question.id, value);
    }
  });
  // Append form to tray
  trayContainer.appendChild(form);
  // Focus text input field
  input.focus();
}
// Process user answer and advance chatbot flow
function handleUserAnswer(questionId, displayAnswer, rawValue) {
  // Clear controls during transition
  trayContainer.replaceChildren();
  // Append user's note to chat stream
  appendUserMessage(displayAnswer);
  // Store answer in nextskillAnswers object
  if (questionId === "skills") {
    // Save skills as array
    nextskillAnswers.skills = rawValue || [displayAnswer];
  // Save scalar answer
  } else {
    // Assign scalar field
    nextskillAnswers[questionId] = displayAnswer;
  }
  // Save updated answers to sessionStorage
  sessionStorage.setItem("nextskillAnswers", JSON.stringify(nextskillAnswers));
  // Log answers to console
  console.log("NEXT-SKILL Answers updated:", nextskillAnswers);
  // Advance question index
  currentQuestionIndex++;
  // Update tally display count
  updateTallyDisplay(currentQuestionIndex);
  // Check if more questions remain
  if (currentQuestionIndex < questions.length) {
    // Ask next question with 600ms delay
    askQuestionWithDelay(currentQuestionIndex);
  // All 6 questions completed: send to API
  } else {
    // Fetch suggestions from /api/suggest
    fetchSuggestionsAndDisplay();
  }
}
// Display bot typing indicator for 600ms before next question
function askQuestionWithDelay(index) {
  // Show typing indicator
  showTypingIndicator("Pip is scribbling");
  // Wait 600ms before revealing question
  setTimeout(() => {
    // Remove typing indicator
    removeTypingIndicator();
    // Retrieve question definition
    const question = questions[index];
    // Append bot prompt note
    appendBotMessage(question.prompt);
    // Render question interactive chips
    renderQuestionInput(question);
  }, 600);
}
// Fetch career recommendations from POST /api/suggest
function fetchSuggestionsAndDisplay() {
  // Clear interactive tray while waiting
  trayContainer.replaceChildren();
  // Show bot typing message "Pip is thinking..."
  showTypingIndicator("Pip is thinking");
  // Map stored answers into required JSON schema in question order
  const payload = {
    // Study field mapped from study
    field: nextskillAnswers.study,
    // Interest area mapped from area
    interest: nextskillAnswers.area,
    // Favorite activity mapped from enjoyment
    enjoy: nextskillAnswers.enjoyment,
    // Skills array mapped from skills
    skills: Array.isArray(nextskillAnswers.skills) ? nextskillAnswers.skills : [nextskillAnswers.skills],
    // Comfort level mapped from comfort
    level: nextskillAnswers.comfort,
    // Next year goal mapped from goal
    goal: nextskillAnswers.goal
  };
  // Send POST request to relative URL /api/suggest
  fetch("/api/suggest", {
    // Set HTTP method
    method: "POST",
    // Set JSON headers
    headers: { "Content-Type": "application/json" },
    // Serialize payload to JSON
    body: JSON.stringify(payload)
  })
  // Handle server response
  .then(async (response) => {
    // Remove typing indicator
    removeTypingIndicator();
    // Check if response status is not OK
    if (!response.ok) {
      // Default error text
      let errorMsg = `Server error (${response.status})`;
      // Try to extract detail from response JSON
      try {
        // Parse error JSON body
        const errJson = await response.json();
        // Extract detail or message
        errorMsg = errJson.detail || errJson.message || errorMsg;
      // Fallback to text parsing
      } catch (_) {
        // Read raw response text
        const textErr = await response.text();
        // Use text if present
        if (textErr) errorMsg = textErr;
      }
      // Render error message and retry button
      showErrorWithRetry(errorMsg);
      // Return early
      return;
    }
    // Parse JSON suggestions
    const data = await response.json();
    // Retrieve suggestions array
    const suggestions = data.suggestions || [];
    // Render suggestions sticky notes, summary card, and restart button
    renderSuccessScreen(suggestions);
  })
  // Handle network exceptions
  .catch(() => {
    // Remove typing indicator
    removeTypingIndicator();
    // Render network error message with retry button
    showErrorWithRetry("Unable to reach the server. Please check your connection.");
  });
}
// Render error note and Try again button when request fails
function showErrorWithRetry(errorText) {
  // Create bot row
  const row = document.createElement("div");
  // Set row class
  row.className = "bot-row";
  // Create avatar container
  const avatar = document.createElement("div");
  // Set avatar class
  avatar.className = "bot-avatar";
  // Append Pip avatar SVG
  avatar.appendChild(createPipAvatar());
  // Create note container
  const note = document.createElement("div");
  // Set note class
  note.className = "bot-note";
  // Create name tag
  const name = document.createElement("span");
  // Set name class
  name.className = "bot-name";
  // Set name safely using textContent
  name.textContent = "Pip";
  // Create error paragraph
  const p = document.createElement("div");
  // Insert error text safely using textContent
  p.textContent = `Oops! ${errorText}`;
  // Append name to note
  note.appendChild(name);
  // Append error text to note
  note.appendChild(p);
  // Append avatar to row
  row.appendChild(avatar);
  // Append note to row
  row.appendChild(note);
  // Append row to message stream
  messagesContainer.appendChild(row);
  // Clear tray
  trayContainer.replaceChildren();
  // Create Try again button
  const retryBtn = document.createElement("button");
  // Set button type
  retryBtn.type = "button";
  // Set button class
  retryBtn.className = "try-again-btn";
  // Set button label safely using textContent
  retryBtn.textContent = "Try again";
  // Attach click listener to resend answers
  retryBtn.addEventListener("click", () => {
    // Re-run suggestion fetch
    fetchSuggestionsAndDisplay();
  });
  // Append retry button to tray
  trayContainer.appendChild(retryBtn);
  // Scroll stream to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  // Focus retry button for keyboard accessibility
  retryBtn.focus();
}
// Render the 3 suggestions as sticky notes, summary card, and Start over button
function renderSuccessScreen(suggestions) {
  // Append Pip's introduction sticky note
  appendBotMessage("Here are 3 career paths tailored to your skills and goals:");
  // Iterate through each suggestion
  suggestions.forEach((item) => {
    // Create bot row for suggestion
    const row = document.createElement("div");
    // Set row class
    row.className = "bot-row";
    // Create avatar container
    const avatar = document.createElement("div");
    // Set avatar class
    avatar.className = "bot-avatar";
    // Append Pip avatar SVG
    avatar.appendChild(createPipAvatar());
    // Create suggestion sticky note container
    const note = document.createElement("div");
    // Set suggestion note classes
    note.className = "bot-note suggestion-note";
    // Create role heading element
    const roleHeading = document.createElement("h3");
    // Set role heading class
    roleHeading.className = "suggestion-role";
    // Insert role safely using textContent
    roleHeading.textContent = item.role || "Career Path";
    // Create why sentence element
    const whyP = document.createElement("p");
    // Set why paragraph class
    whyP.className = "suggestion-why";
    // Insert why explanation safely using textContent
    whyP.textContent = item.why || "";
    // Create learn next section container
    const learnSection = document.createElement("div");
    // Set learn section class
    learnSection.className = "learn-section";
    // Create learn next label element
    const learnLabel = document.createElement("span");
    // Set learn label class
    learnLabel.className = "learn-label";
    // Set label text safely using textContent
    learnLabel.textContent = "Learn next:";
    // Create small chips container
    const chipsWrap = document.createElement("div");
    // Set chips wrapper class
    chipsWrap.className = "learn-chips";
    // Retrieve learn_next array
    const skillsList = Array.isArray(item.learn_next) ? item.learn_next : [item.learn_next];
    // Create small chip for each skill
    skillsList.forEach((skill) => {
      // Create small chip span
      const chip = document.createElement("span");
      // Set chip class
      chip.className = "learn-chip";
      // Insert skill text safely using textContent
      chip.textContent = String(skill);
      // Append chip to wrapper
      chipsWrap.appendChild(chip);
    });
    // Append label to learn section
    learnSection.appendChild(learnLabel);
    // Append chips to learn section
    learnSection.appendChild(chipsWrap);
    // Append role heading to note
    note.appendChild(roleHeading);
    // Append why paragraph to note
    note.appendChild(whyP);
    // Append learn section to note
    note.appendChild(learnSection);
    // Append avatar to row
    row.appendChild(avatar);
    // Append note to row
    row.appendChild(note);
    // Append suggestion row to chat stream
    messagesContainer.appendChild(row);
  });
  // Render existing summary card
  renderSummaryCard();
}
// Render the student answers summary card and Start over button
function renderSummaryCard() {
  // Create summary card element
  const summaryCard = document.createElement("div");
  // Set card class
  summaryCard.className = "summary-card";
  // Create card heading
  const heading = document.createElement("h2");
  // Set heading class
  heading.className = "summary-heading";
  // Set heading text safely using textContent
  heading.textContent = "Your Skill Snapshot";
  // Create subtext paragraph
  const sub = document.createElement("p");
  // Set subtext class
  sub.className = "summary-sub";
  // Set subtext safely using textContent
  sub.textContent = "Saved to session. Pip has generated your personalized paths above!";
  // Create list element
  const list = document.createElement("ul");
  // Set list class
  list.className = "summary-list";
  // Populate answers in list
  questions.forEach(q => {
    // Retrieve saved answer
    const ans = nextskillAnswers[q.id];
    // Format array or string answer
    const formattedAns = Array.isArray(ans) ? ans.join(", ") : (ans || "Not answered");
    // Create list item
    const item = document.createElement("li");
    // Set item class
    item.className = "summary-item";
    // Create question label span
    const qSpan = document.createElement("span");
    // Set question class
    qSpan.className = "summary-q";
    // Set question label safely using textContent
    qSpan.textContent = `${q.summaryLabel}:`;
    // Create answer text span
    const aSpan = document.createElement("span");
    // Set answer class
    aSpan.className = "summary-a";
    // Set answer text safely using textContent
    aSpan.textContent = formattedAns;
    // Append question label to item
    item.appendChild(qSpan);
    // Append answer text to item
    item.appendChild(aSpan);
    // Append item to list
    list.appendChild(item);
  });
  // Create Start over button
  const startOverBtn = document.createElement("button");
  // Set button type
  startOverBtn.type = "button";
  // Set button class
  startOverBtn.className = "start-over-btn";
  // Set button ID
  startOverBtn.id = "start-over-btn";
  // Set button label safely using textContent
  startOverBtn.textContent = "Start over";
  // Attach reset listener
  startOverBtn.addEventListener("click", resetChat);
  // Append heading to card
  summaryCard.appendChild(heading);
  // Append subtext to card
  summaryCard.appendChild(sub);
  // Append list to card
  summaryCard.appendChild(list);
  // Append start over button to card
  summaryCard.appendChild(startOverBtn);
  // Append card to message stream
  messagesContainer.appendChild(summaryCard);
  // Clear tray container
  trayContainer.replaceChildren();
  // Scroll message stream to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  // Focus Start over button for keyboard accessibility
  startOverBtn.focus();
}
// Reset chat state, clear sessionStorage, and restart
function resetChat() {
  // Clear study answer
  nextskillAnswers.study = "";
  // Clear area answer
  nextskillAnswers.area = "";
  // Clear enjoyment answer
  nextskillAnswers.enjoyment = "";
  // Clear skills array
  nextskillAnswers.skills = [];
  // Clear comfort answer
  nextskillAnswers.comfort = "";
  // Clear goal answer
  nextskillAnswers.goal = "";
  // Clear selected skills set
  selectedSkills.clear();
  // Reset question index to 0
  currentQuestionIndex = 0;
  // Clear sessionStorage item
  sessionStorage.removeItem("nextskillAnswers");
  // Log reset action
  console.log("NEXT-SKILL session reset");
  // Clear message stream
  messagesContainer.replaceChildren();
  // Clear tray controls
  trayContainer.replaceChildren();
  // Reset tally counter to 0
  updateTallyDisplay(0);
  // Ask first question with 600ms delay
  askQuestionWithDelay(0);
}
// Initialize chat on page load
document.addEventListener("DOMContentLoaded", () => {
  // Reset tally display to 0
  updateTallyDisplay(0);
  // Start with first question
  askQuestionWithDelay(0);
});
