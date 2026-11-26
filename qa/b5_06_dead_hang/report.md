# QA report: b5:06_dead_hang  (293.9 s)

## 1a. Text over character — 2
- 196.50–196.50s  chip «8 WEEKS LATER» (max 3758 px)
- 198.75–198.75s  chip «8 WEEKS LATER» (max 605 px)

## 1b. Text over text — 2
- 36.50–36.75s  «BENCH» × «PUSH-UPS»
- 37.00–37.25s  «PUSH-UPS» × «PHONE, KEYBOARD»

## 1c. Text outside the frame — 1
- 160.25–161.75s  «4 YEARS»

## 1d. Subtitle position changes — 0
- none

## 1e. On-screen text early/late vs the voice (>1.2 s late or >1 s early) — 0
- none

## 2a. Character cut by the frame edge (sides/top) — 0
- none

## 2b. Sprite jitter: contact point slides between phases — 4
- pushup: Δx 228px Δy 31px (used at [34.6])
- caveman: Δx 124px Δy 7px (used at [42.5])
- lab: Δx 31px Δy 8px (used at [51.4, 55.7, 60.2, 66.4, 70.9, 78.1])
- lazy: Δx 224px Δy 16px (used at [138.0])

## 3a. Spans with no new visual event > 4.5 s — 1
- 253.1–257.7s (4.6s)

## 3b. Same pose on screen > 12 s — 5
- lab: 51.4–75.0s (23.6s)
- hang: 85.7–114.0s (28.3s)
- hang: 190.2–233.8s (43.6s)
- hang: 252.8–267.5s (14.7s)
- hang: 272.3–293.9s (21.6s)

## Contact sheets for manual review