// Branded cover generator for MNEURIX // QUEST article hero images.
// Renders deterministic, on-brand 1200x630 PNG covers (radar motif + game title +
// genre pill) into public/covers/. Used as the branded fallback in the thumbnail
// policy (official-first -> AI-QA -> branded). No AI, no stock, always coherent.
//
// Usage:
//   node tools/gen-covers.mjs <spec.json>
//   node tools/gen-covers.mjs --single <slug> <gameTitle> <genre>
//
// spec.json = [ {slug, gameTitle, genre}, ... ]  -> public/covers/<slug>.png

import sharp from "sharp";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT_DIR = path.resolve(__dirname, "..", "public", "covers");

const CYAN = "#5eead4";
const SKY = "#38bdf8";
const VIOLET = "#a855f7";
const EMERALD = "#10b981";
const AMBER = "#f59e0b";
const BG = "#0a0d12";
const HEADING = "#f8fafc";
const MUTED = "#8a94a6";
const MONO = `ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace`;
const SANS = `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`;

const GENRE_COLOR = { RTS: SKY, MMO: EMERALD, RPG: VIOLET, HARDWARE: AMBER };

function radarReticle(size, stroke, accent = CYAN) {
  const c = size / 2;
  const rOuter = size * 0.4;
  const rMid = size * 0.26;
  const rDot = size * 0.05;
  const arm = size * 0.46;
  const sweepX = c + rOuter * Math.sin(Math.PI / 6);
  const sweepY = c - rOuter * Math.cos(Math.PI / 6);
  return `
  <g stroke="${accent}" fill="none" stroke-width="${stroke}" stroke-linecap="round">
    <circle cx="${c}" cy="${c}" r="${rOuter}" opacity="0.55"/>
    <circle cx="${c}" cy="${c}" r="${rMid}" opacity="0.9"/>
    <line x1="${c - arm}" y1="${c}" x2="${c + arm}" y2="${c}" opacity="0.5"/>
    <line x1="${c}" y1="${c - arm}" x2="${c}" y2="${c + arm}" opacity="0.5"/>
    <circle cx="${c}" cy="${c}" r="${rDot}" fill="${accent}" stroke="none"/>
    <path d="M ${c} ${c} L ${c} ${c - rOuter} A ${rOuter} ${rOuter} 0 0 1 ${sweepX} ${sweepY} Z" fill="${accent}" opacity="0.14" stroke="none"/>
  </g>`;
}

// Word-wrap a title into <=3 lines of <= ~34 chars for the cover layout.
function wrapTitle(title) {
  const max = 34;
  const words = String(title || "").split(/\s+/).filter(Boolean);
  const lines = [];
  let cur = "";
  for (const w of words) {
    if ((cur + " " + w).trim().length > max && cur) {
      lines.push(cur);
      cur = w;
    } else {
      cur = (cur + " " + w).trim();
    }
  }
  if (cur) lines.push(cur);
  return lines.slice(0, 3);
}

function coverSvg(gameTitle, genre) {
  const genreColor = GENRE_COLOR[genre] || CYAN;
  const lines = wrapTitle(gameTitle);
  const lineH = 46;
  const startY = 300 - ((lines.length - 1) * lineH) / 2;
  const titleTspans = lines
    .map((ln, i) => `<text x="72" y="${startY + i * lineH}" font-family="${SANS}" font-size="40" font-weight="700" fill="${HEADING}">${escapeXml(ln)}</text>`)
    .join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="${BG}"/><stop offset="1" stop-color="#0b0e14"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="${CYAN}" stroke-width="1" opacity="0.05"/>
    </pattern>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect width="1200" height="630" fill="url(#grid)"/>
  <rect x="24" y="24" width="1152" height="582" rx="18" fill="none" stroke="${CYAN}" stroke-width="2" opacity="0.3"/>
  <text x="72" y="92" font-family="${MONO}" font-size="20" letter-spacing="3" fill="${CYAN}">MNEURIX // QUEST INTEL</text>
  <rect x="72" y="498" width="${Math.min(40 + genre.length * 13, 260)}" height="44" rx="10" fill="none" stroke="${genreColor}" stroke-width="2" opacity="0.8"/>
  <text x="${72 + 20 + genre.length * 6.5}" y="526" text-anchor="middle" font-family="${MONO}" font-size="22" font-weight="600" fill="${genreColor}">${escapeXml(genre)}</text>
  ${titleTspans}
  <g transform="translate(960, 315)">
    <g transform="translate(-180, -180)">${radarReticle(360, 7, genreColor)}</g>
  </g>
</svg>`;
}

function escapeXml(s) {
  return String(s).replace(/[<>&'"]/g, (ch) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;" }[ch]));
}

async function renderOne(slug, gameTitle, genre) {
  const svg = coverSvg(gameTitle, genre);
  const outPath = path.join(OUT_DIR, `${slug}.png`);
  await sharp(Buffer.from(svg)).png({ quality: 90, compressionLevel: 9 }).toFile(outPath);
  return outPath;
}

async function main() {
  await mkdir(OUT_DIR, { recursive: true });
  let specs;
  if (process.argv[2] === "--single") {
    specs = [{ slug: process.argv[3], gameTitle: process.argv[4], genre: process.argv[5] || "RPG" }];
  } else {
    const raw = await readFile(process.argv[2], "utf8");
    specs = JSON.parse(raw);
  }
  for (const s of specs) {
    if (!s.slug || !s.gameTitle) continue;
    const out = await renderOne(s.slug, s.gameTitle, s.genre || "RPG");
    console.log(`✓ ${out}`);
  }
}

main().catch((e) => { console.error(e); process.exit(1); });