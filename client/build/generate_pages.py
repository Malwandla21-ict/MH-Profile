#!/usr/bin/env python3
"""
Builds the portfolio pages from one data file: client/data/profiles.json.

  index.html     homepage. Holds BOTH design directions: light ("A") and
                 dark ("B"). The visitor's light/dark setting (or the toggle)
                 decides which one shows.
  track.html     all five career tracks on one page (track.html?t=android ...)
  privacy.html   legal pages, same look
  terms.html
  software.html, android.html, ...  tiny redirects to track.html?t=<key>,
                 so old links people saved still work.

Edit profiles.json, then run:
    python3 generate_pages.py
(Run it from anywhere; paths are worked out relative to this file.)

Motion comes from js/fx.js (straight from the design, unchanged) and
behaviour from js/main.js. Styles live in css/site.css.
"""
import json
import urllib.parse
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # client/
DATA_PATH = ROOT / "data" / "profiles.json"
OUT_DIR = ROOT
YEAR = 2026
LEGAL_LAST_UPDATED = "1 October 2026"

A_ACCENT = "oklch(0.62 0.17 148)"
B_ACCENT = "oklch(0.86 0.17 128)"
A_MONO = "font-family:'Geist Mono', monospace;"
B_MONO = "font-family:'JetBrains Mono', monospace;"
NUM_WORDS = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
             "Eleven", "Twelve"]


def e(s):
    """Escape text for HTML."""
    return escape(str(s), quote=True)


def cv_href(rel_path):
    """CVs live in cv/ at the repo root; pages live one level down in client/."""
    return f"../{rel_path}"


def num_word(n):
    return NUM_WORDS[n] if n < len(NUM_WORDS) else str(n)


# ---------------------------------------------------------------------------
# <head>
# ---------------------------------------------------------------------------
FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<circle cx="16" cy="16" r="16" fill="#151511"/>'
    '<text x="16" y="20.2" font-family="ui-monospace,Menlo,monospace" font-size="11" font-weight="600" '
    'fill="#f4f2ec" text-anchor="middle">MH</text>'
    '<circle cx="25.5" cy="24.5" r="3" fill="#3aa65b"/>'
    "</svg>"
)
FAVICON_HREF = "data:image/svg+xml," + urllib.parse.quote(FAVICON_SVG)

# Runs before the page paints, so there's no flash of the wrong theme.
THEME_BOOT = (
    "<script>(function(){var t;try{t=sessionStorage.getItem('mh-theme')}catch(e){}"
    "if(t!=='light'&&t!=='dark'){t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}"
    "document.documentElement.setAttribute('data-theme',t)})();</script>"
)


def head(title, description):
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{e(title)}</title>
<meta name="description" content="{e(description)}" />
<link rel="icon" type="image/svg+xml" href="{FAVICON_HREF}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{e(title)}" />
<meta property="og:description" content="{e(description)}" />
<meta property="og:image" content="images/malwandla-hero.jpg" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="theme-color" content="#f4f2ec" media="(prefers-color-scheme: light)" />
<meta name="theme-color" content="#0c0d0f" media="(prefers-color-scheme: dark)" />
{THEME_BOOT}
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300..800&family=Geist+Mono:wght@400;500&family=Archivo:wdth,wght@62..125,300..900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="css/site.css" />
</head>
"""


def scripts():
    return """<script src="js/fx.js"></script>
<script src="js/main.js"></script>
</body>
</html>
"""


ICON_MOON = ('<svg class="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>')
ICON_SUN = ('<svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 '
            '17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>')


def theme_toggle(extra_style=""):
    return (f'<button type="button" class="theme-toggle" aria-label="Switch theme" style="{extra_style}">'
            f'{ICON_MOON}{ICON_SUN}</button>')


def lightbox_html():
    return """<div class="lightbox" data-lightbox role="dialog" aria-modal="true" aria-label="Image viewer" aria-hidden="true">
  <img src="" alt="Project screenshot, enlarged" />
  <button type="button" class="lb-btn lb-close" aria-label="Close">✕</button>
  <button type="button" class="lb-btn lb-prev" aria-label="Previous image">←</button>
  <button type="button" class="lb-btn lb-next" aria-label="Next image">→</button>
  <div class="lb-count"></div>
</div>
"""


# ---------------------------------------------------------------------------
# Project media (screenshots, phone shots, or a "coming soon" cover)
# ---------------------------------------------------------------------------
def zoom_attrs(images, start=0, label="View screenshot"):
    return (f" data-zoom='{e(json.dumps(images))}' data-start=\"{start}\" tabindex=\"0\" role=\"button\" "
            f"aria-label=\"{e(label)}\"")


def cover_html(p):
    return f"""<div class="cover" aria-hidden="true">
<div class="cover-top"><span>Screenshots coming soon</span></div>
<div class="cover-name">{e(p['name'])}</div>
<div></div>
</div>"""


def media_html(p, variant):
    """variant: 'a' (light homepage), 'b' (dark homepage) or 'card' (track page)."""
    imgs = p.get("images") or []
    name = p["name"]
    if not imgs:
        return cover_html(p)
    if p.get("layout") == "phone":
        shots = imgs[:3]
        if variant == "a":
            wrap = "position:absolute; inset:0; display:flex; justify-content:center; align-items:center; gap:14px; padding:24px;"
            img_style = "height:100%; width:auto; min-width:0; border-radius:14px; box-shadow:0 12px 30px rgba(21,21,17,.18);"
        elif variant == "b":
            wrap = "position:absolute; inset:0; display:flex; justify-content:center; align-items:center; gap:12px; padding:28px;"
            img_style = "height:100%; max-height:520px; width:auto; min-width:0; border-radius:14px; box-shadow:0 16px 40px rgba(0,0,0,.5);"
        else:
            wrap, img_style = None, None
        tags = "".join(
            f'<img src="{e(s)}" alt="{e(name)} screenshot {i + 1}" loading="lazy"'
            f'{zoom_attrs(imgs, i, f"Enlarge {name} screenshot {i + 1}")}'
            + (f' style="{img_style}"' if img_style else "") + ">"
            for i, s in enumerate(shots)
        )
        return (f'<div style="{wrap}">{tags}</div>' if wrap else f'<div class="shots">{tags}</div>')
    style = ' style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; object-position:top left;"' \
        if variant in ("a", "b") else ""
    more = f" ({len(imgs)} screenshots)" if len(imgs) > 1 else ""
    return (f'<img src="{e(imgs[0])}" alt="{e(name)} screenshot" loading="lazy"'
            f'{zoom_attrs(imgs, 0, f"Enlarge {name} screenshots{more}")}{style}>')


def status_html(p):
    return '<span class="status">In progress</span>' if p.get("status", "").lower() == "in progress" else ""


def context_html(p):
    return f'<span class="context">{e(p["context"])}</span>' if p.get("context") else ""


def project_links(p, solid_style, ghost_style, wrap_style):
    out = []
    if p.get("github"):
        out.append(f'<a href="{e(p["github"])}" target="_blank" rel="noopener" data-magnetic style="{solid_style}">GitHub ↗</a>')
    if p.get("demo"):
        out.append(f'<a href="{e(p["demo"])}" target="_blank" rel="noopener" data-magnetic style="{ghost_style}">Live demo ↗</a>')
    if not out:
        return ""
    return f'<div style="{wrap_style}">{"".join(out)}</div>'


# ---------------------------------------------------------------------------
# Homepage — Direction A (light)
# ---------------------------------------------------------------------------
def a_nav(site):
    cv = cv_href(site["combinedCv"])
    return f"""<nav aria-label="Main" style="position:sticky; top:0; z-index:50; display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; padding:14px clamp(20px,4vw,56px); background:rgba(244,242,236,.72); backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); border-bottom:1px solid rgba(21,21,17,.08);">
<a href="#top" style="display:flex; align-items:center; gap:10px; font-weight:600; letter-spacing:-.02em; font-size:16px;"><span style="width:32px; height:32px; border-radius:50%; background:#151511; color:#f4f2ec; display:grid; place-items:center; {A_MONO} font-size:11px; font-weight:500;">MH</span>{e(site['firstName'])}</a>
<div class="nav-links" style="display:flex; gap:clamp(14px,2.6vw,36px); {A_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.06em;">
<a href="#work" data-scramble-host data-scramble-hover>Work</a>
<a href="#tracks" data-scramble-host data-scramble-hover>Tracks</a>
<a href="#about" data-scramble-host data-scramble-hover>About</a>
<a href="#contact" data-scramble-host data-scramble-hover>Contact</a>
</div>
<div class="nav-right">{theme_toggle()}<a href="{e(cv)}" target="_blank" rel="noopener" class="a-btn-dark" data-magnetic style="display:flex; align-items:center; gap:8px; padding:10px 18px; border-radius:999px; background:#151511; color:#f4f2ec; font-size:14px; font-weight:500;">Download CV<span style="{A_MONO}">↓</span></a></div>
</nav>"""


def a_hero(site, home):
    rows = [
        ("Based", site["location"].replace(", South Africa", ", South Africa")),
        ("Study", f"{site['education']['qualification']}, {site['education']['institution']}"),
        ("Focus", home["heroFocus"]),
        ("Status", site["experience"]["status"]),
    ]
    dl = ""
    for i, (k, v) in enumerate(rows):
        bottom = " border-bottom:1px solid rgba(21,21,17,.14);" if i == len(rows) - 1 else ""
        dl += (f'<div style="display:grid; grid-template-columns:96px 1fr; gap:16px; padding:14px 0; border-top:1px solid rgba(21,21,17,.14);{bottom}">'
               f'<dt style="{A_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:#5c5a52; padding-top:2px;">{e(k)}</dt>'
               f'<dd style="margin:0;">{e(v)}</dd></div>\n')
    return f"""<header data-sec="hero" data-drift-host style="position:relative; z-index:1; padding:44px clamp(20px,4vw,56px) clamp(72px,10vw,140px);">
<div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; {A_MONO} font-size:12px; color:#5c5a52; text-transform:uppercase; letter-spacing:.08em;">
<span data-scramble>Portfolio — {YEAR}</span>
<span style="display:flex; align-items:center; gap:10px;"><span style="width:8px; height:8px; border-radius:50%; background:{A_ACCENT}; box-shadow:0 0 0 4px oklch(0.62 0.17 148 / .2);"></span><span data-scramble data-delay="200">{e(site['availability'])}</span></span>
</div>
<h1 style="margin:clamp(32px,5vw,64px) 0 0; font-weight:600; font-size:clamp(60px,14.6vw,236px); line-height:.86; letter-spacing:-.058em;">
<span style="display:block; clip-path:inset(0 -100vw 0 -100vw); padding-bottom:.04em;"><span data-drift="0.35" style="display:block;"><span data-rise style="display:block;">{e(site['firstName'])}</span></span></span>
<span style="display:block; clip-path:inset(0 -100vw 0 -100vw); text-align:right; padding-bottom:.06em;"><span data-drift="-0.35" style="display:inline-block;"><span data-rise data-delay="140" style="display:inline-block;">{e(site['lastName'])}<span style="color:{A_ACCENT};">.</span></span></span></span>
</h1>
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 280px), 1fr)); gap:clamp(28px,4vw,64px); margin-top:clamp(40px,5vw,72px); align-items:end;">
<div data-reveal data-delay="300" style="display:flex; flex-direction:column; gap:32px;">
<p style="margin:0; font-size:clamp(20px,1.9vw,26px); line-height:1.35; letter-spacing:-.012em; max-width:30ch; text-wrap:pretty;">{e(home['heroBlurb'])}</p>
<div style="display:flex; gap:12px; flex-wrap:wrap;">
<a href="#work" class="a-btn-dark" data-magnetic style="padding:16px 26px; border-radius:999px; background:#151511; color:#f4f2ec; font-weight:500; font-size:15px;">See selected work ↓</a>
<a href="#contact" data-magnetic style="padding:16px 26px; border-radius:999px; border:1px solid rgba(21,21,17,.25); font-weight:500; font-size:15px;">Get in touch</a>
</div>
</div>
<div data-reveal data-delay="420" style="position:relative; aspect-ratio:4/5; width:100%; max-width:440px; justify-self:center; overflow:hidden; border-radius:6px; background:#e4e1d8;">
<img data-parallax="-0.1" src="images/malwandla-hero.jpg" alt="{e(site['name'])}" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block;">
</div>
<dl data-reveal data-delay="540" style="margin:0; display:grid; gap:0; font-size:15px;">
{dl}</dl>
</div>
</header>"""


def a_work(projects):
    n = len(projects)
    cards = ""
    for i, p in enumerate(projects, 1):
        chips = "".join(
            f'<span style="{A_MONO} font-size:11px; padding:5px 10px; border-radius:999px; border:1px solid rgba(21,21,17,.18);">{e(t)}</span>'
            for t in p["tech"][:5])
        links = project_links(
            p,
            "padding:10px 16px; border-radius:999px; background:#151511; color:#f4f2ec; font-size:14px; font-weight:500; text-align:center;",
            "padding:10px 16px; border-radius:999px; border:1px solid rgba(21,21,17,.25); font-size:14px; font-weight:500; text-align:center;",
            "display:flex; flex-direction:column; gap:8px;")
        extra = " ".join(x for x in (status_html(p), context_html(p)) if x)
        cards += f"""<article data-glow style="position:relative; flex:none; width:min(86vw, 760px); max-width:100%; background:#fbfaf6; border:1px solid rgba(21,21,17,.12); border-radius:8px; overflow:hidden; display:flex; flex-direction:column;">
<div style="position:relative; height:clamp(220px,40vh,420px); background:#e7e4da; overflow:hidden;">
{media_html(p, 'a')}
<div style="position:absolute; inset:0; pointer-events:none; background:radial-gradient(380px circle at var(--gx, -600px) var(--gy, -600px), rgba(255,255,255,.4), transparent 60%);"></div>
</div>
<div style="padding:22px 26px 26px; display:flex; flex-wrap:wrap; gap:18px 32px; justify-content:space-between; align-items:flex-start;">
<div style="flex:1 1 320px; min-width:0;">
<div style="display:flex; flex-wrap:wrap; align-items:center; gap:10px 14px; {A_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:#5c5a52;"><span>{i:02d}</span><span>{e(p['type'])}</span>{extra}</div>
<h3 style="margin:10px 0 8px; font-size:clamp(24px,2.4vw,34px); line-height:1.05; letter-spacing:-.03em; font-weight:600;">{e(p['name'])} <span style="font-weight:400; color:#5c5a52;">— {e(p['subtitle'])}</span></h3>
<p style="margin:0; font-size:15px; line-height:1.5; color:#3b3a34; max-width:58ch; text-wrap:pretty;">{e(p['description'])}</p>
<div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:16px;">{chips}</div>
</div>
{links}
</div>
</article>
"""
    return f"""<section id="work" data-sec="work" data-hscroll style="position:relative; z-index:1; border-top:1px solid rgba(21,21,17,.1);">
<div data-hstick style="position:sticky; top:0; height:100vh; overflow:hidden; display:flex; flex-direction:column; justify-content:center; gap:clamp(24px,3vw,40px); padding:84px 0 32px;">
<div style="display:flex; justify-content:space-between; align-items:flex-end; gap:24px; flex-wrap:wrap; padding:0 clamp(20px,4vw,56px);">
<div>
<div data-scramble style="{A_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:#5c5a52;">01 — Selected work</div>
<h2 style="margin:12px 0 0; font-size:clamp(40px,5.6vw,84px); line-height:.95; letter-spacing:-.045em; font-weight:600;">{num_word(n)} builds,<br>five tracks.</h2>
</div>
<div class="hide-sm" style="display:flex; align-items:center; gap:14px; {A_MONO} font-size:13px;"><span data-hcount>01</span><span style="color:#5c5a52;">/ {n:02d}</span><span style="position:relative; width:120px; height:2px; background:rgba(21,21,17,.14);"><span data-hbar style="position:absolute; inset:0; background:#151511; transform-origin:left; transform:scaleX(0);"></span></span></div>
</div>
<div data-htrack style="display:flex; gap:clamp(16px,2vw,28px); padding:0 clamp(20px,4vw,56px); width:max-content; will-change:transform;">
{cards}</div>
</div>
</section>"""


def a_tracks(profiles):
    rows = ""
    for i, (key, pr) in enumerate(profiles.items(), 1):
        rows += f"""<a href="track.html?t={key}" class="a-track-row" data-scramble-host style="display:grid; grid-template-columns:auto minmax(0,1fr) auto; align-items:center; gap:clamp(16px,3vw,40px); padding:clamp(20px,2.4vw,32px) 12px; border-bottom:1px solid rgba(21,21,17,.16); transition:background .4s cubic-bezier(.2,.7,.2,1), color .4s, padding .4s cubic-bezier(.2,.7,.2,1);">
<span style="{A_MONO} font-size:13px; opacity:.7;">{i:02d}</span>
<span style="display:flex; flex-wrap:wrap; align-items:baseline; justify-content:space-between; gap:8px 32px;">
<span data-scramble-hover style="flex:1 1 320px; font-size:clamp(28px,4vw,56px); font-weight:600; letter-spacing:-.04em; line-height:1;">{e(pr['label'])}</span>
<span style="flex:0 1 36ch; font-size:16px; line-height:1.4; opacity:.72;">{e(pr['cardDescription'])}</span>
</span>
<span style="font-size:clamp(22px,2.4vw,32px);" aria-hidden="true">→</span>
</a>
"""
    return f"""<section id="tracks" data-sec="tracks" style="position:relative; z-index:1; padding:clamp(88px,12vw,168px) clamp(20px,4vw,56px) clamp(64px,8vw,120px);">
<div style="display:flex; justify-content:space-between; align-items:flex-end; gap:24px; flex-wrap:wrap;">
<div>
<div data-scramble style="{A_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:#5c5a52;">02 — Tracks</div>
<h2 data-reveal style="margin:12px 0 0; font-size:clamp(40px,5.6vw,84px); line-height:.95; letter-spacing:-.045em; font-weight:600;">Hire for the role<br>you need.</h2>
</div>
<p data-reveal data-delay="120" style="margin:0; max-width:34ch; font-size:17px; line-height:1.5; color:#3b3a34;">Each track has its own skills, tools, projects and a CV tailored to it.</p>
</div>
<div style="margin-top:clamp(40px,5vw,64px); border-top:1px solid rgba(21,21,17,.16);">
{rows}</div>
</section>"""


def a_about(site, home):
    words = "".join(f'<span data-word style="transition:opacity .35s ease;">{e(w)} </span>' for w in home["about"].split())
    strengths = "".join(
        f'<span style="padding:6px 12px; border-radius:999px; background:#151511; color:#f4f2ec; font-size:14px;">{e(s)}</span>'
        for s in site["strengths"])
    ed, ex, ce = site["education"], site["experience"], site["certificates"]
    label = f"{A_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:#5c5a52;"
    return f"""<section id="about" data-sec="about" style="position:relative; z-index:1; padding:clamp(64px,8vw,120px) clamp(20px,4vw,56px) clamp(88px,12vw,168px);">
<div data-scramble style="{A_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:#5c5a52;">03 — About</div>
<p data-words style="margin:24px 0 0; max-width:24ch; font-size:clamp(30px,4.4vw,64px); line-height:1.08; letter-spacing:-.035em; font-weight:500; text-wrap:pretty;">{words}</p>
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 230px), 1fr)); gap:clamp(24px,3vw,40px); margin-top:clamp(56px,7vw,96px);">
<div data-reveal style="border-top:2px solid #151511; padding-top:18px; display:flex; flex-direction:column; gap:8px;"><span style="{label}">Education</span><span style="font-size:20px; font-weight:500; letter-spacing:-.015em;">{e(ed['qualification'])}</span><span style="font-size:15px; color:#3b3a34;">{e(ed['institution'])} · {e(ed['status'])}</span></div>
<div data-reveal data-delay="100" style="border-top:2px solid #151511; padding-top:18px; display:flex; flex-direction:column; gap:8px;"><span style="{label}">Experience</span><span style="font-size:20px; font-weight:500; letter-spacing:-.015em;">{e(ex['status'])}</span><span style="font-size:15px; color:#3b3a34;">{e(ex['detail'])}</span></div>
<div data-reveal data-delay="200" style="border-top:2px solid #151511; padding-top:18px; display:flex; flex-direction:column; gap:8px;"><span style="{label}">Certificates</span><span style="font-size:20px; font-weight:500; letter-spacing:-.015em;">{e(ce['status'])}</span><span style="font-size:15px; color:#3b3a34;">{e(ce['detail'])}</span></div>
<div data-reveal data-delay="300" style="border-top:2px solid #151511; padding-top:18px; display:flex; flex-direction:column; gap:10px;"><span style="{label}">Strengths</span><div style="display:flex; flex-wrap:wrap; gap:6px;">{strengths}</div></div>
</div>
</section>"""


def social_links(site, style):
    items = [("GitHub", site["github"]), ("LinkedIn", site["linkedin"]),
             ("Instagram", site["instagram"]), ("TikTok", site["tiktok"])]
    return "".join(f'<a href="{e(u)}" target="_blank" rel="noopener" data-magnetic style="{style}">{n} ↗</a>\n' for n, u in items)


def form_fields(site, label_style, field_style, field_class, rows):
    return f"""<input type="hidden" name="access_key" value="{e(site['web3formsAccessKey'])}">
<input type="checkbox" name="botcheck" tabindex="-1" autocomplete="off" class="sr-only" aria-hidden="true">
<label style="display:grid; gap:6px;"><span style="{label_style}">Name</span><input name="name" autocomplete="name" required placeholder="Your name" class="{field_class}" style="{field_style}"></label>
<label style="display:grid; gap:6px;"><span style="{label_style}">Email</span><input type="email" name="email" autocomplete="email" required placeholder="you@company.com" class="{field_class}" style="{field_style}"></label>
<label style="display:grid; gap:6px;"><span style="{label_style}">Message</span><textarea name="message" rows="{rows}" required placeholder="Role, team, timeline…" class="{field_class}" style="{field_style} resize:vertical;"></textarea></label>
<div data-error role="alert" hidden style="font-size:15px; color:oklch(0.78 0.14 40);"></div>"""


def a_contact(site):
    lab = f"{A_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:#a9a79e;"
    field = "font-size:20px; background:transparent; border:none; border-bottom:1px solid rgba(244,242,236,.3); padding:10px 0; outline:none; color:#f4f2ec; width:100%;"
    return f"""<section id="contact" data-sec="contact" class="a-contact" style="position:relative; z-index:1; background:#151511; color:#f4f2ec; padding:clamp(88px,12vw,160px) clamp(20px,4vw,56px) 40px; border-radius:clamp(20px,3vw,40px) clamp(20px,3vw,40px) 0 0;">
<div data-scramble style="{A_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:#a9a79e;">04 — Contact</div>
<h2 style="margin:20px 0 0; font-size:clamp(56px,10.5vw,170px); line-height:.88; letter-spacing:-.058em; font-weight:600;"><span style="display:block; clip-path:inset(0 -100vw 0 -100vw);"><span data-rise style="display:block;">Let's build</span></span><span style="display:block; clip-path:inset(0 -100vw 0 -100vw);"><span data-rise data-delay="120" style="display:block;">something<span style="color:oklch(0.72 0.17 148);">.</span></span></span></h2>
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 340px), 1fr)); gap:clamp(48px,6vw,96px); margin-top:clamp(56px,7vw,96px);">
<div data-reveal style="display:flex; flex-direction:column; gap:28px;">
<a href="mailto:{e(site['email'])}" class="a-mail" style="font-size:clamp(20px,2.2vw,30px); letter-spacing:-.02em; font-weight:500; word-break:break-all; border-bottom:1px solid rgba(244,242,236,.3); padding-bottom:12px;">{e(site['email'])}</a>
<div style="display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:20px; font-size:16px;">
<div style="display:flex; flex-direction:column; gap:6px;"><span style="{lab}">Phone</span><a href="tel:{e(site['phoneIntl'])}">{e(site['phone'])}</a></div>
<div style="display:flex; flex-direction:column; gap:6px;"><span style="{lab}">Location</span><span>{e(site['locationShort'])}</span></div>
</div>
<div style="display:flex; flex-wrap:wrap; gap:8px;">
{social_links(site, "padding:12px 18px; border-radius:999px; border:1px solid rgba(244,242,236,.25); font-size:14px;")}</div>
</div>
<div data-reveal data-delay="120" data-contact-wrap>
<form data-contact data-email="{e(site['email'])}" novalidate style="display:grid; gap:24px;">
{form_fields(site, lab, field, "a-field", 4)}
<button type="submit" data-magnetic style="justify-self:start; padding:18px 30px; border-radius:999px; border:none; background:oklch(0.8 0.15 148); color:#151511; font-size:16px; font-weight:600; cursor:pointer;"><span data-label>Send message</span> →</button>
</form>
<div data-sent hidden style="flex-direction:column; gap:20px; padding:32px; border-radius:12px; border:1px solid rgba(244,242,236,.2);">
<span style="{A_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:oklch(0.8 0.15 148);">Message sent</span>
<p style="margin:20px 0; font-size:24px; line-height:1.3; letter-spacing:-.015em;">Thanks, <span data-sent-name></span>. I'll get back to you at <span data-sent-email></span> soon.</p>
<button type="button" data-again style="padding:12px 20px; border-radius:999px; border:1px solid rgba(244,242,236,.3); background:transparent; color:#f4f2ec; cursor:pointer;">Send another</button>
</div>
</div>
</div>
<footer style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px; margin-top:clamp(80px,10vw,140px); padding-top:24px; border-top:1px solid rgba(244,242,236,.14); font-size:13px; color:#a9a79e;">
<span>© {YEAR} {e(site['name'])}</span>
<div style="display:flex; gap:20px;"><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="#top" data-magnetic>Back to top ↑</a></div>
</footer>
</section>"""


# ---------------------------------------------------------------------------
# Homepage — Direction B (dark)
# ---------------------------------------------------------------------------
B_LABEL = f"{B_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:#b5b3ab;"
B_PANEL = "border-radius:12px; background:#121316; border:1px solid rgba(236,234,228,.1);"


def b_nav(site):
    cv = cv_href(site["combinedCv"])
    return f"""<nav aria-label="Main" style="position:sticky; top:0; z-index:50; display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; padding:14px clamp(20px,4vw,56px); background:rgba(12,13,15,.7); backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); border-bottom:1px solid rgba(236,234,228,.08);">
<a href="#top" style="display:flex; align-items:center; gap:12px; {B_MONO} font-size:13px;"><span style="width:34px; height:34px; border:1px solid {B_ACCENT}; color:{B_ACCENT}; display:grid; place-items:center; font-weight:500; border-radius:6px;">MH</span>malwandla.dev</a>
<div class="nav-links" style="display:flex; gap:clamp(14px,2.6vw,36px); {B_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:#b5b3ab;">
<a href="#work-b" data-scramble-host data-scramble-hover>Work</a>
<a href="#tracks-b" data-scramble-host data-scramble-hover>Tracks</a>
<a href="#about-b" data-scramble-host data-scramble-hover>About</a>
<a href="#contact-b" data-scramble-host data-scramble-hover>Contact</a>
</div>
<div class="nav-right">{theme_toggle()}<a href="{e(cv)}" target="_blank" rel="noopener" class="b-btn-accent" data-magnetic style="padding:10px 18px; border-radius:6px; background:{B_ACCENT}; color:#0c0d0f; font-size:14px; font-weight:600;">Download CV ↓</a></div>
</nav>"""


def b_hero(site, home):
    cycle = home["heroCycle"]
    return f"""<header data-sec="hero" style="position:relative; z-index:1; display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 420px), 1fr)); gap:clamp(40px,5vw,80px); align-items:center; padding:clamp(48px,7vw,104px) clamp(20px,4vw,56px) clamp(80px,10vw,140px); min-height:calc(100vh - 64px);">
<div style="display:flex; flex-direction:column; gap:clamp(28px,3vw,40px); min-width:0;">
<div style="display:flex; align-items:center; gap:10px; {B_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:#b5b3ab;"><span style="width:8px; height:8px; border-radius:50%; background:{B_ACCENT}; box-shadow:0 0 12px {B_ACCENT};"></span><span data-scramble>Available · Internship &amp; graduate roles</span></div>
<h1 style="margin:0; font-stretch:125%; font-weight:800; text-transform:uppercase; font-size:clamp(44px,7.4vw,128px); line-height:.88; letter-spacing:-.03em;">
<span style="display:block; clip-path:inset(0 -100vw 0 -100vw);"><span data-rise style="display:block;">{e(site['firstName'])}</span></span>
<span style="display:block; clip-path:inset(0 -100vw 0 -100vw);"><span data-rise data-delay="120" style="display:block; color:transparent; -webkit-text-stroke:1.5px #eceae4;">{e(site['lastName'])}</span></span>
</h1>
<div data-reveal data-delay="300" style="font-size:clamp(20px,2vw,28px); line-height:1.3; letter-spacing:-.01em; font-weight:400;">I build <span data-cycle="{e('|'.join(cycle))}" data-text="{e(cycle[0])}" style="{B_MONO} color:{B_ACCENT}; font-size:.86em;">{e(cycle[0])}</span></div>
<p data-reveal data-delay="380" style="margin:0; max-width:46ch; font-size:17px; line-height:1.55; color:#b5b3ab; text-wrap:pretty;">{e(site['education']['qualification'])} at the {e(site['education']['institution'])}. Based in Pretoria, working across five tracks.</p>
<div data-reveal data-delay="460" style="display:flex; gap:12px; flex-wrap:wrap;">
<a href="#work-b" class="b-btn-light" data-magnetic style="padding:16px 26px; border-radius:6px; background:#eceae4; color:#0c0d0f; font-weight:600; font-size:15px;">View projects ↓</a>
<a href="#contact-b" data-magnetic style="padding:16px 26px; border-radius:6px; border:1px solid rgba(236,234,228,.25); font-weight:500; font-size:15px;">Contact me</a>
</div>
</div>
<div data-reveal data-delay="200" style="justify-self:center; width:100%; max-width:460px;">
<div data-tilt data-glow style="position:relative; aspect-ratio:4/5; border-radius:14px; padding:1px; background:radial-gradient(320px circle at var(--gx, 50%) var(--gy, 50%), oklch(0.86 0.17 128 / .9), rgba(236,234,228,.12) 70%); transition:transform .5s cubic-bezier(.2,.7,.2,1); transform-style:preserve-3d;">
<div style="position:relative; width:100%; height:100%; border-radius:13px; overflow:hidden; background:#151619;">
<img src="images/malwandla-hero.jpg" alt="{e(site['name'])}" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover;">
<div style="position:absolute; inset:0; background:linear-gradient(to top, rgba(12,13,15,.85), transparent 45%);"></div>
<div style="position:absolute; left:20px; right:20px; bottom:18px; display:flex; justify-content:space-between; gap:12px; {B_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.06em;"><span>Pretoria, ZA</span><span style="color:{B_ACCENT};">ICT · UMP</span></div>
</div>
</div>
</div>
</header>"""


def b_work(projects):
    n = len(projects)
    done = sum(1 for p in projects if p.get("status", "").lower() != "in progress")
    cards = ""
    for i, p in enumerate(projects, 1):
        chips = "".join(
            f'<span style="{B_MONO} font-size:11px; padding:6px 10px; border-radius:4px; background:rgba(236,234,228,.07);">{e(t)}</span>'
            for t in p["tech"][:6])
        links = project_links(
            p,
            "padding:12px 18px; border-radius:6px; background:#eceae4; color:#0c0d0f; font-size:14px; font-weight:600;",
            "padding:12px 18px; border-radius:6px; border:1px solid rgba(236,234,228,.25); font-size:14px; font-weight:500;",
            "display:flex; gap:10px; flex-wrap:wrap;")
        extra = "".join(x for x in (status_html(p), context_html(p)) if x)
        extra_row = f'<div style="display:flex; flex-wrap:wrap; gap:10px 14px; align-items:center; margin-top:16px;">{extra}</div>' if extra else ""
        cards += f"""<div data-stack style="position:sticky; top:96px;">
<article data-glow style="transform-origin:top center; border-radius:16px; padding:1px; background:radial-gradient(420px circle at var(--gx, -600px) var(--gy, -600px), oklch(0.86 0.17 128 / .8), rgba(236,234,228,.12) 70%); will-change:transform;">
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 340px), 1fr)); min-height:min(72vh, 600px); border-radius:15px; overflow:hidden; background:#121316;">
<div style="display:flex; flex-direction:column; justify-content:space-between; gap:28px; padding:clamp(24px,3vw,44px);">
<div style="display:flex; justify-content:space-between; {B_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:#b5b3ab;"><span style="color:{B_ACCENT};">{i:02d} / {n:02d}</span><span>{e(p['type'])}</span></div>
<div>
<h3 style="margin:0; font-stretch:125%; text-transform:uppercase; font-size:clamp(32px,4vw,60px); line-height:.92; letter-spacing:-.025em; font-weight:800;">{e(p['name'])}</h3>
<div style="margin-top:10px; font-size:18px; color:#b5b3ab;">{e(p['subtitle'])}</div>
{extra_row}
<p style="margin:20px 0 0; max-width:48ch; font-size:16px; line-height:1.55; color:#d6d4cd; text-wrap:pretty;">{e(p['description'])}</p>
<div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:20px;">{chips}</div>
</div>
{links or '<div></div>'}
</div>
<div style="position:relative; min-height:280px; background:#1a1b1f; overflow:hidden;">
{media_html(p, 'b')}
</div>
</div>
</article>
</div>
"""
    blurb = (f"{num_word(n)} builds across enterprise Java, web, mobile, desktop and network design"
             + (f", {num_word(n - done).lower()} still in progress." if n - done else "."))
    return f"""<section id="work-b" data-sec="work" style="position:relative; z-index:1; padding:clamp(40px,6vw,80px) clamp(20px,4vw,56px) clamp(80px,10vw,140px);">
<div style="display:flex; justify-content:space-between; align-items:flex-end; gap:24px; flex-wrap:wrap; margin-bottom:clamp(40px,5vw,64px);">
<div>
<div data-scramble style="{B_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:{B_ACCENT};">[01] Selected work</div>
<h2 data-reveal style="margin:14px 0 0; font-stretch:125%; text-transform:uppercase; font-size:clamp(36px,5.4vw,84px); line-height:.9; letter-spacing:-.03em; font-weight:800;">Projects</h2>
</div>
<p data-reveal data-delay="120" style="margin:0; max-width:36ch; font-size:16px; line-height:1.5; color:#b5b3ab;">{e(blurb)}</p>
</div>
<div style="display:flex; flex-direction:column; gap:clamp(40px,8vh,96px);">
{cards}</div>
</section>"""


def b_tracks(profiles):
    cards = ""
    for i, (key, pr) in enumerate(profiles.items(), 1):
        cards += f"""<a href="track.html?t={key}" class="b-track-card" data-glow data-scramble-host style="display:block; border-radius:12px; padding:1px; background:radial-gradient(260px circle at var(--gx, -600px) var(--gy, -600px), {B_ACCENT}, rgba(236,234,228,.12) 70%);">
<span style="display:flex; flex-direction:column; justify-content:space-between; gap:48px; height:100%; min-height:240px; padding:22px; border-radius:11px; background:#121316; transition:background .3s;">
<span style="display:flex; justify-content:space-between; {B_MONO} font-size:12px; color:#b5b3ab;"><span>{i:02d}</span><span style="color:{B_ACCENT};" aria-hidden="true">↗</span></span>
<span style="display:flex; flex-direction:column; gap:10px;"><span data-scramble-hover style="font-size:24px; font-weight:700; letter-spacing:-.01em; line-height:1.1;">{e(pr['label'])}</span><span style="font-size:15px; line-height:1.45; color:#b5b3ab;">{e(pr['cardDescription'])}</span></span>
</span>
</a>
"""
    return f"""<section id="tracks-b" data-sec="tracks" style="position:relative; z-index:1; padding:clamp(60px,8vw,120px) clamp(20px,4vw,56px);">
<div style="display:flex; justify-content:space-between; align-items:flex-end; gap:24px; flex-wrap:wrap; margin-bottom:clamp(40px,5vw,64px);">
<div>
<div data-scramble style="{B_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:{B_ACCENT};">[02] Tracks</div>
<h2 data-reveal style="margin:14px 0 0; font-stretch:125%; text-transform:uppercase; font-size:clamp(36px,5.4vw,84px); line-height:.9; letter-spacing:-.03em; font-weight:800;">Pick a role</h2>
</div>
<p data-reveal data-delay="120" style="margin:0; max-width:36ch; font-size:16px; line-height:1.5; color:#b5b3ab;">Each track opens its own skills, tools, projects and tailored CV.</p>
</div>
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 210px), 1fr)); gap:12px;">
{cards}</div>
</section>"""


def b_about(site, home):
    text = e(home["aboutDark"]).replace("&lt;em&gt;", f'<span style="color:{B_ACCENT};">').replace("&lt;/em&gt;", "</span>")
    strengths = "".join(
        f'<span style="padding:6px 10px; border-radius:4px; border:1px solid oklch(0.86 0.17 128 / .5); font-size:14px;">{e(s)}</span>'
        for s in site["strengths"])
    ed, ex, ce = site["education"], site["experience"], site["certificates"]
    box = f"display:flex; flex-direction:column; gap:10px; padding:24px; {B_PANEL}"
    big = "font-size:19px; font-weight:600; line-height:1.25;"
    small = "font-size:15px; color:#b5b3ab;"
    return f"""<section id="about-b" data-sec="about" style="position:relative; z-index:1; padding:clamp(60px,8vw,120px) clamp(20px,4vw,56px);">
<div data-scramble style="{B_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:{B_ACCENT}; margin-bottom:clamp(32px,4vw,48px);">[03] About</div>
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 260px), 1fr)); gap:12px;">
<div data-reveal style="grid-column:1 / -1; padding:clamp(28px,4vw,56px); {B_PANEL}">
<p style="margin:0; max-width:30ch; font-size:clamp(26px,3.4vw,48px); line-height:1.12; letter-spacing:-.02em; font-weight:500; text-wrap:pretty;">{text}</p>
</div>
<div data-reveal style="{box}"><span style="{B_LABEL}">Education</span><span style="{big}">{e(ed['qualification'])}</span><span style="{small}">{e(ed['institution'])} · {e(ed['status'])}</span></div>
<div data-reveal data-delay="80" style="{box}"><span style="{B_LABEL}">Experience</span><span style="{big}">{e(ex['status'])}</span><span style="{small}">{e(ex['detail'])}</span></div>
<div data-reveal data-delay="160" style="{box}"><span style="{B_LABEL}">Certificates</span><span style="{big}">{e(ce['status'])}</span><span style="{small}">{e(ce['detail'])}</span></div>
<div data-reveal data-delay="240" style="{box} gap:12px;"><span style="{B_LABEL}">Strengths</span><div style="display:flex; flex-wrap:wrap; gap:6px;">{strengths}</div></div>
</div>
</section>"""


def b_contact(site):
    field = "font-size:17px; background:#0c0d0f; border:1px solid rgba(236,234,228,.14); border-radius:8px; padding:14px 16px; outline:none; color:#eceae4; width:100%;"
    return f"""<section id="contact-b" data-sec="contact" style="position:relative; z-index:1; padding:clamp(60px,8vw,120px) clamp(20px,4vw,56px) 40px;">
<div data-scramble style="{B_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:{B_ACCENT};">[04] Contact</div>
<h2 style="margin:16px 0 0; font-stretch:125%; text-transform:uppercase; font-weight:800; font-size:clamp(44px,8.6vw,150px); line-height:.86; letter-spacing:-.03em;"><span style="display:block; clip-path:inset(0 -100vw 0 -100vw);"><span data-rise style="display:block;">Let's work</span></span><span style="display:block; clip-path:inset(0 -100vw 0 -100vw);"><span data-rise data-delay="120" style="display:block; color:{B_ACCENT};">together</span></span></h2>
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 340px), 1fr)); gap:12px; margin-top:clamp(48px,6vw,80px);">
<div data-reveal style="display:flex; flex-direction:column; gap:24px; padding:clamp(24px,3vw,40px); {B_PANEL}">
<div style="display:flex; flex-direction:column; gap:6px;"><span style="{B_LABEL}">Email</span><a href="mailto:{e(site['email'])}" style="font-size:clamp(18px,1.8vw,22px); font-weight:500; word-break:break-all;">{e(site['email'])}</a></div>
<div style="display:flex; flex-direction:column; gap:6px;"><span style="{B_LABEL}">Phone</span><a href="tel:{e(site['phoneIntl'])}" style="font-size:20px; font-weight:500;">{e(site['phone'])}</a></div>
<div style="display:flex; flex-direction:column; gap:6px;"><span style="{B_LABEL}">Location</span><span style="font-size:20px; font-weight:500;">{e(site['location'])}</span></div>
<div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:auto;">
{social_links(site, "padding:10px 16px; border-radius:6px; border:1px solid rgba(236,234,228,.2); font-size:14px;")}</div>
</div>
<div data-reveal data-delay="100" data-contact-wrap style="padding:clamp(24px,3vw,40px); {B_PANEL}">
<form data-contact data-email="{e(site['email'])}" novalidate style="display:grid; gap:16px;">
{form_fields(site, B_LABEL, field, "b-field", 5)}
<button type="submit" data-magnetic style="justify-self:start; margin-top:8px; padding:16px 28px; border-radius:6px; border:none; background:{B_ACCENT}; color:#0c0d0f; font-size:16px; font-weight:700; cursor:pointer;"><span data-label>Send message</span> →</button>
</form>
<div data-sent hidden>
<span style="{B_MONO} font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:{B_ACCENT};">● Message sent</span>
<p style="margin:20px 0; font-size:26px; line-height:1.3; font-weight:500;">Thanks, <span data-sent-name></span>. I'll reply to <span data-sent-email></span> soon.</p>
<button type="button" data-again style="padding:12px 20px; border-radius:6px; border:1px solid rgba(236,234,228,.25); background:transparent; color:#eceae4; cursor:pointer;">Send another</button>
</div>
</div>
</div>
<footer style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px; margin-top:clamp(72px,9vw,120px); padding-top:24px; border-top:1px solid rgba(236,234,228,.1); {B_MONO} font-size:12px; color:#b5b3ab;">
<span>© {YEAR} {e(site['name'])}</span>
<div style="display:flex; gap:20px;"><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="#top" data-magnetic>Top ↑</a></div>
</footer>
</section>"""


def render_home(site, home, profiles, projects):
    desc = (f"{site['name']}: {site['education']['qualification']}. "
            "Software, Android, database, IT support and networking.")
    return f"""{head(f"{site['name']} · Portfolio", desc)}<body>
<div id="top" style="position:relative; min-height:100vh; overflow-x:clip;">
<div class="only-light" aria-hidden="true"><div class="spot-a"></div></div>
<div class="only-dark" aria-hidden="true"><div class="grid-b"></div><div class="grid-b-spot"></div><div class="glow-b"></div></div>

<div class="only-light" style="position:relative; background:transparent; color:#151511; font-family:'Geist', system-ui, sans-serif;">
{a_nav(site)}
<main>
{a_hero(site, home)}
{a_work(projects)}
{a_tracks(profiles)}
{a_about(site, home)}
{a_contact(site)}
</main>
</div>

<div class="only-dark" style="position:relative; background:transparent; color:#eceae4; font-family:'Archivo', system-ui, sans-serif;">
{b_nav(site)}
<main>
{b_hero(site, home)}
{b_work(projects)}
{b_tracks(profiles)}
{b_about(site, home)}
{b_contact(site)}
</main>
</div>
</div>
{lightbox_html()}{scripts()}"""


# ---------------------------------------------------------------------------
# track.html — one page, five tracks
# ---------------------------------------------------------------------------
def page_backdrop():
    return ('<div class="only-light" aria-hidden="true"><div class="spot-a"></div></div>\n'
            '<div class="only-dark" aria-hidden="true"><div class="grid-b"></div><div class="grid-b-spot"></div>'
            '<div class="glow-b"></div></div>')


def track_project_card(p):
    chips = "".join(f'<span class="chip">{e(t)}</span>' for t in p["tech"])
    links = []
    if p.get("github"):
        links.append(f'<a href="{e(p["github"])}" target="_blank" rel="noopener" class="btn btn-solid" data-magnetic>GitHub ↗</a>')
    if p.get("demo"):
        links.append(f'<a href="{e(p["demo"])}" target="_blank" rel="noopener" class="btn btn-ghost" data-magnetic>Live demo ↗</a>')
    links_html = f'<div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:4px;">{"".join(links)}</div>' if links else ""
    return f"""<article class="pcard" data-glow data-reveal>
<div class="pcard-media">{media_html(p, 'card')}<div class="pcard-glow"></div></div>
<div class="pcard-body">
<div class="pcard-meta"><span>{e(p['type'])}</span>{status_html(p)}{context_html(p)}</div>
<h3>{e(p['name'])} <span class="sub">— {e(p['subtitle'])}</span></h3>
<p>{e(p['description'])}</p>
<div class="chips">{chips}</div>
{links_html}
</div>
</article>"""


def track_panel(i, key, pr, keys, profiles, tools_catalog, projects_catalog, site):
    total = len(keys)
    nxt = keys[(i + 1) % total]
    skills = "".join(
        f"""<div class="skill"><div class="skill-head"><span>{e(s['name'])}</span><span>{s['level']}%</span></div>
<div class="skill-bar" role="progressbar" aria-label="{e(s['name'])}" aria-valuenow="{s['level']}" aria-valuemin="0" aria-valuemax="100"><div data-level="{s['level']}"></div></div></div>"""
        for s in pr["skills"])
    tools = "".join(f'<span class="tool">{e(tools_catalog.get(t, {"label": t})["label"])}</span>' for t in pr["tools"])
    projects = [projects_catalog[k] for k in pr["projects"] if k in projects_catalog]
    cards = "\n".join(track_project_card(p) for p in projects)
    heading_label = "Project for this track" if len(projects) == 1 else "Projects for this track"
    cv = cv_href(pr["cv"])
    hidden = "" if i == 0 else " hidden"
    return f"""<div data-panel="{key}" id="panel-{key}" role="tabpanel" aria-labelledby="tab-{key}" data-cv="{e(cv)}" data-title="{e(pr['headline'])} · {e(site['name'])}"{hidden}>
<header class="pad-x" style="position:relative; z-index:1; padding-top:clamp(48px,7vw,104px); padding-bottom:clamp(56px,7vw,96px);">
<div class="eyebrow accent-dark">Track {i + 1:02d} / {total:02d}</div>
<h1 class="display" style="margin:20px 0 0; font-size:clamp(48px,9.4vw,152px); line-height:.9; min-height:1.8em; text-wrap:balance;"><span data-head data-text="{e(pr['headline'])}">{e(pr['headline'])}</span><span class="dot">.</span></h1>
<div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-end; gap:32px; margin-top:clamp(32px,4vw,56px);">
<p style="margin:0; max-width:34ch; font-size:clamp(20px,1.9vw,26px); line-height:1.35; letter-spacing:-.012em; text-wrap:pretty;">{e(pr['tagline'])}</p>
<div style="display:flex; gap:12px; flex-wrap:wrap;">
<a href="{e(cv)}" target="_blank" rel="noopener" class="btn btn-lg btn-solid" data-magnetic>Download {e(pr['cvLabel'])} CV ↓</a>
<a href="index.html#contact" class="btn btn-lg btn-ghost" data-magnetic>Hire me for this</a>
</div>
</div>
</header>
<section class="section pad-x" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 380px), 1fr)); gap:clamp(48px,6vw,96px);">
<div>
<div class="eyebrow accent-dark" data-scramble>Skills</div>
<div style="display:flex; flex-direction:column; gap:22px; margin-top:28px;">{skills}</div>
</div>
<div>
<div class="eyebrow accent-dark" data-scramble>Tools &amp; technologies</div>
<div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:28px;">{tools}</div>
<p style="margin:40px 0 0; max-width:44ch; font-size:17px; line-height:1.55; color:var(--body); text-wrap:pretty;">{e(pr['summary'])}</p>
</div>
</section>
<section class="section pad-x">
<div class="eyebrow accent-dark" data-scramble>{heading_label}</div>
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 440px), 1fr)); gap:clamp(16px,2vw,28px); margin-top:28px;">
{cards}
</div>
</section>
<section class="next pad-x">
<div class="eyebrow" style="color:inherit; opacity:.65;">Next track</div>
<button type="button" class="next-btn" data-go="{nxt}" data-scramble-host>
<span data-scramble-hover class="display" style="font-size:clamp(44px,8vw,128px); line-height:.92;">{e(profiles[nxt]['headline'])}</span>
<span style="font-size:clamp(32px,5vw,72px);" aria-hidden="true">→</span>
</button>
<footer class="foot" style="margin-top:clamp(64px,8vw,112px);">
<span>© {YEAR} {e(site['name'])}</span>
<div style="display:flex; gap:20px; flex-wrap:wrap;"><a href="index.html#contact">Contact</a><a href="mailto:{e(site['email'])}">Email</a><a href="privacy.html">Privacy</a><a href="#top" data-magnetic>Back to top ↑</a></div>
</footer>
</section>
</div>"""


def render_track(site, profiles, tools_catalog, projects_catalog):
    keys = list(profiles.keys())
    first = profiles[keys[0]]
    tabs = "".join(
        f'<button type="button" role="tab" class="tab" id="tab-{k}" data-tab="{k}" aria-controls="panel-{k}" '
        f'aria-selected="{"true" if i == 0 else "false"}">{e(profiles[k]["short"])}</button>'
        for i, k in enumerate(keys))
    panels = "\n".join(
        track_panel(i, k, profiles[k], keys, profiles, tools_catalog, projects_catalog, site)
        for i, k in enumerate(keys))
    return f"""{head(f"{first['headline']} · {site['name']}", "Five career tracks: software, Android, database, IT support and networking. Skills, tools, projects and a tailored CV for each.")}<body>
<div id="top" class="page" data-track-page>
{page_backdrop()}
<nav class="nav pad-x" aria-label="Main">
<a href="index.html" class="logo"><span class="logo-badge">MH</span>← Home</a>
<div class="tabs nav-links" role="tablist" aria-label="Career tracks">{tabs}</div>
<div class="nav-right">{theme_toggle()}<a href="{e(cv_href(first['cv']))}" target="_blank" rel="noopener" class="btn btn-solid" data-nav-cv data-magnetic>Track CV ↓</a></div>
</nav>
<main>
{panels}
</main>
</div>
{lightbox_html()}{scripts()}"""


def render_redirect(key, profile, site):
    target = f"track.html?t={key}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>{e(profile['headline'])} · {e(site['name'])}</title>
<meta http-equiv="refresh" content="0; url={target}" />
<link rel="canonical" href="{target}" />
<script>location.replace({json.dumps(target)});</script>
</head>
<body><p>This page has moved to <a href="{target}">{e(profile['headline'])}</a>.</p></body>
</html>
"""


# ---------------------------------------------------------------------------
# Legal pages
# ---------------------------------------------------------------------------
def privacy_sections(site):
    email = e(site["email"])
    return [
        ("Overview",
         f"This is the personal portfolio site of {e(site['name'])}, a final-year ICT student showcasing skills, "
         "projects and CVs across five career tracks. This page explains what data the site collects and how it's "
         "used. There are no user accounts, no purchases and no advertising here."),
        ("Contact form",
         "The contact form asks for your name, email address and message. Submitting it sends that information "
         "directly to my email inbox via <strong>Web3Forms</strong>, a third-party form-processing service; this "
         "site doesn't store submissions in a database of its own. Web3Forms may retain submission data, including "
         "your IP address for spam prevention, under its own policy. See "
         '<a href="https://web3forms.com/privacy" target="_blank" rel="noopener">Web3Forms\'s privacy policy</a> for details.'),
        ("Fonts",
         "This site loads its typefaces (Geist, Geist Mono, Archivo and JetBrains Mono) from Google Fonts. Google "
         "states that the Google Fonts service does not use cookies, though requests for font files go to Google's "
         "servers and may include standard technical data such as your IP address. See "
         '<a href="https://fonts.google.com/faq" target="_blank" rel="noopener">Google Fonts\' FAQ</a> for details.'),
        ("Cookies and tracking",
         "This site does not set any cookies and runs no analytics or advertising trackers. The only thing it "
         "remembers is your light/dark choice if you use the toggle, kept in your browser's session storage until "
         "you close the tab. It is never sent anywhere."),
        ("Hosting",
         "This site is hosted on GitHub Pages. Like any web host, GitHub's servers process standard technical data "
         "(such as IP address and browser type) to serve the pages. See "
         '<a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" '
         'target="_blank" rel="noopener">GitHub\'s Privacy Statement</a> for details.'),
        ("Links to other sites",
         "This site links out to GitHub, LinkedIn, Instagram, TikTok and live project demos. Those sites have their "
         "own privacy practices, which this policy doesn't cover."),
        ("Contact", f'Questions about this policy can be sent to <a href="mailto:{email}">{email}</a>.'),
    ]


def terms_sections(site):
    email = e(site["email"])
    return [
        ("About this site",
         f"This site is the personal portfolio of {e(site['name'])} (“I”, “me”), built to showcase skills, projects "
         "and CVs to potential employers and collaborators. It's provided for informational purposes and isn't a "
         "commercial product or service."),
        ("Content and ownership",
         "Project write-ups, CVs, and the site's design and code are mine unless stated otherwise. Group projects "
         "are marked as such. Source code for individual projects linked out to GitHub follows that repository's "
         "own license, where one is provided."),
        ("No warranty",
         "This site is provided “as is.” I’ve done my best to keep it accurate and available, but I don't guarantee "
         "it will be error-free, uninterrupted, or fit for any particular purpose."),
        ("External links",
         "Links to GitHub, LinkedIn, Instagram, TikTok and live project demos lead to third-party sites I don't "
         "control, and I'm not responsible for their content."),
        ("CV downloads",
         "CVs on this site are provided for recruitment and professional review. Please don't redistribute or "
         "repost them without asking first."),
        ("Changes to these terms",
         "I may update this page as the site changes. Continuing to use the site after an update means you accept "
         "the current version."),
        ("Contact", f'Questions about these terms can be sent to <a href="mailto:{email}">{email}</a>.'),
    ]


def render_legal(title, sections, site):
    body = "\n".join(f'<section data-reveal><h2>{e(h)}</h2><p>{c}</p></section>' for h, c in sections)
    return f"""{head(f"{title} · {site['name']}", f"{title} for {site['name']}'s portfolio site.")}<body>
<div id="top" class="page">
{page_backdrop()}
<nav class="nav pad-x" aria-label="Main">
<a href="index.html" class="logo"><span class="logo-badge">MH</span>← Home</a>
<div class="nav-right">{theme_toggle()}<a href="{e(cv_href(site['combinedCv']))}" target="_blank" rel="noopener" class="btn btn-solid" data-magnetic>Download CV ↓</a></div>
</nav>
<main class="legal">
<div class="eyebrow accent-dark">Last updated {LEGAL_LAST_UPDATED}</div>
<h1 class="display">{e(title)}<span class="dot">.</span></h1>
{body}
</main>
</div>
{scripts()}"""


# ---------------------------------------------------------------------------
def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    site, home = data["site"], data["home"]
    tools_catalog = data["toolsCatalog"]
    projects_catalog = data["projectsCatalog"]
    profiles = data["profiles"]

    # Sanity checks: catch typos in profiles.json before they become broken pages
    for key, pr in profiles.items():
        for pk in pr["projects"]:
            if pk not in projects_catalog:
                raise SystemExit(f"profiles.{key}.projects lists '{pk}', which isn't in projectsCatalog")
        for tk in pr["tools"]:
            if tk not in tools_catalog:
                raise SystemExit(f"profiles.{key}.tools lists '{tk}', which isn't in toolsCatalog")
    for pk, p in projects_catalog.items():
        for img in p.get("images", []):
            if not (OUT_DIR / img).exists():
                print(f"  warning: {pk} image '{img}' not found in client/{img}")

    featured = [p for p in projects_catalog.values() if p.get("featured", True)]

    outputs = {
        "index.html": render_home(site, home, profiles, featured),
        "track.html": render_track(site, profiles, tools_catalog, projects_catalog),
        "privacy.html": render_legal("Privacy Policy", privacy_sections(site), site),
        "terms.html": render_legal("Terms & Conditions", terms_sections(site), site),
    }
    for key, pr in profiles.items():
        outputs[pr["page"]] = render_redirect(key, pr, site)

    for name, html in outputs.items():
        (OUT_DIR / name).write_text(html, encoding="utf-8")
        print(f"wrote client/{name}")


if __name__ == "__main__":
    main()
