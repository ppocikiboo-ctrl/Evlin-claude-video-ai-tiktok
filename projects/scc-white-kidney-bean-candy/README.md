# SCC White Kidney Bean + L-Carnitine Candy — TikTok edit

Source: talking/hand-demo clip, 35.6 s → final edit **25.4 s** (`output/scc-tiktok-edit.mp4`).

## What was done
- Long pauses cut (ffmpeg `silencedetect`), speech sped up **1.15x** so it flows.
- Jump-cut punch-in zooms, white flash on each cut, light colour grade, vignette, progress bar, loudness normalised to -14 LUFS.
- Text overlays (Pillow PNGs):

| Time (s) | Overlay |
|---|---|
| 0–3 | Hook: "Craving tengah malam tak boleh tahan?" |
| 3–6 | Hook: "Baju baru dah beli... tapi zip tak naik?" |
| 6–10.6 | Product name + "Bantu kawal selera" / "1/2 tablet sehari je" |
| 10.6–17.4 | Two real buyer reviews (`reference/review-*.jpg`, unedited text) |
| 17.4–23.8 | Soft conclusion: "Bila selera dah 'jinak'... pinggang pun ikut 'senyap'" / "Baju lama terasa longgar, baju baru pun berani pakai" |
| 23.8–end | CTA "KLIK BEG KUNING & cuba sendiri!" + disclaimer |

## Re-render
```
python3 edit.py <input.mp4> output/scc-tiktok-edit.mp4
```
Edit `SEGMENTS`, `SPEED` and `build_overlays()` in `edit.py` to change cuts, speed or text.

## Version 2 — no voice, text-led (`edit_v2.py`)
Voice removed; whole clip kept at 1.10x (31.9 s). Outputs:
- `output/scc-tiktok-v2-features.mp4` — with a soft generated background beat (royalty-free)
- `output/scc-tiktok-v2-features-nosound.mp4` — silent, add a TikTok library sound in-app

| Time (s) | Overlay |
|---|---|
| 0–6.4 | Hook: "Baju impian masih tergantung dalam almari?" / "Dah tiba masa dia 'keluar' dari almari..." |
| 6.4–8.8 | Product name |
| 8.8–17.8 | CARA MAKAN checklist: 1 pack = 5 biji · Belah 2 - 1/2 biji sehari · Makan selepas sarapan · Minum air 3 liter sehari |
| 17.8–22.8 | "Rutin kecil, langkah besar" / "Simple, comel, muat dalam beg tangan" |
| 22.8–27.6 | "Baju lama pun mula 'senyum' balik..." / "Tak perlu tunggu tahun depan, biar baju impian yang tunggu awak" |
| 27.6–end | CTA "KLIK BEG KUNING SEKARANG" + why now + cost of waiting + disclaimer |

No "craving" wording and no buyer-review text in v2 (TikTok strike risk); only layered/figurative lines.

## House style for future edits (agreed with owner)
- Remove the owner's voice; tell the story with on-screen text (silent export + optional generated beat).
- Never say "craving", never show buyer-review text, no direct weight/diet claims or timeline promises.
- Layered/figurative lines only (e.g. "baju impian", "baju lama 'senyum' balik").
- Structure: hook → product → CARA MAKAN checklist → routine lines → figurative benefit → CTA (what / why now / cost of waiting) + disclaimer.
- Captions/hashtags: no craving, kurus, turun berat, weightloss or diet words.
