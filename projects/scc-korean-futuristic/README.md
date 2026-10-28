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

## Text: six lines, one at a time, each in its own solid style

None of the text styles use see-through glass. Each line enters differently.

| Frames | Line | Style | Sound | Placement |
|---|---|---|---|---|
| 2–56 | SELF-CARE BUKAN SEKADAR SKINCARE! ✦ | **sticker**: white sticker pops in with a wiggle, letters bounce in one by one | KLIK + pop, BOING ×2, TING | top left |
| 64–118 | JANGAN LUPA PENJAGAAN BADAN ✨ | **ribbon banner**: pink ribbon with folded tails unfurls, text wipes in | SWISH, KLIK, TIK-TIK, TING | bottom, below the big pack |
| 124–170 | KENALI SCC ✨ | **3D extruded zoom**: chunky 3D letters flip up and spring in, land with coloured dots | WHOOSH, KLIK, TIK-TIK, THUMP, TING | top |
| 174–228 | WHITE KIDNEY BEAN + L-CARNITINE | **split-flap board**: airport-style tiles clatter through letters and settle | WHOOSH, KLIK, FLAP clatter, TING | top |
| 236–284 | JADIKAN SELF-CARE SATU RUTIN 🌸 | **neon sign** on a solid dark plate: words flicker on, stars twinkle | WHOOSH, KLIK, TIK-TIK, TING | top |
| 296–345 | KENALI PRODUK INI ✨ | **3D button**: pops in, words jump up, the button presses down like a stamp, confetti bursts, shine sweeps | WHOOSH, KLIK, TIK-TIK, THUMP + CONFETTI, CHIME | top, stays to the end |

All cues live in `src/timeline.ts`.

## Rotating animation layers

| Frames | Layer | Sound |
|---|---|---|
| 0–345 | twinkling stars, **floating routine counters** at the edges, drifting sakura, glow particles, white/pastel-pink light, pearl sheen | sparkle |
| 6–58 | **hologram woman** builds up from her feet beside the product | |
| 62–130 | sakura burst | sparkle |
| 146–184 | **food plate**: a generous portion; a fork takes three bites and food is left on the plate | pop, BITE ×3 |
| 190–300 | **3D Korean-style woman** in modest sportswear: arms up, side bends, then light presses with **colourful dumbbells**; glowing **light-drop sweat** comes off her; warm **light lines circle her body** | pop, CLINK per rep, swish, PLINK |
| 205–290 | solid badges: **3 L water bottle** filling up (0.0 → 3.0 LITER), **walking shoe** (JALAN), **lotus** (SELF-CARE) | BLOOP, pop |
| 296–345 | sakura burst, butterflies up the sides, **light ring around the product** | sparkle |

The **routine counters** are solid pastel chips with digital-display numbers
that roll up: LANGKAH 0 → 8,000, AIR 0.0 → 3.0 L, RUTIN PAGI 06:30 → 07:00 and
MINIT REGANGAN 0 → 10. They show lifestyle numbers only. There are no body-weight
or scale readings, because TikTok treats them as weight-loss claims on diet
products. There are no heart (love) animations.

The woman (`src/components/KoreanWoman.tsx`) wears a loose long-sleeved
sweatshirt, long joggers and sneakers, with natural proportions. Only her
pose changes; her body shape and size never change, and she fades in and out
rather than scaling. The light lines around her body show general
"using energy" while she moves. They have no fat-burning label or claim.

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
                               + KLIK / TIK-TIK / TING / WHOOSH / SPARKLE and playful SFX:
                               pop, boing, swish, flap, thump, chime, clink, plink, bite, bloop, confetti
src/timeline.ts                every frame number: lines, layers, SFX cues, volumes; SHOW_PLATE switch
src/SccKorean.tsx              the composition: footage, layers, six lines, audio
src/components/TextStyles.tsx  the six solid text styles (sticker, ribbon, 3D zoom, split-flap, neon, button)
src/components/KoreanWoman.tsx 3D-style woman: solid + hologram variants, stretches, dumbbell presses,
                               light-drop sweat, energy light lines
src/components/Atmosphere.tsx  light/grading, pearl sheen, sakura, stars, routine counters, particles, light rings
src/components/Butterfly.tsx   flapping hologram butterflies on smooth paths
src/components/FoodPlate.tsx   plate with a big portion, fork bites, leftovers
src/components/CareIcons.tsx   3 L water bottle (fills up), sneaker, lotus, solid icon badges
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
  (stretching, light dumbbells, 3 L of water, walking).
- **The food plate is the riskiest element.** Food left over on a plate can be
  read as "eating less" (appetite control), which TikTok does not allow diet
  products to imply. It is kept away from the product name and tablets and has
  no text. If review objects, set `SHOW_PLATE = false` in `src/timeline.ts` and
  re-render; this removes the plate and its sounds.
- The only product facts on screen are the name and the ingredients printed on
  the pack.
- The original pack says "DIET SUPPORT" and "Supports Weight Management". It is
  left untouched. **Check that SCC is allowed in your TikTok Shop category
  before posting.**
- All audio is synthesized by `scripts/make_audio.py`, with no samples, so it is
  free to use commercially.
- Remotion is free for individuals and companies of up to 3 people. Larger
  companies need a company licence (see remotion.dev/license).
