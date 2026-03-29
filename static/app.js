let currentCard = null;
let answerShown = false;

// ── Per-user identity ───────────────────────────────────────
function generateUUID() {
  // crypto.randomUUID() requires HTTPS; fall back to manual generation for HTTP
  if (crypto && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  // RFC 4122 v4 fallback
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function getUserId() {
  let userId = localStorage.getItem("flashcard_user_id");

  if (!userId) {
    userId = generateUUID();
    localStorage.setItem("flashcard_user_id", userId);
  }

  return userId;
}

const USER_ID = getUserId();

const statusMessage = document.getElementById("status-message");
const topicSelect = document.getElementById("topic-select");
const cardMeta = document.getElementById("card-meta");
const frontBox = document.getElementById("front-box");
const showAnswerBtn = document.getElementById("show-answer-btn");
const answerSection = document.getElementById("answer-section");
const backBox = document.getElementById("back-box");
const explanationWrap = document.getElementById("explanation-wrap");
const explanationBox = document.getElementById("explanation-box");
const exampleWrap = document.getElementById("example-wrap");
const exampleBox = document.getElementById("example-box");
const whyWrongWrap = document.getElementById("why-wrong-wrap");
const whyWrongBox = document.getElementById("why-wrong-box");
const dashboardTotals = document.getElementById("dashboard-totals");
const weakTopics = document.getElementById("weak-topics");
const hardCards = document.getElementById("hard-cards");
const searchInput = document.getElementById("search-input");
const searchResults = document.getElementById("search-results");

function setStatus(message) {
  statusMessage.textContent = message;
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function textToHtmlBlock(text) {
  if (!text) {
    return "";
  }

  return escapeHtml(text).replace(/\n/g, "<br>");
}

function resetCardDisplay() {
  currentCard = null;
  answerShown = false;

  cardMeta.textContent = "No card loaded yet.";
  frontBox.textContent = "Click “Get Next Card”.";
  backBox.textContent = "";

  explanationBox.textContent = "";
  exampleBox.textContent = "";
  whyWrongBox.textContent = "";

  answerSection.classList.add("hidden");
  explanationWrap.classList.add("hidden");
  exampleWrap.classList.add("hidden");
  whyWrongWrap.classList.add("hidden");

  showAnswerBtn.disabled = true;
}

function prepareForNewCard() {
  answerShown = false;

  backBox.textContent = "";
  explanationBox.textContent = "";
  exampleBox.textContent = "";
  whyWrongBox.textContent = "";

  answerSection.classList.add("hidden");
  explanationWrap.classList.add("hidden");
  exampleWrap.classList.add("hidden");
  whyWrongWrap.classList.add("hidden");
}

function renderWhyWrong(whyWrong) {
  if (!whyWrong) {
    return "";
  }

  const lines = [];

  for (const key of ["A", "B", "C", "D"]) {
    const value = whyWrong[key];
    if (value && value.trim()) {
      lines.push(`<strong>${key}</strong>: ${escapeHtml(value.trim())}`);
    }
  }

  return lines.join("<br><br>");
}

async function fetchJson(url, options = {}) {
  if (!options.headers) {
    options.headers = {};
  }
  options.headers["X-User-Id"] = USER_ID;

  const response = await fetch(url, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }

  return data;
}

async function loadTopicsFromDashboard() {
  try {
    const dashboard = await fetchJson("/api/dashboard");
    populateDashboard(dashboard);

    const topics = ["All"];
    for (const row of dashboard.topics || []) {
      if (!topics.includes(row.topic)) {
        topics.push(row.topic);
      }
    }

    const currentValue = topicSelect.value || "All";
    topicSelect.innerHTML = "";

    for (const topic of topics) {
      const option = document.createElement("option");
      option.value = topic;
      option.textContent = topic;
      topicSelect.appendChild(option);
    }

    if (topics.includes(currentValue)) {
      topicSelect.value = currentValue;
    } else {
      topicSelect.value = "All";
    }
  } catch (error) {
    setStatus(error.message);
  }
}

function populateDashboard(dashboard) {
  dashboardTotals.innerHTML = "";
  weakTopics.innerHTML = "";
  hardCards.innerHTML = "";

  const totals = dashboard.totals || {};
  const statItems = [
    ["Total cards", totals.total_cards || 0],
    ["Due cards", totals.due_cards || 0],
    ["Reviewed cards", totals.reviewed_cards || 0],
    ["New cards", totals.new_cards || 0],
  ];

  for (const [label, value] of statItems) {
    const div = document.createElement("div");
    div.className = "stat";
    div.innerHTML = `<div class="stat-label">${label}</div><div class="stat-value">${value}</div>`;
    dashboardTotals.appendChild(div);
  }

  const weakList = dashboard.weakest_topics || [];
  if (weakList.length === 0) {
    weakTopics.innerHTML = `<div class="muted">No topic data yet.</div>`;
  } else {
    for (const row of weakList) {
      const div = document.createElement("div");
      div.className = "list-item";
      div.innerHTML = `
        <strong>${escapeHtml(row.topic)}</strong><br>
        <span class="small muted">Total: ${row.total} | Due: ${row.due} | Hard: ${row.hard} | New: ${row.new}</span>
      `;
      weakTopics.appendChild(div);
    }
  }

  const hardList = dashboard.hard_cards || [];
  if (hardList.length === 0) {
    hardCards.innerHTML = `<div class="muted">No hard cards yet.</div>`;
  } else {
    for (const row of hardList) {
      const div = document.createElement("div");
      div.className = "list-item";
      div.innerHTML = `
        <strong>${escapeHtml(row.topic)}</strong><br>
        <div class="small">${textToHtmlBlock(row.front)}</div>
        <div class="small muted">Last rating: ${row.last_rating} | Times seen: ${row.times_seen}</div>
      `;
      hardCards.appendChild(div);
    }
  }
}

function renderCard(card) {
  prepareForNewCard();

  currentCard = card;
  showAnswerBtn.disabled = false;

  cardMeta.textContent = `${card.topic} | ${card.subtopic || "General"} | ${card.card_type}`;
  frontBox.textContent = card.front || "";
}

function showAnswer() {
  if (!currentCard || answerShown) {
    return;
  }

  answerShown = true;
  answerSection.classList.remove("hidden");

  backBox.innerHTML = textToHtmlBlock(currentCard.back || "");

  if (currentCard.explanation && currentCard.explanation.trim()) {
    explanationWrap.classList.remove("hidden");
    explanationBox.innerHTML = textToHtmlBlock(currentCard.explanation);
  } else {
    explanationWrap.classList.add("hidden");
    explanationBox.textContent = "";
  }

  if (currentCard.example && currentCard.example.trim()) {
    exampleWrap.classList.remove("hidden");
    exampleBox.innerHTML = textToHtmlBlock(currentCard.example);
  } else {
    exampleWrap.classList.add("hidden");
    exampleBox.textContent = "";
  }

  const whyWrongHtml = renderWhyWrong(currentCard.why_other_options_wrong || {});
  if (whyWrongHtml) {
    whyWrongWrap.classList.remove("hidden");
    whyWrongBox.innerHTML = whyWrongHtml;
  } else {
    whyWrongWrap.classList.add("hidden");
    whyWrongBox.textContent = "";
  }
}

async function loadNextCard() {
  try {
    prepareForNewCard();

    const topic = encodeURIComponent(topicSelect.value || "All");
    const data = await fetchJson(`/api/next-card?topic=${topic}`);

    if (data.message) {
      currentCard = null;
      cardMeta.textContent = "No card loaded.";
      frontBox.textContent = data.message;
      showAnswerBtn.disabled = true;
      setStatus(data.message);
      return;
    }

    renderCard(data);
    setStatus("Card loaded.");
  } catch (error) {
    setStatus(error.message);
  }
}

async function submitReview(rating) {
  if (!currentCard) {
    return;
  }

  if (!answerShown) {
    showAnswer();
    return;
  }

  try {
    await fetchJson("/api/review", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        card_id: currentCard.card_id,
        rating: rating,
      }),
    });

    setStatus(`Saved rating: ${rating}`);
    await loadTopicsFromDashboard();
    await loadNextCard();
  } catch (error) {
    setStatus(error.message);
  }
}

async function runSearch() {
  try {
    const query = encodeURIComponent(searchInput.value || "");
    const topic = encodeURIComponent(topicSelect.value || "All");

    const data = await fetchJson(`/api/search?query=${query}&topic=${topic}`);
    const results = data.results || [];

    searchResults.innerHTML = "";

    if (results.length === 0) {
      searchResults.innerHTML = `<div class="muted">No results found.</div>`;
      return;
    }

    for (const row of results) {
      const div = document.createElement("div");
      div.className = "list-item";
      div.innerHTML = `
        <strong>${escapeHtml(row.topic)} | ${escapeHtml(row.card_type)}</strong><br>
        <div class="small">${textToHtmlBlock(row.front)}</div>
      `;
      searchResults.appendChild(div);
    }
  } catch (error) {
    setStatus(error.message);
  }
}

document.getElementById("next-card-btn").addEventListener("click", loadNextCard);
document.getElementById("show-answer-btn").addEventListener("click", showAnswer);
document.getElementById("search-btn").addEventListener("click", runSearch);

for (const button of document.querySelectorAll("[data-rating]")) {
  button.addEventListener("click", function () {
    submitReview(button.dataset.rating);
  });
}

document.addEventListener("keydown", function (event) {
  if (event.code === "Space") {
    event.preventDefault();
    showAnswer();
    return;
  }

  if (event.key === "1") {
    submitReview("again");
    return;
  }

  if (event.key === "2") {
    submitReview("hard");
    return;
  }

  if (event.key === "3") {
    submitReview("good");
    return;
  }

  if (event.key === "4") {
    submitReview("easy");
    return;
  }
});

resetCardDisplay();
loadTopicsFromDashboard();