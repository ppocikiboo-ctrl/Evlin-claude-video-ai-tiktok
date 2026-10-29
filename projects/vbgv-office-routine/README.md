# VBGV: office routine affiliate video (Remotion)

The latest video is **[`out/VBGV_Office_Routine_v2.mp4`](out/VBGV_Office_Routine_v2.mp4)** (v2, more persuasive).
The first version, [`out/VBGV_Office_Routine.mp4`](out/VBGV_Office_Routine.mp4), is kept for comparison.

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

## Edit (v2)

| Edit time | From the original | On screen | Sound |
|---|---|---|---|
| 0.0–1.8 s | desk work, **3× timelapse** | **Hook** from frame 0: "KERJA **DUDUK LAMA** SEHARIAN? 💻", zoom punch, flash, shockwave, a "⏩ 3X" badge | **BOOM** on frame 0, KLIK, TING |
| 1.8–3.0 s | (timelapse continues) | **Pain point 1:** "TAK SEMPAT JOGING? ⏰"; a runner icon gets a red "no" stamp while a clock spins far too fast | KLIK, fast **tick-tock**, TING |
| 3.0–7.0 s | takes out the pack | "KENALI VBGV ✨" + gold "VBGV L-CARNITINE CANDY" pill, sparkles | WHOOSH, POP, sparkle, KLIK, TIK-TIK, TING |
| 7.0–11.0 s | opens the pack | **Pain point 2:** "SELALU TERGODA NAK SNEK? 🍩"; a donut, bubble tea, fries and a cookie pop in around her, wobble, then drift away | WHOOSH, KLIK, TIK-TIK, TING, **BOING** ×4 |
| 11.0–16.0 s | tablet, then drinks water | **Routine checklist** "RUTIN HARIAN SAYA": Jalan kaki 10 minit ✓, Makan seimbang ✓, VBGV selepas sarapan* ✓, Minum air cukup ✓ (the last ticks as she drinks), plus "*Ikut arahan pada label produk" | KLIK, **rising dings** C-E-G-C (one per tick), bloop |
| 16.0–18.5 s | smiling close-up | **CTA:** "CEK HARGA PROMO 🛍️ / TEKAN BEG KUNING", a swinging **PROMO** price tag, a **finger taps** the yellow product-bag area with ripples and sparkles | KLIK, TIK-TIK, TING, **TAP**, **KA-CHING** |

Every cut lands on a beat with a zoom punch and a whoosh. Text sits above her
head or below her face, never over the face or the pack.

### What v2 deliberately does not say

The brief asked for "rasa kenyang sentiasa" (always feel full) and "craving
tiada kawalan" (VBGV controlling cravings). These are appetite / fullness
efficacy claims. TikTok does not allow them for weight-management products,
and Malaysian rules for food and supplement advertising restrict them, so they
are not in the video. Instead:

- **"Tak sempat joging?"** is a pain point only. It is followed by a general
  daily routine (walking, balanced meals, water), so the product is not shown
  as a replacement for exercise.
- **"Selalu tergoda nak snek?"** is a relatable question with no promise. The
  snacks drift away on their own; nothing says VBGV controls cravings.
- **"PROMO" / "Cek harga promo"**: only keep this if a promo is actually
  running. Otherwise change the label in `src/components/PersuadeLayers.tsx`
  and the line in `src/VbgvOffice.tsx`.

## Run it

You need Node 18+, Python 3 with `numpy`, and `ffmpeg`.

```bash
cd projects/vbgv-office-routine
npm install
python3 scripts/prep_footage.py   # cut + grade the original -> public/footage.mp4 (original audio dropped)
python3 scripts/make_audio.py     # music + SFX -> public/audio/
npm run studio                    # live preview
npm run render                    # -> out/VBGV_Office_Routine_v2.mp4
```

The first render downloads Remotion's Chrome Headless Shell automatically.
To use one you already have instead, set `REMOTION_BROWSER=/path/to/chrome-headless-shell`.

## Folder layout

```
input/original.mp4              your untouched upload (35 s)
input/reference-infographic.jpg the VBGV infographic (product name / usage reference)
scripts/prep_footage.py         shot list (source in/out -> edit length), speed changes, colour grade
scripts/make_audio.py           music (120 BPM, no vocals) + BOOM / KLIK / TIK-TIK / TING / WHOOSH / SPARKLE / POP / BLOOP
                                + v2: tick-tock, check1-4 (rising dings), boing, tap, ka-ching
src/timeline.ts                 shot boundaries, text cue frames, SFX cues, volumes
src/VbgvOffice.tsx              the composition: footage, hook, panels, badges, CTA, audio
src/components/PersuadeLayers.tsx  v2: no-time-to-jog runner + clock, snack temptation, routine checklist, CTA tap + price tag
src/components/GlassPanel.tsx   see-through glass panel in VBGV purple (open / slide / scan)
src/components/DecodeText.tsx   digital decode typing
src/components/VbgvIcons.tsx    💻 🛍️ ⏩ 🏃‍♀️ ⏰ 🍩 🧋 🍟 🍪 👆 🏷️ as SVG
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
