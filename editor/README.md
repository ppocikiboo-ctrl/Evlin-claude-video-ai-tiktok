# Ageless Studio: TikTok editor for *Ageless by NYO3*

A browser-based video editor (HTML, CSS and JavaScript, no build step) that turns your
**original** product footage into a premium K-beauty style TikTok. Concept:
**"My Self-Care Era Before 30"**.

It never generates or replaces footage. Your clip is only colour-graded, then
captions, labels and sound are added on top.

## Run it

1. Use **Chrome or Edge** (version 113 or later) on desktop.
2. Open `editor/index.html`. Double-clicking the file works, because every script, font and
   library is bundled locally, so it also runs offline.
3. Click **Upload original MP4**, or drop the file onto the preview.

Your edit is saved in the browser automatically. Use **Save project** / **Open project**
to keep it as a JSON file. The video file itself is never uploaded anywhere: it stays on your
computer.

## Templates

Pick a template from the selector in the top bar. Each template keeps its own saved edit, so switching never loses work, and **Reset** restores only the current template.

| Template | Look | Structure |
|---|---|---|
| **Luxe Ivory: My Self-Care Era** (video 1) | soft ivory & champagne, Playfair serif, frosted cards, dreamy ~100 BPM piano | mood-led story |
| **Bold FAB + CTA: 2 biji sehari** (video 2) | ruby red, black & white editorial, bold Poppins, kinetic type, checklist cards, chapter bar, cut-zooms & flashes, ~118 BPM pop groove | Hook → Advantages → Emotion → Why → Features → Benefits → CTA |

## Template 1: what's in the edit

| Time | Element | Animation | Sound |
|---|---|---|---|
| 0.15–4 s | "Menuju usia 30-an… 🥹" | fade · rise · subtle zoom | shimmer + airy whoosh |
| 1.0–2.7 s | **DAY CARE ☀️** → red softgel, **NIGHT CARE 🌙** → black softgel | tracked dot → gold line → frosted card | delicate pop / glass chime |
| 4–8 s | "Saya mula serius jaga kecantikan dari **DALAM** ✨" (DALAM in champagne gold, light sweep) | slide up | gentle swoosh |
| 8–12 s | "Sebab saya nak / *aging gracefully* 🤍" | cinematic reveal | sparkle |
| 12–17 s | DAY CARE ☀️ · Morning Routine card | floating card | pop + rising shimmer |
| 17–22 s | NIGHT CARE 🌙 · Evening Routine card | floating card | glass chime |
| 22–26 s | "Astaxanthin • PQQ • Ergothioneine" / "Antioksidan untuk rutin penjagaan dalaman ✨" | staggered items with glints, frosted panel | 3 sparkle ticks, one per ingredient |
| 26–30.1 s | "*Growing older is natural.* / Taking care of myself is a **choice.** 💗" | slow cinematic fade, drift, fade-out | shimmer → piano resolution |

Music fades out over the final 2 s.

### About the softgel labels (please read)

The blister pack is only on screen at about **0.9–2.7 s** and **29.0–30.1 s**. Between 12 and
22 s the footage shows the box (front, then back), so no softgel is visible to attach a
label to. The edit therefore uses:

- **Tracked labels** where the softgels really are (1.0–2.7 s). Their keyframes were
  **measured from your clip** by frame-by-frame template matching (OpenCV, normalised
  cross-correlation, score ≥ 0.93 kept). There is a second pair for 29.15–30.1 s, switched
  off by default to keep the ending calm. Tick it on in *Labels & Tracking* if you want it.
- **Floating cards** for Scenes 4–5 (12–22 s), as timed in the brief, without a connector line.

The footage is mirrored (selfie camera), so on screen the **red column appears on the left**
and the **black column on the right**. The labels follow the real capsule colours.

### Motion tracking: what actually works

- **Keyframe editor**: select a tracked label, turn on **Click-to-keyframe**, then click or drag
  the capsule in the preview at any frame. Use ←/→ to step frames, **K** to key the playhead
  and **Delete** to remove a key. Keys are listed in a table and shown on the timeline.
- **Auto-track** (forward or backward): a real in-browser point tracker. It seeks frame by
  frame, matches a luminance patch with normalised cross-correlation and writes keyframes.
  It **stops and tells you** when the match falls below the confidence threshold (object
  covered, blurred or out of view). Add a keyframe after that point and continue.
- Labels hide automatically where there are no keyframes (object off screen). Card motion
  is smoothed so it floats naturally with the hand. The dot sits beside the capsule (dot
  offset), never on top of it.

## Template 2: Bold FAB + CTA

The same original footage with a different edit, built as a sales structure. Each beat sits on
the footage that fits it.

| Time | Beat | On screen | Footage |
|---|---|---|---|
| 0–2.75 s | **HOOK** | "2 BIJI **SEHARI.**" punch-zoom + flash; "Ini sebab saya tak pernah skip 👇" word by word | holding the box, then the blister |
| 1.0–2.7 s | labels | **PAGI ☀️** (red card) → red softgel, **MALAM 🌙** (black card) → black softgel, tracked | blister in view |
| 2.85–7.95 s | **ADVANTAGES** | ✓ Formula PAGI & MALAM berasingan · ✓ Hanya 2 softgel sehari · ✓ Mudah: ambil bersama makanan | taking a softgel |
| 8.0–12.7 s | **EMOTION** | "*Bukan nak nampak muda selamanya…*" → "…cuma nak **YAKIN** tengok cermin, *tanpa filter* 🤍" | drinking water, smiling |
| 12.7–14.1 s | **WHY** | "Skincare luar dah ada… Yang dari **DALAM?** 🤔" | smiling to camera |
| 14.1–17.0 s | **FEATURES** | Ageless by NYO3 · Ergothioneine & PQQ Day & Night Softgels | box front |
| 17.0–20.8 s | **FEATURES** | ☀️ red softgel: Astaxanthin 5mg · PQQ 15mg · SOD 20mg · Vitamin C 20mg | box back (MORNING table) |
| 20.8–24.4 s | **FEATURES** | 🌙 black softgel: L-Ergothioneine 30mg · Krill Oil 50mg · Sage Extract 50mg · Zinc · B2 & B3 | box back (EVENING table) |
| 24.4–27.0 s | **BENEFITS** | ✓ Bantu sokong kulit nampak sihat & berseri · ✓ Antioksidan bantu lindungi sel daripada tekanan oksidatif | box side |
| 27.0–30.1 s | **CTA** (Action → Reason → Benefit) | "TEKAN BEG **KUNING** 👇" · "Mulakan rutin 30 hari anda minggu ini" · "untuk sokongan antioksidan pagi & malam ✨" | holding box & blister |

- **Product facts:** every amount is copied from the printed pack. The benefit lines follow the
  pack's own wording ("helps support", "helps shield cells from oxidative stress"). There are
  no anti-ageing, wrinkle or medical claims, and no invented promotions. If you have a real
  promo, add it to the CTA.
- **Music:** "Pulse" style, original and synthesised in code: pluck synth, soft four-on-the-floor,
  claps, off-beat hats and a rounded sub bass. The drums drop out from 25.9 s while a riser
  builds into an impact on the CTA.
- **Sound effects:** impact, snap ticks synced to every ✓, swooshes, sparkle, riser.
- **Grade:** "Crisp Clean Editorial", with more contrast and clarity, still using skin and
  product protection.
- **New editor features:** animations *Punch zoom*, *Word-by-word pop* and *Checklist slide-in*;
  a *Solid card* backdrop with an accent bar; line options *Section chip*, *Checkmark ✓*,
  *Bounce* and *Solid box* highlight; *Solid colour* label cards; a project-level chapter bar,
  cut-zooms and flashes (`fx` in the project JSON); the *Pulse* music style.

## Colour grade: "Warm Ivory & Champagne Luxury" (template 1)

This is real per-pixel GPU processing (a WebGL shader), not a tinted overlay. Every value
below has its own slider.

Exposure +0.20 EV · Brightness +5 · Contrast +8 · Highlights −18 · Shadows +12 · Whites +5 ·
Blacks −5 · Saturation +4 · Vibrance +8 · Temperature +10 (slightly warm) · Tint 0 · light
3×3 bilateral noise reduction · very subtle clamped sharpening · soft highlight roll-off · 5%
vignette.

Extra controls protect the things the brief cares about:

- **Skin protect**: skin keeps its original hue and chroma and only takes the new brightness.
  This prevents orange or pink skin and any whitening.
- **Product protect**: the deep-red packaging and reddish-brown softgels keep their
  original colour.
- **Shadows**: a bell curve lifts the low-mids, so the black softgels stay deep and glossy.
- **Cast cleanup**: pulls near-neutral bright areas (beige wall, curtain) toward a clean
  warm ivory and neutralises the shadows.

To compare, use **Before | After split**, **Before**, or hold **B**.

## Music and sound

- **Original score (built in)**: composed and synthesised in code for this project at 100 BPM
  (adjustable from 95 to 105). It has a dreamy FM electric piano, detuned ambient pads, a
  soft sub bass, a gentle kick/snare/hat groove that enters at bar 3, and bell arpeggios.
  There are no vocals, drops or harsh highs. **No third-party samples or recordings are
  used**, so nothing needs licensing.
- To use a track from TikTok's Commercial Music Library, or any other track you hold a
  licence for, choose **My licensed track** and upload it.
- The 9 sound-effect types (shimmer, whoosh, swoosh, sparkle, pop, rising shimmer, glass
  chime, sparkle tick, piano resolution) are synthesised and **linked** to captions or
  labels, so they move when you retime the element.
- Separate volume controls exist for master, music, sound effects and original audio. Original
  audio is muted (0) by default.
- The master bus has gentle compression, a 12.5 kHz soft top and a limiter, so the mix does
  not clip. In the test render of your clip the mix peaked at −2.2 dBFS, with a steady loudness of about −15 dB RMS.

## Export

**Export MP4 · 1080×1920 · 30 fps** runs a frame-accurate offline render. Every source frame is
seeked, graded and composited at full resolution, encoded with the browser's **H.264**
encoder (WebCodecs) and muxed to MP4 with [mp4-muxer](https://github.com/Vanilagy/mp4-muxer)
(MIT, bundled in `vendor/`). The audio is rendered offline with the same engine as the
preview, so sound and animation stay in sync.

- **Audio codec**: AAC whenever the browser can encode it (Chrome/Edge on Windows and macOS
  normally can). If it can't (for example on some Linux builds), the editor says so and
  writes Opus audio instead. TikTok accepts that. To get strict H.264 + AAC, run:

  ```
  ffmpeg -i export.mp4 -c:v copy -c:a aac -b:a 192k -movflags +faststart final.mp4
  ```

- **Fallbacks**: *Real-time recording* (MediaRecorder: MP4 or WebM, depending on the browser)
  and *Download audio mix (WAV)*.

## Product claims

The text describes a routine and antioxidant ingredients that appear on the pack
(Astaxanthin, PQQ, Ergothioneine). It makes no claims about reversing ageing, removing
wrinkles or medical results. Keep any text you add within the same limits.

## Files

```
editor/
  index.html          UI shell
  css/editor.css      editor styling + bundled @font-face (Playfair Display, Poppins: OFL)
  js/project.js       default edit, measured tracking data, save/load
  js/grade.js         WebGL colour grader
  js/compositor.js    frame renderer (captions, labels, compare, safe zones)
  js/tracker.js       keyframe interpolation + auto point tracker
  js/audio.js         music composition, SFX synthesis, mixer, WAV export
  js/timeline.js      interactive timeline
  js/exporter.js      WebCodecs → MP4 export, real-time fallback
  js/app.js           app state, playback, panels
  vendor/mp4-muxer.js MP4 muxer (MIT)
  fonts/              Playfair Display + Poppins 300–800 woff2 (SIL OFL)
```
