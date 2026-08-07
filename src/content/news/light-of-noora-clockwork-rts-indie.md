---
title: Unusual Fish Outlines Light of Noora Deterministic Rollback Lockstep Netcode
date: '2026-07-29'
gameTitle: Light of Noora
developer: Unusual Fish / Indie RTS
genre: RTS
platforms:
- PC
releaseWindow: Q4 2026 Target
heroImage: /covers/light-of-noora-clockwork-rts-indie.png
impactScore: 8
sourceUrl: https://mneurix.quest/genre/rts
summary: Unusual Fish details deterministic lockstep simulation, rollback netcode
  frame prediction, and esports spectating APIs for Light of Noora.
specs:
  minimum: Intel Core i3-10100 / AMD Ryzen 3 3100, 8 GB RAM, NVIDIA GTX 1050 Ti
  recommended: Intel Core i5-12400 / AMD Ryzen 5 5600, 16 GB RAM, NVIDIA GTX 1660
    Super
---


Indie developer Unusual Fish has released technical blog posts for *Light of Noora*, a competitive fast-paced RTS built around zero-latency rollback netcode and high-APM micro-management. The disclosure is notable less for any single feature than for the combination: a solo-to-small-team studio openly committing to the hardest networking problem in the genre, on a custom engine, with an esports spectating layer already specified. That is a stack most indie RTS projects either defer to post-launch or quietly abandon.

## 1. Rollback Netcode in Real-Time Strategy

While fighting games adopted rollback netcode years ago, RTS titles traditionally relied on lockstep networking, where high ping causes unit input delays. *Light of Noora* solves this via deterministic rollback prediction:

- **Input Frame Prediction**: Unit commands execute locally on frame 0 while client sockets reconcile opponent inputs across network ticks.
- **State Rewind & Resimulation**: If a network packet drops, the engine rewinds simulation states up to 4 frames silently, preventing input lag during intense 1v1 micro battles.

### Why rollback in RTS is a different problem than in fighting games

The headline framing — "rollback for RTS" — risks understating what makes this hard. In a 2D fighter, the simulation state is small: two characters, a fixed stage, a handful of active hitboxes. Rewinding and resimulating a few frames is cheap, and the visual feedback window is short enough that most players never consciously notice the correction.

An RTS inverts every one of those assumptions. The state space is large and structurally coupled: hundreds of units, pathing graphs, fog-of-war visibility, projectile pools, and resource economies that compound nonlinearly. Rewinding "up to 4 frames" sounds modest, but resimulating even a handful of ticks across a full unit population means the determinism contract has to be airtight — same floats, same iteration order, same hash for every entity on every client. A single non-deterministic RNG call, a platform-dependent math intrinsic, or an out-of-order map iteration desyncs the match. The fact that Unusual Fish is building a custom engine rather than bolting this onto an existing RTS framework is consistent with the difficulty: rollback-grade determinism is an architectural decision, not a networking module you can drop in.

## 2. Competitive Spectator APIs

The custom engine exposes WebSocket APIs for live caster overlays, displaying real-time APM counters, unspent resource reserves, and tech tree progress during tournaments.

### What it signals about the project's ambition

Shipping a caster API at the blog-post stage — before the game is even out — tells you something about where Unusual Fish expects *Light of Noora* to live in the market. Overlay data is pure cost unless a competitive scene exists to consume it. Surfacing APM, banked resources, and tech progression specifically is also telling: those are the metrics the 1v1 RTS audience reads as the language of skill. Unspent resources and tech-tree timing are the difference between "this player is winning" and "this player is winning correctly," and the genre's viewership has historically withered when casts can only show the first reading.

The comparison point is *StarCraft II* and its long-after-the-fact third-party overlay ecosystem, which had to be reverse-engineered because the base game treated spectating as a secondary concern. Building the data channel into the engine from the start removes the friction that kept grassroots RTS broadcasting technically janky for a decade.

## 3. The take: a genre where the infrastructure is the game

The RTS genre has spent the last several years being "revived" on the back of nostalgia-engine remasters and AA single-player campaigns. Those are valid products, but they do not address the thing that actually killed competitive RTS: the netcode. A 2010-era lockstep implementation that makes cross-region ladder feel like wading through mud is not a cosmetic problem — it is the load-bearing reason the 1v1 scene consolidated onto a single title and then slowly aged out.

*Light of Noora* is betting the opposite: that the path back to a healthy competitive RTS runs through the transport layer, not the art bible. Rollback-grade determinism plus first-class spectating is, mechanically, the minimum viable infrastructure for a game that wants a ladder people actually queue. Most studios will not pay that cost up front. If Unusual Fish executes on the determinism contract — and that is a large, unforgiving "if" — the result is the rare indie RTS that is not asking players to tolerate the genre's worst historical friction.

## 4. Context and risk

The honest caveats are the ones the blog posts cannot resolve. A 4-frame rollback window is a tuning parameter, not a guarantee; under sustained packet loss or transcontinental pings, the silent-resimulation approach can only hide so much before players perceive rubber-banding, and the trade-off between input snappiness and correction visibility is a live design decision that ships with the game, not the devlog. Determinism across PC hardware is also where many rollback RTS prototypes quietly die — different FPUs, different compiler float behavior, and the perennial temptation to use a non-deterministic language feature for a one-line convenience.

The Q4 2026 target and the modest spec sheet (a GTX 1050 Ti floor) suggest a studio optimizing for reach rather than fidelity, which is the correct instinct for a competitive title trying to build a player pool. But the same frugality means there is little margin for the long tail of desync debugging that rollback RTS projects notoriously consume. The technical direction is right; whether a small team can carry it to a stable release is the open question that will determine whether *Light of Noora* matters as a shipped game or only as an interesting blog series.