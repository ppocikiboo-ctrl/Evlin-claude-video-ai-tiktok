"""v4 "sticker meme" timeline for the 16.6s hand-held clip.

Rule for this clip: the product sits in the middle of the frame and the
burned-in captions sit at the bottom, so every overlay stays in the top band
(y < SAFE_BOTTOM on the 1080x1920 canvas), and the footage is not zoomed.
"""

FPS = 30
W, H = 1080, 1920
SAFE_BOTTOM = 600

# Story beats, matched to the voice-over
HOOK = (0.00, 3.90)          # "siapa korang yang dah lama stuck"
STRUGGLE = (3.90, 7.90)      # "tapi susah sangat nak disiplin, teringin melantak"
CRAVE_IN = (5.6, 7.4)        # food emojis drop in one by one
POOF = 7.90                  # cravings vanish
BRAND = (8.00, 10.40)        # "kenalkan korang dengan MIRORA ni"
HOWTO = (10.40, 13.00)       # "hanya ambil sebiji, cukup untuk 10 hari"
CTA = (13.00, 16.00)         # "klik kuning sekarang ... harga kawan-kawan"
FRIEND_PRICE = 14.20
OUTRO = (16.00, 99.0)        # "semoga berjaya"

CUTS = [STRUGGLE[0], BRAND[0], HOWTO[0], CTA[0], OUTRO[0]]
BPM = 118
