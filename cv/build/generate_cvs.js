/* generate_cvs.js — generates all CV .docx files from cv-data.json.
 *
 * Same idea as client/build/generate_pages.py: cv-data.json is the single
 * source of truth for content, this script is the single source of truth
 * for layout/design. Edit the JSON, re-run this script, never hand-edit
 * the .docx files.
 *
 * Visual language matches the portfolio site's theme, translated for print/
 * ATS: white background (not literal dark mode), Poppins for headings /
 * Inter for body (same fonts as the site), electric blue (#0A84FF) as the
 * one accent color, no gradients, no pill shapes, no em dashes.
 *
 * Usage: node generate_cvs.js
 */
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ExternalHyperlink,
  HeadingLevel, AlignmentType, BorderStyle, LevelFormat,
  convertInchesToTwip,
} = require("docx");

const DATA_PATH = path.join(__dirname, "cv-data.json");
const OUT_DIR = path.join(__dirname, "..");
const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));

const COLOR = {
  text: "1D1D1F",   // near-black body text — matches the site's light-mode text color
  muted: "6E6E73",  // secondary/meta text — matches the site's light-mode muted color
  accent: "0A84FF", // electric blue — the site's one accent color
  rule: "D9D9DE",   // faint neutral divider
};
const FONT_HEAD = "Poppins";
const FONT_BODY = "Inter";

const BULLET_REF = "cv-bullets";

function run(text, opts = {}) {
  return new TextRun({ text, font: FONT_BODY, size: 20, color: COLOR.text, ...opts });
}

function segmentsToRuns(segments, opts = {}) {
  return segments.map((s) =>
    run(s.text, { bold: !!s.bold, ...opts })
  );
}

function link(displayText, url) {
  return new ExternalHyperlink({
    link: url,
    children: [
      new TextRun({
        text: displayText,
        font: FONT_BODY,
        size: 20,
        color: COLOR.accent,
        underline: {},
      }),
    ],
  });
}

function sectionHeader(text) {
  return new Paragraph({
    spacing: { before: 180, after: 80 },
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 6, color: COLOR.accent, space: 4 },
    },
    children: [
      new TextRun({
        text: text.toUpperCase(),
        font: FONT_HEAD,
        bold: true,
        size: 20,
        color: COLOR.text,
        characterSpacing: 12,
      }),
    ],
  });
}

function bodyParagraph(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 115, line: 238 },
    children: [run(text)],
    ...opts,
  });
}

function bulletParagraph(children, indent = 0) {
  return new Paragraph({
    numbering: { reference: BULLET_REF, level: 0 },
    indent: { left: convertInchesToTwip(0.22 + indent) },
    spacing: { after: 38, line: 226 },
    children,
  });
}

function buildHeader(site, roleTitle) {
  const [firstName, ...rest] = site.name.split(" ");
  const lastName = rest.join(" ");
  return [
    new Paragraph({
      spacing: { after: 40 },
      children: [
        new TextRun({ text: firstName.toUpperCase() + " ", font: FONT_HEAD, bold: true, size: 40, color: COLOR.text }),
        new TextRun({ text: lastName.toUpperCase(), font: FONT_HEAD, bold: true, size: 40, color: COLOR.accent }),
      ],
    }),
    new Paragraph({
      spacing: { after: 95 },
      children: [
        new TextRun({ text: roleTitle, font: FONT_BODY, bold: true, size: 22, color: COLOR.muted }),
      ],
    }),
    new Paragraph({
      spacing: { before: 90, after: 180 },
      border: { top: { style: BorderStyle.SINGLE, size: 10, color: COLOR.accent, space: 8 } },
      children: [
        run(site.location, { color: COLOR.muted }),
        run("  |  ", { color: COLOR.rule }),
        run(site.phone, { color: COLOR.muted }),
        run("  |  ", { color: COLOR.rule }),
        link(site.email, `mailto:${site.email}`),
        run("  |  ", { color: COLOR.rule }),
        link(site.linkedinDisplay, site.linkedinUrl),
        run("  |  ", { color: COLOR.rule }),
        link(site.githubDisplay, `https://${site.githubDisplay}`),
      ],
    }),
  ];
}

function buildProject(project) {
  const paras = [
    new Paragraph({
      spacing: { before: 95, after: 12 },
      children: [
        new TextRun({ text: project.name, font: FONT_HEAD, bold: true, size: 21, color: COLOR.text }),
      ],
    }),
    new Paragraph({
      spacing: { after: 50 },
      children: [
        run(project.techLabel || "Tech: ", { bold: true, color: COLOR.muted, italics: true }),
        run(project.tech, { color: COLOR.muted, italics: true }),
      ],
    }),
    bodyParagraph(project.description, { spacing: { after: project.bullets && project.bullets.length ? 38 : 65 } }),
  ];
  (project.bullets || []).forEach((b) => paras.push(bulletParagraph([run(b)])));
  if (project.github) {
    paras.push(
      new Paragraph({
        spacing: { after: 100 },
        children: [run("GitHub: ", { bold: true, color: COLOR.muted }), link(project.github, `https://${project.github}`)],
      })
    );
  } else {
    paras.push(new Paragraph({ spacing: { after: 100 }, children: [] }));
  }
  return paras;
}

function buildDocxChildren(cv, site, education) {
  const children = [];
  children.push(...buildHeader(site, cv.roleTitle));

  children.push(sectionHeader("Professional Summary"));
  children.push(bodyParagraph(cv.summary));

  children.push(sectionHeader("Technical Skills"));
  cv.skills.forEach((segs) => children.push(bulletParagraph(segmentsToRuns(segs))));

  cv.projectSections.forEach((section) => {
    children.push(sectionHeader(section.title));
    section.projects.forEach((project) => children.push(...buildProject(project)));
  });

  children.push(sectionHeader("Relevant Coursework"));
  cv.coursework.forEach((segs) => children.push(bulletParagraph(segmentsToRuns(segs))));

  children.push(sectionHeader("Education"));
  children.push(
    new Paragraph({
      spacing: { after: 20 },
      children: [new TextRun({ text: education.qualification, font: FONT_BODY, bold: true, size: 20, color: COLOR.text })],
    })
  );
  children.push(
    new Paragraph({
      spacing: { after: 0 },
      children: [
        run(education.institution, { color: COLOR.muted }),
        run("  |  ", { color: COLOR.rule }),
        run(education.average, { color: COLOR.muted }),
      ],
    })
  );

  return children;
}

function buildDocument(cv, site, education) {
  return new Document({
    numbering: {
      config: [
        {
          reference: BULLET_REF,
          levels: [
            {
              level: 0,
              format: LevelFormat.BULLET,
              text: "•",
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: convertInchesToTwip(0.22), hanging: convertInchesToTwip(0.18) } } },
            },
          ],
        },
      ],
    },
    styles: {
      default: {
        document: { run: { font: FONT_BODY, size: 20, color: COLOR.text } },
      },
    },
    sections: [
      {
        properties: {
          page: {
            margin: {
              top: convertInchesToTwip(0.45),
              bottom: convertInchesToTwip(0.45),
              left: convertInchesToTwip(0.65),
              right: convertInchesToTwip(0.65),
            },
          },
        },
        children: buildDocxChildren(cv, site, education),
      },
    ],
  });
}

async function main() {
  for (const cv of data.cvs) {
    const doc = buildDocument(cv, data.site, data.education);
    const buf = await Packer.toBuffer(doc);
    const outPath = path.join(OUT_DIR, `${cv.fileBase}.docx`);
    fs.writeFileSync(outPath, buf);
    console.log("wrote", path.relative(path.join(OUT_DIR, ".."), outPath));
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
