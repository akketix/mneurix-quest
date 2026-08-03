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


Indie developer Unusual Fish has released technical blog posts for *Light of Noora*, a competitive fast-paced RTS built around zero-latency rollback netcode and high-APM micro-management.

## 1. Rollback Netcode in Real-Time Strategy

While fighting games adopted rollback netcode years ago, RTS titles traditionally relied on lockstep networking, where high ping causes unit input delays. *Light of Noora* solves this via deterministic rollback prediction:

- **Input Frame Prediction**: Unit commands execute locally on frame 0 while client sockets reconcile opponent inputs across network ticks.
- **State Rewind & Resimulation**: If a network packet drops, the engine rewinds simulation states up to 4 frames silently, preventing input lag during intense 1v1 micro battles.

## 2. Competitive Spectator APIs

The custom engine exposes WebSocket APIs for live caster overlays, displaying real-time APM counters, unspent resource reserves, and tech tree progress during tournaments.
