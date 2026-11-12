# FRANKLY PDRN — UGC selfie re-edit with a hook (15.6s, 9:16)

Finished video: [`output/frankly-pdrn-ugc-hook.mp4`](output/frankly-pdrn-ugc-hook.mp4)

| Time | What happens |
|---|---|
| 0.0–1.3 | **Hook:** a teaser of the glowiest close-up (source 13.0–14.3s, with its own audio so the lip-sync holds), a white flash, a punch zoom, sparkles, "RAHSIA KULIT GLOWING AKU 👀" and "Serum ada BOLA OREN dalam botol! 🧡" |
| 1.3–3.5 | A flash cut back to the start: "FRANKLY PDRN Bounce Ball Serum 🧡" + "Salmon DNA PDRN" |
| 3.6–13.3 | Captions: Sapu & tepuk perlahan ✨ · Rasa lembap & segar 💧 · Bouncy & comel! 🧡 · Kulit nampak glowing ✨ |
| 13.3–15.6 | CTA: "Nak cuba? 👀" + a pulsing "Tekan BAKUL KUNING 🛒" button |

The footage gets a gentle warm colour grade and a pop sound on every caption. The
original song is kept and stays in sync with the video. Captions sit over the
curtain at the top so they never cover the face.

Re-render (needs ../frankly-pdrn-bounce-ball-serum/render for fonts and effects):

```
python3 edit.py --video /path/to/selfie.mp4
```

## Version 2 — voice-over + animated karaoke subtitles (`vo_edit.py`)

Current file: [`output/frankly-pdrn-ugc-karaoke.mp4`](output/frankly-pdrn-ugc-karaoke.mp4).
It has word-by-word karaoke subtitles and keeps the original song. **It has no
voice yet**, because this environment's network policy blocks every TTS host
(`speech.platform.bing.com`, `translate.google.com`, `huggingface.co`). The
subtitles are timed from a syllable estimate.

To get the voice-over, allow `speech.platform.bing.com` in the environment's
network settings and run:

```
pip install edge-tts
python3 vo_edit.py --video /path/to/selfie.mp4                              # female voice (Yasmin)
python3 vo_edit.py --video /path/to/selfie.mp4 --voice ms-MY-OsmanNeural    # male voice
```

When the voice works, the subtitles follow the real timing of every word and the
song is ducked under the voice.

### Voice-over script (Bahasa Melayu, ~15 s)

| Time | Line |
|---|---|
| 0.1 | Nak tahu rahsia kulit glowing aku? |
| 2.0 | Ni dia, FRANKLY PDRN Bounce Ball Serum! |
| 4.5 | Dalam botol ada bola serum oren dengan salmon DNA PDRN. |
| 7.6 | Goncang dulu, sapu, lepas tu tepuk perlahan. |
| 10.1 | Kulit rasa lembap dan nampak glowing! |
| 12.6 | Nak cuba? Tekan bakul kuning sekarang! |

## Version 3 — sharp hook + Feature/Advantage/Benefit + CTA formula (`fab_edit.py`)

File: [`output/frankly-pdrn-ugc-fab-cta.mp4`](output/frankly-pdrn-ugc-fab-cta.mp4) (18.8 s)

| Time | Part | Visuals |
|---|---|---|
| 0.0–2.0 | **Hook (curiosity):** "KENAPA ADA **BOLA** DALAM SERUM NI?! 😳" → "Jawapan dia... 👇" | Punch-zoom on the bottle, RGB glitch, a red circle drawn around the orange ball, a hand-drawn arrow from the headline |
| 2.0–5.0 | **FEATURE 🧬** Bola Salmon PDRN 100,000 ppm* + ekstrak telur salmon | Card slides in, product polaroid, F-A-B tracker, footnote |
| 5.0–9.3 | **ADVANTAGE 🔥** Goncang, bola pecah jadi partikel mikro & sebati dengan esen | Polaroid flips from "Sebelum goncang" to "Lepas goncang" |
| 9.3–12.0 | **BENEFIT ✨** ✅ Kulit rasa lembap ✅ Nampak segar & glowing ✅ Mudah masuk rutin harian | Checklist ticks one by one |
| 12.0–14.3 | **Action** | "Nak cuba sendiri? 👀" + a pulsing yellow "TEKAN BAKUL KUNING 🛒" button + a bouncing 👇 |
| 14.3–18.8 | **CTA formula end card** | 🚨 JANGAN TERLEPAS! + product hero + 4 rows: ACTION · BENEFIT (untuk apa klik) · REASON (kenapa sekarang) · KALAU TAK (kesan kalau tak buat) |

Throughout: a progress bar along the top, zoom pulses timed to the song's beat,
a glitch on each section change, a warm grade with a vignette, and sound effects.
The original song plays unbroken, so the lip-sync holds. The end card reuses the
song's opening.
