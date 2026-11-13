"""Version 2 timeline: "Closet Diary" fashion-magazine look.

Same voiceover and subtitles as v1, different layered copy and visuals.
Avoid the word "bio" anywhere on screen.
"""
from timeline import KEYWORDS, SUBS  # noqa: F401  (same voiceover)

# Section changes: diagonal swipe wipe + glitch + zoom punch.
PUNCHES = [0.0, 5.95, 14.65, 28.78, 32.18, 34.70]

HEADLINES = [
    dict(t0=0.05, t1=2.95, y=430, anim="rise",
         lines=[("POV:", "kicker"), ("baju lama dalam almari", "serif"),
                ("dah lama tunggu kamu 👀", "serif")]),
    dict(t0=3.0, t1=5.9, y=330, anim="rise",
         lines=[("Atau OOTD baru idaman?", "serif")]),
    dict(t0=6.05, t1=10.9, y=400, anim="rise",
         lines=[("Dress kesayangan tahun lepas", "serif"),
                ("masih tunggu giliran 💃", "serif"),
                ("jom bagi dia peluang kedua", "pinkpill")]),
    dict(t0=10.95, t1=14.6, y=400, anim="rise",
         lines=[("Gaya sama,", "serif"), ("keyakinan baru ✨", "serif")]),
    dict(t0=28.85, t1=32.1, y=420, anim="rise",
         lines=[("Jangan biar baju cantik", "serif"),
                ("terus 'bersara' 😌", "serif"),
                ("OOTD kamu, peraturan kamu", "pinkpill")]),
    dict(t0=34.75, t1=36.13, y=420, anim="pop",
         lines=[("TEKAN BEG KUNING", "shout"), ("sebelum sold out 🛒", "pinkpill")]),
]

# Hook "versus" card (3.0 - 5.9 s).
VERSUS = dict(t0=3.0, t1=5.9, y=560, left="BAJU LAMA 👗", right="BAJU BARU 🛍️",
              sub=("Pilih je, dua-dua jadi ✨", 3.6))

# Rubber stamp slammed on "puluhan ribu".
STAMP = dict(t0=11.40, t1=14.6, x=690, y=700, lines=["PULUHAN RIBU", "DAH BERJAYA"])

# Notes-app style routine card.
NOTES = dict(t0=14.75, t1=28.7, y0=300, title="📝 Rutin OOTD Ready", items=[
    (18.80, "½ biji sehari"),
    (20.20, "Selepas sarapan 🍳"),
    (22.30, "3 liter air sehari 💧"),
])

# Scrolling caution-tape banners (32.2 - 34.65 s).
TAPE = dict(t0=32.2, t1=34.65, text="STOK LAJU  •  CEPAT LICIN  •  ")

# Bouncing pointer toward the yellow basket (bottom-left on TikTok).
POINTERS = [(8.6, 10.9), (34.75, 36.13)]

CORNER_TAG = dict(t0=6.0, t1=36.13, text="Closet Diary 👗")

SPARKLES = [(0.0, 5.9), (10.95, 14.6), (28.8, 32.1), (34.7, 36.13)]

SFX = [
    (0.00, "whoosh"), (0.08, "wip"),
    (3.00, "whoosh_down"), (3.05, "pop"), (3.25, "wup"),
    (5.85, "whoosh"), (6.08, "wip"),
    (8.60, "pop"),
    (10.95, "wup"), (11.40, "thud"),
    (14.55, "whoosh"), (14.80, "wip"),
    (18.80, "ding"), (20.20, "ding"), (22.30, "ding"),
    (28.68, "whoosh"), (28.90, "wup"),
    (32.10, "whoosh_down"), (32.22, "thud"),
    (34.60, "whoosh"), (34.78, "wip"), (34.95, "wup"),
]
