# Sample Score tips — edited TikTok video

Final: `sample-score-tips-edited.mp4` (1080x1920, 30 fps, ~65 s)

## Edits
- **Voice:** de-clipped, de-noised, EQ (less mud, more clarity/presence), de-essed,
  compressed, loudness-normalised to -14 LUFS (TikTok level).
- **Pacing:** dead air cut (~6 s removed) at 0–0.85 s, 21.6–23.15 s, 25.0–27.45 s, 31.15–31.95 s.
- **Colour:** highlights tamed on the over-bright tablet screen, more contrast/saturation, sharpened.
- **Visuals:** hook title (0–3.4 s), STEP 1–4 labels, 1/4–4/4 metric callouts with punch-in zoom,
  animated word captions with keyword highlight, end card with follow CTA.

## Scripts
- `scripts/transcribe.py` — Whisper (sherpa-onnx) + VAD transcription
- `scripts/render.py` — overlays/captions/zoom renderer (`python3 render.py cut.mov out.mp4`)
- `scripts/transcript-raw.json` — raw transcript (captions in `render.py` are corrected by hand)
