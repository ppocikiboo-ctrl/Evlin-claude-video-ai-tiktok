"""Shared settings and the edit timeline for the VBGV 30-second TikTok ad."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
BUILD = ROOT / "build"
OUTPUT = ROOT / "output"

W, H = 1080, 1920
FPS = 30
DURATION = 30.0
FRAMES = int(DURATION * FPS)
BPM = 120  # one beat = 0.5 s, so every scene boundary lands on a beat

# Brand palette (RGB)
DEEP_PURPLE = (46, 16, 92)
PURPLE = (124, 58, 237)
LAVENDER = (200, 170, 255)
WHITE = (255, 255, 255)
GOLD = (232, 197, 120)  # champagne gold
GOLD_HI = (255, 228, 160)

FONT_BLACK = FONTS / "InterDisplay-Black.otf"
FONT_XBOLD = FONTS / "InterDisplay-ExtraBold.otf"
FONT_BOLD = FONTS / "InterDisplay-Bold.otf"
FONT_SEMI = FONTS / "InterDisplay-SemiBold.otf"

# TikTok safe area: keep text clear of the top bar, the right-hand action
# icons and the caption / product-anchor area at the bottom.
SAFE_TOP = 200
SAFE_BOTTOM = H - 380
SAFE_LEFT = 60
SAFE_RIGHT = W - 150

# Footage plan. Every shot comes from the original upload; nothing is
# generated. The source clip is only 11.2 s long, so shots are slowed down
# (frame-blended to 30 fps) and two of them are played as a boomerang.
#   src_in / src_out: seconds in the original clip
#   dur: seconds the shot occupies in the final edit
#   boomerang: play forward then backward
SHOTS = [
    # scene 1 hook: pack swings into frame
    dict(src_in=0.90, src_out=2.70, dur=3.0),
    # scene 2 problem: front of the pack
    dict(src_in=2.70, src_out=4.70, dur=3.0),
    # scene 3 reveal: front of the pack held steady
    dict(src_in=2.90, src_out=4.40, dur=3.0),
    # scene 4 highlights: tablets poured from the pack
    dict(src_in=5.60, src_out=7.60, dur=4.0),
    # scene 5 lifestyle: back of the pack
    dict(src_in=8.80, src_out=11.15, dur=4.0),
    # scene 6 info: tablets in the palm, pack above
    dict(src_in=6.70, src_out=7.70, dur=4.0, boomerang=True),
    # scene 7 self-care: front of the pack, natural speed
    dict(src_in=1.80, src_out=5.40, dur=4.0),
    # scene 8 CTA: final close-up of the front of the pack
    dict(src_in=2.90, src_out=4.60, dur=5.0, boomerang=True),
]

SCENE_STARTS = [0, 3, 6, 9, 13, 17, 21, 25]
CUTS = SCENE_STARTS[1:]

# Colour grade applied to the footage (ffmpeg filters): a little brighter,
# a little more contrast with lifted blacks, lavender in the highlights and
# a light sharpen so the pack lettering stays crisp.
GRADE = ",".join([
    "eq=brightness=0.035:contrast=1.07:saturation=1.04:gamma=1.03",
    "curves=all='0/0.025 0.5/0.52 1/1'",
    "colorbalance=rh=0.025:gh=-0.01:bh=0.04:rs=0.01:bs=0.015",
    "unsharp=5:5:0.45:5:5:0.0",
])
