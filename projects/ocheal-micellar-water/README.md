# O'CHEAL Hyalurose Micellar Water 300ML — TikTok affiliate edit

This folder holds a script pipeline that turns the original 96 s UGC clip into a
29.7 s, 1080×1920, 30 fps TikTok ad with Bahasa Melayu motion graphics. The
original footage is the only video source. Nothing is AI-generated: no hands,
bottle, label or demo is invented. All on-screen text is in Bahasa Melayu.

Output: `output/ocheal_micellar_tiktok.mp4` (H.264 High, AAC 192k, −14 LUFS).

## How to run

```bash
pip install opencv-python-headless numpy pillow   # ffmpeg with libvidstab + libx264 required
cp /path/to/original.mp4 src/original.mp4
python3 build_base.py   # cut, stabilise, speed-ramp, colour grade  -> build/base.mp4
python3 track.py        # track the pink cap in product shots       -> build/track.json
python3 render.py       # graphics + music/SFX + encode             -> output/
python3 render.py --stills   # preview frames only, in build/stills/
```

## Edit (real footage → story beat)

| Out time | Source | Footage | On screen |
|---|---|---|---|
| 0.0–1.9 | 53.8–55.7 | cotton pad on cheek | **MASIH TIDUR DENGAN SISA MAKEUP? 😳** (kinetic, sparkle burst) |
| 1.9–4.9 | 17.6–20.6 | two bottles to camera | **JOM KENAL MICELLAR WATER INI! 🌸** → card **O’CHEAL MICELLAR WATER / 300ML \| PENCUCI SOLEKAN**, leader line tracked to the cap, falling petals |
| 4.9–6.5 | 21.55–23.1 | bottle lifted and turned | **✨ BANTU TANGGALKAN SOLEKAN / Membersihkan sisa makeup & kotoran**, makeup particles dissolve into droplets |
| 6.5–8.2 | 23.1–24.15 (0.6× slow-mo) | front label held still | **🌹 HYALURONIC ACID + ROSE / Membantu mengekalkan kelembapan kulit**, rose orb, rising bubbles |
| 8.2–10.6 | 40.0–42.4 | bottle close-up with pad on pump | **💗 RASA SEGAR SELEPAS MEMBERSIH / Rutin pembersihan wajah yang mudah**, ripples at the cap |
| 10.6–13.2 | 44.6–48.4 (1.45×) | pad pressed on the pump | **CARA PENGGUNAAN 🌸**, step **1. Basahkan kapas** highlighted |
| 13.2–15.3 | 76.8–78.9 | pads held on both eyes | step **2. Tekap seketika** (hold-timer ring) |
| 15.3–17.7 | 57.4–60.4 (1.25×) | pad wiped across forehead | step **3. Lap perlahan-lahan** |
| 17.7–24.0 | 63.4–73.5 (1.3–1.5×) | real cheek and nose wipes | one benefit at a time: MEMBANTU MENANGGALKAN SOLEKAN · MEMBERSIHKAN SISA KOTORAN · DENGAN HYALURONIC ACID · MEMBANTU KEKALKAN KELEMBAPAN |
| 24.0–26.9 | 92.0–94.9 | clean face, smile | **RASA SEGAR & SELESA** → **MAKEUP DAH TANGGAL, BARU LEGA! 💗** |
| 26.9–29.7 | 22.6–24.0 (0.5× slow-mo) | product hero close-up | **O’CHEAL MICELLAR WATER 300ML 🌸** + pulsing CTA **NAK CUBA? / CHECK BEG KUNING 🛍️** |

The edit drops the unboxing (0–15 s), the moments where the bottle leaves the
frame, the head-out-of-frame bits (27 s, 35 s) and repeated wipes.

## What each step does

- **Stabilisation:** two-pass `vidstab` on each segment, using optimal zoom so no black borders appear.
- **Colour grade:** in RGB, the cyan wall is pulled towards pearl, skin is warmed slightly, contrast is soft, and a highlight-only bloom is added.
- **Camera:** a Ken Burns zoom per segment, plus a 5 % punch-in that settles at every cut, with a soft pink light-leak flash. Product shots drift towards the tracked cap.
- **Tracking:** `track.py` uses a hue mask and nearest-blob association on the pink cap, seeded per shot, run forwards and backwards, then smoothed. Leader lines, ripples and particles hang off this track, and they hide when tracking confidence drops.
- **Graphics:** glass panels are sampled live from the frame underneath. The fonts are Playfair Display and Montserrat (OFL). Emoji use Noto Color Emoji. The rose element is cut from slide 4/9 of the product images.
- **Safe zones:** all text sits at y 250–900 (top info zone) or inside x 60–880 for the CTA, which keeps it clear of TikTok's right-hand buttons and the bottom caption.
- **Sound:** an original 116 BPM bed is synthesised in `render.py` (pad, plucked arpeggio, soft kick/snap/hat, sub bass), so there are no licensing issues. SFX are synthesised too and fire from the graphics timeline: POP on words, TING on benefits, CLICK on cards, WHOOSH/SWISH on cuts, SPARKLE on rose and hydration moments, and a CHIME on the CTA. The original voice is removed.

## Claims policy

- Benefit copy comes from the brand's own images (slides 2, 3, 4, 7, 9). It is softened to "membantu…" and makes no guarantees.
- Not used: "Sesuai untuk kulit berjerawat" (acne), the before/after comparison panels, and "cleanses in one swipe".
- **BUY 1 TAKE 1 is left out on purpose.** Slide 1 shows it, but it can't be confirmed as currently active. To add it, append an `InfoCard` in the hero block of `build_elements()` once it's confirmed.

## Tweaking

- Change cuts or speeds in `edl.py`, then rerun all three steps. Segments are cached by their parameters.
- Change copy, timing or placement in `build_elements()` in `render.py`.
- To use a TikTok Commercial Music Library track instead of the synth bed, mute the bed in TikTok's editor or replace `build/audio.wav` and remux.
