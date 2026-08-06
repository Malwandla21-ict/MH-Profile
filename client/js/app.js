// ---- Config ----
const CONTACT_EMAIL = " MalwandlaHlongwaneICT@outlook.com"; // TODO: replace with your real address
const DEFAULT_PROFILE = "software";

// ---- State ----
let profiles = {};
let activeProfile = DEFAULT_PROFILE;

// ---- Boot ----
document.getElementById("year").textContent = new Date().getFullYear();

fetch("data/profiles.json")
  .then((res) => res.json())
  .then((data) => {
    profiles = data;
    renderProfileCards();
    setActiveProfile(DEFAULT_PROFILE);
    startTypingLoop(Object.values(profiles).map((p) => p.headline));
    updateStats();
  })
  .catch((err) => {
    console.error("Failed to load profiles.json", err);
  });

// ---- Profile cards ----
function renderProfileCards() {
  const container = document.getElementById("profileCards");
  container.innerHTML = "";
  Object.entries(profiles).forEach(([key, profile]) => {
    const btn = document.createElement("button");
    btn.className =
      "profile-card bg-card border border-white/10 rounded-full px-5 py-2 text-sm font-medium";
    btn.textContent = profile.label;
    btn.dataset.key = key;
    btn.addEventListener("click", () => setActiveProfile(key));
    container.appendChild(btn);
  });
}

function setActiveProfile(key) {
  if (!profiles[key]) return;
  activeProfile = key;

  // highlight active card
  document.querySelectorAll(".profile-card").forEach((el) => {
    el.classList.toggle("active", el.dataset.key === key);
  });

  const profile = profiles[key];

  // About summary
  const summaryEl = document.getElementById("profileSummary");
  summaryEl.classList.remove("fade-in");
  void summaryEl.offsetWidth; // restart animation
  summaryEl.textContent = profile.summary;
  summaryEl.classList.add("fade-in");

  // Skills
  renderSkills(profile.skills);

  // CV download buttons
  document.getElementById("downloadCvBtn").onclick = () => downloadCv(profile.cv);
  document.getElementById("downloadCvBtnHero").onclick = () => downloadCv(profile.cv);
}

function downloadCv(path) {
  const link = document.createElement("a");
  link.href = path;
  link.download = "";
  link.click();
}

// ---- Skills ----
function renderSkills(skillNames) {
  const container = document.getElementById("skillsList");
  container.innerHTML = "";
  skillNames.forEach((name, i) => {
    // Placeholder level — replace with real proficiency data per skill later
    const level = 65 + ((i * 7) % 30);
    const card = document.createElement("div");
    card.className = "bg-card border border-white/5 rounded-xl p-4 fade-in";
    card.innerHTML = `
      <div class="flex justify-between text-sm mb-2">
        <span>${name}</span>
        <span class="text-muted font-mono">${level}%</span>
      </div>
      <div class="skill-bar-track">
        <div class="skill-bar-fill" style="width:${level}%"></div>
      </div>
    `;
    container.appendChild(card);
  });
}

// ---- Typing animation ----
function startTypingLoop(phrases) {
  const el = document.getElementById("typedHeadline");
  el.classList.add("typing-cursor");
  let phraseIndex = 0;
  let charIndex = 0;
  let deleting = false;

  function tick() {
    const current = phrases[phraseIndex];
    el.textContent = deleting
      ? current.slice(0, charIndex--)
      : current.slice(0, charIndex++);

    let delay = deleting ? 40 : 80;

    if (!deleting && charIndex === current.length + 1) {
      deleting = true;
      delay = 1200;
    } else if (deleting && charIndex === 0) {
      deleting = false;
      phraseIndex = (phraseIndex + 1) % phrases.length;
      delay = 300;
    }

    setTimeout(tick, delay);
  }
  tick();
}

// ---- Stats (placeholder — wire to real data / GitHub API later) ----
function updateStats() {
  const stats = { projects: 1, technologies: 10, certificates: 0, years: 2, repos: 3 };
  Object.entries(stats).forEach(([key, value]) => {
    const el = document.querySelector(`[data-stat="${key}"]`);
    if (el) el.textContent = value;
  });
}

// ---- Contact form (MVP: mailto, no backend yet) ----
document.getElementById("contactForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const form = e.target;
  const name = form.name.value;
  const email = form.email.value;
  const message = form.message.value;

  const subject = encodeURIComponent(`Portfolio contact from ${name}`);
  const body = encodeURIComponent(`${message}\n\nFrom: ${name} (${email})`);
  window.location.href = `mailto:${CONTACT_EMAIL}?subject=${subject}&body=${body}`;

  const status = document.getElementById("contactStatus");
  status.classList.remove("hidden");
  form.reset();
});
