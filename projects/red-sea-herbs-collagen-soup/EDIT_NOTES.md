# Red Sea Herbs Collagen Soup — TikTok Shop video edit

Output: [`collagen_soup_tiktok.mp4`](collagen_soup_tiktok.mp4). It is 62 s long, 1080x1920, 30 fps, about 9.5 Mbps, with the audio normalised to -14 LUFS.
The source is the full-quality recording, uploaded in 5 parts and joined in this order: `144538` → `144924` → `144944` → `144807` → `145453`. The timings in `SEGMENTS` match that joined file. To render it again, run `python3 edit.py SOURCE.mp4 OUT.mp4`. The script needs ffmpeg, Pillow and numpy.

## Structure

| Time | Section | What's on screen |
|---|---|---|
| 0–3s | **Hook** | Push-in on the finished jelly soup, starting with a white flash. Text: "RAHSIA CANTIK DARI DALAM / RM9 JE DAPAT **4-6 MANGKUK** SUP COLLAGEN!". The product bag pops in with a FLASH SALE badge |
| 3–10s | Intro | Product bag with Halal / 100% Organic / 100% Natural badges. The ingredients photo pops out with "6 BAHAN DALAM 1 PEK" |
| 10–29s | Steps 1–3 | Step banners. Each ingredient name pops in as you say it. Big numbers "24 JAM" and "1.5 LITER" |
| 29–53s | Steps 4–6 | Adding the ingredients, "45 MINIT", and the last 5 minutes (gula Melaka + sarang burung salji) |
| 53–58s | Result | The bowl photo pops out ("HASILNYA… 🤤"), then a ✅ benefit list from the listing |
| 58–63s | **CTA** | Blurred background, product card, **RM9.76**, FREE SHIPPING, "TEKAN BEG KUNING SEKARANG 👇" |

Captions are word by word (the current word is yellow) and use your own narration, transcribed with Whisper. The transcript is in `assets/transcript.json`.

## Cuts made to the original

- Removed the silences and fumbling, such as the 46–53s gap and the plate-scraping at 63–70s.
- Removed repeated lines: "dan kita boleh ikut cara-cara… belakang paket", the first "masukkan getah peach", and the duplicate "5 minit terakhir… gula melaka dengan sarang burung salji".
- Sped up the talking segments to 1.15x, with the pitch kept the same.

## Advertising approach used

- Show the result (the jelly soup) in the first 3 seconds and say the offer straight away. This follows TikTok's guidance to state the value within 3 seconds and to use text overlays.
- Each step has its own banner, and something new pops in every 2–3 seconds to keep attention.
- The ending has one CTA, the yellow basket, together with the price and free shipping.
- Claims are kept to what the product listing says: no preservatives, clean hand-picked grade, enjoy hot or cold, serves 4–6, Halal. There are no medical or "glowing skin" promises, because those get ads rejected.

## Before posting

- Check the price (RM9.76) and the FLASH SALE badge are still correct. Change `C1` / `FLASH` in `edit.py` if they have changed.
- Add a trending sound from the TikTok **Commercial Music Library** inside the app at about 10–15% volume. No music is baked in, to avoid copyright problems.
- Link the product (yellow basket) when posting.

---

# Video 2 — short FAB ad (`collagen_soup_tiktok_v2_FAB.mp4`)

The video is 32 s long. It is made from the same full-quality source by `python3 edit_v2.py SOURCE.mp4 OUT.mp4`.

| Time | Block | Content |
|---|---|---|
| 0–3s | Hook (problem) | "NAK DESSERT COLLAGEN TAPI TAK NAK **BAYAR MAHAL?**" with a screen shake. The product pops in with "RM9.76 JE" and "TENGOK NI 👇" |
| 3–9s | FAB 1 | **F** 6 bahan premium dalam 1 pek → **A** Tak payah cari satu-satu → **B** Jimat masa & duit |
| 9–16s | FAB 2 | **F** Bahan semulajadi, gred bersih → **A** Tanpa bahan pengawet → **B** Tenang hidang untuk keluarga |
| 16–19s | FAB 3 | **F** Rendam + rebus 45 minit → **A** Tak perlu pandai masak → **B** Sesiapa pun boleh buat |
| 19–22s | FAB 4 | **F** Tekstur berjeli & lembut → **A** Sedap panas atau sejuk → **B** Rahsia cantik dari dalam |
| 22–26s | Value | 1 pek RM9.76 = 4–6 mangkuk → counter runs down to **CUMA RM2.44 SEMANGKUK** (RM9.76 ÷ 4) |
| 26–32s | CTA | **Why now:** ⏰ Flash sale tak kekal · **Reason:** harga flash sale + free shipping · **Benefit:** minggu ni dah boleh hidang sendiri · **Action:** 🛒 TEKAN BEG KUNING (pulsing) · **If not:** "Tunggu esok = harga naik semula" |

Visual style: a yellow progress bar along the top, whip-blur transitions at every cut, a stacked F/A/B card with coloured badges, captions with the current word on a yellow block, and a price-per-bowl counter.

Check before posting: the flash sale price, and that it really ends. "Harga naik semula" is only true while a flash sale price is active.

---

# Video 3 — "3 SEBAB" listicle (`collagen_soup_tiktok_v3_3SEBAB.mp4`)

The video is 33.5 s long. It is made from the same full-quality source by `python3 edit_v3.py SOURCE.mp4 OUT.mp4`. Its colours follow the pack (deep green and cream).

| Time | Block | Content |
|---|---|---|
| 0–3s | Hook (split screen) | The top half shows the raw ingredients ("DARI INI…") and the bottom half the jelly soup ("…JADI INI! 🤤"). An "RM9.76 JE!" stamp lands in the middle |
| 3–8s | Title | "3 SEBAB KAMU WAJIB CUBA SUP COLLAGEN NI 👇" over the product, with her intro line |
| 8–16s | #1 Semua bahan dah ada | A spinning #1 badge. The ingredients photo pops out, then a chip for each ingredient appears as she names it |
| 16–22s | #2 Senang gila nak masak | A live checklist that ticks off: Rendam 24 jam ✓, Didih 1.5L air ✓, Rebus 45 minit ✓, Siap dihidang ✓ |
| 22–27s | #3 Jimat & cukup sekeluarga | The bowl photo pops out, then "≈ RM2.44 SEMANGKUK!" |
| 27–33.5s | CTA end card | Cream background with scrolling FLASH SALE tickers and the full promo image. **Sebab** (reason): harga flash sale + free shipping · **Untung** (benefit): dessert collagen cukup sekeluarga · **Action:** pulsing "TEKAN BEG KUNING" button · **If not:** "Flash sale tamat = harga naik semula" |

Captions sit in a cream box, with the current word on a green block. Every cut has a green and yellow diagonal wipe.
