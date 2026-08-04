---
title: "AMD Zen 5 Microarchitecture Powers Ryzen 9000 Series with Two-Ahead Branch Prediction and N4X Fabrication"
date: "2025-08-30"
gameTitle: "AMD Ryzen 9000 series (Zen 5)"
developer: "AMD"
genre: "HARDWARE"
platforms: ["PC"]
releaseWindow: "Mobile: July 17, 2024; Desktop: August 8, 2024; HEDT: August 30, 2025; Server: October 10, 2024"
heroImage: "/covers/amd-ryzen-9000-series-zen-5-hardware.png"
impactScore: 8
sourceUrl: "https://en.wikipedia.org/wiki/Zen_5"
summary: "Zen 5 is a ground-up redesign of Zen 4 with a wider front-end, increased floating-point throughput, and more-accurate branch prediction, fabricated on TSMC's N4X process for desktop and server CCDs."
---

AMD's Zen 5 microarchitecture introduces a ground-up redesign of the Zen 4 architecture, featuring a wider front-end, increased floating-point throughput, and more-accurate branch prediction. Zen 5 powers the Ryzen 9000 series desktop processors (codenamed "Granite Ridge"), EPYC 9005 server processors (codenamed "Turin"), and Ryzen AI 300 mobile processors (codenamed "Strix Point").

## Release Timeline and Platforms
Mobile processors utilizing Zen 5 launched on July 17, 2024, followed by desktop releases on August 8, 2024. Server processors entered the market on October 10, 2024, with high-end desktop (HEDT) variants scheduled for August 30, 2025. Desktop processors utilize the Socket AM5, server processors use Socket SP5, and HEDT/Workstation variants use Socket sTR5.

## Fabrication and Die Specifications
Desktop and server Core Complex Dies (CCDs) are fabricated on TSMC's N4X process, which is intended to accommodate higher frequencies for high-performance computing. N4X offers a 6% frequency gain over the N4P node at the same power, and up to 15% higher frequencies compared to the N5 node used for Zen 4 CCDs while running at 1.2V. Mobile processors use the N4P node, targeting power efficiency, while the I/O die is fabricated on the N6 node. 

The Zen 5 CCD, codenamed "Eldora", measures 70.6mm² and contains 8.315 billion transistors. This represents a 0.5% reduction in area compared to Zen 4's 71mm² CCD, alongside a 28% increase in transistor density. Cache configurations include 80 KB of L1 cache per core (32 KB instructions, 48 KB data) and 1 MB of L2 cache per core. L3 cache ranges from 32–128 MB on desktop and server configurations, with 24 MB present in the Strix Point mobile monolithic die.

## Core Architectural Improvements
The most significant architectural change in Zen 5 is the implementation of two-ahead branch prediction. Zen 5 is the first microarchitecture to fully implement this feature, capable of predicting up to two branches per clock cycle. Previous architectures were limited to one branch instruction per clock cycle, which constrained instruction-fetch throughput in branch-heavy programs. Additionally, the architecture features a wider front-end and increased floating-point throughput compared to its predecessor.
