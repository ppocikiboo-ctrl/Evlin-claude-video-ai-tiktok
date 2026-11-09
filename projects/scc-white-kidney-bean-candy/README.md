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
