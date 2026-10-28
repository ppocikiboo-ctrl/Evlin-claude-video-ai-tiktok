# SCC: Korean futuristic body care (Remotion)

The finished video is **[`out/SCC_Korean_Futuristic.mp4`](out/SCC_Korean_Futuristic.mp4)**.

| Setting | Value |
|---|---|
| Duration | 11.5 s (345 frames) |
| Size and frame rate | 1080 × 1920, 9:16, 30 fps |
| Video | H.264 at about 18 Mbps |
| Audio | AAC, 48 kHz, 320 kbps |
| Language | Bahasa Melayu text, no voice-over |

The style is Korean beauty × futuristic wellness tech × 3D body-care animation.

**One continuous take.** The original SCC clip plays once, start to finish,
with no cuts or reordering. It gets only a light denoise, brighten and sharpen.
Every graphic is a layer that fades or animates in and out on top. The SCC
name, logo, pack text and colours, the hands and the original movement are
untouched, and nothing is drawn over the label.

## Text: six lines, one at a time, each with its own style

| Frames | Line | Style | Placement |
|---|---|---|---|
| 2–56 | SELF-CARE BUKAN SEKADAR SKINCARE! ✦ | **hologram**: glass panel switches on, digital decode typing | top |
| 64–118 | JANGAN LUPA PENJAGAAN BADAN ✨ | **glass bubble**: wobbly bubble pops in, words pop one by one, tiny bubbles rise | bottom, below the big pack |
| 124–170 | KENALI SCC ✨ | **zoom**: zooms in from 2.8× out of a blur, letters pull together, light-burst ring on landing | top |
| 174–228 | WHITE KIDNEY BEAN + L-CARNITINE | **moving digital text**: HUD strip opens, characters slide in from the right as glowing blocks, scan line, progress bar | top |
| 236–284 | JADIKAN SELF-CARE SATU RUTIN 🌸 | **neon**: neon frame draws itself, words flicker on like neon tubes, stars twinkle | top |
| 296–345 | KENALI PRODUK INI ✨ | **slide**: glass panel slides in from the left with a star trail, words slide in | top, stays to the end |

Every line has **KLIK** (appears), **TIK-TIK** (text moving in) and **TING**
(animation complete). There is a **WHOOSH** at each transition, and a
**sparkle** whenever stars, butterflies or sakura appear (`src/timeline.ts`).

## Rotating animation layers

| Frames | Layer |
|---|---|
| 0–345 | twinkling stars, **floating routine counters** at the edges, drifting sakura petals, glow particles, white/pastel-pink light, pearl sheen |
| 6–58 | **hologram woman** builds up from her feet beside the product |
| 62–130 | sakura burst |
| 150–186 | glass badges with a **water bottle, walking shoe and lotus** (self-care), each with a light circling it; **digital light ring** around the pack |
| 186–290 | **hologram butterflies** |
| 200–300 | **3D Korean-style woman** in modest sportswear doing light stretches: arms up, side bend left and right, arms out, rest |
| 296–345 | sakura burst, butterflies up the sides, **light ring around the product** |

There are no heart (love) animations. The **routine counters** are small glass
chips with digital-display numbers that roll up like a scale or fitness-tracker
readout: LANGKAH 0 → 8,000, GELAS AIR 0/8 → 8/8, RUTIN PAGI 06:30 → 07:00 and
MINIT REGANGAN 0 → 10. They show lifestyle numbers only. Body weight and scale
readings are deliberately left out, because TikTok treats them as weight-loss
claims on diet products (`FloatingCounters` in `src/components/Atmosphere.tsx`).

The woman (`src/components/KoreanWoman.tsx`) wears a loose long-sleeved
sweatshirt, long joggers and sneakers, with natural proportions. Only her
pose changes; her body shape and size never change. She fades in and out
rather than scaling.

## Run it

You need Node 18+, Python 3 with `numpy`, and `ffmpeg`.

```bash
cd projects/scc-korean-futuristic
npm install
npm run prep      # footage -> public/footage.mp4, synthesized audio -> public/audio/
npm run studio    # live preview in the browser
npm run render    # -> out/SCC_Korean_Futuristic.mp4
```

The first render downloads Remotion's Chrome Headless Shell automatically.
To use one you already have instead, set `REMOTION_BROWSER=/path/to/chrome-headless-shell`.
For a single frame, run `npm run still -- out/frame.png --frame=200`. To see
all of the woman's poses on one sheet, run `npx remotion still WomanTest out/woman.png`.

## Folder layout

```
input/original.mp4             your untouched upload
scripts/prep_footage.sh        whole clip -> 11.5 s @ 30 fps H.264, light denoise/brighten/sharpen
scripts/make_audio.py          K-beauty electro-pop bed (120 BPM, IV-V-iii-vi, bouncy off-beat stabs)
                               + KLIK / TIK-TIK / TING / WHOOSH / SPARKLE
src/timeline.ts                every frame number: lines, layers, SFX cues, volumes
src/SccKorean.tsx              the composition: footage, layers, six lines, audio
src/components/TextStyles.tsx  the six text styles (hologram, bubble, zoom, digital, neon, slide)
src/components/KoreanWoman.tsx 3D-style woman: solid + hologram variants, stretch routine
src/components/Atmosphere.tsx  light/grading, pearl sheen, sakura, stars, routine counters, particles, light rings
src/components/Butterfly.tsx   flapping hologram butterflies on smooth paths
src/components/CareIcons.tsx   water bottle, sneaker, lotus, glowing icon badges
src/components/GlassPanel.tsx  glassmorphism panel (open / slide right / slide left / scan)
src/components/DecodeText.tsx  digital decode typing
src/dev/WomanTest.tsx          pose check sheet (development only)
```

## Colour grade

The footage gets a light denoise and sharpen and a little brightness; the hue
is untouched, so SCC keeps its colours and hands stay natural. On top of that
sit a white key light from above, pastel pink and lavender from the lower
corners, and a slow pearl-white reflection that moves across the edges only.
The centre of the frame, where the product is, is kept clean.

## Safety

- There are no weight-loss, fat-burning or body-change claims, no before/after,
  and no product-efficacy visuals. The woman shows a general healthy routine
  (stretching, water, walking).
- The only product facts on screen are the name and the ingredients printed on
  the pack.
- The original pack says "DIET SUPPORT" and "Supports Weight Management". It is
  left untouched. **Check that SCC is allowed in your TikTok Shop category
  before posting.**
- All audio is synthesized by `scripts/make_audio.py`, with no samples, so it is
  free to use commercially.
- Remotion is free for individuals and companies of up to 3 people. Larger
  companies need a company licence (see remotion.dev/license).
