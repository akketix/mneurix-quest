---
title: "Intel Launches Arrow Lake Core Ultra Series 2 Processors with TSMC-Fabricated Disaggregated Design and No SMT"
date: "2024-10-24"
gameTitle: "Intel Arrow Lake"
developer: "Intel"
genre: "HARDWARE"
platforms: ["Desktop", "Mobile"]
releaseWindow: "October 24, 2024"
heroImage: "/covers/intel-arrow-lake-hardware.png"
impactScore: 8
sourceUrl: "https://en.wikipedia.org/wiki/Arrow_Lake_(microprocessor)"
summary: "Arrow Lake is the codename for Intel Core Ultra Series 2 processors, released on October 24, 2024, using a disaggregated MCM design fabricated on TSMC nodes."
---

Intel launched Arrow Lake, the codename for its Core Ultra Series 2 processor family, on October 24, 2024. The lineup spans socketable desktop processors using the LGA 1851 socket and mainstream/enthusiast mobile processors in BGA packages, with Core Ultra 200H and 200HX mobile series following in early 2025.

## Architecture and Process Node

Arrow Lake continues the disaggregated multi-chip module (MCM) approach introduced with Meteor Lake. The design is fabricated across multiple TSMC nodes rather than Intel's own foundries. The compute tile uses TSMC's N3B node (117.241 mm²), the graphics tile uses N5P (23 mm²), and both the SoC tile (86.648 mm²) and I/O extender tile (24.475 mm²) use N6. A Foveros interposer base tile built on Intel 16 (22FFL) measures 302.944 mm².

Arrow Lake was originally planned for Intel's 20A node, which would have introduced RibbonFET gate-all-around transistors and PowerVia backside power delivery. In September 2024, Intel cancelled the 20A node to prioritize 18A development, shifting the compute tile to TSMC N3B.

## Core Design Changes

Arrow Lake introduces Lion Cove P-cores and Skymont E-cores, both shared with Lunar Lake. Lion Cove features wider decoder and dispatch engines, more integer ALUs, larger L2 caches, and a redesigned cache hierarchy. Intel claims a 9% IPC improvement for Lion Cove cores. P-cores receive 3 MB of L2 cache per core, up from the 2.5 MB found in Lunar Lake's implementation.

A notable architectural shift is the removal of Simultaneous Multithreading (SMT/HyperThreading) from Lion Cove P-cores, marking a significant departure for Intel's desktop processor line.

## I/O and Platform Features

Arrow Lake desktop CPUs integrate Thunderbolt 4 and USB4 support directly in the processor, bypassing the PCIe 3.0 speed limitations of previous implementations and using simple re-timers instead. The chipset supports up to five integrated USB 3.2 2×2 ports and is Thunderbolt 5 ready when paired with a discrete board. The integrated GPU adds HDMI 2.1 FRL at 48 Gbit/s and variable refresh rate support. The platform supports DDR5-6400 memory across two channels with a maximum capacity of 256 GB, with CU-DIMM DDR5 support added for optimal performance. Peak core clocks reach up to 5.7 GHz.
