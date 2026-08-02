# MNEURIX // QUEST — Autonomous Agent Editorial Protocol

This guide defines the explicit operational rules, schemas, and workflow for autonomous agents modifying or generating content for **`mneurix.quest`**.

---

## 1. Target Domain & Mission

- **Domain**: `https://mneurix.quest`
- **Focus**: Real-Time Strategy (**RTS**), Massively Multiplayer Online (**MMO**), Role-Playing Games (**RPG**), and **Gaming Hardware Silicon**.
- **Core Value**: High-signal, objective press release intelligence. Zero low-effort "AI slop" or buzzword filler.

---

## 2. Strict Content Schema (Astro Frontmatter)

Every generated article file MUST be placed in `src/content/news/{slug}.md` and MUST adhere to this exact YAML frontmatter structure:

```yaml
---
title: "Exact Descriptive Article Title"
date: "YYYY-MM-DD"
gameTitle: "Official Game Name or Hardware Target"
developer: "Developer, Publisher, or Manufacturer"
genre: "RTS" | "MMO" | "RPG" | "HARDWARE"
platforms: ["PC", "PS5", "Xbox Series X|S"]
releaseWindow: "Q4 2026" or "Available Now"
heroImage: "https://valid-image-url.jpg"
trailerId: "YouTube_Video_ID" (optional)
impactScore: 8 (Integer 1-10)
sourceUrl: "https://verified-press-release-url.com"
summary: "Single concise sentence summarizing the main news break."
specs:
  minimum: "Intel Core i5-8400, 16 GB RAM, GTX 1060"
  recommended: "Intel Core i7-12700K, 32 GB RAM, RTX 3070"
---

Article markdown body prose starts here...
```

---

## 3. Banned AI Words Directive

Agents generating content **MUST NOT** include any of the following cliché terms or phrases:

- ❌ `delve into` / `delve`
- ❌ `testament to`
- ❌ `game-changer`
- ❌ `tapestry`
- ❌ `poised to`
- ❌ `beacon` / `nestled`
- ❌ `revolutionize` / `groundbreaking`
- ❌ `seamlessly` / `breathtaking`

---

## 4. Image Prompting & Curation Protocol

Agents selecting or generating hero cover art MUST follow the rules in `IMAGE_PROMPTING_GUIDANCE.md`:

- **Hardware Articles**: MUST use a macro close-up of RAM sticks, memory slots, silicon wafers, or motherboard sockets (e.g. `https://images.unsplash.com/photo-1587202372775-e229f172b9d7?q=80&w=1200&auto=format&fit=crop`).
- **No Generic Abstract Imagery**: Never use generic stock light trails or abstract blue servers for specific hardware pieces.
- **Negative Quality Rules**: Exclude watermarks, blurry textures, white backgrounds, and low-contrast stock photos.

---

## 5. Execution Commands

### Ingest & Generate Dry Run
```bash
python pipeline/run_pipeline.py --dry-run
```

### Ingest & Generate via Local Ollama
```bash
python pipeline/run_pipeline.py --provider ollama
```

### Build & Validate Site HTML locally
```bash
npm run build
```

---

## 6. Automated Git Commit & Deployment Trigger

When a new article passes validation, publish it to Git:

```bash
git add src/content/news/
git commit -m "feat(news): add new intelligence report for [GameTitle]"
git push origin main
```
*DigitalOcean App Platform auto-detects the push and deploys to `mneurix.quest`.*
