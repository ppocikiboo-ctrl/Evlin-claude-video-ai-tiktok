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
