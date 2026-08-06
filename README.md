# Malwandla Hlongwane — Portfolio Site

Multi-profile developer portfolio. One site, five professional identities:
Software Development · Android Development · Database Development · IT Help Desk · Networking.

The core feature is the **Profile Switcher** — selecting a track updates skills,
projects, CV download, certificates, and headline without a page reload.

## Build Stages

- [ ] **MVP** — static frontend, profile switcher on local JSON, static CV PDFs, mailto contact form
- [ ] **V2** — Express + MySQL backend, contact form → DB, profile data served from DB
- [ ] **V3** — Admin dashboard (auth + CRUD) for managing content without touching code
- [ ] **V4** — GitHub live stats, extras (dark mode polish, command palette, etc.)

See `client/data/profiles.json` for the profile-switcher data contract used in the MVP.
The `server/` folder is scaffolded now but stays empty until V2.

## Folder Structure

```
client/
  css/
  js/
  images/
  data/          # MVP data source (profiles.json)
server/
  routes/
  controllers/
  middleware/
  database/
  models/
public/
uploads/
cv/              # static CV PDFs, one per profile
```

## Stack

- Frontend: HTML5, CSS3, Tailwind CSS, vanilla JS
- Backend (from V2): Node.js, Express.js
- Database (from V2): MySQL
- Version control: Git + GitHub
