# VBGV: office routine affiliate video (Remotion)

The finished video is **[`out/VBGV_Office_Routine.mp4`](out/VBGV_Office_Routine.mp4)**.

| Setting | Value |
|---|---|
| Duration | 18.5 s (555 frames) |
| Size and frame rate | 1080 × 1920, 9:16, 30 fps |
| Video | H.264 at about 18 Mbps |
| Audio | AAC, 48 kHz |
| Language | Bahasa Melayu text, no voice-over |

The 35 s original recording is cut down to 18.5 s of the strongest moments.
**The original audio is removed** and replaced with an original upbeat
electro-pop track (120 BPM, no vocals) plus sound effects, all synthesized by
`scripts/make_audio.py`, so the audio is free to use commercially. Every shot is
from the original recording; nothing is AI-generated. The VBGV pack is shown as
it is.

## Edit

| Edit time | From the original | On screen | Sound |
|---|---|---|---|
| 0.0–3.0 s | desk work 2–11 s, **3× timelapse** | **Hook** from frame 0: "KERJA **DUDUK LAMA** SEHARIAN? 💻" (big white text, purple neon outline, gold highlight), zoom punch, flash, shockwave, a short shake, a "⏩ 3X" badge; then "INI RUTIN KECIL SAYA 💜" | **BOOM** on frame 0, KLIK, TING, TIK-TIK |
| 3.0–7.0 s | takes out the pack, 11.7–15.7 s | "KENALI VBGV ✨" + gold "VBGV L-CARNITINE CANDY" pill; sparkles around the pack | WHOOSH, POP, sparkle, KLIK, TIK-TIK, TING |
| 7.0–11.0 s | opens the pack, 17–25 s (2×) | "SENANG BAWA KE OFIS 👜" | WHOOSH, KLIK, TIK-TIK, TING |
| 11.0–14.0 s | holds up a tablet, 24.8–27.8 s | "1/2 BIJI SELEPAS SARAPAN PAGI 🌞" + "*Ikut arahan pada label produk" | WHOOSH, KLIK, TIK-TIK, TING |
| 14.0–16.0 s | drinks water, 28.4–30.4 s | "JANGAN LUPA MINUM AIR 💧" | WHOOSH, bloop, KLIK, TIK-TIK, TING |
| 16.0–18.5 s | smiling close-up, 33.1–35 s (slight slow-mo) | CTA: "NAK CUBA JUGA? 🛍️ TEKAN BEG KUNING" + an arrow bouncing toward the yellow product bag | WHOOSH, KLIK, TIK-TIK, TING, sparkle |

Every cut lands on a beat, with a quick zoom punch and a whoosh. The text sits
above her head or below her face, never over the face or the pack. The usage
line comes from the product's own infographic (1/2 biji selepas sarapan pagi)
and points viewers to the label.

## Run it

You need Node 18+, Python 3 with `numpy`, and `ffmpeg`.

```bash
cd projects/vbgv-office-routine
npm install
python3 scripts/prep_footage.py   # cut + grade the original -> public/footage.mp4 (original audio dropped)
python3 scripts/make_audio.py     # music + SFX -> public/audio/
npm run studio                    # live preview
npm run render                    # -> out/VBGV_Office_Routine.mp4
```

The first render downloads Remotion's Chrome Headless Shell automatically.
To use one you already have instead, set `REMOTION_BROWSER=/path/to/chrome-headless-shell`.

## Folder layout

```
input/original.mp4              your untouched upload (35 s)
input/reference-infographic.jpg the VBGV infographic (product name / usage reference)
scripts/prep_footage.py         shot list (source in/out -> edit length), speed changes, colour grade
scripts/make_audio.py           music (120 BPM, no vocals) + BOOM / KLIK / TIK-TIK / TING / WHOOSH / SPARKLE / POP / BLOOP
src/timeline.ts                 shot boundaries, text cue frames, SFX cues, volumes
src/VbgvOffice.tsx              the composition: footage, hook, panels, badges, CTA, audio
src/components/GlassPanel.tsx   see-through glass panel in VBGV purple (open / slide / scan)
src/components/DecodeText.tsx   digital decode typing
src/components/VbgvIcons.tsx    💻 👜 🛍️ 🌞 💧 ⏩ and the CTA arrow as SVG
src/components/Atmosphere.tsx   soft light, pearl sheen, stars, glow particles
```

To change a line of text, edit it in `src/VbgvOffice.tsx`; its timing is in
`src/timeline.ts`. To change which part of the original is used, edit `SHOTS`
in `scripts/prep_footage.py` and re-run it.

## Colour grade

The footage gets a light denoise, a little more brightness and warmth, gentle
contrast and saturation, and a mild sharpen, so the office looks less grey
while skin and the purple pack stay natural. Soft lavender and white light at
the edges is kept subtle.

## Safety

- There are no weight-loss, slimming, appetite or guaranteed-result claims, and
  no before/after.
- The infographic spells the ingredient "L-CARITINE". The video uses the
  standard "L-CARNITINE". **Check this against the physical pack before
  posting.**
- **Check that VBGV is allowed in your TikTok Shop category before posting.**
- Remotion is free for individuals and companies of up to 3 people. Larger
  companies need a company licence (see remotion.dev/license).
