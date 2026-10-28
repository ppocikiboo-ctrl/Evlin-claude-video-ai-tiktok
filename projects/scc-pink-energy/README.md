# SCC: Pink Energy × 3D body care (Remotion)

The finished video is **[`out/SCC_Pink_Energy.mp4`](out/SCC_Pink_Energy.mp4)**.

| Setting | Value |
|---|---|
| Duration | 11.5 s (345 frames) |
| Size and frame rate | 1080 × 1920, 9:16, 30 fps |
| Video | H.264 at about 18 Mbps |
| Audio | AAC, 48 kHz, 320 kbps |
| Language | Bahasa Melayu text, no voice-over |

This version is built around a **strong hook in the first 2 seconds**. It fixes
the problems with the earlier SCC edits:

| Problem | Fix |
|---|---|
| Hook not clear enough | the hook is on screen from **frame 0**: big bold white text with a neon pink outline, top centre |
| Opening text didn't stand out | 104 px text, a fast zoom punch, an impact flash, shockwave rings, a short screen shake and BOOM on frame 0 |
| Too many animations | stars cut to 18 and sakura to 6, no floating counters, at most one character/animation group at a time |
| Product not dominant enough | panels sit above or below the pack, never over the label; light rings frame the product |
| Text too small | every line is 56–104 px; there are no small sub-lines |

**One continuous take.** The original clip plays once, start to finish, with no
cuts. The product is untouched.

## Timeline

The timings are guides for the graphics only; the footage itself is never cut.

| Time | Text (one at a time) | Animation | Sound |
|---|---|---|---|
| 0.0–1.8 s | **JAGA MUKA DAH, BADAN PULA? 👀💗** | hook: visible on frame 0, zoom punch, flash, shockwave, sparkles, footage shake | **BOOM** (frame 0) → KLIK → TING |
| 1.8–3.4 s | SELF-CARE BUKAN SEKADAR SKINCARE ✨ | glass panel slides in (bottom); small 3D woman stretching beside it | WHOOSH, KLIK, TIK-TIK, TING |
| 3.4–5.0 s | KENALI SCC 💕 | hologram panel below the pack; digital light ring around the pack | WHOOSH, KLIK, TIK-TIK, TING, sparkle |
| 5.0–7.2 s | WHITE KIDNEY BEAN + L-CARNITINE | hologram panel scans in (top) | WHOOSH, KLIK, TIK-TIK, TING |
| 7.2–9.2 s | RUTIN PENJAGAAN DIRI 🌸 | 3D woman walks in, does 3 light presses with colourful dumbbells (light-drop sweat), then sips water; icons: water bottle filling to 3 L, walking shoe, balanced plate, each with a light circling it | WHOOSH, KLIK, TIK-TIK, TING; soft clink, plink, pop, bloop |
| 9.2 s–end | NAK TAHU LEBIH LANJUT? 🛍️ | panel (top), product centred with a light ring, 2 pink butterflies, sakura | WHOOSH, KLIK, TIK-TIK, TING, sparkle |

The music (an original K-beauty electro-pop track, 120 BPM, no vocals) starts on
frame 0 at full energy and sits under the SFX.

## Run it

You need Node 18+, Python 3 with `numpy`, and `ffmpeg`.

```bash
cd projects/scc-pink-energy
npm install
npm run prep      # footage -> public/footage.mp4, synthesized audio -> public/audio/
npm run studio    # live preview in the browser
npm run render    # -> out/SCC_Pink_Energy.mp4
```

The first render downloads Remotion's Chrome Headless Shell automatically.
To use one you already have instead, set `REMOTION_BROWSER=/path/to/chrome-headless-shell`.
For a single frame, run `npm run still -- out/frame.png --frame=0`. To see the
woman's poses (stretch, walk, dumbbell press, drink), run
`npx remotion still WomanTest out/woman.png`.

## Folder layout

```
input/original.mp4             your untouched upload
scripts/prep_footage.sh        whole clip -> 11.5 s @ 30 fps H.264, light denoise/brighten/sharpen
scripts/make_audio.py          K-beauty electro-pop bed + BOOM / KLIK / TIK-TIK / TING / WHOOSH / SPARKLE
                               and soft pop / clink / plink / bloop
src/timeline.ts                every frame: text lines, layers, the woman's routine, SFX cues, volumes
src/SccPinkEnergy.tsx          the composition: footage, hook, panels, woman, icons, audio
src/components/KoreanWoman.tsx 3D-style woman: stretch, walk, dumbbell presses, sweat light drops,
                               drinking water (two-bone arm IK)
src/components/GlassPanel.tsx  see-through hologram glass panel (open / slide / scan)
src/components/DecodeText.tsx  digital decode typing
src/components/CareIcons.tsx   3 L water bottle, sneaker, balanced plate, icon badges
src/components/Atmosphere.tsx  pearl/white/pink light, stars, sakura, particles, light rings
src/components/Butterfly.tsx   pink hologram butterflies
src/components/Icons.tsx       👀 💗 ✨ ✦ as SVG
src/dev/WomanTest.tsx          pose check sheet (development only)
```

## Colour grade

The footage gets a light denoise, a little brightness and contrast and a mild
sharpen. The hue is untouched, so the SCC colours and skin tones stay natural
and nothing on the pack is blurred. On top sit a white key light, pastel pink
corners and a pearl-white reflection at the edges only.

## Safety

- There are no fat-burning, weight-loss, metabolism or body-change claims, no
  before/after and no testimonials.
- The workout, dumbbells, sweat drops and water are general lifestyle visuals,
  never linked to the product. The woman's body shape and size never change.
- The plate is a balanced plate (half vegetables, a quarter protein, a quarter
  rice) shown as an icon. There is no "eat a lot" or leftover-food animation.
- The hearts appear only as small icons inside the text (💗 💕), as the brief
  asks; there are no floating heart animations.
- The pack itself says "DIET SUPPORT" and "Supports Weight Management", and it
  is left untouched. **Check that SCC is allowed in your TikTok Shop category
  before posting.**
- All audio is synthesized by `scripts/make_audio.py`, with no samples, so it is
  free to use commercially.
- Remotion is free for individuals and companies of up to 3 people. Larger
  companies need a company licence (see remotion.dev/license).
