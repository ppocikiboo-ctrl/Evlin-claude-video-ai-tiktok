# VBGV — "Baju lama vs baju baru OOTD" edit

Final video: `vbgv-ootd-baju-lama-edit.mp4` (1080x1920, 30 fps, 36 s).

Layered copy (no direct slimming claims): hook "Baju lama terperap dalam almari…
atau nak beli baju baru untuk OOTD idaman?", then lines like "Almari penuh, tapi 'tiada baju'?"
and "Zip naik tanpa tahan nafas". Karaoke-style subtitles from the
voiceover, a "Cara ambil VBGV" checklist, yellow-basket arrows, sparkles, zoom
punches and synthesized whoosh/wip/wup/pop/ding SFX.

Rebuild:

```
ffmpeg -i source.mp4 -ac 1 -ar 44100 voice.wav
python3 edit/sfx.py voice.wav mix.wav
python3 edit/render.py source.mp4 mix.wav out.mp4
```

Edit text and timings in `edit/timeline.py`.
