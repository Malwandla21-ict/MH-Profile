#!/usr/bin/env python3
"""
Generates the static role pages (software.html, android.html, database.html,
helpdesk.html, networking.html) and the index.html landing page from a
single data source: client/data/profiles.json.

Why this exists: hand-writing five near-identical pages means every future
edit (a new skill, a fixed CV path, a new project) has to be repeated five
times and will eventually drift out of sync. This script is the single
source of truth for the page *structure* — profiles.json is the single
source of truth for the *content*. Edit the JSON, re-run this script.

Usage:
    python3 generate_pages.py
Run from anywhere; paths are resolved relative to this file.
"""
import json
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # client/
DATA_PATH = ROOT / "data" / "profiles.json"
OUT_DIR = ROOT


def cv_href(rel_path):
    """profiles.json stores CV paths as 'cv/Whatever.pdf' relative to the repo
    root (cv/ is a sibling of client/, per README's documented folder
    structure). Every generated page lives inside client/, one level below
    the repo root, so the actual href needs to climb out first."""
    return f"../{rel_path}"

# ---------------------------------------------------------------------------
# Icon system — one consistent minimal line-icon language (24x24, stroke 2,
# currentColor). No emoji, no third-party brand logos: tools are grouped by
# category (language / database / runtime / versioning / generic tool /
# networking) rather than given one bespoke logo redraw each.
# ---------------------------------------------------------------------------
ICONS = {
    "code": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
    "smartphone": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>',
    "database": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/></svg>',
    "wrench": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a4 4 0 1 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.8 2.8-2-2z"/></svg>',
    "globe": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20z"/></svg>',
    "github": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.7.5.5 5.7.5 12c0 5 3.3 9.3 7.9 10.8.6.1.8-.3.8-.6v-2.1c-3.2.7-3.9-1.4-3.9-1.4-.5-1.3-1.2-1.7-1.2-1.7-1-.7.1-.7.1-.7 1.1.1 1.7 1.2 1.7 1.2 1 1.7 2.6 1.2 3.2.9.1-.7.4-1.2.7-1.5-2.6-.3-5.3-1.3-5.3-5.7 0-1.3.5-2.3 1.2-3.1-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.3 1.2 1-.3 2-.4 3-.4s2 .1 3 .4c2.3-1.5 3.3-1.2 3.3-1.2.6 1.6.2 2.8.1 3.1.8.8 1.2 1.9 1.2 3.1 0 4.4-2.7 5.4-5.3 5.7.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6 4.6-1.5 7.9-5.8 7.9-10.8C23.5 5.7 18.3.5 12 .5z"/></svg>',
    "linkedin": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20.5 2h-17A1.5 1.5 0 0 0 2 3.5v17A1.5 1.5 0 0 0 3.5 22h17a1.5 1.5 0 0 0 1.5-1.5v-17A1.5 1.5 0 0 0 20.5 2zM8 19H5v-9h3zM6.5 8.7A1.7 1.7 0 1 1 8.2 7a1.7 1.7 0 0 1-1.7 1.7zM19 19h-3v-4.6c0-1.1 0-2.5-1.5-2.5s-1.8 1.2-1.8 2.4V19h-3v-9h2.9v1.3a3.1 3.1 0 0 1 2.8-1.5c3 0 3.6 2 3.6 4.5z"/></svg>',
    "mail": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16v16H4z"/><path d="m4 6 8 7 8-7"/></svg>',
    "external": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>',
    "box": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 8l-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/></svg>',
    "branch": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="6" y1="3" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg>',
    "network": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="4" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><path d="M12 6v6"/><path d="M12 12L5 16"/><path d="M12 12l7 4"/></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 15V3M7 10l5 5 5-5M5 21h14"/></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>',
    "router": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="10" width="18" height="7" rx="1.5"/><path d="M8 10V7M16 10V7"/><circle cx="8" cy="13.5" r=".6" fill="currentColor" stroke="none"/><circle cx="12" cy="13.5" r=".6" fill="currentColor" stroke="none"/></svg>',
    "monitor": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M8 20h8M12 16v4"/></svg>',
    "server": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="3" width="16" height="6" rx="1"/><rect x="4" y="15" width="16" height="6" rx="1"/><circle cx="7.5" cy="6" r=".6" fill="currentColor" stroke="none"/><circle cx="7.5" cy="18" r=".6" fill="currentColor" stroke="none"/></svg>',
    "cloud": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 18H6.5a4 4 0 1 1 .8-7.9 5 5 0 0 1 9.6 1.7A3.5 3.5 0 0 1 17 18z"/></svg>',
    "moon": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
    "sun": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "chevron-left": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>',
    "chevron-right": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>',
    "arrow-right": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
    "expand": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3H5a2 2 0 0 0-2 2v3M16 3h3a2 2 0 0 1 2 2v3M8 21H5a2 2 0 0 1-2-2v-3M16 21h3a2 2 0 0 0 2-2v-3"/></svg>',
    "close": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    "menu": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg>',
    "instagram": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>',
    "tiktok": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M16.5 3c.4 2.2 1.9 3.7 4 4v3c-1.5 0-2.9-.4-4-1.2v6.3a5.6 5.6 0 1 1-5.6-5.6c.3 0 .6 0 .9.1v3.1a2.5 2.5 0 1 0 1.7 2.4V3h3z"/></svg>',
    "phone": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .3 2 .6 3a2 2 0 0 1-.4 2.1L8 10a16 16 0 0 0 6 6l1.2-1.3a2 2 0 0 1 2.1-.4c1 .3 2 .5 3 .6a2 2 0 0 1 1.7 2z"/></svg>',
    "map-pin": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 6-9 12-9 12s-9-6-9-12a9 9 0 1 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
}

# A tiny inline mark (matches the "</>" nav logo) used as the site favicon —
# no separate image asset to keep track of, and it recolors instantly if the
# accent color ever changes since it's generated from the same source file.
FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
    '<rect width="24" height="24" rx="6" fill="#0A84FF"/>'
    '<path d="M9 8 5 12l4 4M15 8l4 4-4 4" stroke="#FAFAFA" stroke-width="2" '
    'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)
FAVICON_HREF = "data:image/svg+xml," + urllib.parse.quote(FAVICON_SVG)

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<meta name="description" content="{description}" />
<link rel="icon" type="image/svg+xml" href="{favicon}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{description}" />
<meta property="og:image" content="images/malwandla-hero.jpg" />
<meta name="twitter:card" content="summary" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {{
    theme: {{
      extend: {{
        colors: {{
          primary: '#0A84FF',
          secondary: '#64D2FF',
          bg: '#0A0A0A',
          card: '#141414',
          text: '#FAFAFA',
          muted: '#A1A1AA'
        }},
        fontFamily: {{
          display: ['Poppins', 'sans-serif'],
          body: ['Inter', 'sans-serif'],
          mono: ['JetBrains Mono', 'monospace']
        }}
      }}
    }}
  }}
</script>
<link rel="stylesheet" href="css/style.css" />
</head>
"""

NAV_LINKS = [
    ("index.html", "Home"),
    ("index.html#about", "About"),
    ("index.html#tracks", "Tracks"),
    ("index.html#contact", "Contact"),
]


def nav_html(cv_href, active_page):
    links = "\n        ".join(
        f'<a href="{href}" class="{"text-text border-b-2 border-primary pb-1 -mb-1" if href.split("#")[0] == active_page else "hover:text-text transition"}">{label}</a>'
        for href, label in NAV_LINKS
    )
    # A separate markup block from the desktop links above — full-width,
    # generously padded rows read far better as a tap target list than the
    # inline row does shrunk down, so it's its own layout rather than a
    # reused one.
    mobile_links = "\n          ".join(
        f'<a href="{href}" class="mobile-nav-link block py-3 text-base font-medium {"text-primary" if href.split("#")[0] == active_page else "text-text"}">{label}</a>'
        for href, label in NAV_LINKS
    )
    return f"""  <header class="sticky top-0 z-40 bg-bg/80 backdrop-blur border-b border-white/5">
    <nav class="max-w-6xl mx-auto flex items-center justify-between px-6 py-4">
      <a href="index.html" class="flex items-center gap-2 font-display font-semibold text-lg shrink-0">
        <span class="text-primary font-mono">&lt;/&gt;</span> Malwandla <span class="font-normal hidden sm:inline">Hlongwane</span>
      </a>
      <div class="hidden md:flex gap-8 text-sm text-muted">
        {links}
      </div>
      <div class="flex items-center gap-2 sm:gap-3">
        <button id="mobileNavToggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobileNav" class="md:hidden w-10 h-10 flex items-center justify-center rounded-lg border border-white/10 text-muted hover:text-text transition active:scale-90 shrink-0">
          <span class="menu-icon-open">{ICONS['menu']}</span>
          <span class="menu-icon-close hidden">{ICONS['close']}</span>
        </button>
        <button id="themeToggle" aria-label="Toggle light and dark mode" class="w-10 h-10 flex items-center justify-center rounded-lg border border-white/10 text-muted hover:text-text transition active:scale-90 shrink-0">
          <span class="theme-icon-dark">{ICONS['moon']}</span>
          <span class="theme-icon-light hidden">{ICONS['sun']}</span>
        </button>
        <a href="{cv_href}" download aria-label="Download CV" class="download-cv-btn text-sm font-medium bg-primary hover:bg-primary/90 transition px-3 sm:px-4 py-2 rounded-lg flex items-center gap-2 active:scale-95 shrink-0">
          {ICONS['download']}
          <span class="hidden sm:inline">Download CV</span>
        </a>
      </div>
    </nav>
    <div id="mobileNav" class="mobile-nav-panel md:hidden">
      <div class="mobile-nav-panel-inner border-t border-white/5 bg-bg/95 backdrop-blur px-6">
        {mobile_links}
      </div>
    </div>
  </header>"""


def social_row():
    return f"""      <div class="flex items-center gap-4 mt-6 text-muted">
        <a href="{{github}}" target="_blank" rel="noopener" aria-label="GitHub" class="hover:text-text transition">{ICONS['github']}</a>
        <a href="{{linkedin}}" target="_blank" rel="noopener" aria-label="LinkedIn" class="hover:text-text transition">{ICONS['linkedin']}</a>
        <a href="{{instagram}}" target="_blank" rel="noopener" aria-label="Instagram" class="hover:text-text transition">{ICONS['instagram']}</a>
        <a href="{{tiktok}}" target="_blank" rel="noopener" aria-label="TikTok" class="hover:text-text transition">{ICONS['tiktok']}</a>
        <a href="mailto:{{email}}" aria-label="Email" class="hover:text-text transition">{ICONS['mail']}</a>
      </div>"""


def other_tracks_html(profiles, current_key):
    cards = []
    for key, p in profiles.items():
        if key == current_key:
            continue
        cards.append(
            f"""<a href="{p['page']}" class="track-pill active:scale-95 flex items-center gap-2 bg-card border border-white/10 rounded-lg pl-3 pr-4 py-2 text-sm text-muted hover:text-text hover:border-white/20 transition shrink-0">
          <span class="text-primary">{ICONS[p['icon']]}</span>{p['label']}
        </a>"""
        )
    return "\n        ".join(cards)


def skills_html(skills):
    rows = []
    for i, s in enumerate(skills):
        delay = i * 60
        rows.append(
            f"""<div class="reveal border-b border-white/5 py-5 first:pt-0 last:border-b-0" style="transition-delay:{delay}ms">
          <div class="flex items-baseline justify-between gap-4">
            <p class="font-display text-lg sm:text-xl font-medium">{s['name']}</p>
            <span class="font-mono text-xl sm:text-2xl text-primary shrink-0">{s['level']}%</span>
          </div>
          <div class="skill-bar-track mt-3">
            <div class="skill-bar-fill" data-level="{s['level']}" style="transition-delay:{delay}ms"></div>
          </div>
        </div>"""
        )
    return "\n        ".join(rows)


def tools_html(tool_keys, catalog):
    chips = []
    for key in tool_keys:
        tool = catalog[key]
        chips.append(
            f"""<div class="bg-card border border-white/5 rounded-lg py-3 px-2 text-center text-xs text-muted flex flex-col items-center gap-2">
          <span class="text-primary">{ICONS[tool['icon']]}</span>
          {tool['label']}
        </div>"""
        )
    return "\n        ".join(chips)


def section_header_html(number, eyebrow, heading):
    """Editorial section header: a small index number + vertical rule beside
    the eyebrow/heading pair, used consistently across every section instead
    of a plain centered heading."""
    return f"""<div class="reveal flex items-start gap-4 sm:gap-6 mb-10">
        <span aria-hidden="true" class="font-mono text-xs sm:text-sm text-primary/50 pt-1 sm:pt-2 shrink-0">{number}</span>
        <div class="flex-1 border-l border-white/10 pl-4 sm:pl-6">
          <p class="text-xs font-semibold text-primary tracking-wide">{eyebrow}</p>
          <h2 class="font-display text-3xl sm:text-4xl font-semibold mt-1 tracking-tight">{heading}</h2>
        </div>
      </div>"""


def flow_steps_html(steps):
    """A minimal numbered-step process diagram — used for each role's
    development/troubleshooting process and the landing page's career-focus
    strip. Horizontal with a connecting line on desktop, stacked on mobile."""
    circles = []
    for i, label in enumerate(steps):
        circles.append(
            f"""<div class="reveal flex-1 flex flex-col items-center text-center gap-3 min-w-[88px]" style="transition-delay:{i * 70}ms">
          <div class="w-10 h-10 rounded-full bg-card border border-primary/30 flex items-center justify-center font-mono text-sm text-primary shrink-0 relative z-10">{i + 1}</div>
          <p class="text-xs sm:text-sm font-medium text-text">{label}</p>
        </div>"""
        )
    circles_html = "\n          ".join(circles)
    return f"""<div class="relative">
        <div class="hidden md:block absolute top-5 left-[44px] right-[44px] h-px bg-white/10 z-0"></div>
        <div class="flex flex-col md:flex-row md:items-start gap-8 md:gap-2 relative z-10">
          {circles_html}
        </div>
      </div>"""


# A small fixed network diagram for the Networking track — hand-placed nodes
# (percent-based so it stays responsive) connected by lines, with a click/hover
# info panel. Not data-driven like the rest of the site since it's one bespoke
# diagram, not a repeated pattern.
TOPOLOGY_NODES = [
    {"id": "cloud", "icon": "cloud", "name": "Internet", "ip": "N/A", "role": "External network / WAN uplink.", "top": 8, "left": 50},
    {"id": "router", "icon": "router", "name": "Router", "ip": "192.168.1.1", "role": "Routes traffic between the LAN and the internet; handles NAT and DHCP.", "top": 38, "left": 50},
    {"id": "switch", "icon": "network", "name": "Switch", "ip": "192.168.1.2", "role": "Connects devices within the LAN and forwards traffic by MAC address.", "top": 68, "left": 50},
    {"id": "pc1", "icon": "monitor", "name": "Workstation A", "ip": "192.168.1.10", "role": "Staff workstation on VLAN 10.", "top": 94, "left": 15},
    {"id": "pc2", "icon": "monitor", "name": "Workstation B", "ip": "192.168.1.11", "role": "Staff workstation on VLAN 10.", "top": 94, "left": 50},
    {"id": "server", "icon": "server", "name": "Server", "ip": "192.168.1.20", "role": "Hosts shared files and internal services on VLAN 20.", "top": 94, "left": 85},
]
TOPOLOGY_LINKS = [("cloud", "router"), ("router", "switch"), ("switch", "pc1"), ("switch", "pc2"), ("switch", "server")]


def network_topology_html():
    by_id = {n["id"]: n for n in TOPOLOGY_NODES}
    lines = "\n          ".join(
        f'<line x1="{by_id[a]["left"]}%" y1="{by_id[a]["top"]}%" x2="{by_id[b]["left"]}%" y2="{by_id[b]["top"]}%" stroke="currentColor" stroke-width="1.5" class="text-white/15" />'
        for a, b in TOPOLOGY_LINKS
    )
    nodes = "\n          ".join(
        f"""<button type="button" class="topology-node absolute -translate-x-1/2 -translate-y-1/2 w-11 h-11 rounded-full bg-card border border-white/15 flex items-center justify-center text-primary active:scale-90 transition" style="top:{n['top']}%; left:{n['left']}%" data-name="{n['name']}" data-ip="{n['ip']}" data-role="{n['role']}" aria-label="{n['name']}">{ICONS[n['icon']]}</button>"""
        for n in TOPOLOGY_NODES
    )
    return f"""<div class="reveal bg-card/50 border border-white/5 rounded-xl p-6">
        <div class="relative h-72 sm:h-80">
          <svg class="absolute inset-0 w-full h-full" preserveAspectRatio="none">
            {lines}
          </svg>
          {nodes}
        </div>
        <div id="topologyInfo" class="mt-6 bg-bg border border-white/10 rounded-lg p-4 text-sm">
          <p class="text-muted text-xs">Tap or hover a device</p>
          <p class="font-display font-semibold mt-1">Network Topology</p>
        </div>
      </div>"""


# Per-role "signature section" — a small process diagram distinct to that
# track. Networking gets the interactive topology above instead.
ROLE_FLOWS = {
    "software": ("Development Process", ["Requirements", "Design", "Development", "Testing", "Deployment", "Maintenance"]),
    "android": ("Development Process", ["Idea", "Planning", "UI Design", "Development", "Testing", "Deployment"]),
    "database": ("Database Architecture", ["Frontend", "Backend", "API", "Database"]),
    "helpdesk": ("Troubleshooting Process", ["Problem Reported", "Diagnose", "Identify Cause", "Apply Solution", "Test", "Document"]),
}


def gallery_html(images, alt):
    if not images:
        return '<div class="w-full h-48 sm:h-64 rounded-lg border border-white/5 bg-bg flex items-center justify-center text-muted text-xs">No preview image yet</div>'

    controls = ""
    if len(images) > 1:
        # Each dot's actual button is a larger invisible touch target (32px)
        # around a small visible indicator span, so it's comfortable to tap
        # on a phone without the dot row looking oversized.
        dots = "\n            ".join(
            f'<button class="gallery-dot w-8 h-8 flex items-center justify-center active:scale-90" data-i="{i}" aria-label="Screenshot {i + 1}"><span class="w-1.5 h-1.5 rounded-full {"bg-primary" if i == 0 else "bg-white/30"} transition"></span></button>'
            for i in range(len(images))
        )
        controls = f"""
          <button class="gallery-prev active:scale-90 absolute left-1 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-bg/70 backdrop-blur text-text flex items-center justify-center transition" aria-label="Previous screenshot">{ICONS['chevron-left']}</button>
          <button class="gallery-next active:scale-90 absolute right-1 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-bg/70 backdrop-blur text-text flex items-center justify-center transition" aria-label="Next screenshot">{ICONS['chevron-right']}</button>
          <div class="gallery-dots absolute bottom-0.5 left-1/2 -translate-x-1/2 flex">
            {dots}
          </div>"""

    # Every gallery (even single-image) is click-to-expand — a shared
    # data-images attribute lets the one lightbox in site.js handle all of
    # them, and images render uncropped (object-contain) so nothing is cut
    # off, with the bg-bg backdrop filling any letterboxing.
    return f"""<div class="project-media gallery relative w-full h-48 sm:h-64 rounded-lg border border-white/5 overflow-hidden bg-bg cursor-zoom-in" data-images='{json.dumps(images)}' data-alt="{alt}" data-current-index="0">
          <img src="{images[0]}" alt="{alt}" class="gallery-img w-full h-full object-contain" />
          {controls}
          <span class="expand-hint hidden sm:flex absolute top-2 right-2 w-7 h-7 rounded-full bg-bg/70 backdrop-blur text-text items-center justify-center opacity-0 transition">{ICONS['expand']}</span>
        </div>"""


def project_card_html(project, i):
    media = gallery_html(project["images"], project["name"])
    tags = "\n            ".join(
        f'<span class="bg-bg px-2 py-1 rounded border border-white/10">{t}</span>' for t in project["tech"]
    )
    demo = (
        f'<a href="{project["demo"]}" target="_blank" rel="noopener" class="text-primary hover:underline inline-flex items-center gap-1">Live Demo {ICONS["external"]}</a>'
        if project["demo"]
        else ""
    )
    github = (
        f'<a href="{project["github"]}" target="_blank" rel="noopener" class="text-primary hover:underline inline-flex items-center gap-1">{ICONS["github"]} GitHub</a>'
        if project["github"]
        else ""
    )
    # Alternating image/text sides instead of a symmetric card grid — an
    # editorial "zig-zag" feature layout, full width per project.
    reverse = "md:flex-row-reverse" if i % 2 else "md:flex-row"
    return f"""<div class="reveal flex flex-col {reverse} gap-8 md:gap-14 items-center" style="transition-delay:{i * 80}ms">
          <div class="w-full md:w-1/2">
            {media}
          </div>
          <div class="w-full md:w-1/2">
            <div class="flex items-center justify-between gap-2 mb-3">
              <p class="font-display text-2xl sm:text-3xl font-semibold">{project['name']}</p>
              <span class="text-[10px] uppercase tracking-wide text-secondary border border-secondary/30 rounded-lg px-2 py-0.5 shrink-0">{project['status']}</span>
            </div>
            <p class="text-muted leading-relaxed mb-4">{project['description']}</p>
            <div class="flex flex-wrap gap-2 text-xs mb-6">
              {tags}
            </div>
            <div class="flex gap-4 text-sm">{github}{demo}</div>
          </div>
        </div>"""


def summary_band_html(site, cv_href):
    return f"""<div class="reveal grid sm:grid-cols-2 lg:grid-cols-[1fr_1fr_1fr_1.3fr] gap-4">
      <div class="bg-card rounded-xl border border-white/5 p-5">
        <p class="text-xs font-semibold text-primary tracking-wide mb-3">EXPERIENCE</p>
        <p class="font-display font-semibold text-sm">{site['experience']['status']}</p>
        <p class="text-muted text-xs mt-1">{site['experience']['detail']}</p>
      </div>
      <div class="bg-card rounded-xl border border-white/5 p-5">
        <p class="text-xs font-semibold text-primary tracking-wide mb-3">EDUCATION</p>
        <p class="font-display font-semibold text-sm">{site['education']['qualification']}</p>
        <p class="text-muted text-xs mt-1">{site['education']['institution']} · {site['education']['status']}</p>
      </div>
      <div class="bg-card rounded-xl border border-white/5 p-5">
        <p class="text-xs font-semibold text-primary tracking-wide mb-3">CERTIFICATES</p>
        <p class="font-display font-semibold text-sm">{site['certificates']['status']}</p>
        <p class="text-muted text-xs mt-1">{site['certificates']['detail']}</p>
      </div>
      <div class="bg-card rounded-xl border border-primary/30 p-5 flex flex-col">
        <p class="text-xs font-semibold text-primary tracking-wide mb-3">DOWNLOAD CV</p>
        <p class="text-muted text-xs mb-4 flex-1">The CV tailored to this track.</p>
        <a href="{cv_href}" download class="download-cv-btn active:scale-95 bg-primary hover:bg-primary/90 transition px-4 py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-2">
          {ICONS['download']}
          Download CV
        </a>
      </div>
    </div>"""


def quick_facts_html(site):
    return f"""<div class="bg-card rounded-xl border border-white/5 p-6 text-sm space-y-3">
        <p><span class="text-muted block text-xs">Name</span>{site['name']}</p>
        <p><span class="text-muted block text-xs">Location</span>{site['location']}</p>
        <p><span class="text-muted block text-xs">Email</span>{site['email']}</p>
        <p><span class="text-muted block text-xs">Phone</span>{site['phone']}</p>
        <p><span class="text-muted block text-xs">Availability</span>{site['availability']}</p>
      </div>"""


def contact_info_row_html(icon, label, value, href=None):
    inner = f"""<span class="w-10 h-10 rounded-full bg-bg flex items-center justify-center text-primary shrink-0">{ICONS[icon]}</span>
        <div class="min-w-0">
          <p class="text-xs text-muted">{label}</p>
          <p class="font-medium truncate">{value}</p>
        </div>"""
    classes = "flex items-center gap-4 bg-card border border-white/5 rounded-xl p-4"
    if href:
        return f'''<a href="{href}" class="{classes} hover:border-white/20 transition">
        {inner}
      </a>'''
    return f'''<div class="{classes}">
        {inner}
      </div>'''


def contact_section_html(number, site):
    phone_tel = "tel:+27" + "".join(ch for ch in site["phone"] if ch.isdigit())[1:]
    social = social_row().format(
        github=site["github"], linkedin=site["linkedin"],
        instagram=site["instagram"], tiktok=site["tiktok"], email=site["email"],
    )
    info_cards = "\n      ".join([
        contact_info_row_html("mail", "Email", site["email"], href=f"mailto:{site['email']}"),
        contact_info_row_html("phone", "Phone", site["phone"], href=phone_tel),
        contact_info_row_html("map-pin", "Location", site["location"]),
        contact_info_row_html("check", "Availability", site["availability"]),
    ])
    return f"""  <section id="contact" class="max-w-6xl mx-auto px-6 py-14 border-t border-white/5">
    {section_header_html(number, "GET IN TOUCH", "Contact")}
    <div class="reveal grid md:grid-cols-2 gap-8">
      <div class="space-y-4">
        {info_cards}
        <div class="pt-2">
          <p class="text-xs text-muted mb-3">Find me elsewhere</p>
{social}
        </div>
      </div>
      <form id="contactForm" class="bg-card border border-white/5 rounded-xl p-6 space-y-4 h-fit">
        <!-- Submits via Web3Forms (web3forms.com) — no backend of my own needed.
             Get a free access key at web3forms.com and drop it into
             site.web3formsAccessKey in profiles.json, then re-run the generator. -->
        <input type="hidden" name="access_key" value="{site['web3formsAccessKey']}" />
        <input type="hidden" name="subject" value="New message from your portfolio contact form" />
        <input type="checkbox" name="botcheck" class="hidden" style="display:none" tabindex="-1" autocomplete="off" />
        <input type="text" name="name" placeholder="Your name" required class="w-full bg-bg border border-white/10 rounded-lg px-4 py-3 text-sm outline-none focus:border-primary" />
        <input type="email" name="email" placeholder="Your email" required class="w-full bg-bg border border-white/10 rounded-lg px-4 py-3 text-sm outline-none focus:border-primary" />
        <textarea name="message" placeholder="Message" rows="4" required class="w-full bg-bg border border-white/10 rounded-lg px-4 py-3 text-sm outline-none focus:border-primary"></textarea>
        <button type="submit" class="bg-primary hover:bg-primary/90 transition px-6 py-3 rounded-lg font-medium active:scale-95">Send Message</button>
        <p id="contactStatus" class="text-sm text-secondary hidden" role="status"></p>
      </form>
    </div>
  </section>"""


def footer_html():
    return """  <footer class="border-t border-white/5 py-8 px-6 flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-4 text-center text-muted text-xs">
    <span>Built by Malwandla Hlongwane · <span id="year"></span></span>
    <span class="hidden sm:inline text-white/15">|</span>
    <span class="flex items-center gap-4">
      <a href="privacy.html" class="hover:text-text transition">Privacy Policy</a>
      <a href="terms.html" class="hover:text-text transition">Terms &amp; Conditions</a>
    </span>
  </footer>"""


def lightbox_html():
    """One shared full-image viewer per page — every project-media thumbnail
    (single or multi-image) opens into this on click. site.js wires it up."""
    return f"""  <div id="lightbox" class="fixed inset-0 z-50 hidden items-center justify-center bg-black/90 backdrop-blur-sm p-4 sm:p-10">
    <button id="lightboxClose" type="button" class="absolute top-4 right-4 sm:top-6 sm:right-6 w-11 h-11 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center transition active:scale-90" aria-label="Close">{ICONS['close']}</button>
    <button id="lightboxPrev" type="button" class="absolute left-2 sm:left-6 top-1/2 -translate-y-1/2 w-11 h-11 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center transition active:scale-90" aria-label="Previous image">{ICONS['chevron-left']}</button>
    <img id="lightboxImg" src="" alt="" class="gallery-img max-w-full max-h-full object-contain rounded-lg" />
    <button id="lightboxNext" type="button" class="absolute right-2 sm:right-6 top-1/2 -translate-y-1/2 w-11 h-11 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center transition active:scale-90" aria-label="Next image">{ICONS['chevron-right']}</button>
  </div>"""


# ---------------------------------------------------------------------------
# Role page
# ---------------------------------------------------------------------------
def render_role_page(key, profile, site, tools_catalog, projects_catalog, all_profiles):
    track_index = list(all_profiles.keys()).index(key) + 1
    projects = [projects_catalog[pid] for pid in profile["projects"] if pid in projects_catalog]
    projects_html = '<div class="space-y-16 md:space-y-20">' + "\n        ".join(
        project_card_html(p, i) for i, p in enumerate(projects)
    ) + "</div>" if projects else (
        '<p class="text-muted text-sm">No projects tagged to this track yet.</p>'
    )

    if key == "networking":
        signature_title, signature_html = "Network Topology", network_topology_html()
    else:
        signature_title, steps = ROLE_FLOWS[key]
        signature_html = flow_steps_html(steps)

    social = social_row().format(github=site["github"], linkedin=site["linkedin"], instagram=site["instagram"], tiktok=site["tiktok"], email=site["email"])

    body = f"""{HEAD.format(title=f"{profile['headline']} · Malwandla Hlongwane", description=profile['tagline'], favicon=FAVICON_HREF)}
<body class="bg-bg text-text font-body">

{nav_html(cv_href(profile['cv']), profile['page'])}

  <!-- HERO -->
  <section id="hero" class="relative max-w-6xl mx-auto px-6 pt-14 pb-10 grid md:grid-cols-[3fr_2fr] gap-10 items-center">
    <span aria-hidden="true" class="hidden md:block absolute top-0 right-6 text-[160px] font-display font-bold text-white/[0.04] leading-none select-none pointer-events-none z-0">0{track_index}</span>
    <div class="relative z-10">
      <span class="inline-flex items-center gap-2 text-xs bg-card border border-white/10 rounded-lg px-3 py-1.5 text-muted">
        <span class="text-primary">{ICONS[profile['icon']]}</span>{profile['headline']}
      </span>
      <h1 class="font-display text-5xl sm:text-6xl font-bold mt-5 leading-[1.05] tracking-tight">
        {site['firstName']}<br />
        <span class="text-primary">{site['lastName']}</span>
      </h1>
      <p class="mt-4 text-muted max-w-md">{profile['tagline']}</p>

{social}
    </div>

    <div class="relative z-10 flex justify-center md:justify-end">
      <div class="w-64 h-72 rounded-2xl bg-card border border-white/10 overflow-hidden relative">
        <img src="images/malwandla-hero.jpg" alt="{site['name']}" class="w-full h-full object-cover" />
        <span class="absolute bottom-3 left-3 w-3 h-3 rounded-full bg-secondary border-2 border-bg"></span>
      </div>
      <div class="hidden md:block absolute -bottom-6 -left-6 bg-card border border-white/10 rounded-xl p-4 font-mono text-[11px] leading-relaxed shadow-xl w-56">
        <p class="text-primary">const <span class="text-secondary">track</span> = {{</p>
        <p class="pl-3 text-muted">role: <span class="text-text">'{profile['headline']}'</span>,</p>
        <p class="pl-3 text-muted">status: <span class="text-text">'{site['experience']['status']}'</span></p>
        <p class="text-primary">}};</p>
      </div>
    </div>
  </section>

  <!-- OTHER TRACKS -->
  <section class="max-w-6xl mx-auto px-6 pb-10">
    <p class="text-xs text-muted mb-3">Also open to:</p>
    <div class="flex gap-3 overflow-x-auto pb-1">
        {other_tracks_html(all_profiles, key)}
    </div>
  </section>

  <!-- ABOUT -->
  <section id="about" class="max-w-6xl mx-auto px-6 py-14 border-t border-white/5">
    {section_header_html("01", "ABOUT THIS TRACK", profile['headline'])}
    <div class="reveal grid md:grid-cols-[1.3fr_1fr_1fr] gap-6">
      <div>
        <p class="text-muted leading-relaxed">{profile['summary']}</p>
      </div>
      {quick_facts_html(site)}
      <div class="bg-card rounded-xl border border-white/5 p-5 font-mono text-[12px] leading-relaxed overflow-x-auto">
        <p class="text-muted">&gt; malwandla@portfolio:~$</p>
        <p class="text-primary mt-2">const <span class="text-secondary">malwandla</span> = {{</p>
        <p class="pl-3 text-muted">education: <span class="text-text">'{site['education']['qualification']}'</span>,</p>
        <p class="pl-3 text-muted">focus: <span class="text-text">'{profile['headline']}'</span>,</p>
        <p class="pl-3 text-muted">goal: <span class="text-text">'Make an impact through tech'</span></p>
        <p class="text-primary">}};</p>
      </div>
    </div>
  </section>

  <!-- SKILLS -->
  <section id="skills" class="max-w-6xl mx-auto px-6 py-14 border-t border-white/5">
    {section_header_html("02", "CAPABILITIES", "Technical Skills")}
    <div class="max-w-2xl">
        {skills_html(profile['skills'])}
    </div>

    <h3 class="font-display text-sm font-semibold text-muted mt-10 mb-4 tracking-wide">TOOLS &amp; TECHNOLOGIES</h3>
    <div class="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-3">
        {tools_html(profile['tools'], tools_catalog)}
    </div>
  </section>

  <!-- PROCESS / TOPOLOGY -->
  <section id="process" class="max-w-6xl mx-auto px-6 py-14 border-t border-white/5">
    {section_header_html("03", "HOW I WORK", signature_title)}
    {signature_html}
  </section>

  <!-- PROJECT -->
  <section id="projects" class="max-w-6xl mx-auto px-6 py-14 border-t border-white/5">
    {section_header_html("04", "SELECTED WORK", "Featured Work")}
    {projects_html}
  </section>

  <!-- SUMMARY BAND -->
  <section class="max-w-6xl mx-auto px-6 py-14 border-t border-white/5">
    {summary_band_html(site, cv_href(profile['cv']))}
  </section>

{contact_section_html("05", site)}

{footer_html()}

{lightbox_html()}

  <script src="js/site.js"></script>
</body>
</html>
"""
    return body


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------
def render_landing(site, profiles, projects_catalog):
    total_projects = len(projects_catalog)
    combined_cv = cv_href("cv/CV_Malwandla_Hlongwane_Combined.pdf")
    social = social_row().format(github=site["github"], linkedin=site["linkedin"], instagram=site["instagram"], tiktok=site["tiktok"], email=site["email"])

    cards = []
    for idx, (key, p) in enumerate(profiles.items()):
        offset = "md:mt-6" if idx % 2 else ""
        cards.append(
            f"""<a href="{p['page']}" class="track-card active:scale-95 relative bg-card border border-white/10 rounded-xl p-4 block hover:border-white/20 transition {offset}">
          <span class="text-primary">{ICONS[p['icon']]}</span>
          <p class="font-display font-semibold text-sm mt-3">{p['label']}</p>
          <p class="text-muted text-xs mt-1 leading-snug">{p['cardDescription']}</p>
          <span class="mt-3 text-xs text-primary inline-flex items-center gap-1">View track {ICONS['arrow-right']}</span>
        </a>"""
        )
    cards_html = "\n        ".join(cards)

    landing_description = (
        f"{site['name']}, {site['education']['qualification']} at {site['education']['institution']}. "
        "One ICT graduate, five specializations: software, Android, database, IT support, and networking."
    )
    body = f"""{HEAD.format(title=f"{site['name']} · Portfolio", description=landing_description, favicon=FAVICON_HREF)}
<body class="bg-bg text-text font-body">

{nav_html(combined_cv, 'index.html')}

  <!-- HERO -->
  <section id="hero" class="relative max-w-6xl mx-auto px-6 pt-14 pb-16 grid md:grid-cols-[3fr_2fr] gap-10 items-center">
    <span aria-hidden="true" class="hidden md:block absolute top-0 right-6 text-[180px] font-display font-bold text-white/[0.04] leading-none select-none pointer-events-none z-0">MH</span>
    <div class="relative z-10">
      <h1 class="font-display text-6xl sm:text-7xl font-bold leading-[1.02] tracking-tight">
        {site['firstName']}<br />
        <span class="text-primary">{site['lastName']}</span>
      </h1>
      <p class="mt-4 text-muted">
        Diploma in ICT <span class="text-primary">(Application Development)</span>
      </p>
      <p class="mt-2 text-muted max-w-md">
        One ICT graduate, five specializations. Pick the track that matches what you're hiring for.
      </p>

{social}

      <div class="reveal grid grid-cols-3 gap-3 mt-8">
        <div class="bg-card rounded-xl border border-white/5 py-4 text-center">
          <p class="font-display text-xl font-semibold text-secondary">{total_projects}</p>
          <p class="text-[11px] text-muted mt-1">Projects</p>
        </div>
        <div class="bg-card rounded-xl border border-white/5 py-4 text-center">
          <p class="font-display text-xl font-semibold text-secondary">{len(profiles)}</p>
          <p class="text-[11px] text-muted mt-1">Tracks</p>
        </div>
        <div class="bg-card rounded-xl border border-white/5 py-4 text-center">
          <p class="font-display text-xl font-semibold text-secondary">5</p>
          <p class="text-[11px] text-muted mt-1">CVs Tailored</p>
        </div>
      </div>
    </div>

    <div class="relative z-10 flex justify-center md:justify-end">
      <div class="w-64 h-72 rounded-2xl bg-card border border-white/10 overflow-hidden relative">
        <img src="images/malwandla-hero.jpg" alt="{site['name']}" class="w-full h-full object-cover" />
        <span class="absolute bottom-3 left-3 w-3 h-3 rounded-full bg-secondary border-2 border-bg"></span>
      </div>
      <div class="hidden md:block absolute -bottom-6 -left-6 bg-card border border-white/10 rounded-xl p-4 font-mono text-[11px] leading-relaxed shadow-xl w-56">
        <p class="text-primary">const <span class="text-secondary">developer</span> = {{</p>
        <p class="pl-3 text-muted">passion: <span class="text-text">'Problem solving'</span>,</p>
        <p class="pl-3 text-muted">focus: <span class="text-text">'Full Stack'</span>,</p>
        <p class="pl-3 text-muted">learning: <span class="text-text">'Everyday'</span></p>
        <p class="text-primary">}};</p>
      </div>
    </div>
  </section>

  <!-- TRACKS -->
  <section id="tracks" class="max-w-6xl mx-auto px-6 py-14 border-t border-white/5">
    {section_header_html("01", "EXPLORE MY PROFESSIONAL PROFILES", "Choose a track to see skills, tools, and a dedicated project for that role.")}
    <div class="mt-8 grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {cards_html}
    </div>
  </section>

  <!-- CAREER FOCUS -->
  <section class="max-w-6xl mx-auto px-6 py-14 border-t border-white/5">
    {section_header_html("02", "CAREER FOCUS", "Five tracks, one developer identity.")}
    {flow_steps_html([p["label"] for p in profiles.values()])}
  </section>

  <!-- ABOUT -->
  <section id="about" class="max-w-6xl mx-auto px-6 py-14 border-t border-white/5">
    {section_header_html("03", "ABOUT ME", "Get to know me!")}
    <div class="reveal grid md:grid-cols-[1.3fr_1fr_1fr] gap-6">
      <div>
        <p class="text-muted leading-relaxed">Final-year ICT student at the University of Mpumalanga, comfortable moving between frontend, backend, mobile, databases, and networking. I build across whichever track a role calls for.</p>
        <div class="grid grid-cols-2 gap-y-3 mt-6 text-sm">
          <span class="text-secondary">{ICONS['check']} Problem solver</span>
          <span class="text-secondary">{ICONS['check']} Team player</span>
          <span class="text-secondary">{ICONS['check']} Fast learner</span>
          <span class="text-secondary">{ICONS['check']} Attention to detail</span>
        </div>
      </div>
      {quick_facts_html(site)}
      <div class="bg-card rounded-xl border border-white/5 p-5 font-mono text-[12px] leading-relaxed overflow-x-auto">
        <p class="text-muted">&gt; malwandla@portfolio:~$</p>
        <p class="text-primary mt-2">const <span class="text-secondary">malwandla</span> = {{</p>
        <p class="pl-3 text-muted">education: <span class="text-text">'{site['education']['qualification']}'</span>,</p>
        <p class="pl-3 text-muted">focus: <span class="text-text">'Full Stack Development'</span>,</p>
        <p class="pl-3 text-muted">goal: <span class="text-text">'Make an impact through tech'</span></p>
        <p class="text-primary">}};</p>
        <p class="mt-2 text-secondary">console.log("Let's build something great together");</p>
      </div>
    </div>
  </section>

  <!-- SUMMARY BAND -->
  <section class="max-w-6xl mx-auto px-6 py-14 border-t border-white/5">
    {summary_band_html(site, combined_cv)}
  </section>

{contact_section_html("04", site)}

{footer_html()}

{lightbox_html()}

  <script src="js/site.js"></script>
</body>
</html>
"""
    return body


# ---------------------------------------------------------------------------
# Legal pages (Privacy Policy, Terms & Conditions)
# ---------------------------------------------------------------------------
LEGAL_LAST_UPDATED = "11 September 2026"


def privacy_sections(site):
    return [
        (
            "Overview",
            f"<p>This is the personal portfolio site of {site['name']}, a final-year ICT student "
            "showcasing skills, projects, and CVs across five career tracks. This page explains what "
            "data the site collects and how it's used. There are no user accounts, no purchases, and "
            "no advertising here.</p>",
        ),
        (
            "Contact form",
            "<p>The contact form asks for your name, email address, and message. Submitting it sends "
            "that information directly to my email inbox via <strong>Web3Forms</strong>, a third-party "
            "form-processing service; this site doesn't store submissions in a database of its own. "
            "Web3Forms may retain submission data, including your IP address for spam prevention, for "
            "up to three years under its own policy. See "
            '<a href="https://web3forms.com/privacy" target="_blank" rel="noopener" class="text-primary hover:underline">'
            "Web3Forms's privacy policy</a> for details.</p>",
        ),
        (
            "Fonts",
            "<p>This site loads its typefaces (Poppins, Inter, JetBrains Mono) directly from Google "
            "Fonts. Google states that the Google Fonts service does not use cookies, though requests "
            "for font files go to Google's servers and may include standard technical data such as your "
            'IP address. See <a href="https://fonts.google.com/faq" target="_blank" rel="noopener" '
            'class="text-primary hover:underline">Google Fonts\' FAQ</a> for details.</p>',
        ),
        (
            "Cookies and tracking",
            "<p>This site does not set any cookies, does not use browser local storage, and runs no "
            "analytics or advertising trackers. The only thing that can change between visits is a "
            "light/dark theme preference, which is remembered only for the current browser session and "
            "is never saved anywhere.</p>",
        ),
        (
            "Hosting",
            "<p>This site is hosted on GitHub Pages. Like any web host, GitHub's servers process "
            "standard technical data (such as IP address and browser type) to serve the pages. See "
            '<a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" '
            'target="_blank" rel="noopener" class="text-primary hover:underline">GitHub\'s Privacy Statement</a> '
            "for details.</p>",
        ),
        (
            "Links to other sites",
            "<p>This site links out to GitHub, LinkedIn, Instagram, TikTok, and live project demos. "
            "Those sites have their own privacy practices, which this policy doesn't cover.</p>",
        ),
        (
            "Contact",
            f'<p>Questions about this policy can be sent to <a href="mailto:{site["email"]}" '
            f'class="text-primary hover:underline">{site["email"]}</a>.</p>',
        ),
    ]


def terms_sections(site):
    return [
        (
            "About this site",
            f"<p>This site is the personal portfolio of {site['name']} (“I”, “me”), "
            "built to showcase skills, projects, and CVs to potential employers and collaborators. It's "
            "provided for informational purposes and isn't a commercial product or service.</p>",
        ),
        (
            "Content and ownership",
            "<p>Project write-ups, CVs, and the site's design and code are mine unless stated otherwise. "
            "Source code for individual projects linked out to GitHub follows that repository's own "
            "license, where one is provided.</p>",
        ),
        (
            "No warranty",
            '<p>This site is provided "as is." I’ve done my best to keep it accurate and available, '
            "but I don't guarantee it will be error-free, uninterrupted, or fit for any particular "
            "purpose.</p>",
        ),
        (
            "External links",
            "<p>Links to GitHub, LinkedIn, Instagram, TikTok, and live project demos lead to "
            "third-party sites I don't control, and I'm not responsible for their content.</p>",
        ),
        (
            "CV downloads",
            "<p>CVs on this site are provided for recruitment and professional review. Please don't "
            "redistribute or repost them without asking first.</p>",
        ),
        (
            "Changes to these terms",
            "<p>I may update this page as the site changes. Continuing to use the site after an update "
            "means you accept the current version.</p>",
        ),
        (
            "Contact",
            f'<p>Questions about these terms can be sent to <a href="mailto:{site["email"]}" '
            f'class="text-primary hover:underline">{site["email"]}</a>.</p>',
        ),
    ]


def legal_page_html(page_file, title, sections, site):
    combined_cv = cv_href("cv/CV_Malwandla_Hlongwane_Combined.pdf")
    body_sections = "\n\n".join(
        f"""    <div class="reveal mb-10 last:mb-0">
      <h2 class="font-display text-xl font-semibold mb-3">{heading}</h2>
      <div class="text-muted leading-relaxed text-sm sm:text-base space-y-3">
        {content}
      </div>
    </div>"""
        for heading, content in sections
    )
    description = f"{title} for {site['name']}'s portfolio site."
    return f"""{HEAD.format(title=f"{title} · {site['name']}", description=description, favicon=FAVICON_HREF)}
<body class="bg-bg text-text font-body">

{nav_html(combined_cv, page_file)}

  <section class="max-w-3xl mx-auto px-6 pt-14 pb-16">
    <p class="text-xs text-muted mb-3">Last updated {LEGAL_LAST_UPDATED}</p>
    <h1 class="font-display text-4xl sm:text-5xl font-semibold tracking-tight mb-10">{title}</h1>

{body_sections}

  </section>

{footer_html()}

  <script src="js/site.js"></script>
</body>
</html>
"""


def main():
    data = json.loads(DATA_PATH.read_text())
    site = data["site"]
    tools_catalog = data["toolsCatalog"]
    projects_catalog = data["projectsCatalog"]
    profiles = data["profiles"]

    for key, profile in profiles.items():
        html = render_role_page(key, profile, site, tools_catalog, projects_catalog, profiles)
        out_path = OUT_DIR / profile["page"]
        out_path.write_text(html)
        print(f"wrote {out_path.relative_to(OUT_DIR.parent)}")

    landing_html = render_landing(site, profiles, projects_catalog)
    (OUT_DIR / "index.html").write_text(landing_html)
    print(f"wrote {(OUT_DIR / 'index.html').relative_to(OUT_DIR.parent)}")

    privacy_html = legal_page_html("privacy.html", "Privacy Policy", privacy_sections(site), site)
    (OUT_DIR / "privacy.html").write_text(privacy_html)
    print(f"wrote {(OUT_DIR / 'privacy.html').relative_to(OUT_DIR.parent)}")

    terms_html = legal_page_html("terms.html", "Terms & Conditions", terms_sections(site), site)
    (OUT_DIR / "terms.html").write_text(terms_html)
    print(f"wrote {(OUT_DIR / 'terms.html').relative_to(OUT_DIR.parent)}")


if __name__ == "__main__":
    main()
