# Image Prompting & Curation Best Practices for Gaming & Hardware Intelligence

This guide establishes the mandatory **Image Prompting & Curation Protocol** for autonomous publishing agents operating on **`mneurix.quest`**.

---

## 1. Core Visual Principles for Gaming & Hardware News

To deliver a premium, high-signal experience that WOWs gamers and hardware enthusiasts, all hero cover art must adhere to these core visual principles:

### 1. Lore & Universe Accuracy (Zero Anachronisms or Contradictions)
- ❌ **Anti-Pattern**: Using desert imagery with trees for a *Dune: Spice Wars* article (Arrakis is a desert planet with zero trees).
- ✅ **Best Practice**: Pure, endless golden sand dunes with zero vegetation.
- ❌ **Anti-Pattern**: Using futuristic sci-fi armor for *Kingdom Come: Deliverance II* (15th-century medieval Bohemia).
- ✅ **Best Practice**: Authentic 15th-century steel broadswords and plate armor.

### 2. Subject-Specific Precision (No Generic Abstract Imagery)
- ❌ **Anti-Pattern**: Using generic blue server racks or stock light trails for a DDR5 RAM article.
- ✅ **Best Practice**: Using a macro close-up shot of RGB DDR5 RAM sticks mounted on an ATX motherboard or a silicon wafer DRAM die.

### 3. High Contrast & Dark Theme Harmony
- Images must feature rich, vibrant colors set against dark, cinematic backgrounds to seamlessly complement our dark mode design system (`#0a0d12`, `#5eead4` cyan, `#38bdf8` sky blue, `#a855f7` violet).

### 4. Aspect Ratio & Resolution Standards
- **Aspect Ratio**: 16:9 widescreen format (`1200x675` or `1920x1080`).
- **Compression**: WebP / JPG formatted with `q=80` and `auto=format&fit=crop`.

---

## 2. Sector-by-Sector Prompting Templates

### A. HARDWARE & Silicon Sector
- **Keywords**: Macro lens, extreme close-up, circuit traces, silicon wafer, RGB heatsink, copper heat pipes, gold pins, ATX motherboard socket.
- **Example Prompt**: `"Macro photography of high-performance RGB DDR5 memory sticks seated in a black gaming motherboard slot, cinematic dark lighting, vibrant neon cyan accents, 8k resolution"`

### B. RTS (Real-Time Strategy) Sector
- **Keywords**: Isometric perspective, base building, resource refineries, sci-fi military command center, laser turrets, tactical fog of war, tree-free desert dunes (for Dune).
- **Example Prompt**: `"Vast endless golden desert sand dunes under a harsh sun, zero trees, cinematic Dune desert planet Arrakis landscape"`

### C. MMO Radar Sector
- **Keywords**: Grand scale landscape, subterranean crystalline caverns, massive raid boss encounter, mystical portals, high fantasy spires.
- **Example Prompt**: `"A grand subterranean fantasy cavern with giant luminescent purple crystals and a towering ancient stone portal, cinematic fog, epic scale MMO raid environment"`

### D. RPG Devlog Sector
- **Keywords**: Atmospheric lighting, dark fantasy gothic architecture, elemental spellcasting, ancient temple ruins, medieval knight armor.
- **Example Prompt**: `"Dark gothic fantasy cathedral courtyard illuminated by blue spell runes and moonlight, high-detail dark fantasy RPG environment"`

---

## 3. Negative Prompt & Quality Exclusion List

Autonomous image generation and curation engines MUST append the following negative quality rules:

```text
Negative Rules: trees in Arrakis/Dune, anachronisms, blurry, low-resolution, generic stock photo, white background, watermarked, text overlay, distorted geometry, overexposed, washed out colors, generic corporate office.
```

---

## 4. Integration into Agent Pipeline

This guidance is embedded directly into:
- `AGENT_INSTRUCTIONS.md` (Root protocol for LLM agents)
- `pipeline/publisher.py` (Automated markdown publisher image resolution step)
