// ---- Config ----
const CONTACT_EMAIL = "MalwandlaHlongwaneICT@outlook.com";
const DEFAULT_PROFILE = "software";

const ICONS = {
  code: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
  smartphone: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>',
  database: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/></svg>',
  wrench: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a4 4 0 1 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.8 2.8-2-2z"/></svg>',
  globe: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20z"/></svg>',
  github: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.7.5.5 5.7.5 12c0 5 3.3 9.3 7.9 10.8.6.1.8-.3.8-.6v-2.1c-3.2.7-3.9-1.4-3.9-1.4-.5-1.3-1.2-1.7-1.2-1.7-1-.7.1-.7.1-.7 1.1.1 1.7 1.2 1.7 1.2 1 1.7 2.6 1.2 3.2.9.1-.7.4-1.2.7-1.5-2.6-.3-5.3-1.3-5.3-5.7 0-1.3.5-2.3 1.2-3.1-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.3 1.2 1-.3 2-.4 3-.4s2 .1 3 .4c2.3-1.5 3.3-1.2 3.3-1.2.6 1.6.2 2.8.1 3.1.8.8 1.2 1.9 1.2 3.1 0 4.4-2.7 5.4-5.3 5.7.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6 4.6-1.5 7.9-5.8 7.9-10.8C23.5 5.7 18.3.5 12 .5z"/></svg>',
  external: '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>'
};

// Generic tool/software icon grid (mockup Phase 5) — not profile-specific.
const TOOL_STACK = [
  "Java", "JavaScript", "PHP", "SQL", "HTML5", "CSS3",
  "MySQL", "Node.js", "Express", "Git", "GitHub",
  "VS Code", "Android Studio", "Tailwind", "Postman"
];

// ---- Real contact / social info ----
const SOCIAL_LINKS = {
  github: "https://github.com/Malwandla21-ict",
  linkedin: "https://www.linkedin.com/in/malwandla-hlongwane-8484603a3"
};

// ---- State ----
let profiles = {};
let projectsCatalog = {};
let activeProfile = DEFAULT_PROFILE;

// ---- Boot ----
document.getElementById("year").textContent = new Date().getFullYear();
wireContactLinks();
renderToolStack();

fetch("data/profiles.json")
  .then((res) => res.json())
  .then((data) => {
    profiles = data.profiles;
    projectsCatalog = data.projectsCatalog;
    renderProfileCards();
    setActiveProfile(DEFAULT_PROFILE);
    updateStats();
  })
  .catch((err) => {
    console.error("Failed to load profiles.json", err);
  });

// ---- Contact / social links ----
function wireContactLinks() {
  const githubLink = document.getElementById("socialGithub");
  const linkedinLink = document.getElementById("socialLinkedin");
  const emailLink = document.getElementById("socialEmail");
  if (githubLink) githubLink.href = SOCIAL_LINKS.github;
  if (linkedinLink) linkedinLink.href = SOCIAL_LINKS.linkedin;
  if (emailLink) emailLink.href = `mailto:${CONTACT_EMAIL}`;
}

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
  renderProjects(profile.projects || []);

  document.querySelectorAll(".download-cv-btn").forEach((btn) => {
    btn.onclick = () => downloadCv(profile.cv);
  });
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

function renderToolStack() {
  const container = document.getElementById("toolStack");
  if (!container) return;
  container.innerHTML = TOOL_STACK.map(
    (tool) => `
      <div class="bg-card border border-white/5 rounded-lg py-3 px-2 text-center text-xs text-muted hover:text-text hover:border-white/15 transition">
        ${tool}
      </div>
    `
  ).join("");
}

// ---- Projects ----
function renderProjects(projectIds) {
  const container = document.getElementById("projectsGrid");
  if (!container) return;

  if (!projectIds.length) {
    container.innerHTML = `<p class="text-muted text-sm">No projects tagged to this profile yet.</p>`;
    return;
  }

  container.innerHTML = projectIds
    .map((id) => projectsCatalog[id])
    .filter(Boolean)
    .map((project) => {
      const media = project.image
        ? `<img src="${project.image}" alt="${project.name}" class="w-full h-40 object-cover rounded-lg mb-4 border border-white/5" />`
        : `<div class="w-full h-40 rounded-lg mb-4 border border-white/5 bg-bg flex items-center justify-center text-muted text-xs">No preview image yet</div>`;

      const tags = project.tech
        .map((t) => `<span class="bg-bg px-2 py-1 rounded border border-white/10">${t}</span>`)
        .join("");

      const demoLink = project.demo
        ? `<a href="${project.demo}" target="_blank" rel="noopener" class="text-primary hover:underline inline-flex items-center gap-1">Live Demo ${ICONS.external}</a>`
        : "";

      const githubLink = project.github
        ? `<a href="${project.github}" target="_blank" rel="noopener" class="text-primary hover:underline inline-flex items-center gap-1">${ICONS.github} GitHub</a>`
        : "";

      return `
        <div class="bg-card rounded-xl border border-white/5 p-5 fade-in">
          ${media}
          <div class="flex items-center justify-between gap-2 mb-2">
            <p class="font-display font-semibold text-sm">${project.name}</p>
            <span class="text-[10px] uppercase tracking-wide text-secondary border border-secondary/30 rounded-full px-2 py-0.5 shrink-0">${project.status}</span>
          </div>
          <p class="text-muted text-sm mb-3">${project.description}</p>
          <div class="flex flex-wrap gap-2 text-xs mb-4">${tags}</div>
          <div class="flex gap-4 text-sm">${githubLink}${demoLink}</div>
        </div>
      `;
    })
    .join("");
}

// ---- Stats ----
function updateStats() {
  const stats = { projects: 3, technologies: 10, certificates: 0, years: 2, repos: 3 };
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
