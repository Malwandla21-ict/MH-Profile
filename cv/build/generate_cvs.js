/* generate_cvs.js — generates all CV .docx files from cv-data.json.
 *
 * Same idea as client/build/generate_pages.py: cv-data.json is the single
 * source of truth for content, this script is the single source of truth
 * for layout/design. Edit the JSON, re-run this script, never hand-edit
 * the .docx files.
 *
 * ATS rules this layout follows (Applicant Tracking Systems are the robots
 * that read CVs before a human does):
 *   - One column, no tables, no text boxes, no images, no headers/footers
 *     holding contact details (many ATS skip those areas).
 *   - Standard section names (Professional Summary, Technical Skills,
 *     Project Experience, Education) so the parser knows what each part is.
 *   - Calibri: a font every Windows/Office machine has, so nothing gets
 *     swapped or garbled.
 *   - Every link is written out as readable text (not "click here"), so the
 *     URL survives even when the ATS strips hyperlinks.
 *   - Plain characters only: real Word bullets, "|" separators, no arrows,
 *     no emoji, no em dashes.
 *   - Document title/author metadata filled in.
 * Visual language still matches the site: near-black text, one electric
 * blue (#0A84FF) accent, thin rules, no gradients.
 *
 * Projects live once in data.projects; each CV references them by "ref" and
 * may pick bullets by index ("bullets": [0, 2]), add its own
 * ("extraBullets"), or override "meta"/"tech".
 *
 * Usage: node generate_cvs.js
 */
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ExternalHyperlink,
  AlignmentType, BorderStyle, LevelFormat, convertInchesToTwip,
} = require("docx");

const DATA_PATH = path.join(__dirname, "cv-data.json");
const OUT_DIR = path.join(__dirname, "..");
const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));

const COLOR = {
  text: "1D1D1F",
  muted: "55555A",
  accent: "0A84FF",
  rule: "C9C9CE",
};
const FONT = "Calibri";
const SIZE = 21; // half-points: 10.5pt body
const BULLET_REF = "cv-bullets";

function run(text, opts = {}) {
  return new TextRun({ text, font: FONT, size: SIZE, color: COLOR.text, ...opts });
}

function segmentsToRuns(segments) {
  return segments.map((s) => run(s.text, { bold: !!s.bold }));
}

function link(displayText, url, opts = {}) {
  return new ExternalHyperlink({
    link: url,
    children: [run(displayText, { color: COLOR.accent, underline: {}, ...opts })],
  });
}

function sep() {
  return run("  |  ", { color: COLOR.rule });
}

function sectionHeader(text) {
  return new Paragraph({
    spacing: { before: 200, after: 80 },
    keepNext: true,
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: COLOR.accent, space: 3 } },
    children: [run(text.toUpperCase(), { bold: true, size: 23, characterSpacing: 10 })],
  });
}

function bodyParagraph(text) {
  return new Paragraph({
    spacing: { after: 60, line: 252 },
    children: [run(text)],
  });
}

function bulletParagraph(children, keepNext = false) {
  return new Paragraph({
    numbering: { reference: BULLET_REF, level: 0 },
    spacing: { after: 30, line: 245 },
    keepNext,
    children,
  });
}

function buildHeader(site, roleTitle) {
  return [
    new Paragraph({
      spacing: { after: 20 },
      children: [run(site.name.toUpperCase(), { bold: true, size: 40, characterSpacing: 20 })],
    }),
    new Paragraph({
      spacing: { after: 80 },
      children: [run(roleTitle, { bold: true, size: 24, color: COLOR.accent })],
    }),
    new Paragraph({
      spacing: { after: 20 },
      children: [
        run(site.location, { color: COLOR.muted }),
        sep(),
        run(site.phone, { color: COLOR.muted }),
        sep(),
        link(site.email, `mailto:${site.email}`),
      ],
    }),
    new Paragraph({
      spacing: { after: 20 },
      children: [
        run("Portfolio: ", { bold: true, color: COLOR.muted }),
        link(site.portfolioDisplay, site.portfolioUrl),
        sep(),
        run("GitHub: ", { bold: true, color: COLOR.muted }),
        link(site.githubDisplay, site.githubUrl),
      ],
    }),
    new Paragraph({
      spacing: { after: 60 },
      children: [
        run("LinkedIn: ", { bold: true, color: COLOR.muted }),
        link(site.linkedinDisplay, site.linkedinUrl),
      ],
    }),
  ];
}

function resolveProject(entry) {
  const base = data.projects[entry.ref];
  if (!base) throw new Error(`Unknown project ref: ${entry.ref}`);
  let bullets = base.bullets;
  if (Array.isArray(entry.bullets)) bullets = entry.bullets.map((i) => base.bullets[i]);
  if (entry.extraBullets) bullets = [...bullets, ...entry.extraBullets];
  return { ...base, ...entry, bullets };
}

function buildProject(p) {
  const paras = [
    new Paragraph({
      spacing: { before: 110, after: 0 },
      keepNext: true,
      children: [run(p.name, { bold: true, size: 22 })],
    }),
  ];
  if (p.meta) {
    paras.push(new Paragraph({
      spacing: { after: 0 },
      keepNext: true,
      children: [run(p.meta, { italics: true, color: COLOR.muted })],
    }));
  }
  paras.push(new Paragraph({
    spacing: { after: 40 },
    keepNext: true,
    children: [run(p.techLabel || "Tech: ", { bold: true, color: COLOR.muted }), run(p.tech, { color: COLOR.muted })],
  }));
  p.bullets.forEach((b, i) => paras.push(bulletParagraph([run(b)], i === 0)));
  if (p.links && p.links.length) {
    const kids = [];
    p.links.forEach((l, i) => {
      if (i) kids.push(sep());
      kids.push(run(`${l.label}: `, { bold: true, color: COLOR.muted }));
      kids.push(link(l.display, l.url));
    });
    paras.push(new Paragraph({ spacing: { before: 20, after: 40 }, children: kids }));
  }
  return paras;
}

function buildDocxChildren(cv) {
  const { site, education } = data;
  const children = [...buildHeader(site, cv.roleTitle)];

  children.push(sectionHeader("Professional Summary"));
  children.push(bodyParagraph(cv.summary));

  children.push(sectionHeader("Technical Skills"));
  cv.skills.forEach((segs) => children.push(bulletParagraph(segmentsToRuns(segs))));

  cv.projectSections.forEach((section) => {
    children.push(sectionHeader(section.title));
    section.projects.forEach((entry) => children.push(...buildProject(resolveProject(entry))));
  });

  children.push(sectionHeader("Education"));
  children.push(new Paragraph({
    spacing: { after: 10 },
    keepNext: true,
    children: [run(education.qualification, { bold: true })],
  }));
  children.push(new Paragraph({
    spacing: { after: 40 },
    keepNext: true,
    children: [
      run(education.institution, { color: COLOR.muted }),
      sep(),
      run(education.dates, { color: COLOR.muted }),
      sep(),
      run(education.average, { color: COLOR.muted }),
    ],
  }));
  children.push(new Paragraph({
    spacing: { before: 40, after: 30 },
    keepNext: true,
    children: [run("Relevant coursework:", { bold: true, color: COLOR.muted })],
  }));
  cv.coursework.forEach((segs) => children.push(bulletParagraph(segmentsToRuns(segs))));

  return children;
}

function buildDocument(cv) {
  return new Document({
    creator: data.site.name,
    title: cv.docTitle,
    description: `CV of ${data.site.name}: ${cv.roleTitle}`,
    keywords: cv.roleTitle,
    numbering: {
      config: [{
        reference: BULLET_REF,
        levels: [{
          level: 0,
          format: LevelFormat.BULLET,
          text: "•",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: convertInchesToTwip(0.22), hanging: convertInchesToTwip(0.16) } } },
        }],
      }],
    },
    styles: { default: { document: { run: { font: FONT, size: SIZE, color: COLOR.text } } } },
    sections: [{
      properties: {
        page: {
          size: { width: 11906, height: 16838 }, // A4, the South African standard
          margin: {
            top: convertInchesToTwip(0.55),
            bottom: convertInchesToTwip(0.55),
            left: convertInchesToTwip(0.7),
            right: convertInchesToTwip(0.7),
          },
        },
      },
      children: buildDocxChildren(cv),
    }],
  });
}

async function main() {
  const only = process.argv[2];
  for (const cv of data.cvs) {
    if (only && cv.key !== only) continue;
    const buf = await Packer.toBuffer(buildDocument(cv));
    const outPath = path.join(OUT_DIR, `${cv.fileBase}.docx`);
    fs.writeFileSync(outPath, buf);
    console.log("wrote", path.relative(path.join(OUT_DIR, ".."), outPath));
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
