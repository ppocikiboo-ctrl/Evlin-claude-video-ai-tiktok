# VBGV L-Carnitine Candy: 30 s TikTok affiliate ad

The finished video is **[`output/VBGV_TikTok_30s.mp4`](output/VBGV_TikTok_30s.mp4)**.
It is 1080×1920 (9:16), 30 fps, exactly 30.0 s long, H.264 with AAC audio at −12 LUFS.
All on-screen text is in Bahasa Melayu and there is no voice-over.

Every shot comes from the original phone clip (`input/original.mp4`). The
VBGV packaging, logo and hands are never altered or generated. The clip is
only 11.2 s long, so shots are slowed down with frame blending (no warping
of the pack lettering) and two shots play as a boomerang to fill 30 s.

## Timeline

| Time | Scene | On-screen text | Footage | Sound |
|---|---|---|---|---|
| 0–3 s | Hook | 😩 BOSAN PENAMPILAN / **TAK BERUBAH?** (gold) | pack swings in, punch zoom + shake, purple glow | bass impact, beat starts |
| 3–6 s | Problem | 🍟 **SUKA MAKAN** (lavender), TAPI / RISAU NAK **JAGA BADAN?** (gold) | front of pack | whoosh, sparkles |
| 6–9 s | Reveal | ✨ KENALI **VBGV** ✨ + pill "VBGV L-CARNITINE CANDY" | slow push-in, purple backlight, gold light sweep | shimmer + beat drop |
| 9–13 s | Highlights | 💜 RUTIN PENJAGAAN BADAN + 3 cards: ✨ L-CARNITINE 90%\* · 💜 MUDAH DIBAWA · 🌸 MUDAH DIJADIKAN RUTIN + footer | tablets poured from pack | 3 pops, one per card on the beat |
| 13–17 s | Lifestyle | UNTUK YANG SIBUK / SETIAP HARI ✨ + floating bubbles Kerja · Aktiviti harian · Rutin penjagaan diri | back of pack | upbeat groove, sparkles |
| 17–21 s | Info | glass panel: 💜 **1** PEK = **5** BIJI (gold pulse), Maklumat produk: L-Carnitine 90%\*, \*Sahkan kandungan melalui label rasmi. | tablets in palm (boomerang) | |
| 21–25 s | Self-care | JAGA BADAN, / JAGA **KEYAKINAN** 💜 + "Pemakanan seimbang dan gaya hidup aktif tetap penting." | front of pack, lavender light rays | snare roll + riser |
| 25–30 s | CTA | 💜 NAK KENAL **VBGV?** (pulsing) + button "TEKAN BEG KUNING / UNTUK INFO LANJUT 🛍️" + bouncing arrow | final close-up push-in on the pack | impact, energetic beat, shimmer tail |

There is a short punch-zoom and lavender flash at every cut. The music runs
at 120 BPM, so every cut and every card pop lands on a beat.

### Compliance choices

- The video makes no claims about weight loss, appetite suppression or side effects.
- The 90% figure always carries an asterisk and a "check the official label" footer.
- The infographic spells it "L-CARITINE". On screen the video uses the standard
  "L-CARNITINE", as the brief asked. **Before posting, check the spelling and
  the 90% figure against the physical label.**

## Run it yourself

You need Python 3.10+ with `numpy` and `pillow`, and `ffmpeg` (with libx264) on your PATH.

```bash
pip install numpy pillow
cd projects/vbgv-lcarnitine-candy
./render.sh                               # -> output/VBGV_TikTok_30s.mp4  (~7 min on 4 cores)
./render.sh path/to/other_clip.mp4        # different source footage
MUSIC=licensed_track.mp3 ./render.sh      # swap the music bed, keep the SFX
```

To preview single frames while you tweak something:

```bash
python3 src/build_base.py                 # once, builds build/base.mp4
python3 src/overlay.py --stills 1,10,27   # -> build/stills/*.png in seconds
```

## Project layout

| File | What it does |
|---|---|
| `src/config.py` | Canvas, palette, fonts, TikTok safe zones, **shot list** (source in/out → output duration) and the colour grade |
| `src/build_base.py` | ffmpeg cut, retime, boomerang and grade → `build/base.mp4` |
| `src/overlay.py` | Per-frame compositor: camera moves (zoom, shake, punch-ins), light effects, and all text/card animations per scene |
| `src/gfx.py` | Text rendering (gold gradient, glow, stroke, shadow, inline icons), glass panels, pills, light fields, particles, sparkles |
| `src/icons.py` | Emoji-style icons drawn as vectors, so no emoji font is needed |
| `src/audio.py` | Original 120 BPM synth-pop bed (kick, clap, hats, bass, pad, pluck arpeggio, sidechain, reverb) and SFX (impact, whoosh, pop, sparkle, shimmer, riser) |
| `render.sh` | Runs all steps, then muxes with loudness normalisation |
| `fonts/` | Inter Display (SIL OFL 1.1, licence included) |

### Colour grade

The grade lifts brightness slightly, adds a little contrast with lifted
blacks, puts lavender in the highlights and adds a light sharpen for the pack
lettering (`GRADE` in `config.py`). Saturation is only +4%, so the purple
packaging stays true to the original. A purple vignette and top/bottom shading
keep the text readable and the TikTok UI clear.

### Safe zones

All headline text sits between y = 200 and 560 px. Lower elements stay above
y = 1540 px and left of x = 930 px, which keeps them clear of the caption,
the product anchor (the yellow bag) and the right-hand action buttons.

### Audio licensing

Every sound is synthesized by `src/audio.py`. There are no samples or
third-party recordings, so the soundtrack is yours to use. If you'd rather use
a trending TikTok Commercial Music Library track, upload the video without
music and add the track in TikTok, or render with `MUSIC=...` using a track
you hold a licence for.
