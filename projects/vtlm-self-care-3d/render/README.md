# VTLM ad — motion-graphics render

This folder holds a code-rendered 30-second version of the ad from
[`../PROMPT_PACK.md`](../PROMPT_PACK.md): 1080×1920, 30 fps, with the soundtrack included.
It follows the pack's timeline, Malay typography, transitions and sound cues,
and uses the **real VTLM pouch** cut from the reference video. The packaging is never redrawn.

It is a 2.5D motion-graphics cut, **not** the full 3D character animation.
The girl, the food characters and the 3D scenes still come from the AI video
tools (pack sections 2–5). Use this render in either of two ways:

- **As a postable ad on its own.** The hook, mind map, product reveal and
  call to action all work without the character.
- **As the timing guide and graphics layer for the AI-generated cut.** Every
  text and sound cue is already placed on the music grid.

## Files

| File | What it does |
|---|---|
| `prep_pouch.py` | Cuts the pouch out of a reference-video frame (rembg), straightens it and removes the thumb, producing `assets/vtlm_pouch.png` |
| `vtlm_render.py` | Renders every frame (PIL + numpy, in parallel) and encodes H.264 with ffmpeg |
| `vtlm_audio.py` | Synthesizes an original K-pop-style instrumental (~122 BPM) and all the SFX, writing `music.wav`, `sfx.wav` and `mix.wav` |
| `fonts/` | Baloo 2, Poppins and Playfair Display (SIL Open Font License) |

The emoji come from Noto Color Emoji (`/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf`;
set `EMOJI_FONT` to use another path).

## Build

```bash
pip install numpy pillow scipy opencv-python-headless rembg   # rembg only for prep_pouch.py
python3 vtlm_audio.py out/
python3 vtlm_render.py out/VTLM_self_care_ad.mp4 --audio out/mix.wav
# preview single frames:
python3 vtlm_render.py out/preview.png --frames 100,400,620,890
```

A full render takes about 5–10 minutes on 4 cores.

## Timeline (bars locked to the music)

| Time | Scene |
|---|---|
| 0.0–4.5 | Midnight bedroom, 12:00 AM clock, moon. Food characters pop in on the beat, "SELALU / LAPAR / TENGAH / MALAM? 🌙" word by word, BOOM and crash zoom at 3.2 |
| 4.5–9.1 | Whip transition, the pink heart, touch at 5.17, the portal opens into the self-care universe, "MASA UNTUK JAGA DIRI! 💗" scans in at 7.14 |
| 9.1–17.0 | Glass mind map: "RUTIN JAGA DIRI ✨", three glass bubbles joined by light trails, rack focus on 🌸 JAGA BADAN (11.09), 💖 JAGA DIRI (13.06), ✨ SAYANG DIRI (15.03) |
| 17.0–22.9 | Silk ribbons part and the real pouch appears on a floating glass pedestal (18.4), with a light sweep, "VTLM 💜" (18.97) and "RUTIN PENJAGAAN DIRI ✨" (20.94) |
| 22.9–26.9 | Pastel boutique, the pouch on a display stand, yellow bag with sparkles, "JAGA BADAN 🌸" / "JAGA DIRI 💖" / "KERANA DIRI ANDA BERHARGA ✨" |
| 26.9–30.0 | End card: "KENALI VTLM DI BEG KUNING 🛍️", a pulsing gold arrow pointing toward the TikTok yellow basket |

All text and the product stay inside the TikTok safe zone. Only the arrow
reaches into the bottom-left caption area, where the basket appears. Only the
front of the pouch is ever shown, so the back label stays out of the frame.
