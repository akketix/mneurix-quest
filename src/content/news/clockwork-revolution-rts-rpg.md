---
title: inXile Entertainment Outlines Clockwork Revolution Time-Bending Steam Engine
date: '2026-07-25'
gameTitle: Clockwork Revolution
developer: inXile Entertainment / Xbox Game Studios
genre: RPG
platforms:
- PC
- Xbox Series X|S
releaseWindow: 2026 Target
heroImage: /covers/clockwork-revolution-rts-rpg.jpg
impactScore: 9
sourceUrl: https://www.xbox.com/en-US/games/clockwork-revolution
summary: inXile Entertainment details time-travel Chronometer mechanics, steampunk
  city reactivity in Avalon, and Unreal Engine 5 rendering.
specs:
  minimum: Intel Core i5-8400 / AMD Ryzen 5 2600, 16 GB RAM, NVIDIA GTX 1070
  recommended: Intel Core i7-11700K / AMD Ryzen 7 5800X, 16 GB RAM, NVIDIA RTX 3080
---




inXile Entertainment (creators of *Wasteland 3*) has detailed core gameplay mechanics for *Clockwork Revolution*, a first-person steampunk action RPG set in the Victorian metropolis of Avalon.

## Chronometer & Time Mechanics

- **Chronometer Travel**: Using a mysterious time-travel device, players travel back to key historical moments in Avalon's past to alter events, instantly transforming present-day city architecture and NPC lives.
- **Steampunk Armaments**: Weapons combine steam-powered mechanics with custom ammunition types, including lightning revolvers, steam cannons, and temporal grenades.
- **Reactive World Systems**: Altering past events reshapes city district wealth distributions, political rulers, and companion relationships.

## Production Status

inXile confirmed that development is progressing steadily on Unreal Engine 5, featuring advanced particle physics and detailed brass automaton animations.

## Why the Chronometer is a bigger deal than it sounds

Time travel in games is usually a narrative device — a cutscene trigger, a level theme, or a checkpoint gimmick. What inXile is describing here is something structurally different: time travel as a *simulation input*. The distinction matters enormously. When altering a historical moment "instantly transforms present-day city architecture and NPC lives," you're not talking about swapping a skybox or re-dressing a set piece. You're talking about a persistent world-state system that has to track cause and effect across two parallel versions of the same city, then render both coherently.

The closest genre precedent is dishonored-style mission reactivity or the timeline shifts of a *Titanfall 2* set piece — but those are scripted, linear transformations. inXile's pitch implies that district wealth distributions, political rulers, and companion relationships all hang off the same dependency graph. If that graph is real — and *Wasteland 3*'s faction and consequence systems suggest inXile knows how to build one — then the Chronometer isn't a mechanic bolted onto an RPG. It is the RPG's systemic backbone, and every quest, vendor, and companion arc has to be authored twice: once for each state of Avalon.

That is an enormous content-multiplication problem, and it's the single most important thing to watch between now and release. Games that promise stateful worlds live or die on how many states actually exist. Two timelines with deep reactivity will feel revolutionary. Two timelines with cosmetic differences will feel like a reskin.

## Context: where this sits in inXile's trajectory

inXile's identity under Xbox Game Studios has been quietly shifting. The studio built its reputation on isometric, party-based CRPGs — *Wasteland 2* and *Wasteland 3*, games where consequence modeling was the core competency and rendering fidelity was very much not. *Clockwork Revolution* is the second major pivot in the studio's modern era (after the VR-first *Frostpoint* experiment) and the first aimed at the audience *The Outer Worlds* carved out: the first-person reactive RPG with a strong art identity.

That puts it in direct conversation with Obsidian's output — which is notable, because Obsidian and inXile are sister studios under the same Xbox RPG umbrella. If *Clockwork Revolution* lands its world-state ambitions, Xbox will effectively hold the two most consequential first-person reactive RPG pipelines in the industry simultaneously. The more interesting question is differentiation: where *Avowed* and *The Outer Worlds* lean on zone-based exploration, Avalon appears to be a single dense metropolis whose reactivity is the point. Vertical density over horizontal sprawl is a deliberate cost-shaping decision — it lets a mid-sized team pour budget into simulation depth rather than square kilometers of terrain.

## What the hardware specs actually tell us

The published PC requirements are unusually revealing for a game this far from release. A GTX 1070 minimum and RTX 3080 recommended is a wide spread — roughly a full GPU generation and two performance tiers apart — and it suggests inXile is scaling the same content across very different fidelity budgets rather than gating features behind hardware.

A few readings:

- **The min-spec is honest about UE5's baseline.** An i5-8400 / Ryzen 5 2600 with a GTX 1070 means the game is not leaning on Nanite/virtualized-geometry extremes or hardware ray tracing as a requirement. Brass automatons, particle-heavy steam effects, and dense Victorian interiors are achievable on rasterized pipelines if the art direction carries the weight — which steampunk, with its hard-surface geometry and baked-in grime, happens to do exceptionally well.
- **The 3080 recommendation is about effects density, not geometry.** Advanced particle physics is one of the confirmed focuses, and temporal-transformation sequences — a city's architecture reflowing in real time — are exactly the kind of shader-and-effect load that justifies a four-tier GPU jump between min and rec without changing the underlying game.
- **16 GB across both tiers** is now the de facto floor for systemic RPGs. World-state graphs, reactive NPC schedules, and dual-timeline assets have memory costs that don't scale down with resolution. Don't expect that number to move.

For players on mid-range 2018-era hardware, the practical takeaway is that *Clockwork Revolution* looks designed to be completed on a GTX 1070-class machine — but the spectacle moments, which are the marketing, are where the extra silicon goes.

## The take

The Chronometer concept is the most mechanically ambitious premise inXile has ever shipped, and also the riskiest. Reactive-world promises are the cheapest currency in RPG marketing, and the gap between "alters NPC lives" in a press bullet and "alters NPC lives" in a 60-hour playthrough is where most ambitious RPGs quietly downsize. What buys inXile credibility is track record: *Wasteland 3* shipped genuinely divergent faction outcomes and endgame states, on a fraction of this budget, without collapsing under its own branching.

The real bet is architectural. If inXile has built Avalon's world state as a single queryable graph — where wealth, politics, and relationships are data, not scripts — then the Chronometer becomes an interface onto deep systems rather than a gimmick. If it's a collection of bespoke toggles, the game will feel shallow by act two regardless of how good the lightning revolvers feel.

What it signals: Xbox Game Studios is funding inXile to compete in first-person reactive RPGs at a scope the studio has never attempted, and it's doing so on systems design rather than open-world acreage. With a 2026 target and UE5 as the foundation, this is one of the few remaining big-budget attempts at the *immersive*-sim-adjacent single-city RPG — a design space the industry keeps circling and rarely commits to. We'll be tracking whether the timeline reactivity survives contact with a full vertical slice; that's the moment this game either becomes the genre's next reference point or its next cautionary tale.
