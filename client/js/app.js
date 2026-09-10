// ---- Config ----
const CONTACT_EMAIL = "your.email@example.com"; // TODO: replace with your real address
const DEFAULT_PROFILE = "software";

const ICONS = {
  code: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
  smartphone: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>',
  database: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/></svg>',
  wrench: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a4 4 0 1 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.8 2.8-2-2z"/></svg>',
  globe: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20z"/></svg>'
};

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
    const card = document.createElement("button");
    card.className =
      "profile-card bg-card border border-white/10 rounded-xl p-4";
    card.dataset.key = key;
    card.innerHTML = `
      <span class="check-badge absolute -top-2 -right-2 w-5 h-5 rounded-full bg-primary items-center justify-center">
        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
      </span>
      <span class="text-primary">${ICONS[profile.icon] || ""}</span>
      <p class="font-display font-semibold text-sm mt-3">${profile.label}</p>
      <p class="text-muted text-xs mt-1 leading-snug">${profile.cardDescription}</p>
    `;
    card.addEventListener("click", () => setActiveProfile(key));
    container.appendChild(card);
  });
}

function setActiveProfile(key) {
  if (!profiles[key]) return;
  activeProfile = key;

  document.querySelectorAll(".profile-card").forEach((el) => {
    el.classList.toggle("active", el.dataset.key === key);
  });

  const profile = profiles[key];

  const summaryEl = document.getElementById("profileSummary");
  summaryEl.classList.remove("fade-in");
  void summaryEl.offsetWidth;
  summaryEl.textContent = profile.summary;
  summaryEl.classList.add("fade-in");

  renderSkills(profile.skills);

  document.getElementById("downloadCvBtn").onclick = () => downloadCv(profile.cv);
}

function downloadCv(path) {
  const link = document.createElement("a");
  link.href = path;
  link.download = "";
  link.click();
}

// ---- Skills ----
function renderSkills(skills) {
  const container = document.getElementById("skillsList");
  if (!container) return;
  container.innerHTML = "";
  skills.forEach((skill) => {
    const card = document.createElement("div");
    card.className = "bg-card border border-white/5 rounded-xl p-4 fade-in";
    card.innerHTML = `
      <div class="flex justify-between text-sm mb-2">
        <span>${skill.name}</span>
        <span class="text-muted font-mono">${skill.level}%</span>
      </div>
      <div class="skill-bar-track">
        <div class="skill-bar-fill" style="width:${skill.level}%"></div>
      </div>
    `;
    container.appendChild(card);
  });
}

// ---- Stats (placeholder — wire to real data / GitHub API later) ----
function updateStats() {
  const stats = { projects: 1, technologies: 10, certificates: 0, years: 2, repos: 3 };
  Object.entries(stats).forEach(([key, value]) => {
    const el = document.querySelector(`[data-stat="${key}"]`);
    if (el) el.textContent = value;
  });
}

// ---- Theme toggle (light/dark) ----
document.getElementById("themeToggle").addEventListener("click", () => {
  document.body.classList.toggle("light");
});

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
