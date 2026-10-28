# FRANKLY PDRN Bounce Ball Serum — Korean-luxury skincare ad (45s, 9:16)

Finished video: [`output/frankly-pdrn-bounce-ball-serum.mp4`](output/frankly-pdrn-bounce-ball-serum.mp4)
(1080×1920, 30 fps, H.264 + AAC, about −13 LUFS).

All on-screen text is in Bahasa Melayu. There is no voice-over. The video uses the
original product panels (in `reference/`) and clips from the hands-on phone video of
the real bottle, so the bottle, the FRANKLY logo, the product name and the orange
serum ball all come from real images and are never redrawn.

## Timeline

| Time | Scene | Source images | On-screen text |
|---|---|---|---|
| 0.0–4.6 | Hook: close-up of glowing skin, a droplet crossing the frame, a peach light sweep, a zoom into the next scene | 04 (model, cropped to exclude the "Clinic Level" text) | DAH MASUK 30-AN? 👀 · Kulit nampak kusam & kurang lembap? · JOM KENAL PDRN SERUM! 🧡 |
| 4.6–10.2 | Product reveal: a pseudo-3D spin-in, orbiting salmon spheres, gold ribbons, holographic rings, a gloss sweep, then a macro push into the orange ball | 02 (main bottle), 07 (label macro, cropped to exclude "0.00 Zero Irritation") | FRANKLY PDRN · BOUNCE BALL SERUM · SALMON DNA 🧡 |
| 10.2–16.2 | What is PDRN: an animated DNA double helix with a mind map that draws in four glowing branches | 03 (title only; the before/after photos are cut out) | KENALI PDRN 🧬 + 4 branches · disclaimer that PDRN is a cosmetic ingredient |
| 16.2–22.0 | Ingredient: a floating orange sphere with shimmer particles and ingredient cards | 05 (liquid ball area, no claim text) | SALMON PDRN · 100,000 ppm* · SALMON EGG EXTRACT · 3 cards · *footnote |
| 22.0–28.0 | Shake to activate: real shaking footage, a waving hand icon, then the ball breaking into particles | hands-on video 5.4–8.6 s, 06 (the two bottle boxes only) | GONCANG DAHULU! 🧡 · Sebatikan serum sebelum digunakan. |
| 28.0–32.6 | Hydration and glow: droplets gliding over the skin, a light sweep | 04 | KULIT NAMPAK SEGAR ✨ · LEMBAP & BERSERI 💧 · JAGA KULIT DARI SEKARANG 🧡 |
| 32.6–39.6 | How to use: 4 steps with numbered badges, a progress row and an effect for each step | 08 (three bottles), hands-on video (shake, apply, pat) | CARA PENGGUNAAN 🧡 + steps 1–4 |
| 39.6–45.0 | CTA: both packaging versions on a pearl pedestal with light rays, hearts, spheres and a pulsing yellow button | 09 (the "Skin Repair" headline is cropped out) | SKINCARE ROUTINE UPGRADE! 🧡 · JAGA KULIT, JAGA KEYAKINAN ✨ · KENALI FRANKLY PDRN SERUM · SEMAK BAKUL KUNING 🛒 |

## Compliance choices

- The before/after photos (03), "Clinic Level / real clinical treatments" (04),
  "0.00 ZERO Irritation" (07), "Skin Repair Results" (09) and "fast absorption /
  instant glow / elasticity" (05) are cropped out. None of these claims appears in the video.
- The 100,000 ppm figure carries an asterisk and the footnote *"Angka berdasarkan bahan
  pemasaran jenama."*
- The PDRN scene states that PDRN is a cosmetic skincare ingredient. The video makes no
  anti-ageing, medical or injectable claims.
- The CTA notes *"Formula sama • Pembungkusan mungkin berbeza"*.

## Re-rendering

```
cd render
python3 render.py --video /path/to/hands-on.mp4                      # full video -> ../output/
python3 render.py --video /path/to/hands-on.mp4 --stills 1,6.5,13.5  # preview frames
```

Requirements: Python 3 with numpy and Pillow, and ffmpeg. A full render takes about 3
minutes on 4 cores. The hands-on video is not stored in the repo; pass it with `--video`.
The music (a soft 100 BPM Fmaj9–G6–Em7–Am9 instrumental with bell arpeggios) and all
sound effects (whoosh, pop, ting, shake, splash, tik) are synthesised in
`render/audio.py`, so the audio carries no licensing issues. For extra polish you can
swap in a track from TikTok's commercial music library in CapCut.

Asset credits: Poppins and Playfair Display (SIL Open Font License); emoji from
[Twemoji](https://github.com/jdecked/twemoji) (CC-BY 4.0).
