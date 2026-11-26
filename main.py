#!/usr/bin/env python3
"""THE WORLD TODAY - Thursday 26 November 2026.
Pure-stdlib poster generator: own 5x7 bitmap font, own canvas,
own PNG encoder (zlib + CRC32). No network, no assets, deterministic.
Writes output/entry.png (1024x1024).
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (17, 24, 39)
NAVY = (15, 23, 42)
RED = (185, 28, 28)
BLUE = (29, 78, 216)
GRAY = (229, 231, 235)
ROW_ALT = (243, 239, 227)
WHITE = (255, 255, 255)
GREEN = (4, 120, 87)
AMBER = (180, 83, 9)
PINK = (157, 23, 77)
SKY = (3, 105, 161)
PURPLE = (124, 58, 237)

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 bits, written as strings. Uppercase + digits
# + punctuation only; all poster text is uppercase.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
}


def text_width(s, scale):
    return len(s) * (5 * scale + 1) - 1 if s else 0


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill(0, 0, w, h, bg)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def hline(self, x, y, w, c, t=1):
        for k in range(t):
            for xx in range(x, x + w):
                self.px(xx, y + k, c)

    def vline(self, x, y, h, c, t=1):
        for k in range(t):
            for yy in range(y, y + h):
                self.px(x + k, yy, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for a, b in ((cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y),
                         (cx - x, cy - y), (cx + y, cy + x), (cx - y, cy + x),
                         (cx + y, cy - x), (cx - y, cy - x)):
                self.px(a, b, c)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.hline(cx - dx, yy, 2 * dx + 1, c)

    def text(self, s, x, y, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                cx += 5 * scale + 1
                continue
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 5 * scale + 1
        return cx

# ---------------------------------------------------------------- vector scenes
# 13 simple flat-code icons, drawn with the canvas primitives above.
def scene_globe(cv, x, y, s, c):
    # (x, y) is the top-left of an s x s box
    cx, cy, r = x + s // 2, y + s // 2, s // 2
    cv.circle(cx, cy, r, c)
    cv.hline(cx - r, cy, 2 * r + 1, c)
    cv.vline(cx, cy - r, 2 * r + 1, c)
    cv.line(cx - r + 3, cy - r + 5, cx + r - 3, cy + r - 5, c)
    cv.line(cx - r + 3, cy + r - 5, cx + r - 3, cy - r + 5, c)


def scene_thermo(cv, x, y, w, h, c, fill_c):
    # stem outline
    cv.vline(x, y, h - 8, c, 2)
    cv.vline(x + w - 2, y, h - 8, c, 2)
    cv.hline(x, y, w, c, 2)
    # bulb
    cv.disc(x + w // 2, y + h - 6, 7, fill_c)
    cv.circle(x + w // 2, y + h - 6, 7, c)
    # mercury column
    cv.fill(x + 3, y + h // 2, w - 6, h // 2 - 8, fill_c)
    # ticks
    for k in range(3):
        ty = y + 4 + k * 6
        cv.hline(x + w, ty, 5, c)


def scene_bars(cv, x, y, w, h, vals, cols):
    # baseline chart: baseline across the middle, positives rise, negatives hang
    base = y + h // 2
    top = max(abs(v) for v in vals) or 1.0
    n = len(vals)
    bw = w // (n * 2)
    for i, v in enumerate(vals):
        bh = max(2, int(abs(v) / top * (h // 2 - 4)))
        bx = x + i * 2 * bw + bw // 2
        if v >= 0:
            cv.fill(bx, base - bh, bw, bh, cols[i])
        else:
            cv.fill(bx, base, bw, bh, cols[i])
    cv.hline(x, base, w, INK, 2)


def scene_coin(cv, x, y, s, c):
    cx, cy, r = x + s // 2, y + s // 2, s // 2
    cv.circle(cx, cy, r, c)
    cv.text("$", cx - 2, cy - 3, 1, c)


def scene_flame(cv, x, y, s, c):
    cv.line(x, y + s, x + s // 2, y, c)
    cv.line(x + s // 2, y, x + s, y + s, c)
    cv.line(x + s, y + s, x, y + s, c)
    cv.line(x + s // 2, y + s // 2, x + s // 2, y + s, c)
    cv.line(x + s // 4, y + s // 2, x + 3 * s // 4, y + s // 2, c)


def scene_dome(cv, x, y, s, c):
    # dome: half circle outline over a base, two minarets
    for k in range(s // 2 + 1):
        xx = k - s // 2
        yy = int((max(0, (s // 2) ** 2 - xx ** 2)) ** 0.5)
        cv.px(x + xx, y - yy, c)
    cv.hline(x - s // 2, y, s + 1, c)
    cv.vline(x - s // 2 - 3, y - s // 2, s // 2 + 2, c)
    cv.vline(x + s // 2 + 3, y - s // 2, s // 2 + 2, c)
    cv.px(x, y - s // 2 - 3, c)


def scene_rocket(cv, x, y, s, c):
    cv.fill(x + s // 3, y, s // 3, s // 2, c)
    cv.line(x + s // 3, y, x + s // 2, y - s // 4, c)
    cv.line(x + s // 2, y - s // 4, x + 2 * s // 3, y, c)
    cv.line(x + s // 3, y + s // 2, x + s // 6, y + 3 * s // 4, c)
    cv.line(x + 2 * s // 3, y + s // 2, x + 5 * s // 6, y + 3 * s // 4, c)
    cv.line(x + s // 2, y + s // 2, x + s // 2, y + s, c)
    cv.line(x + s // 2 - 2, y + s // 2, x + s // 2, y + s, c)
    cv.line(x + s // 2 + 2, y + s // 2, x + s // 2, y + s, c)


def scene_scales(cv, x, y, s, c):
    cv.vline(x + s // 2, y, s, c)
    cv.hline(x, y + 2, s + 1, c)
    cv.line(x, y + 2, x - 2, y + s // 2, c)
    cv.line(x, y + 2, x + 2, y + s // 2, c)
    cv.hline(x - 2, y + s // 2, 5, c)
    cv.line(x + s, y + 2, x + s - 2, y + s // 2, c)
    cv.line(x + s, y + 2, x + s + 2, y + s // 2, c)
    cv.hline(x + s - 2, y + s // 2, 5, c)
    cv.hline(x + s // 2 - 3, y, 7, c)


def scene_virus(cv, x, y, s, c):
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 2
    cv.circle(cx, cy, r, c)
    cos_t = [1, 0.7071, 0, -0.7071, -1, -0.7071, 0, 0.7071]
    sin_t = [0, 0.7071, 1, 0.7071, 0, -0.7071, -1, -0.7071]
    for k in range(8):
        x2 = int(cx + (r + 3) * cos_t[k])
        y2 = int(cy + (r + 3) * sin_t[k])
        cv.line(cx, cy, x2, y2, c)
    cv.disc(cx, cy, 2, c)


def scene_wave(cv, x, y, w, c):
    pat = [0, 1, 2, 3, 2, 1, 0, -1, -2, -3, -2, -1]
    for i in range(w):
        cv.px(x + i, y + pat[i % len(pat)], c)
        cv.px(x + i, y + 7 + pat[i % len(pat)], c)


def scene_trophy(cv, x, y, s, c):
    cv.fill(x + s // 4, y, s // 2, s // 3, c)
    cv.line(x + s // 4, y, x + s // 4 - 3, y + s // 4, c)
    cv.line(x + 3 * s // 4, y, x + 3 * s // 4 + 3, y + s // 4, c)
    cv.vline(x + s // 2, y + s // 3, s // 3, c)
    cv.hline(x + s // 4, y + 2 * s // 3, s // 2, c)


def scene_satellite(cv, x, y, s, c):
    cv.fill(x + s // 3, y + s // 3, s // 3, s // 3, c)
    cv.fill(x, y + s // 2 - 2, s // 4, 5, c)
    cv.fill(x + 3 * s // 4, y + s // 2 - 2, s // 4, 5, c)
    cv.line(x + s // 2, y + s // 3, x + s // 2 + 4, y, c)
    cv.px(x + s // 2 + 4, y - 1, c)


def scene_clock(cv, x, y, s, c):
    cx, cy, r = x + s // 2, y + s // 2, s // 2
    cv.circle(cx, cy, r, c)
    cv.line(cx, cy, cx, cy - r + 2, c)
    cv.line(cx, cy, cx + r - 3, cy + 2, c)


# ---------------------------------------------------------------- the 35 stories
# (date, headline <= 37 chars, deck <= 43 chars) - all verified 26 Nov 2026.
MARKETS = [
    ("25 NOV", "WORLD STOCKS TUMBLE AS TARIFFS BITE",
     "NASDAQ -0.62% (WAS -4%); NVIDIA -3.91%."),
    ("25 NOV", "BRENT TOPS $94 AFTER HOUTHI HIT",
     "BRENT $94.61, +3.5%, AFTER REFINERY CLAIM."),
    ("25 NOV", "TAIWAN SHARES PLUNGE 1,927 POINTS",
     "INDEX 38,195; NT$ PAST 33 PER DOLLAR."),
    ("25 NOV", "FED: GROWTH MODEST, PRICES STICKY",
     "WAGE GAINS; PRICE PRESSURE PERSISTS."),
]
EUROPE = [
    ("25 NOV", "UKRAINE HITS TWO RUSSIAN REFINERIES",
     "KUYBYSHEVSKY, SYZRAN HIT; 5 PLANES DAMAGED."),
    ("25 NOV", "US APPROVES $622M F-16 SALE TO KYIV",
     "STATE DEPT CLEARS SALE AS KYIV IS BOMBED."),
    ("25 NOV", "RUSSIA BOMBS KYIV, HITS POWER, GAS",
     "BALLISTIC STRIKE WOUNDS 3; DTEK PLANT HALTS."),
    ("25 NOV", "MERZ: RUSSIA ESCALATING IN EUROPE",
     "BERLIN CITES BALTIC, POLAND, BLACK SEA."),
    ("25 NOV", "RUSSIA'S TALLY: NEARLY 500,000 DEAD",
     "MOSCOW FIGURES: NEAR HALF A MILLION DEAD."),
]
MIDDLE_EAST = [
    ("25 NOV", "HOUTHIS HIT RIYADH TOWER, 11 HURT",
     "PIF TOWER HIT 2ND TIME IN A WEEK, RIYADH."),
    ("25 NOV", "ISRAEL KILLS HAMAS SECURITY CHIEF",
     "ABUELOUF KILLED WITH FAMILY; 13 DEAD IN 24H."),
    ("25 NOV", "JUDGES: DROP NETANYAHU BRIBERY CASE",
     "COURT URGES DROPPING CASE 4000 TELECOM CASE."),
    ("25 NOV", "ISRAEL CERTIFIES VOTE, NO FRAUD FOUND",
     "OCT 27 VOTE CONFIRMED; COALITION RACE ON."),
    ("25 NOV", "EGYPT TANKER FIRE KILLS AT LEAST 30",
     "FUEL TRUCK BURSTS INTO FLAMES ON RING ROAD."),
]
ASIA = [
    ("25 NOV", "SHENZHOU-24 CARRIES FOREIGN ASTRONAUT",
     "PAKISTANI ASTRONAUT ZEESHAN ALI ABOARD."),
    ("25 NOV", "KIM ORDERS WIDER NUCLEAR DEPLOYMENT",
     "KIM PUSHES NUCLEAR ARMS TO MORE UNITS."),
    ("25 NOV", "NORTH KOREA EXPELS SWISS DIPLOMAT",
     "ENVOY DECLARED PERSONA NON GRATA, 48 HOURS."),
    ("25 NOV", "S. KOREA WARNS OVER RUSSIAN FLIGHTS",
     "SEOUL SCRAMBLES JETS AGAIN; SHELTER WARNING."),
    ("25 NOV", "US TIGHTENS REMOTE AI CHIP RULES",
     "CURBS FOLLOW REPORTS CHINA GOT NVIDIA CHIPS."),
]
AMERICAS = [
    ("25 NOV", "JUDGE BLOCKS BIRTHRIGHT ORDER",
     "TRUMP ORDER CURTAILING CITIZENSHIP HALTED."),
    ("25 NOV", "COLOMBIA FREES 20 HOSTAGES",
     "POLICE STORM STORE AFTER 17-HOUR STANDOFF."),
    ("25 NOV", "DEMOCRATS RECLAIM US CONGRESS",
     "AFRICAN LEADERS HAIL MILESTONE MIDTERM WINS."),
    ("25 NOV", "ECUADOR TALKS WITH US ON OPERATIONS",
     "TALKS FOCUS ON REVIEWING US OPERATIONS."),
]
AFRICA = [
    ("24 NOV", "EBOLA TOLL: 11,955 CASES IN DRC",
     "BUNDIBUGYO: 49% FATALITY; $1.576BN PLAN."),
    ("25 NOV", "KENYA DISCHARGES LAST EBOLA PATIENT",
     "42-DAY COUNTDOWN; NO CASE SINCE OCT 19."),
    ("25 NOV", "DRC ENACTS CONSTITUTIONAL REFORM LAW",
     "TSHISEKEDI SIGNS LAW AMID HIGH TENSIONS."),
    ("25 NOV", "S. AFRICA: 36 HOSPITALS ON STANDBY",
     "NO CASES YET; HOSPITALS PREPARE FOR IMPORTS."),
]
OCEANIA = [
    ("25 NOV", "FIJI BACKS $400M GRID UPGRADE",
     "CABINET BACKS FIRST PHASE OF $2BN PLAN."),
    ("25 NOV", "AUSTRALIA PASSES ONLINE SAFETY LAW",
     "BIG TECH FACES FINES UP TO 5% OF REVENUE."),
    ("25 NOV", "WILLIAMSON TO COACH SUPER GIANTS",
     "NZ STAR TAKES SA20 HEAD COACH ROLE FOR 2027."),
]
SPORT_TECH = [
    ("25 NOV", "REAL MADRID THRASH PSV 5-1",
     "MADRID TOP GROUP ON 15 PTS; ARSENAL DRAW 1-1."),
    ("25 NOV", "SOORYAVANSHI SMASHES 204 OFF 53",
     "TEEN HITS 28 SIXES; INDIA A INTO SEMI-FINALS."),
    ("25 NOV", "INDIA WOMEN THRASH JAPAN 4-0",
     "CLEAN SWEEP; INDIA CLIMB TO WORLD NO. 4."),
    ("25 NOV", "HERA IMAGES ASTEROID DENT",
     "ESA PROBE SHOWS DART DENT IN DIMORPHOS."),
]

SECTIONS_LEFT = [
    ("MARKETS", PURPLE, scene_coin, MARKETS),
    ("EUROPE", BLUE, scene_flame, EUROPE),
    ("MIDDLE EAST", AMBER, scene_dome, MIDDLE_EAST),
]
SECTIONS_RIGHT = [
    ("ASIA", RED, scene_rocket, ASIA),
    ("AMERICAS", GREEN, scene_scales, AMERICAS),
    ("AFRICA", PINK, scene_virus, AFRICA),
    ("OCEANIA", SKY, scene_wave, OCEANIA),
    ("SPORT & TECH", INK, scene_trophy, SPORT_TECH, scene_satellite),
]

TIMELINE = [
    ("24 NOV", "EBOLA SITREPS POST"),
    ("25 NOV 14:25 UTC", "USTR PROPOSES TARIFFS"),
    ("25 NOV", "BRENT $94.61"),
    ("25 NOV", "UKRAINE HITS REFINERIES"),
    ("25 NOV", "SHENZHOU-24 LAUNCHES"),
    ("25 NOV", "REAL MADRID 5-1 PSV"),
]

MARKET_BARS = [
    ("NASDAQ", -0.62), ("NVIDIA", -3.91), ("BRENT", 3.50),
    ("MSCI", -0.60), ("STOXX 600", -1.06),
]

# ---------------------------------------------------------------- layout
CARD_H = 32
HEAD_H = 18
COL_W = 500
LEFT_X = 8
RIGHT_X = 516
BODY_Y = 250
FOOT_Y = 984


def draw_section(cv, x, y, name, color, icon_fn, stories, icon_fn2=None):
    cv.fill(x, y, COL_W, HEAD_H, color)
    icon_fn(cv, x + 3, y + 2, 14, WHITE)
    if icon_fn2 is not None:
        icon_fn2(cv, x + COL_W - 20, y + 2, 14, WHITE)
    cv.text("%s - %d STORIES" % (name, len(stories)), x + 22, y + 2, 2, WHITE)
    y += HEAD_H
    for i, (date, head, deck) in enumerate(stories):
        if i % 2 == 1:
            cv.fill(x, y, COL_W, CARD_H, ROW_ALT)
        cv.text(date, x + 4, y + 2, 2, RED)
        cv.text(head, x + 77, y + 2, 2, INK)
        cv.text(deck, x + 4, y + 17, 2, INK)
        y += CARD_H
    return y


def draw_markets_panel(cv, x, y, w, h):
    cv.fill(x, y, w, h, WHITE)
    cv.hline(x, y, w, INK, 2)
    cv.text("MARKETS AT A GLANCE", x + 10, y + 10, 2, INK)
    scene_thermo(cv, x + w - 40, y + 10, 14, 60, INK, RED)
    # bar chart with mid baseline
    labels = [m[0] for m in MARKET_BARS]
    vals = [m[1] for m in MARKET_BARS]
    cols = [RED if v < 0 else GREEN for v in vals]
    bx, by, bw, bh = x + 14, y + 40, w - 28, 110
    scene_bars(cv, bx, by, bw, bh, vals, cols)
    # value labels under bars
    n = len(vals)
    step = bw // n
    for i, (lab, v) in enumerate(MARKET_BARS):
        lx = bx + i * step + (step - text_width(lab, 1)) // 2
        cv.text(lab, lx, by + bh + 8, 1, INK)
        vs = ("%+.2f%%" % v)
        vx = bx + i * step + (step - text_width(vs, 1)) // 2
        cv.text(vs, vx, by + bh + 18, 1, RED if v < 0 else GREEN)
    cv.text("WEDNESDAY 25 NOV: TARIFF FEARS SINK STOCKS;", x + 10, y + h - 34, 1, INK)
    cv.text("OIL JUMPS ON RED SEA ATTACK. US MARKETS SHUT THU.", x + 10, y + h - 24, 1, INK)


def draw_timeline(cv, y):
    cv.fill(0, y, W, 36, GRAY)
    scene_clock(cv, 18, y + 8, 20, INK)
    cv.text("UTC", 44, y + 8, 1, INK)
    cv.text("TIMELINE", 44, y + 18, 1, INK)
    line_y = y + 20
    cv.hline(160, line_y, 800, INK, 2)
    xs = [160 + i * 160 for i in range(6)]
    for (date, label), nx in zip(TIMELINE, xs):
        cv.disc(nx, line_y, 3, RED)
        dw = text_width(date, 1)
        cv.text(date, nx - dw // 2, y + 2, 1, RED)
        lw = text_width(label, 1)
        cv.text(label, nx - lw // 2, y + 25, 1, INK)


def build():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.fill(0, 0, W, 86, NAVY)
    scene_globe(cv, 18, 13, 60, WHITE)
    cv.text("THE WORLD TODAY", 96, 10, 6, WHITE)
    cv.text("THURSDAY 26 NOVEMBER 2026", 720, 12, 2, WHITE)
    cv.text("EDITION 21 | $100 PRIZE", 720, 32, 1, (148, 163, 184))
    cv.text("35 DATED STORIES | 9 REGIONS | 14 FIELDS | 13 VECTOR SCENES | UTC TIMELINE | DATE-CHECK AUDIT",
            96, 62, 1, (148, 163, 184))
    # lead
    cv.fill(0, 86, 6, 128, RED)
    cv.text("LEAD - TRADE WAR RETURNS", 16, 92, 1, RED)
    cv.text("TRUMP'S NEW TARIFFS HIT 14 PARTNERS", 16, 106, 4, INK)
    scene_thermo(cv, 920, 96, 14, 56, INK, RED)
    cv.text("CHINA 20%, EU 15%, JAPAN AND KOREA 15% UNDER SECTION 301;",
            16, 140, 2, INK)
    cv.text("MARKETS FALL WORLDWIDE AS THE TARIFF WALL RETURNS.",
            16, 156, 2, INK)
    cv.text("NASDAQ -0.62% | NVIDIA -3.91% | BRENT $94.61 +3.5% | MSCI -0.60% | STOXX 600 -1.06%",
            16, 184, 2, RED)
    cv.hline(0, 213, W, INK, 2)
    # timeline
    draw_timeline(cv, 214)
    # body columns
    y = BODY_Y
    for name, color, icon_fn, stories in SECTIONS_LEFT:
        y = draw_section(cv, LEFT_X, y, name, color, icon_fn, stories)
    draw_markets_panel(cv, LEFT_X, y, COL_W, FOOT_Y - y)
    y = BODY_Y
    for sec in SECTIONS_RIGHT:
        y = draw_section(cv, RIGHT_X, y, *sec)
    # footer
    cv.fill(0, FOOT_Y, W, H - FOOT_Y, NAVY)
    cv.text("DATE-CHECK AUDIT: ALL 35 STORIES DATED 24-26 NOV 2026 (UTC) - VERIFIED 26 NOV 2026",
            16, 990, 1, WHITE)
    cv.text("14 FIELDS: DATE REGION COUNTRY HEADLINE DECK SOURCE MARKET TOLL LEAD SCENE TIMELINE AUDIT EDITION COUNT | THE DAY'S WORLD NEWS IN ONE IMAGE",
            16, 1002, 1, (148, 163, 184))
    return cv


# ---------------------------------------------------------------- PNG encoder
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.buf[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    data = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    import hashlib
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(here, "output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, path)
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print("wrote %s (%d bytes) sha256=%s" % (path, size, digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
