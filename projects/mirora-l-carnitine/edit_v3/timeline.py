"""v3 "digicam aesthetic" timeline (seconds, matched to the source voice-over)."""

FPS = 30
W, H = 1080, 1920

# name, start, end — each section's two text lines
SECTIONS = [
    ("hook",    0.00,  4.50, "sehari sebiji je?", "RUTIN PAGI AKU SEKARANG"),
    ("brand",   4.70,  8.50, "mirora", "L-CARNITINE COMPLEX"),
    ("benefit", 8.60, 14.40, "sokong tenaga & metabolisme*", "*HASIL BERBEZA BAGI SETIAP INDIVIDU"),
    ("pack",   15.00, 19.30, "10 kapsul · 10 hari", "CUKUP UNTUK CUBA DULU"),
    ("howto",  19.30, 22.30, "1 biji, lepas sarapan", "SETIAP PAGI"),
    ("water",  22.30, 28.80, "+ 3 liter air sehari", "WAJIB, JANGAN SKIP"),
    ("bag",    29.80, 36.00, "kecil, cantik, premium.", "MUAT DALAM BEG TANGAN"),
    ("cta",    36.10, 99.00, "tekan beg kuning", "STOK TERHAD"),
]

# Light-leak transitions + film-wind SFX
CUTS = [4.70, 8.60, 15.00, 19.30, 22.30, 29.80, 36.10]

TYPE_CPS = 24          # typewriter speed, characters per second
WATER_COUNT = (22.9, 25.0)
DAY_COUNT = (15.5, 17.5)
DATE_STAMP = "24 11 2026"
BPM = 76
