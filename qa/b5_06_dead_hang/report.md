# QA report: b5:06_dead_hang  (362.9 s)

## 1a. Text over character — 4
- 245.75–245.75s  chip «8 WEEKS LATER» (max 7188 px)
- 248.00–248.00s  chip «8 WEEKS LATER» (max 605 px)
- 251.25–251.75s  chip «LEVELS» (max 4901 px)
- 359.75–359.75s  chip «THAT'S WHY NOBODY DOES IT» (max 3984 px)

## 1b. Text over text — 7
- 46.50–46.75s  «BENCH» × «PUSH-UPS»
- 202.00–202.00s  «ADULTS» × «4 YEARS»
- 202.00–202.00s  «17 COUNTRIES» × «4 YEARS»
- 202.25–204.00s  «ADULTS» × «4 YEARS»
- 251.00–251.00s  «NO CHANGE» × «LEVELS»
- 351.00–351.00s  «START: 9s» × «5 WEEKS»
- 352.50–352.50s  «5 WEEKS» × «52s»

## 1c. Text outside the frame — 1
- 202.00–202.00s  «4 YEARS»

## 1d. Subtitle position changes — 0
- none

## 1e. On-screen text early/late vs the voice (>1.2 s late or >1 s early) — 0
- none

## 2a. Character cut by the frame edge (sides/top) — 0
- none

## 2b. Sprite jitter: contact point slides between phases — 4
- pushup: Δx 228px Δy 31px (used at [43.8])
- caveman: Δx 124px Δy 7px (used at [54.2])
- lab: Δx 31px Δy 8px (used at [65.2, 70.4, 76.0, 83.6, 89.2, 97.8])
- lazy: Δx 224px Δy 16px (used at [173.8])

## 3a. Spans with no new visual event > 4.5 s — 2
- 313.8–319.5s (5.7s)
- 332.2–337.8s (5.6s)

## 3b. Same pose on screen > 12 s — 6
- hang: 0.0–13.1s (13.1s)
- lab: 65.2–94.1s (28.9s)
- hang: 106.7–145.0s (38.3s)
- hang: 238.4–291.1s (52.7s)
- hang: 313.5–331.5s (18.0s)
- hang: 337.8–362.9s (25.1s)

## Contact sheets for manual review