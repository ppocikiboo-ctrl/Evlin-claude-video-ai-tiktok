# O'CHEAL Micellar Water — talking-head ad (v5, creator's own voice)

This edit keeps the creator's real voice as the main track. To build it, run
`build_base.py`, then `render.py`. Graphic building blocks are loaded from the
v1, v2 and v3 folders, so keep them alongside this one.

Output: `output/ocheal_micellar_tiktok_v5.mp4`. It is 25.2 s, 1080×1920, 30 fps, about −14 LUFS.

## Editing

- **Dead air removed:** three pauses are cut (7.2–8.15 s, 19.2–19.85 s, 20.82–21.63 s of the source). Speech is never cut mid-word, and each join has a 12 ms fade so it doesn't click.
- **Pace:** everything plays 1.07× faster with the pitch kept (`atempo`), for a brisker, more confident delivery.
- **Jump cuts:** every cut becomes a deliberate punch-in. Zoom alternates between parts, with a 6 % punch on the cut and a white flash.
- **Product tail:** after she stops talking, the last frame is held for 2.6 s with a slow push-in and the yellow-bag CTA, with music only.

## Voice processing (her own voice, not replaced or cloned)

`highpass 90 Hz → afftdn denoise → −3 dB @ 250 Hz (mud) → +4 dB @ 3.2 kHz (presence/clarity) → +2.5 dB @ 9.5 kHz (air) → de-ess → 4:1 compressor + 7 dB make-up → limiter`

- Raw cut: −21.6 LUFS, LRA 8.0.
- Processed: −18.9 LUFS, LRA 5.0. It is louder and steadier, with clearer consonants.
- Final mix: the music (A–F#m–D–E, 118 BPM) is side-chain ducked under the voice, then the whole mix is normalised to −14 LUFS.

## Graphics

| Out | When (source) | On screen |
|---|---|---|
| 0–2.6 s | opening | **STOP SCROLL! 🛑** tape + *nak makeup tanggal tanpa pedih? 😍* |
| bottles appear (6.8 s) | lower-third | *O’CHEAL Micellar Water — 300ML · Hyaluronic Acid + Rose 🌹* |
| handling the bottle (10.6 s) | checklist | **KENAPA SUKA? 💗** ✅ X PEDIH ✅ X BERMINYAK ✅ X RASA KERING |
| pad on the pump (15.6 s) / first wipe (17.45 s) | STEP chips | **STEP 1 BASAHKAN KAPAS**, **STEP 2 LAP LEMBUT-LEMBUT** |
| talking (19.9 s) | payoff | *kulit terasa lembut & segar 🤍*, light sweep, sparkles |
| bottles held up (25.15 s) + tail | CTA | **TEKAN BEG KUNING 🛍️**, *harga terkini dalam beg kuning*, 👇 + pulse rings |

## Not done

- **No word-for-word subtitles.** Automatic transcription needs the Whisper model from Hugging Face's CDN, and that host is not allowed in this environment. The overlays follow what is visible on screen, not her exact words.
