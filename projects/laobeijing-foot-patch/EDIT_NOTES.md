# Laobeijing foot patch (老北京足贴) — TikTok Shop video edit

Output: [`laobeijing_foot_patch_tiktok.mp4`](laobeijing_foot_patch_tiktok.mp4). It is 29.6 s long, 1080x1920, 30 fps, with the audio normalised to -14 LUFS.
To render it again, run `python3 edit.py SOURCE.mp4 OUT.mp4` (needs ffmpeg, Pillow and numpy). Add `--preview` with an output folder instead of `OUT.mp4` to get a contact sheet of frames.

## Structure

| Time | Section | What's on screen |
|---|---|---|
| 0–5.7s | **Hook** | "KAKI LENGUH? 😩", then "KERJA LAMA BERDIRI?" when you say it. "50 KEPING CUMA RM9.99!" pops in at 0.6 s, with the product photo and a -72% badge |
| 5.8–10.5s | Value | Big "50 KEPING / dalam 1 kotak", then a price card: ~~RM36.00~~ **DARI RM9.99** |
| 10.5–13s | Social proof | A buyer's 5-star review ("bangun tidur rasa ringan badan…"), ⭐4.7 (6.7K review), 🔥44.3K terjual, and "RASA SELESA BETUL" |
| 13–22.7s | How to use | Step banners: Cara pasang senang je → Langkah 1 Koyak sticker besar → Langkah 2 Letak pad, bunga di luar → Langkah 3 Tampal di tapak kaki → Langkah 4 Pakai masa tidur. The shop's "Cara Guna" image covers the shot of empty floor |
| 22.7–25s | Why buy | Slow motion on both feet with patches on, and a ✅ list: kaki lenguh & lama berdiri, cuka buluh + arang buluh, bau herba tak busuk, pakai malam buka lepas 8 jam |
| 25–29.6s | **CTA** | Blurred background, product photo, ~~RM36.00~~ **DARI RM9.99**, 50 KEPING / KOTAK, FREE SHIPPING, "TEKAN BEG KUNING SEKARANG 👇" |

Captions follow your own narration. It was transcribed with Whisper and corrected by hand (`PHRASES` in `edit.py`). The current word is shown in yellow.

## Cuts made to the original

- Removed the quiet first 0.45 s. All the narration is kept, because there was no dead air.
- Sped up to 1.1x with the pitch kept the same.
- The two shots of empty floor (when the hands leave the frame) are covered by overlays.

## Advertising approach

- The problem ("kaki lenguh?") and the price both appear in the first 3 seconds.
- The price is shown three times: in the hook, when you say "harga pun tak mahal", and in the CTA.
- The social proof (rating, review count, number sold) comes right after "rasa selesa betul".
- **No detox or "buang toksin" claims.** TikTok rejects health claims, so the listing's "Buang Tok Sin" heading was cropped out. Review photos of black, used patches were also left out, because they imply toxins are coming out. Claims stay with comfort, ingredients and how to use the patch.

## Before posting

- **Check the price.** The listing says "From RM9.99", which may be the price of the cheapest variant (reviews mention both 10 PCS and 50 PCS boxes). If RM9.99 is not the 50-piece box, change `PRICE` / `PRICE_OLD` / `DISCOUNT` at the top of `edit.py`, or change "50 KEPING" to match, and render again.
- The last ~7 s have no sound. Add a trending sound from the TikTok **Commercial Music Library** inside the app at about 10–15% volume.
- Link the product (yellow basket) when posting.
