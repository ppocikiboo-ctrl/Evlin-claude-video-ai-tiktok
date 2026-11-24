"""Version 3 timeline: "Chat Bestie" — group-chat story + phone notifications.

Same voiceover and subtitles as v1/v2. Avoid the word "bio" on screen.
"""
from timeline import KEYWORDS, SUBS  # noqa: F401  (same voiceover)

# Whip-pan transitions.
PUNCHES = [0.0, 5.95, 14.65, 28.78, 32.18, 34.70]

CHAT_HEADER = "Geng OOTD 👗"

# Chat groups: (t_end, [(t0, side, text)]). side "L" = bestie, "R" = saya.
CHATS = [
    (14.6, [
        (0.10, "L", "Weekend ni jom OOTD! 📸"),
        (1.50, "R", "Baju lama dalam almari tu… boleh ke? 🥲"),
        (3.00, "L", "Atau beli baju baru je? 🛍️"),
        (4.40, "R", "Kejap, aku ada rahsia 🤫"),
        (6.20, "L", "Rahsia apa?! 👀"),
        (8.60, "R", "Tekan beg kuning, tengok review 👇"),
        (11.40, "L", "Puluhan ribu dah cuba?! 😱"),
        (12.80, "R", "Dress lama aku pun dah ready keluar jalan 💃"),
    ]),
    (32.1, [
        (28.85, "L", "Baju lama ke baru, dua-dua jadi! ✨"),
        (30.40, "R", "Weekend ni kita OOTD 📸💜"),
    ]),
]
CHAT_AREA = dict(top=270, bottom=860)

# Phone notification banners stacking down from the top.
NOTIFS = dict(t1=28.7, y0=300, gap=150, items=[
    (14.75, "Rutin OOTD Ready 🔔", "3 langkah je, jom mula!"),
    (18.80, "Langkah 1", "½ biji sehari"),
    (20.20, "Langkah 2", "Selepas sarapan 🍳"),
    (22.30, "Langkah 3", "Minum air 3 liter sehari 💧"),
])

ALERT = dict(t0=32.2, t1=34.65, y=460, title="⚠️ STOK HAMPIR HABIS!",
             body="Stok laju & cepat licin 🔥")

CTA = dict(t0=34.75, t1=36.13, y=440, text="🛒 TEKAN BEG KUNING", sub="sebelum sold out!")

POINTERS = [(8.6, 11.3), (34.75, 36.13)]

# Floating live-style reactions rising on the right.
REACTIONS = dict(windows=[(0.3, 5.9), (11.4, 14.6), (28.85, 36.13)],
                 emojis=["💜", "😍", "🔥", "👗", "✨", "🛍️"])

SFX = [
    (0.00, "whoosh"), (0.10, "pop"),
    (1.50, "wip"), (3.00, "pop"), (4.40, "wip"),
    (5.85, "whoosh_down"), (6.20, "pop"),
    (8.60, "wip"), (11.40, "pop"), (12.80, "wip"),
    (14.55, "whoosh"), (14.75, "ding"),
    (18.80, "ding"), (20.20, "ding"), (22.30, "ding"),
    (28.68, "whoosh"), (28.85, "pop"), (30.40, "wip"),
    (32.10, "whoosh_down"), (32.22, "thud"), (32.30, "wup"),
    (34.60, "whoosh"), (34.78, "wip"), (34.95, "wup"),
]
