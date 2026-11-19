# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/raraaeth/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/raraaeth/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

**The World in One Picture — Thursday, 19 November 2026.** A newspaper-style front page that sums up one day's world news in a single 1024×1024 image: the date set large in the masthead, one lead story, and five further stories from five different beats, each with a small flat illustration, a headline and a one-line summary.

The lead is the day's biggest story — the launch of GTA VI, drawn as an original sunset skyline of palms, towers and a sports car (no game artwork, logos or characters). Below it: Voyager 1 reaching one light-day from Earth (space), the EU's proposed €45bn loan for Ukraine (Europe), Hakeem Jeffries nominated for US House Speaker (United States), Cyclone Akvan bearing down on India's Andhra–Odisha coast (Asia), and the ICJ's judgment in the Rohingya genocide case at The Hague (world).

## How it was made

- `stories.json` holds the editorial content — kicker, headline and sublabel for every panel — so the words can be refreshed by editing data only. Every story is an event of 19 November 2026 as reported that day; nothing is invented, and the date is named in the image itself.
- `render_image.py` composes `entry.png` from that data with Python/PIL: it draws the masthead, the lead illustration and each panel's icon scene from flat vector-style primitives, and renders every text string itself (DejaVu and Liberation fonts), so no text can come out garbled. It renders at 2× and downscales for clean edges.
- `main.ts` is the entry program the grader runs. The rules allow shipping the finished image with a program that copies it, so `main.ts` verifies `entry.png` (present, PNG signature, IHDR dimensions within 1024×1024, within the 1 MiB cap) and copies its bytes unchanged to the output directory — two runs therefore write identical bytes.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

To rebuild the artwork after editing the stories: `python3 render_image.py` (needs Pillow).

---
<sub>Entered on [make.fun](https://make.fun/?ref=ainur-irawan&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
