"""Edit timeline: subtitles (from the voiceover), layered-copy overlays, SFX cues.

Times are seconds in the source video (36.13 s).
"""

# Voiceover transcript, word@start. Corrected from Whisper output
# (VBGV, beg kuning, check out, dehidrasi).
_WORDS = """
Fakta@0.00 atau@0.90 auta?@1.10 |
Ramai@1.82 cakap@1.94 produk@2.22 ni@2.52 boleh@2.70 buat@2.92 result,@3.16 |
jadi@3.80 saya@4.06 try@4.26 sendiri@4.44 untuk@4.76 buktikan.@5.04 |
Kalau@6.00 korang@6.14 tertanya-tanya@6.32 |
dan@6.96 belum@7.12 kenal@7.28 apakah@7.60 produk@7.80 ni,@8.08 |
silakan@8.62 korang@8.88 tekan@9.10 beg@9.30 kuning@9.54 |
untuk@9.72 tengok@9.94 review@10.28 orang@10.68 |
yang@11.00 dah@11.22 puluhan@11.40 ribu@11.74 berjaya@12.12 |
capai@12.58 apa@12.84 yang@13.04 diorang@13.20 mahu.@13.42 |
Untuk@14.70 cara@14.94 pengambilan@15.16 VBGV@15.92 ni,@16.56 |
dalam@17.22 sehari@17.42 korang@18.02 cuma@18.34 ambil@18.56 |
separuh@18.82 daripada@19.16 sebiji@19.50 ni@19.92 |
selepas@20.20 sarapan,@20.54 |
dan@21.06 pastikan@21.38 korang@21.70 ambil@21.94 |
3@22.34 liter@22.56 air@22.76 sehari@23.04 |
untuk@23.80 mempercepatkan@24.08 proses@24.82 |
metabolisme@25.52 korang@26.14 |
dan@26.50 juga@26.84 agar@27.22 diri@27.54 korang@27.76 |
tidak@27.90 dehidrasi.@28.10 |
Korang@28.80 tak@29.56 perlu@29.70 tunggu@29.86 lama@30.12 |
untuk@30.40 check@30.84 out@31.02 benda@31.12 ni@31.38 |
sebab@31.60 stok@32.22 memang@32.54 laju@32.90 |
dan@33.24 cepat@33.50 licin!@34.14 |
Klik@34.76 beg@34.98 kuning@35.20 sekarang!@35.28
"""

# Words to tint purple even when not being spoken.
KEYWORDS = {"vbgv", "result,", "separuh", "3", "liter", "air", "laju", "licin!",
            "beg", "kuning", "berjaya", "review"}


def _chunks():
    out = []
    for raw in _WORDS.strip().split("|"):
        words = []
        for tok in raw.split():
            w, t = tok.rsplit("@", 1)
            words.append((w, float(t)))
        out.append(words)
    res = []
    for i, words in enumerate(out):
        start = words[0][1]
        nxt = out[i + 1][0][1] if i + 1 < len(out) else 36.13
        end = min(nxt, words[-1][1] + 1.1)
        res.append((start, end, words))
    return res


SUBS = _chunks()

# Section boundaries where the video gets a zoom punch + flash.
PUNCHES = [0.0, 5.95, 14.65, 28.78, 34.70]

# Overlays. Lines: (text, style). Styles defined in render.py.
OVERLAYS = [
    # --- Hook: baju lama vs baju baru (layered, never says "slimming") ---
    dict(t0=0.05, t1=3.0, y=420, anim="slide_l",
         lines=[("Baju lama terperap", "big"), ("dalam almari… 👗", "big"),
                ("dah rindu nak disarung semula?", "hl")]),
    dict(t0=3.0, t1=5.95, y=420, anim="slide_r",
         lines=[("ATAU", "tag"), ("Nak beli baju baru", "big"),
                ("untuk OOTD idaman? 🛍️", "big")]),
    # --- Ayat berlapis while explaining ---
    dict(t0=6.05, t1=9.9, y=400, anim="pop",
         lines=[("Almari penuh, tapi 'tiada baju'? 😏", "mid"),
                ("jom bagi baju lama peluang kedua", "hl")]),
    dict(t0=11.0, t1=14.6, y=400, anim="pop",
         lines=[("Zip naik tanpa tahan nafas 🤭", "mid"),
                ("butang pun tak 'menjerit' lagi", "hl")]),
    # --- Cara ambil ---
    dict(t0=14.75, t1=28.7, y=330, anim="pop",
         lines=[("CARA AMBIL VBGV 💜", "head")]),
    # --- CTA ---
    dict(t0=28.85, t1=32.15, y=420, anim="slide_l",
         lines=[("Baju lama? Baju baru?", "big"),
                ("Dua-dua 'muat' dengan yakin ✨", "hl")]),
    dict(t0=32.2, t1=34.65, y=420, anim="shake",
         lines=[("STOK LAJU", "huge"), ("& CEPAT LICIN! 🔥", "huge")]),
    dict(t0=34.7, t1=36.13, y=420, anim="pop",
         lines=[("KLIK BEG KUNING", "huge"), ("SEKARANG! 🛒", "huge")]),
]

# Checklist rows that pop in on the spoken word.
CHECKLIST = dict(t1=28.7, y0=470, gap=112, items=[
    (18.80, "½ biji sehari ✅"),
    (20.20, "Selepas sarapan 🍳"),
    (22.30, "3 liter air sehari 💧"),
])

# Bouncing arrow toward the yellow basket (bottom-left on TikTok).
ARROWS = [(8.6, 11.0), (34.7, 36.13)]

# Persistent corner tag after the hook.
CORNER_TAG = dict(t0=6.0, t1=36.13, text="OOTD mode: ON 👗")

# Sparkle windows.
SPARKLES = [(0.0, 5.9), (11.0, 14.6), (28.8, 36.13)]

SFX = [
    (0.00, "whoosh"), (0.05, "wip"),
    (3.00, "whoosh"), (3.02, "wup"),
    (5.85, "whoosh_down"), (6.05, "wip"),
    (8.60, "pop"),
    (11.00, "wip"), (11.05, "wup"),
    (14.55, "whoosh"), (14.75, "pop"),
    (18.80, "ding"), (20.20, "ding"), (22.30, "ding"),
    (28.70, "whoosh"), (28.85, "wip"),
    (32.20, "wup"), (32.22, "whoosh_down"),
    (34.60, "whoosh"), (34.75, "wip"), (34.90, "wup"),
]
