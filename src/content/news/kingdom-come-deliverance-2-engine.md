---
title: 'Warhorse Studios Details Kingdom Come: Deliverance II CryEngine Physics &
  Combat'
date: '2026-07-21'
gameTitle: 'Kingdom Come: Deliverance II'
developer: Warhorse Studios / Deep Silver
genre: RPG
platforms:
- PC
- PS5
- Xbox Series X|S
releaseWindow: February 11, 2026
heroImage: /covers/kingdom-come-deliverance-2-engine.png
impactScore: 9
sourceUrl: https://www.kingdomcomerpg.com/
summary: Warhorse Studios outlines expanded 15th-century Bohemia map size, crossbow
  mechanics, gunpowder weaponry, and CryEngine physics improvements.
specs:
  minimum: Intel Core i5-8400 / AMD Ryzen 5 2600, 16 GB RAM, NVIDIA GTX 1060 (6GB)
  recommended: Intel Core i7-12700K / AMD Ryzen 7 5800X3D, 32 GB RAM, NVIDIA RTX 3080
---

Warhorse Studios has released a technical overview of *Kingdom Come: Deliverance II*, detailing improvements to the directional swordplay combat engine along with the addition of early gunpowder firearms and crossbows. For a genre that has spent the last decade converging on a single combat grammar — light attack, heavy attack, dodge-roll, finisher — the overview is a quiet but pointed reassertion of a different design philosophy: combat as a *simulation* of a historical martial practice, not a stylized rhythm game.

## Combat & World Simulation

- **Crossbows & Early Firearms**: Long-range engagements introduce realistic reload animations, armor-penetrating bolts, and smoke field effects from hand cannons.
- **Directional Combat Engine**: The directional attack star returns with updated parry windows, master strikes, and stamina management mechanics.
- **Expanded Map Scope**: Two distinct map regions (including Kuttenberg city) double the geographical area of the original title.

## Crime & Reputation AI

Town guard AI utilizes long-term crime memory. Committing infractions in one district alerts neighboring watch posts via alarm bells.

## Why it matters: the sim-RPG bet, renewed

The original *Kingdom Come: Deliverance* was a commercial long shot — a Czech studio insisting that clunky directional swordplay, diegetic UI, and a genuine 15th-century setting could carry a 40-hour RPG. It sold well enough to fund a sequel with a markedly larger scope. The technical overview tells us Warhorse is doubling down on the same bet rather than smoothing the edges toward the genre mainstream. The directional attack star, master strikes, and stamina management are all returning, which means the studio is keeping the input grammar that divided players the first time and refining it rather than replacing it.

That is the meaningful signal. The AAA RPG market has largely settled on a control schema inherited from *The Witcher 3* and refined by *God of War*: context-sensitive light/heavy strings, i-frames on dodge, generous parry windows. Warhorse is declining that schema. The directional combat system asks the player to choose an attack angle, read the defender's guard, and commit — closer to a fighting game's neutral game than an action-RPG's combo chain. Refined parry windows and master strikes suggest the sequel is investing in *readability* (can you see the opening?) rather than *leniency* (can you mash through it?). That is a niche play, but it is the niche the franchise owns.

## What the gunpowder transition actually changes

The addition of crossbows and early hand cannons is not just a weapon-type list expansion — it threads the late-medieval military transition into the combat economy. Armor-penetrating bolts and gunpowder weapons change the cost calculus of engagement: a heavily armored knight who was effectively a damage sponge under melee rules now has a counter in ranged armor penetration, and the smoke field effects from hand cannons introduce a visibility variable that melee-only systems never had to model.

For an RPG built on a stamina-and-stance melee loop, that is a real systems perturbation. It opens ranged kiting as a viable playstyle, changes the value of heavy armor (the thing the first game's crafting and repair economy was built around), and gives the encounter designers a lever to pull for difficulty without simply inflating enemy HP. The reload animations being "realistic" rather than animation-canceled also tells you the design intent: ranged power is gated by *time* and *exposure*, the same way melee power is gated by stamina. The two systems share an economy, which is the thing that makes a combat sandbox feel coherent rather than like a menu of unrelated weapons.

## CryEngine, and what the recommended spec is telling you

Warhorse remains on CryEngine — a choice worth noting at a time when the mid-budget RPG market has been migrating wholesale to Unreal Engine 5. CryEngine's longstanding strengths are exactly what an open-world historical sim needs: dense foliage, large terrain streaming, and physically-grounded rendering. The cost is tooling maturity and the engineering burden of maintaining a bespoke pipeline, which is why most studios without a Crytek heritage have left.

The recommended specification — an Intel Core i7-12700K or AMD Ryzen 7 5800X3D, 32 GB of RAM, and an NVIDIA RTX 3080 — is the part of the overview that should make hardware-conscious players sit up. A 3080 / 32 GB target for a February 2026 release is steep but not unreasonable for an open-world CryEngine title pushing dense vegetation and a doubled map. The minimum spec (GTX 1060 6GB, 16 GB RAM) is genuinely accessible and tells you the floor is a 2018-era mid-range machine — but the gap between minimum and recommended is wider than most contemporaries, which is the tell: this engine is doing meaningful CPU-side simulation work (crime memory, guard alerting, physics) that scales hard with the world state, not just GPU-side pretty.

## What the crime AI signals about systemic ambition

The crime and reputation detail — long-term guard memory, alarm bells propagating alerts between neighboring watch posts — is easy to read as flavor. It is more than that. Long-term memory means the world state persists your infractions across time, not just across a single chase; alarm-bell propagation means the alert is a *spatially routed* event, not a global aggro flag. Both are the building blocks of an immersive-sim adjacent reactivity layer — the kind of systemic behavior that *Dishonored* and *Deus Ex* trade in, transplanted into a historical open world.

Doubled map scope, with Kuttenberg as a distinct second region, is the other half of that equation. A systemic crime model only earns its complexity if the world is large enough for district-level reputation to mean something — if guards in one city don't know you, but the watch in the next town does. Two regions is the minimum viable geometry for that kind of cross-jurisdiction reactivity to pay off.

## The take

The overview reads as a studio that knows exactly what kind of game it is making and is spending its sequel budget on *depth* rather than *reach*. Refined combat readability, a ranged layer that shares the melee economy, a systemic crime model, and a doubled map are all vertical investments in the same sim-RPG thesis. The risk is the same as the first game's: a control and systems grammar that is genuinely harder to learn than the genre default, and a hardware ask that narrows the PC audience at the high end. The upside is that there is no other AAA RPG competing in this exact lane. *Kingdom Come: Deliverance II* is not trying to out-*Skyrim* Bethesda or out-cinematic-*Witcher* CD Projekt. It is trying to be the only game that does *this* — and the technical overview suggests it intends to do it more completely than the first one did.