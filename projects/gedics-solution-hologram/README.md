# Gedics Solution: romantic hologram glass effect (Remotion)

The finished video is **[`out/Gedics_Hologram_10s.mp4`](out/Gedics_Hologram_10s.mp4)**.

| Setting | Value |
|---|---|
| Duration | 10.0 s (300 frames) |
| Size and frame rate | 1080 × 1920, 9:16, 30 fps |
| Video | H.264 at about 18 Mbps |
| Audio | AAC, 48 kHz, 320 kbps |
| Language | Bahasa Melayu text, no voice-over |

The base layer is the original phone clip (`input/original.mp4`). It is only
trimmed, lightly denoised, brightened and sharpened. The pack, the logo, the
label text, the pack colour and the hand are never covered, recoloured or
replaced, and nothing is AI-generated.

## Timeline

Times are in frames at 30 fps. The music is 120 BPM, so one beat is 15 frames.

| Time | Text | Visuals | Sound (each line gets KLIK → TIK-TIK → TING) |
|---|---|---|---|
| 0–2 s | BAHAGIA ITU BILA SALING MENGHARGAI 💗 | gold sunlight, twinkling stars, floating hearts; the panel opens like a hologram switching on, with a neon flicker and HUD corners; a heart-shaped light line draws itself around a hologram of the couple in a polite side hug | sparkle, KLIK, TIK-TIK, TING |
| 2–4 s | KEJUTAN UNTUK ORANG RUMAH 🎁❤️ | panel slides in from the right; a gift box pops open with a star burst and two glowing hearts rise out of it; the couple hologram holds hands | WHOOSH, KLIK, TIK-TIK, TING, sparkle |
| 4–7 s | WARNA-WARNI KASIH SAYANG 🌈✨ | the panel is revealed by a digital scan line; a pastel rainbow draws itself behind the panel with light moving along it; hearts orbit the panel in 3D; the couple hologram sits side by side on a bench | KLIK, TIK-TIK, SPARKLE, TING |
| 7–10 s | KENALI GEDICS SOLUTION 💗 / KETAHUI LEBIH LANJUT 🛍️ | two glass panels frame the product (above and below it, clear of the label); slow push-in; the text pulses on the beat; ends on a clean product shot | WHOOSH, KLIK, TIK-TIK, TING (twice), closing shimmer |

A pastel rainbow light sweep marks each scene change. All text types in with
a digital "decode" effect: the characters just ahead of the cursor flash as
random glyphs.

## Run it

You need Node 18+, Python 3 with `numpy`, and `ffmpeg`.

```bash
cd projects/gedics-solution-hologram
npm install
npm run prep      # trims/cleans the footage -> public/footage.mp4, synthesizes audio -> public/audio/
npm run studio    # live preview + timeline in the browser
npm run render    # -> out/Gedics_Hologram_10s.mp4 (H.264, 18 Mbps, AAC 48 kHz)
```

The first render downloads Remotion's Chrome Headless Shell automatically.
To use one you already have instead, set `REMOTION_BROWSER=/path/to/chrome-headless-shell`.
For a single frame, run `npm run still -- out/frame.png --frame=150`.

## Folder layout

```
input/original.mp4              your untouched upload
scripts/prep_footage.sh         trim 0.45 s off the front, 10 s @ 30 fps H.264, denoise/brighten/sharpen
scripts/make_audio.py           synthesizes music + KLIK / TIK-TIK / TING / WHOOSH / SPARKLE
public/footage.mp4              prepared footage (generated)
public/audio/*.wav              soundtrack pieces (generated)
public/fonts/                   Inter Display (SIL OFL 1.1, licence included)
src/timeline.ts                 every frame number: scenes, panel cues, SFX cue list, volumes
src/GedicsVideo.tsx             the composition: footage, layers, scenes, audio placement
src/components/GlassPanel.tsx   glassmorphism panel: ~35% glass, neon pink border, HUD corners, scan lines,
                                three entrances (open / slide from right / digital scan)
src/components/DecodeText.tsx   digital typing reveal + beat pulse
src/components/Couple.tsx       modest hologram silhouettes: holding hands, sitting, side hug
src/components/Atmosphere.tsx   grading light (gold sun, pink glow), stars, hearts, particles,
                                rainbow arc, rainbow transition sweep
src/components/Icons.tsx        💗❤️🎁🌈✨🛍️ as inline SVG (renders the same on every machine)
```

To change wording or timing, edit `src/GedicsVideo.tsx` (text) and
`src/timeline.ts` (frames). The SFX follow the panel cues automatically.

## Colour grade

The footage gets a light denoise (`hqdn3d`), a little brightness and contrast,
and a mild sharpen. The hue is not touched, so the pack keeps its original pink.
The romantic look comes from light layers that sit mostly at the edges of the
frame: golden sunlight top-left, a soft pink glow from below, and pink
soft-light edges. The centre of the frame, where the product is, is left clean.

## Audio

The music and every sound effect are synthesized from scratch by
`scripts/make_audio.py`. There are no samples, so the audio is free to use
commercially. The music plays at 45% volume so every KLIK, TIK-TIK and TING
can be heard over it.

## Content and policy notes

- The couple appears only as modest, fully clothed hologram line art (the wife
  in a hijab and long dress): holding hands, sitting together, a side hug.
  Nothing is sexual or suggestive.
- The text makes no product claims, has no testimonials, no before/after and
  says nothing about intimacy or saving a marriage. The product is never shown
  as the cause of anything between the couple.
- The pack says "Solusi Wanita — Wanita Lebih Bertenaga". **Check that the
  product's TikTok Shop category allows promotion before posting.** If it is
  listed as a sexual-wellness or enhancement product, don't use this for sales.
- Remotion is free for individuals and companies of up to 3 people. Larger
  companies need a company licence (see remotion.dev/license).
