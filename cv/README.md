# CV folder

CVs are generated, not hand-edited — same pattern as `client/build/generate_pages.py`
generating the site pages from `client/data/profiles.json`.

- `build/cv-data.json` — single source of truth for CV content (contact info,
  education, and per-track summary/skills/projects/coursework).
- `build/generate_cvs.js` — single source of truth for CV layout/design
  (docx-js). Visual language matches the portfolio site's theme translated
  for print: white background, Poppins headings / Inter body, electric blue
  (#0A84FF) as the one accent color, no gradients, no pill shapes, no em
  dashes.

## Regenerating

```
cd cv/build
node generate_cvs.js
```

This writes one `.docx` per track directly into this folder:

- `CV_Malwandla_Hlongwane_SoftwareWebDev.docx`
- `CV_Malwandla_Hlongwane_AndroidDev.docx`
- `CV_Malwandla_Hlongwane_DatabaseDev.docx`
- `CV_Malwandla_Hlongwane_ITSupportNetworking.docx` (shared by the IT Help
  Desk and Networking tracks)
- `CV_Malwandla_Hlongwane_Combined.docx`

Then export each `.docx` to a same-named `.pdf` (e.g. via Word/LibreOffice
"Export as PDF" or `soffice --headless --convert-to pdf`) and keep both
files here. The site only links to the `.pdf`s — see the `cv` field on each
profile in `client/data/profiles.json`. Filenames must stay exactly as
above or the download links on the site will break.

## To change CV content

Edit `build/cv-data.json`, then regenerate. Do not hand-edit the `.docx`
files — the next regeneration will overwrite them.

## To change CV design

Edit `build/generate_cvs.js`, then regenerate.
