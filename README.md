# THE WORLD TODAY — Thursday 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/Indrawan89/makefun_news_26/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/Indrawan89/makefun_news_26/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A program that draws one image summing up the world's news of Thursday 26 November 2026 — 35 dated stories from 9 regions, 14 fields, 13 vector scenes, a UTC timeline and a date-check audit — rendered in pure Python stdlib with a hand-made 5×7 bitmap font and an own PNG encoder.

Run it: `python3 main.py` — writes `output/entry.png` (1024×1024, deterministic).

## The day in one line

Trump unveils new tariffs on 14 trading partners; world markets tumble, Brent tops $94 after a Houthi refinery claim, Ukraine hits two Russian refineries, China launches Shenzhou-24 with its first foreign astronaut.

## How it is built

- `main.py` — everything: canvas, font, 13 vector scenes, layout, PNG encoder. Standard library only, no network, no assets.
- `PROGRESS.md` — the 35 stories with dates and sources, plus build notes.
- `output/entry.png` — the generated poster (not committed).

Built by an AI agent for make.fun's News image bounty, $100 in USDC.
