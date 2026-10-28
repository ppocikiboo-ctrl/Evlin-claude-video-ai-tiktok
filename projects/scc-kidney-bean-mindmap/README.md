# SCC White Kidney Bean + L-Carnitine Candy — mind-map TikTok ad

Final video: [`output/scc-mindmap-tiktok.mp4`](output/scc-mindmap-tiktok.mp4)
(1080×1920, 30 fps, 18 s, H.264 + AAC, no voice-over, all on-screen text in Bahasa Melayu).

| Time | Scene |
| --- | --- |
| 0–3.5 s | Hook: worried cartoon girl with burger, pizza, fries, cake and donut; "NAK MAKAN TAPI TAKUT **NAIK?** 😱" with comic POP and shake |
| 3.5–10 s | Original footage in a framed card; "JOM JAGA DIRI! 💜" grows into 3 bubbles (scale, happy girl, opening wardrobe) |
| 10–18 s | Product centred inside a rotating circular mind map (4 bubbles); "JAGA DIRI, YAKIN SETIAP HARI! 💜" + "KENALI PRODUK INI ✨" |

The product footage is used as-is (light brightness/contrast grade only); the pack is never redrawn or relabelled,
and animations stay around the card instead of over the pack. No before/after or result claims.

## Rebuild

```
./build.sh                    # full render -> output/scc-mindmap-tiktok.mp4
./build.sh preview 1.2,5,14   # PNG stills only
```

- `scene.html` — canvas renderer (`renderFrame(t)`), all characters/bubbles drawn in code
- `render.js` — Playwright frame capture piped into ffmpeg
- `audio.py` — synthesised 120 BPM K-pop style track + POP/TING/WHOOSH/BOING/sparkle SFX
- `timeline.json` — shared timing so visuals and sound effects stay in sync
