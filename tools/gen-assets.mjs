// Brand asset generator for MNEURIX // QUEST.
// Produces favicon.svg, apple-touch-icon.png, and og-image.png into public/.
// Usage: node tools/gen-assets.mjs   (requires `sharp` as a devDependency)
//
// Design language:
//   --bg #0a0d12  --bg-card #0b0e14  --cyan #5eead4  --sky #38bdf8
//   --violet #a855f7  --emerald #10b981  --amber #f59e0b
//   --text-heading #f8fafc  --text-muted #8a94a6
//   mono: ui-monospace, Menlo, Consolas, 'Segoe UI', monospace
//   sans: -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif
//
// The radar reticle motif encodes the "intelligence radar" positioning.

import sharp from "sharp";
import { writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.resolve(__dirname, "..", "public");

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

// ---- Radar reticle (pure geometry, no font dependency) ----
// size: square edge length. Returns an SVG <g> string centered at (size/2, size/2).
function radarReticle(size, stroke, accent = CYAN) {
	const c = size / 2;
	const rOuter = size * 0.4;
	const rMid = size * 0.26;
	const rDot = size * 0.05;
	const arm = size * 0.46;
	return `
  <g stroke="${accent}" fill="none" stroke-width="${stroke}" stroke-linecap="round">
    <circle cx="${c}" cy="${c}" r="${rOuter}" opacity="0.55"/>
    <circle cx="${c}" cy="${c}" r="${rMid}" opacity="0.9"/>
    <line x1="${c - arm}" y1="${c}" x2="${c + arm}" y2="${c}" opacity="0.5"/>
    <line x1="${c}" y1="${c - arm}" x2="${c}" y2="${c + arm}" opacity="0.5"/>
    <circle cx="${c}" cy="${c}" r="${rDot}" fill="${accent}" stroke="none"/>
    <!-- radar sweep wedge -->
    <path d="M ${c} ${c} L ${c} ${c - rOuter} A ${rOuter} ${rOuter} 0 0 1 ${c + rOuter * Math.sin(Math.PI / 6)} ${c - rOuter * Math.cos(Math.PI / 6)} Z" fill="${accent}" opacity="0.14" stroke="none"/>
  </g>`;
}

// ---- favicon.svg (vector, crisp at 16px) ----
const faviconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <rect x="1.5" y="1.5" width="61" height="61" rx="14" fill="${BG}" stroke="${CYAN}" stroke-width="2"/>
  ${radarReticle(64, 2.5)}
</svg>`;

// ---- apple-touch-icon.png (180x180, iOS masks corners) ----
const appleTouchSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180" width="180" height="180">
  <rect x="0" y="0" width="180" height="180" fill="${BG}"/>
  ${radarReticle(180, 6)}
</svg>`;

// ---- og-image.png (1200x630 branded banner) ----
const ogSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <defs>
    <linearGradient id="bggrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0a0d12"/>
      <stop offset="1" stop-color="#0b0e14"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.82" cy="0.5" r="0.5">
      <stop offset="0" stop-color="${CYAN}" stop-opacity="0.10"/>
      <stop offset="1" stop-color="${CYAN}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="${CYAN}" stroke-width="1" opacity="0.05"/>
    </pattern>
  </defs>

  <rect x="0" y="0" width="1200" height="630" fill="url(#bggrad)"/>
  <rect x="0" y="0" width="1200" height="630" fill="url(#grid)"/>
  <rect x="0" y="0" width="1200" height="630" fill="url(#glow)"/>
  <rect x="24" y="24" width="1152" height="582" rx="18" fill="none" stroke="${CYAN}" stroke-width="2" opacity="0.35"/>

  <!-- eyebrow -->
  <text x="72" y="96" font-family="${MONO}" font-size="20" letter-spacing="3" fill="${CYAN}">AUTONOMOUS R&amp;D INTELLIGENCE RADAR</text>

  <!-- wordmark -->
  <text x="68" y="250" font-family="${MONO}" font-size="84" font-weight="700" letter-spacing="2" fill="${HEADING}">MNEURIX<tspan fill="${CYAN}"> // </tspan>QUEST</text>

  <!-- tagline -->
  <text x="72" y="312" font-family="${SANS}" font-size="30" fill="${MUTED}">Systems for Mind, Play &amp; Gaming Intelligence</text>

  <!-- sector pills -->
  <g font-family="${MONO}" font-size="22" font-weight="600">
    <rect x="72"  y="372" width="118" height="46" rx="10" fill="none" stroke="${SKY}"     stroke-width="2" opacity="0.7"/><text x="131" y="402" text-anchor="middle" fill="${SKY}">RTS</text>
    <rect x="202" y="372" width="128" height="46" rx="10" fill="none" stroke="${EMERALD}" stroke-width="2" opacity="0.7"/><text x="266" y="402" text-anchor="middle" fill="${EMERALD}">MMO</text>
    <rect x="344" y="372" width="128" height="46" rx="10" fill="none" stroke="${VIOLET}"  stroke-width="2" opacity="0.7"/><text x="408" y="402" text-anchor="middle" fill="${VIOLET}">RPG</text>
    <rect x="486" y="372" width="220" height="46" rx="10" fill="none" stroke="${AMBER}"   stroke-width="2" opacity="0.7"/><text x="596" y="402" text-anchor="middle" fill="${AMBER}">HARDWARE</text>
  </g>

  <!-- value props -->
  <g font-family="${SANS}" font-size="22" fill="${MUTED}">
    <text x="72" y="470">High-signal press release intelligence · technical engine analyses</text>
    <text x="72" y="506">· hardware silicon benchmarks for RTS, MMO &amp; RPG gaming.</text>
  </g>

  <!-- domain footer -->
  <text x="72" y="568" font-family="${MONO}" font-size="22" fill="${CYAN}" letter-spacing="2">MNEURIX.QUEST</text>

  <!-- radar reticle on the right -->
  <g transform="translate(960, 315) scale(1.6)">
    <g transform="translate(-200, -200)">
      ${radarReticle(400, 8)}
    </g>
  </g>
</svg>`;

async function main() {
	await writeFile(path.join(outDir, "favicon.svg"), faviconSvg, "utf8");
	await sharp(Buffer.from(appleTouchSvg))
		.png()
		.toFile(path.join(outDir, "apple-touch-icon.png"));
	await sharp(Buffer.from(ogSvg))
		.png({ quality: 90, compressionLevel: 9 })
		.toFile(path.join(outDir, "og-image.png"));
	console.log(
		"✓ Generated public/favicon.svg, public/apple-touch-icon.png, public/og-image.png",
	);
}

main().catch((e) => {
	console.error(e);
	process.exit(1);
});
