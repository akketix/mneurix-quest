---
title: "Throne and Liberty"
date: "2026-05-07"
gameTitle: "Throne and Liberty"
developer: "FirstSpark Games"
genre: "MMO"
platforms: ["PC", "PS5", "Xbox Series X/S"]
releaseWindow: "October 1, 2024 (NA/EU/JP); December 7, 2023 (KR); May 19, 2026 (RU)"
heroImage: "/covers/throne-and-liberty-mmo.png"
impactScore: 8
sourceUrl: "https://en.wikipedia.org/wiki/Throne_and_Liberty"
summary: "Throne and Liberty is an MMORPG developed by FirstSpark Games and published by Amazon Games for NA/EU/JP on PC, PlayStation 5, and Xbox Series X/S with full cross-platform support."
---

Throne and Liberty, a massively multiplayer online role-playing game developed by FirstSpark Games, launched in North America, Europe, and Japan on October 1, 2024, across PC, PlayStation 5, and Xbox Series X/S with full cross-platform support. Amazon Games handled publishing for those Western and Japanese regions, while NC Corporation published the Korean version which released earlier on December 7, 2023.

## Launch Performance and Player Metrics

Within its first week of global availability, Throne and Liberty attracted over 3 million players worldwide. Players collectively logged more than 24 million hours of gameplay during that initial period. On Steam specifically, the title peaked at over 300,000 concurrent users, ranking as the No. 4 most-played game on the platform at the time, trailing only Counter-Strike 2 and Dota 2. The free-to-play model and guild-based MMORPG mechanics contributed to the strong early adoption.

## Server Infrastructure Consolidation

Despite the robust launch, population density did not sustain across all deployed servers. On February 14, 2025—roughly four months after the Western and Japanese release—Throne and Liberty consolidated its server count from 107 down to 25. The reduction was attributed to sparse population density across the server network.

## Regional Expansion Plans

NC Corporation has outlined further regional rollouts. On May 7, 2026, the publisher announced that Throne and Liberty will expand services to Russia, Eastern Europe, and the Middle East, covering 11 countries including Georgia, Moldova, Belarus, Armenia, Azerbaijan, Kazakhstan, Uzbekistan, Kyrgyzstan, Tajikistan, and Turkmenistan. Astrum Entertainment, a Russia-based publisher, will partner on this expansion, with the Russian release scheduled for May 19, 2026.

## Development Background

Throne and Liberty runs on Unreal Engine 4 and was originally announced in 2011 as Lineage Eternal, a sequel within the Lineage series. The project underwent multiple delays, engine changes, and a leadership restructuring before being officially rebranded to its current title in 2022.

## Why the 107-to-25 Server Cut Actually Matters

A four-month collapse from 107 servers to 25 is not a routine post-launch optimization—it is a structural admission about how modern MMORPGs consume population. The launch-day figure was almost certainly a deliberately high provisioning buffer designed to absorb the concurrent-user spike that free-to-play, cross-platform titles reliably generate in week one. The interesting signal is the *ratio*: a roughly 76% reduction, which implies the original shard count was sized for a peak that the steady-state population never approached.

This matters for two reasons. First, it reframes the "3 million players in week one" headline. That number is a reach metric, not a concurrency metric; the 300,000 Steam peak is the figure that actually constrains server economics. Second, the consolidation tells rival publishers that the legacy MMO impulse to over-shard at launch remains expensive in 2025 even with modern cross-server matchmaking—sparse density degrades the guild-vs-guild and open-world PvP loops that are the entire retention engine for this subgenre, so the merge was as much a design correction as a cost cut.

## The Cross-Platform Convergence Play

Full cross-platform support across PC, PlayStation 5, and Xbox Series X/S is the load-bearing architectural decision in the entire release, and it deserves more scrutiny than the launch headlines gave it. Western MMOs have historically gated console versions behind separate ecosystems or delayed ports; Throne and Liberty shipped all three simultaneously under one Amazon Games publishing umbrella. That collapses the player pool into a single queue, which is precisely what makes the server-consolidation problem more solvable—merged concurrency is the only reason a 25-server footprint can still feel populated post-merge.

The cost is input asymmetry. A free-to-play MMORPG with meaningful PvP cannot fully neutralize the mouse-and-keyboard versus controller gap without either homogenizing the action combat or segregating matchmaking, and either choice has retention consequences. The fact that NC Corporation bet on a unified pool rather than segregated ladders is a deliberate statement about where the genre's audience now sits: the console MMO install base is large enough that gating it off is more damaging than the balance friction of mixing it in.

## What the Unreal Engine 4 Lineage Heritage Signals

The 2011 Lineage Eternal origin story is not just trivia; it is the reason the game's technical profile looks the way it does. A project that began on an older engine, survived a rebrand, leadership change, and engine migration, and shipped in 2023–2024 on Unreal Engine 4—rather than Unreal Engine 5—is a project whose foundational systems were locked in years before UE5's Nanite and Lumen pipelines became production-viable. The visible result is a competent but architecturally conservative MMO: large-scale open world and guild warfare optimized for stability and headcount rather than rendering frontier.

For the genre, that conservatism is arguably the right call. UE5's virtualized geometry and real-time GI are demanding in a single-player context; in an MMO with hundreds of visible actors per engagement, the per-frame cost can sabotage the very concurrency the game is selling. Throne and Liberty's choice to stabilize on UE4 and layer cross-platform networking on top is a tacit acknowledgment that the MMO genre's bottleneck in 2024 was not visual fidelity but simultaneity.

## The Regional Expansion as a Second-Life Strategy

Expanding into Russia, Eastern Europe, and the Middle East via Astrum Entertainment in May 2026—nearly two years after the Western launch—is a distinct strategy from the original release, not a continuation of it. These are markets where Western publishers face distribution friction and where a regional partner is a functional necessity rather than a convenience. The country list is notable: it spans the Caucasus, Central Asia, and Eastern European states that large Western MMOs routinely leave unserved, often pushing those players onto VPN-routed servers that distort the publisher's own concurrency metrics.

Layered on top of the server consolidation, this reads as a deliberate population-replenishment move. A title that just compressed its shard count by 76% is acutely aware of the relationship between density and retention; opening 11 new markets with a local publisher is the cleanest way to add concurrent users without re-fragmenting the existing pool. It is, in effect, a second launch engineered to feed the consolidated infrastructure rather than recapitulate the over-provisioning mistake of the first one.

## The Take

Throne and Liberty is best read as a case study in how the modern Korean-developed, Western-published MMORPG reconciles two opposing pressures: the launch-spike economics of free-to-play cross-platform distribution, and the steady-state density requirements of guild-based open-world PvP. The 107-to-25 server correction is the unflattering but honest accounting of that reconciliation, and the 2026 regional expansion is the forward-looking response. The Lineage Eternal lineage and UE4 foundation explain why the game shipped technically conservative; the cross-platform unified queue explains why it survived its own over-sharding. For anyone tracking where the MMO genre goes next, the lesson is not in the week-one headline numbers but in what the operator did four months and two years later.