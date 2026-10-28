# SCC: body-care hologram (Remotion)

The finished video is **[`out/SCC_BodyCare_Hologram.mp4`](out/SCC_BodyCare_Hologram.mp4)**.

| Setting | Value |
|---|---|
| Duration | 11.5 s (345 frames) |
| Size and frame rate | 1080 × 1920, 9:16, 30 fps |
| Video | H.264 at about 18 Mbps |
| Audio | AAC, 48 kHz, 320 kbps |
| Language | Bahasa Melayu text, no voice-over |

The whole original SCC clip (`input/original.mp4`) is the base layer. It gets
only a light denoise, brighten and sharpen. The pack, its printed text and
colours, and the hands are not altered, and nothing is drawn over the label.

## Timeline

Times are in frames at 30 fps. The music is 120 BPM, so one beat is 15 frames.

| Time | Text | Animation | Sound |
|---|---|---|---|
| 0–2 s | SELF-CARE BUKAN SEKADAR SKINCARE! 💗 | glass panel switches on; twinkling stars; the hologram woman builds up slowly from her feet beside the product, behind a bright scan line; a pink light line draws a heart around her | KLIK → TIK-TIK → TING |
| 2–4 s | JANGAN LUPA PENJAGAAN BADAN ✨ | panel slides in from the right below the product; inside it the woman slowly turns 0 → 15°, while a pink light ring travels up and down around her; hearts and stars float beside the panel | WHOOSH → KLIK → TING |
| 4–7 s | KENALI SCC 💗 + "White Kidney Bean + L-Carnitine Candy" | title panel is revealed by a scan line; two ingredient panels (WHITE KIDNEY BEAN, L-CARNITINE) scan in; hologram butterflies appear; a light ring draws itself and a lotus (self-care symbol) forms inside it; the product stays clear in the middle | KLIK → TIK-TIK → KLIK, KLIK → SPARKLE |
| 7–9 s | JADIKAN SELF-CARE SATU RUTIN 💕 | the woman walks slowly across the empty top-left of the frame (arms and hem sway); a water bottle, a walking shoe and a heart pop up in glass badges, each with a pink light circling it; small stars twinkle | WHOOSH → KLIK → TING |
| 9–11.5 s | SCC – KENALI PRODUK INI ✨ | main panel appears; the woman shrinks away into sparkles; butterflies drift slowly up the sides; a light ring draws itself around the product, which becomes the focus | KLIK → TIK-TIK → TING, sparkle |

## Run it

You need Node 18+, Python 3 with `numpy`, and `ffmpeg`.

```bash
cd projects/scc-body-care-hologram
npm install
npm run prep      # footage -> public/footage.mp4, synthesized audio -> public/audio/
npm run studio    # live preview in the browser
npm run render    # -> out/SCC_BodyCare_Hologram.mp4
```

The first render downloads Remotion's Chrome Headless Shell automatically.
To use one you already have instead, set `REMOTION_BROWSER=/path/to/chrome-headless-shell`.
For a single frame, run `npm run still -- out/frame.png --frame=200`.

## Folder layout

```
input/original.mp4             your untouched upload
scripts/prep_footage.sh        whole clip -> 11.5 s @ 30 fps H.264, light denoise/brighten/sharpen
scripts/make_audio.py          synthesized feminine electro-pop (120 BPM) + KLIK / TIK-TIK / TING / WHOOSH / SPARKLE
src/timeline.ts                every frame number: scenes, panel cues, SFX cues, volumes
src/SccVideo.tsx               the composition: footage, scenes, woman track, butterflies, audio
src/components/Woman.tsx       hologram woman (hijab, long sleeves, loose full-length abaya): build-up, 3D turn,
                               walk cycle, travelling light ring, projector base
src/components/Butterfly.tsx   flapping hologram butterflies on smooth flight paths
src/components/CareIcons.tsx   water bottle, walking shoe, kidney bean, molecule, lotus, glowing icon badge
src/components/Atmosphere.tsx  white + pastel-purple light, stars, edge hearts, glow particles, light rings
src/components/GlassPanel.tsx  glassmorphism panel (~35% glass), neon border, HUD corners, scan lines
src/components/DecodeText.tsx  digital typing reveal + beat pulse
src/components/Icons.tsx       💗✨ and other icons as inline SVG
```

## Safety choices

- The woman is a modest, fully clothed hologram. She keeps exactly the same
  shape and size from the moment she appears until she exits. The shrink at
  the end scales the whole figure down as she vanishes; her proportions never
  change. There is no before/after, no slimming of the waist or thighs, no
  fat-burning effect, and no weight-loss or guaranteed-result claims.
- The only product facts on screen are the name and the ingredients printed on
  the pack (White Kidney Bean, L-Carnitine).
- The pack itself says "DIET SUPPORT" and "Supports Weight Management". That
  is the original packaging, so it is left untouched. **Check that SCC is
  allowed in the TikTok Shop category you list it under before posting.**
- All audio is synthesized by `scripts/make_audio.py`, with no samples, so it is
  free to use commercially.
- Remotion is free for individuals and companies of up to 3 people. Larger
  companies need a company licence (see remotion.dev/license).
