"""Shared timeline for the v2 edit (seconds, matched to the source voice-over)."""

FPS = 30
W, H = 1080, 1920

# name, start, end, y (top of card on 1080x1920 canvas)
CARDS = [
    ("hook",    0.00,  4.50, 150),
    ("brand",   4.70,  8.50, 160),
    ("benefit", 8.60, 14.40, 150),
    ("pack",   15.00, 19.30, 150),
    ("howto",  19.30, 22.30, 160),
    ("water",  22.30, 28.80, 150),
    ("bag",    29.80, 36.00, 160),
    ("cta",    36.10, 99.00, 150),
]

# Section changes: white flash + whoosh + zoom punch
CUTS = [4.70, 8.60, 15.00, 19.30, 22.30, 29.80, 36.10]

# Feature animations
DAY_DOTS = (15.40, 17.40)   # 10 dots light up one by one
WATER_FILL = (22.70, 24.90)  # 3L bar fills
BPM = 100
