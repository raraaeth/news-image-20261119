#!/usr/bin/env python3
"""Render entry.png: 'The World in One Picture' for Thursday 19 November 2026.

Reads stories.json (kicker / headline / sublabel per panel) and composes a
newspaper-style front page at 2x supersampling, then downscales to
1024x1024 for clean edges. All text is drawn by PIL from the JSON data,
so the wording can be refreshed by editing stories.json only.
"""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
S = 2  # supersample factor
W = 1024
M = 34  # page margin
RX = W - M  # right edge of the content column
CW = RX - M  # content width

PAPER = (247, 242, 231)
CARD = (255, 253, 246)
INK = (27, 42, 74)
RED = (179, 39, 30)
FAINT = (90, 96, 110)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
DJ_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size * S)


def u(v):
    """Scale a base-unit length to render pixels."""
    return int(round(v * S))


def draw_tracked(d, cx, y, text, fnt, fill, tracking):
    """Draw text centred at cx with extra letter tracking (base units)."""
    widths = [d.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + u(tracking) * (len(text) - 1)
    x = u(cx) - total / 2
    for ch, w in zip(text, widths):
        d.text((x, u(y)), ch, font=fnt, fill=fill)
        x += w + u(tracking)


def draw_tracked_left(d, x, y, text, fnt, fill, tracking):
    """Draw tracked text starting exactly at x (base units)."""
    cx = u(x)
    for ch in text:
        d.text((cx, u(y)), ch, font=fnt, fill=fill)
        cx += d.textlength(ch, font=fnt) + u(tracking)


def fit_size(d, text, path, start, max_width):
    """Largest font size <= start (base units) whose text fits max_width."""
    size = start
    while size > 10:
        if d.textlength(text, font=font(path, size)) <= u(max_width):
            return size
        size -= 2
    return size


def wrap(d, text, fnt, max_width):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=fnt) <= u(max_width):
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_one_line(d, text, path, start, max_width, minimum=15):
    size = start
    while size > minimum and d.textlength(text, font=font(path, size)) > u(max_width):
        size -= 1
    return font(path, size)


# ---------------------------------------------------------------- icons

def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((u(cx) + rad * S * math.cos(ang), u(cy) + rad * S * math.sin(ang)))
    d.polygon(pts, fill=fill)


def icon_space(d, x, y):
    d.rectangle([u(x), u(y), u(x + 82), u(y + 82)], fill=(27, 42, 74))
    for sx, sy in [(14, 12), (30, 8), (66, 44), (12, 40), (52, 62), (72, 14)]:
        star(d, x + sx, y + sy, 1.8, (220, 226, 240))
    # Earth, top right
    d.ellipse([u(x + 56), u(y + 8), u(x + 78), u(y + 30)], fill=(127, 178, 224))
    d.ellipse([u(x + 61), u(y + 13), u(x + 69), u(y + 20)], fill=(94, 150, 104))
    # signal arcs from dish toward Earth
    for r in (9, 15, 21):
        d.arc([u(x + 38 - r), u(y + 34 - r), u(x + 38 + r), u(y + 34 + r)],
              start=-70, end=35, fill=(242, 194, 48), width=u(2.5))
    # dish: bowl + stand
    d.pieslice([u(x + 6), u(y + 26), u(x + 46), u(y + 62)], start=195, end=335,
               fill=(232, 228, 216))
    d.line([u(x + 26), u(y + 50), u(x + 26), u(y + 70)], fill=(232, 228, 216), width=u(4))
    d.line([u(x + 15), u(y + 70), u(x + 37), u(y + 70)], fill=(232, 228, 216), width=u(4))
    d.ellipse([u(x + 35), u(y + 31), u(x + 41), u(y + 37)], fill=(242, 194, 48))


def icon_summit(d, x, y):
    d.rectangle([u(x), u(y), u(x + 82), u(y + 82)], fill=(24, 58, 74))
    gold = (242, 194, 48)
    for cx in (21, 41, 61):
        star(d, x + cx, y + 20, 7, gold)
    d.rectangle([u(x + 12), u(y + 48), u(x + 70), u(y + 58)], fill=gold)
    d.rectangle([u(x + 18), u(y + 58), u(x + 24), u(y + 70)], fill=gold)
    d.rectangle([u(x + 58), u(y + 58), u(x + 64), u(y + 70)], fill=gold)


def icon_europe(d, x, y):
    d.rectangle([u(x), u(y), u(x + 82), u(y + 82)], fill=(39, 70, 144))
    for i in range(12):
        ang = 2 * math.pi * i / 12 - math.pi / 2
        star(d, x + 41 + 24 * math.cos(ang), y + 41 + 24 * math.sin(ang), 5.2,
             (242, 194, 48))


def icon_us(d, x, y):
    d.rectangle([u(x), u(y), u(x + 82), u(y + 82)], fill=(122, 31, 31))
    cream = (243, 237, 221)
    d.line([u(x + 41), u(y + 6), u(x + 41), u(y + 14)], fill=cream, width=u(3))
    d.ellipse([u(x + 39), u(y + 3), u(x + 43), u(y + 7)], fill=cream)
    d.pieslice([u(x + 25), u(y + 12), u(x + 57), u(y + 44)], start=180, end=360, fill=cream)
    d.rectangle([u(x + 19), u(y + 42), u(x + 63), u(y + 48)], fill=cream)
    d.rectangle([u(x + 23), u(y + 48), u(x + 59), u(y + 68)], fill=cream)
    for cx in (28, 35, 42, 49, 56):
        d.line([u(x + cx), u(y + 50), u(x + cx), u(y + 66)], fill=(122, 31, 31), width=u(2.5))
    d.rectangle([u(x + 15), u(y + 68), u(x + 67), u(y + 74)], fill=cream)


def icon_asia(d, x, y):
    d.rectangle([u(x), u(y), u(x + 82), u(y + 82)], fill=(14, 110, 110))
    for r, start in ((11, 20), (18, 110), (25, 200)):
        d.arc([u(x + 41 - r), u(y + 34 - r), u(x + 41 + r), u(y + 34 + r)],
              start=start, end=start + 235, fill=(234, 246, 246), width=u(5))
    d.ellipse([u(x + 37), u(y + 30), u(x + 45), u(y + 38)], fill=(234, 246, 246))
    coast = [(x, y + 82), (x, y + 68), (x + 18, y + 64), (x + 38, y + 70),
             (x + 58, y + 63), (x + 82, y + 69), (x + 82, y + 82)]
    d.polygon([(u(px), u(py)) for px, py in coast], fill=(228, 200, 127))
    d.arc([u(x + 6), u(y + 52), u(x + 30), u(y + 64)], start=180, end=330,
          fill=(234, 246, 246), width=u(2.5))


def icon_world(d, x, y):
    d.rectangle([u(x), u(y), u(x + 82), u(y + 82)], fill=(61, 52, 139))
    gold = (232, 184, 75)
    d.line([u(x + 41), u(y + 16), u(x + 41), u(y + 64)], fill=gold, width=u(4))
    d.line([u(x + 14), u(y + 20), u(x + 68), u(y + 20)], fill=gold, width=u(4))
    d.ellipse([u(x + 38), u(y + 9), u(x + 44), u(y + 15)], fill=gold)
    for cx in (14, 68):
        d.line([u(x + cx), u(y + 20), u(x + cx - 7), u(y + 42)], fill=gold, width=u(2.5))
        d.line([u(x + cx), u(y + 20), u(x + cx + 7), u(y + 42)], fill=gold, width=u(2.5))
        d.pieslice([u(x + cx - 11), u(y + 34), u(x + cx + 11), u(y + 52)],
                   start=0, end=180, fill=gold)
    d.line([u(x + 29), u(y + 70), u(x + 53), u(y + 70)], fill=gold, width=u(4))
    d.line([u(x + 34), u(y + 64), u(x + 48), u(y + 64)], fill=gold, width=u(3))


ICONS = {"space": icon_space, "europe": icon_europe, "summit": icon_summit,
         "us": icon_us, "asia": icon_asia, "world": icon_world}


# ---------------------------------------------------------------- lead art

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lead_art(d, x, y, w, h):
    stops = [(0.0, (46, 26, 71)), (0.45, (122, 42, 77)), (0.7, (198, 80, 63)),
             (0.88, (232, 132, 95)), (1.0, (242, 166, 90))]
    for row in range(u(h)):
        t = row / max(1, u(h) - 1)
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                col = lerp(c0, c1, (t - t0) / (t1 - t0))
                break
        d.line([u(x), u(y) + row, u(x + w), u(y) + row], fill=col)
    sil = (23, 31, 51)
    base = y + h
    # sun, low over the skyline
    d.ellipse([u(x + 600), u(base - 52), u(x + 652), u(base)], fill=(255, 217, 160))
    # skyline
    towers = [(0, 30), (46, 44), (96, 26), (140, 56), (196, 34), (240, 24),
              (282, 48), (336, 30), (384, 62), (446, 28), (492, 40), (548, 24),
              (700, 42), (756, 28), (800, 52), (856, 32), (902, 44), (940, 26)]
    for tx, th in towers:
        d.rectangle([u(x + tx), u(base - th), u(x + tx + 40), u(base)], fill=sil)
    d.rectangle([u(x), u(base - 4), u(x + w), u(base)], fill=sil)

    def palm(px, ph, lean):
        top_x, top_y = px + lean, base - ph
        steps = 14
        for i in range(steps):
            t0, t1 = i / steps, (i + 1) / steps
            xa = px + lean * t0 * t0
            xb = px + lean * t1 * t1
            d.line([u(x + xa), u(base - ph * t0), u(x + xb), u(base - ph * t1)],
                   fill=sil, width=u(4))
        for ang in (-165, -125, -85, -40, -5):
            ex = top_x + 26 * math.cos(math.radians(ang))
            ey = top_y - 12 * math.sin(math.radians(ang)) + 7
            d.line([u(x + top_x), u(top_y), u(x + ex), u(ey)], fill=sil, width=u(3.5))

    palm(96, 74, 14)
    palm(872, 66, -12)
    # sports car silhouette, low and sleek
    cx0, cy = x + 356, base - 8
    body = [(cx0, cy - 12), (cx0 + 14, cy - 14), (cx0 + 44, cy - 16),
            (cx0 + 66, cy - 27), (cx0 + 108, cy - 29), (cx0 + 132, cy - 17),
            (cx0 + 168, cy - 14), (cx0 + 178, cy - 11), (cx0 + 178, cy - 4),
            (cx0, cy - 4)]
    d.polygon([(u(px), u(py)) for px, py in body], fill=sil)
    for wx in (cx0 + 34, cx0 + 142):
        d.ellipse([u(wx - 10), u(cy - 12), u(wx + 10), u(cy + 8)], fill=sil)
        d.ellipse([u(wx - 4), u(cy - 6), u(wx + 4), u(cy + 2)], fill=(242, 166, 90))


# ---------------------------------------------------------------- compose

def main():
    data = json.loads((HERE / "stories.json").read_text(encoding="utf-8"))
    img = Image.new("RGB", (W * S, W * S), PAPER)
    d = ImageDraw.Draw(img)
    mast, lead, panels = data["masthead"], data["lead"], data["panels"]

    # masthead
    draw_tracked(d, W / 2, 24, mast["kicker"], font(DJ_BOLD, 24), INK, 7)
    s1 = fit_size(d, mast["date_line_1"], SERIF_BOLD, 104, CW)
    d.text((u(W / 2), u(52)), mast["date_line_1"], font=font(SERIF_BOLD, s1),
           fill=INK, anchor="ma")
    s2 = fit_size(d, mast["date_line_2"], SERIF_BOLD, 100, CW)
    d.text((u(W / 2), u(158)), mast["date_line_2"], font=font(SERIF_BOLD, s2),
           fill=INK, anchor="ma")
    d.rectangle([u(M), u(258), u(RX), u(264)], fill=INK)
    d.rectangle([u(M), u(268), u(RX), u(270)], fill=INK)

    # lead panel
    lead_art(d, M, 286, CW, 118)
    d.rectangle([u(M), u(286), u(RX), u(404)], outline=INK, width=u(2.5))
    draw_tracked_left(d, M, 414, lead["kicker"], font(DJ_BOLD, 18), RED, 4)
    d.text((u(M), u(436)), lead["headline"], font=font(SANS_BOLD, 46), fill=INK)
    sub_f = font(SANS, 23)
    ly = 492
    for line in wrap(d, lead["sublabel"], sub_f, CW)[:2]:
        d.text((u(M), u(ly)), line, font=sub_f, fill=(40, 44, 54))
        ly += 29
    d.rectangle([u(M), u(556), u(RX), u(558)], fill=INK)

    # five story strips
    y = 574
    for panel in panels:
        d.rectangle([u(M), u(y), u(RX), u(y + 80)], fill=CARD)
        d.rectangle([u(M), u(y), u(RX), u(y + 80)], outline=INK, width=u(2))
        ICONS[panel["id"]](d, M, y)
        tx = M + 82 + 16
        tw = RX - tx
        d.text((u(tx), u(y + 5)), panel["kicker"], font=font(DJ_BOLD, 16), fill=RED)
        hf = fit_one_line(d, panel["headline"], SANS_BOLD, 29, tw, minimum=22)
        d.text((u(tx), u(y + 24)), panel["headline"], font=hf, fill=INK)
        sf = fit_one_line(d, panel["sublabel"], SANS, 20, tw, minimum=15)
        d.text((u(tx), u(y + 55)), panel["sublabel"], font=sf, fill=(40, 44, 54))
        y += 89

    img = img.resize((W, W), Image.LANCZOS)
    out = HERE / "entry.png"
    img.save(out, optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
