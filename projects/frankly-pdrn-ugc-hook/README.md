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
