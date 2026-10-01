# Malwandla Hlongwane — Portfolio Site

Multi-track developer portfolio. One site, five professional identities:
Software Development · Android Development · Database Development · IT Help Desk · Networking.

## The design

The site has two looks, and the visitor's device setting picks one (the moon/sun button switches it):

- **Light ("Direction A")**: cream background, black type, green accent. Projects scroll sideways as you scroll down.
- **Dark ("Direction B")**: near-black background with a grid, lime accent. Projects stack on top of each other as you scroll.

Motion (scrambling text, buttons that follow the cursor, scroll effects) comes from `client/js/fx.js`, taken
unchanged from the design files.

## How to change content

Everything you'd want to edit lives in **`client/data/profiles.json`**: your details, projects, tracks, skills
and tools. After editing it, rebuild the pages:

```bash
cd client/build
python3 generate_pages.py
```

**To add screenshots to a project:** put the image files in that project's folder inside `client/images/`
(e.g. `client/images/Taskify/`), list them in the project's `"images"` array in `profiles.json`, and run the
script again. The order in the list is the order the slideshow plays. Projects without images show a
"Screenshots coming soon" cover. Use `"layout": "phone"` for tall phone screenshots (shown side by side) or
`"desktop"` for wide screenshots (shown as a slideshow, never cropped).

**To change your photos:** put them in `client/images/My_IMG/` and list them in `site.heroImages` in
`profiles.json`. They play as a slideshow at the top of the homepage.

**To make the contact form deliver mail:** get a free access key at web3forms.com and paste it into
`site.web3formsAccessKey` in `profiles.json`. Until then the form asks people to email you directly.

## Pages (all generated, don't edit the HTML by hand)

| File | What it is |
|---|---|
| `client/index.html` | Homepage, with both looks in one file |
| `client/track.html` | All five tracks; `track.html?t=software` / `android` / `database` / `helpdesk` / `networking` |
| `client/privacy.html`, `client/terms.html` | Legal pages |
| `client/software.html` etc. | Redirects to `track.html?t=...` so old links still work |

## Build stages

- [x] **MVP v1–v3**: hero, about, track pages, projects, contact, CV downloads
- [x] **Redesign (Oct 2026)**: new light/dark design, single track page, StokVault, UMP Events and STAMS added
- [ ] **V2**: Express + MySQL backend, contact form → DB, profile data served from DB
- [ ] **V3**: Admin dashboard (auth + CRUD) for managing content without touching code
- [ ] **V4**: GitHub live stats and extras

The `server/` folder is scaffolded but stays empty until V2.

## Folder structure

```
client/
  build/         # generate_pages.py (builds the HTML)
  css/site.css
  js/fx.js       # motion effects from the design
  js/main.js     # theme toggle, contact form, lightbox, track switcher
  images/
  data/          # profiles.json, the single source of content
server/          # scaffolded for V2
cv/              # static CV PDFs, one per track
```

## Stack

- Frontend: HTML5, CSS3, vanilla JS (no framework, no build tools beyond the Python script)
- Backend (from V2): Node.js, Express.js
- Database (from V2): MySQL
- Version control: Git + GitHub
