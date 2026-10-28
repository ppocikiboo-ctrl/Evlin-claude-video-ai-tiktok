# VTLM — Self-Care 3D Animated TikTok Ad (30s, 9:16)

A premium, stylized 3D animated TikTok affiliate ad (Pixar / high-end CGI beauty
look) with on-screen text in Bahasa Melayu, Korean-aesthetic pop music and no voice-over.

Claude cannot render video. This pack is a ready-to-use production sequence:
keyframe prompts, image-to-video prompts, camera moves, timing, typography,
sound cues and the edit, for tools such as Kling 2.x, Veo 3, Runway Gen-4,
Hailuo, Sora and Midjourney / Nano Banana for keyframes, finished in CapCut.

**Product reference:** [`reference/product-front.jpg`](reference/product-front.jpg)
(a frame from the uploaded reference video).
**All reference frames:** [`reference/reference-video-frames.jpg`](reference/reference-video-frames.jpg)

---

## 0. Product facts (from the reference video)

| Feature | What the video shows |
|---|---|
| Pack type | Small flat stand-up zip pouch, about palm-sized, rounded corners, press-zip seal near the top, tear notches |
| Colour | Matte soft lavender / light violet, with a gentle satin sheen and soft crinkles |
| Front print | Gold foil serif wordmark **"VTLM"**, centred just below the zip. Under it, small gold italic serif tagline **"Jadikan diri anda lebih cantik"** |
| Back | Gold body text plus a white sticker with "VTLM" and a QR code, bottom right |
| Contents | Oval, lavender-white pressed tablets / candies |

**Rule:** only ever show the **front** of the pouch. Never show the back.

---

## 1. ⚠️ Compliance notes (read before producing)

1. **The back label reads "VTLM Slimming & Whitening Candy".** If the back is
   ever visible, the ad makes slimming and whitening claims that TikTok Shop
   restricts. Keep the back off-screen in every shot, and don't animate the tablets
   being eaten.
2. **The hook "SELALU LAPAR TENGAH MALAM?" next to a slimming product reads as an
   implied appetite-control claim**, even though the text never says so.
   TikTok reviewers judge the implied message. To lower the risk:
   - Never show the girl eating, refusing food or taking VTLM *because of* the
     food characters. The food characters stay cute and playful, are never "bad",
     are never crossed out and never disappear because of the product.
   - The story beat is *"craving late at night → I'd rather spend this time on
     myself"*. The answer to the hook is **self-care time**, not the product.
   - No scales, measuring tapes, slimmer bodies, before/after shots or body checks.
     Her outfit and body stay identical from start to end.
   - **Safer alternative hook** if the ad is rejected:
     **"TAK BOLEH TIDUR MALAM NI? 🌙"** ("Can't sleep tonight?") Every other
     scene stays the same.
3. The tagline printed on the pack ("Jadikan diri anda lebih cantik") is part of
   the real packaging and may stay visible. Don't repeat it as a claim in the
   added typography.
4. The brief's mind-map heading "SELF-CARE ROUTINE ✨" is English, which breaks the
   "Bahasa Melayu only / no random English" rule. This pack uses
   **"RUTIN JAGA DIRI ✨"** instead.
5. Music: use a track from TikTok's **Commercial Music Library** (search "K-pop
   aesthetic", "cute kpop instrumental", "korean pop upbeat"). Don't use a
   copyrighted K-pop song in a paid or affiliate ad.

---

## 2. Production workflow (best quality + exact packaging)

Video models redraw packaging text badly. **Never let an AI model generate the
VTLM pouch.** Use the real pouch as a composited plate instead.

1. **Build the character sheet first** (Prompt CS below). Generate it in one
   image model and pick one face, hairstyle and pyjama set. Use that image as the
   character / subject reference for **every** keyframe so her identity stays
   the same.
2. **Make one keyframe image per shot** (prompts in section 5), with the
   character sheet attached as reference. Generate 4–8 per shot and keep the best.
3. **Animate each keyframe** in an image-to-video tool (start frame = keyframe;
   add the end-frame where the tool supports start/end frames). Generate 5s or
   10s clips at 1080×1920 and upscale to 4K (Topaz Video AI or the tool's own
   upscaler).
4. **Product plate:** cut the pouch out of
   [`reference/product-front.jpg`](reference/product-front.jpg) (CapCut "Remove
   background", Photoroom or Photoshop), and keep the hand only if the shot needs it.
   Export as PNG. Composite it onto the empty pedestal / bag-area plates in shots 5–6,
   then add a slow 3D-feel move in CapCut / After Effects: scale 100→106%, ±4° Y
   rotation using a 3D layer, a soft drop shadow, and a reflection made by flipping
   the layer vertically at 20% opacity with a gradient mask.
   - If you want the pouch to rotate in true 3D: use the image as the reference in
     an image-to-3D tool (Meshy, Tripo, Rodin), then **replace the generated front
     texture with the real photo**, and render the turn in Blender. Never accept
     AI-redrawn gold text.
5. **Typography, particles and SFX are added in the edit** (CapCut or After Effects),
   not generated by the video model. Video models misspell Malay text.
6. Assemble using the timeline in section 4, grade with section 8, and export
   using section 10.

---

## 3. Style bible (paste the global style block into every prompt)

**GLOBAL STYLE BLOCK**
```
premium stylized 3D animation, Pixar / Disney-quality CGI, high-end beauty
commercial, dreamy Pinterest aesthetic, lavender purple, blush pink, pearl white,
champagne gold, soft peach and moonlight-blue palette, cinematic global
illumination, soft volumetric light, ambient occlusion, subsurface-scattered
skin, subtle bloom, gentle film grain, shallow depth of field, 4K, ultra detailed,
vertical 9:16 composition
```

**GLOBAL NEGATIVE PROMPT**
```
text, letters, words, captions, watermark, logo, packaging, distorted face,
extra fingers, missing fingers, fused hands, deformed limbs, flicker, morphing
face, changing outfit, changing hairstyle, low resolution, blurry, plastic skin,
uncanny, cheap cartoon, flat lighting, clutter, scale, measuring tape, body
comparison, before and after
```
(Do not list "text" as a negative in the shots where the model must leave a clean
empty area for the product. Leave the area empty and composite the product later.)

**Prompt CS — Character sheet (image model)**
```
Character turnaround sheet of one cute stylized 3D young Malaysian woman, early
20s, soft round face, big expressive dark-brown eyes, natural lashes, light-tan
warm skin, rosy cheeks, small smile, shoulder-length dark-brown hair with soft
curtain bangs and a lavender scrunchie, wearing a pastel lavender satin pyjama
set (button-up short-sleeve top with white piping, long pants) and fluffy white
slippers. Front, 3/4 and side views plus 4 facial expressions (surprised,
happy, calm eyes-closed, confident smile). Neutral pearl-white background,
soft studio lighting. [GLOBAL STYLE BLOCK]
```
Keep this exact outfit through shots 1–4. In shots 5–6 she can change into a
casual outfit (cream knit cardigan, white top, lavender skirt). The clothes
change, but her face, hair and scrunchie stay the same.

**Recurring motifs:** a floating pink heart, lavender light trails, golden
sparkles. Use them to link the shots together.

---

## 4. Master timeline (30.0s @ 30 fps = 900 frames)

| # | Time | Scene | Camera | On-screen text |
|---|---|---|---|---|
| 1A | 0.0–1.2 | Midnight bedroom, clock reads 12:00 AM, moon | Fast push-in from the window to the bed | — |
| 1B | 1.2–3.2 | Food characters pop in and float around her in slow motion | Slow orbit, 20° | "SELALU" / "LAPAR" / "TENGAH" / "MALAM? 🌙" (word by word) |
| 1C | 3.2–4.5 | Surprised face, crash zoom, BOOM | Crash zoom onto her face | Full line, 3D extruded |
| 2 | 4.5–9.0 | She touches a floating heart, a portal opens, the bedroom dissolves into the self-care universe | 180° orbit | "MASA UNTUK JAGA DIRI! 💗" |
| 3A | 9.0–11.0 | Holographic mind map forms | Pull back plus rise | "RUTIN JAGA DIRI ✨" |
| 3B | 11.0–13.0 | Bubble 1: wardrobe | Rack focus to the bubble | "🌸 JAGA BADAN" |
| 3C | 13.0–15.0 | Bubble 2: relaxing self-care | Rack focus | "💖 JAGA DIRI" |
| 3D | 15.0–17.0 | Bubble 3: mirror, confident smile; light trails connect all three | Pull back to wide | "✨ SAYANG DIRI" |
| 4 | 17.0–23.0 | Silk ribbons part, the VTLM pouch on a glass pedestal | Dolly-in plus slight arc | "VTLM 💜" → "RUTIN PENJAGAAN DIRI ✨" |
| 5 | 23.0–27.0 | Pastel boutique, she holds a yellow bag, the pouch is shown | Tracking, parallax | "JAGA BADAN 🌸" / "JAGA DIRI 💖" / "KERANA DIRI ANDA BERHARGA ✨" |
| 6 | 27.0–30.0 | CTA end card, pouch hero, gold arrow pointing to the yellow basket | Locked, gentle float | "KENALI VTLM DI BEG KUNING 🛍️" |

Music hits: match the beat drop to **3.2s** (BOOM) and the second drop / chorus
to **17.0s** (product reveal). At about 110–125 BPM, one bar ≈ 2s, so most of the
cuts above land on bar lines. Nudge the cuts to the actual beats of your track.

---

## 5. Shot-by-shot prompts

Each shot has a **KEYFRAME** prompt (image model, with the character sheet as
reference) and a **MOTION** prompt (image-to-video). Add the GLOBAL STYLE BLOCK
and the negative prompt to each one.

### Shot 1 — Hook: "SELALU LAPAR TENGAH MALAM?" (0.0–4.5s)

**KEYFRAME 1**
```
Cozy stylized 3D bedroom at midnight, seen from slightly above the window. The
character [ref] sits cross-legged on a fluffy bed with blush-pink and lavender
bedding and fairy lights on the headboard, wearing her lavender satin pyjamas
and holding a pillow. A giant glowing full moon fills the window behind her,
casting moonlight-blue rim light and long soft shadows. On the bedside table, a
cute white digital clock glows pink. Plush toys, a small plant, warm lamp glow.
Moonlight-blue and lavender night palette with warm pink accents. Volumetric
moonbeams with dust motes. [GLOBAL STYLE BLOCK]
```
(The clock text is added in the edit: it shows **12:00 AM** and blinks
on the cut at 0.0s. Leave the clock face blank in the keyframe.)

**MOTION 1A (0–1.2s)**
```
Fast smooth push-in from the window toward the girl on the bed, slight
downward tilt, moonbeams streaming past the camera, fairy lights twinkling,
she blinks and looks up. Cinematic, fluid, no cuts.
```

**KEYFRAME 1B**
```
Same bedroom and character [ref]. Four adorable miniature 3D food characters
float in the air around her in slow motion: a pink-frosted doughnut with sprinkles
and a big smile, a chocolate-chip cookie dancing with tiny arms, a little
paper cone of golden fries waving, and a tiny strawberry cake bouncing. Each
has big shiny cartoon eyes and rosy cheeks. Soft glow trails behind them. The
girl looks surprised, mouth in a small "o", eyes wide. [GLOBAL STYLE BLOCK]
```

**MOTION 1B (1.2–3.2s)**
```
Slow-motion: the food characters pop into existence one by one with a soft
sparkle, then drift and twirl around the girl in a gentle circle. The doughnut
spins, the cookie dances, the fries wiggle, the cake bounces. Camera slowly
orbits 20 degrees to the right. The girl's eyes follow the doughnut, surprised.
Natural, smooth character animation.
```

**MOTION 1C (3.2–4.5s)**
```
Rapid crash zoom into the girl's surprised face, the food characters whipping
past the lens with motion blur, ending on a close-up of her big sparkling eyes.
```

**Typography (edit):**
- 1.2s "SELALU" → 1.6s "LAPAR" → 2.0s "TENGAH" → 2.4s "MALAM? 🌙". Each word
  scales 0→115→100% with an elastic overshoot (about 8 frames), drops 6px of gold
  extrusion, gets a 3-frame motion blur, and adds a pink particle burst plus a star trail.
- 3.2s **BOOM**: the full line slams to 120% then settles to 100% (back-out ease),
  with a screen shake (2 frames, 12px), a white flash (2 frames at 60%) and a radial pink
  particle explosion.
- Text sits in the upper third (y ≈ 18–32% of the frame).

**SFX:** clock tick (0.0), soft sparkle (0.3), 4× cute "pop" on each food
character (1.2–2.0), "pop" per word, deep **BOOM** plus whoosh on the crash zoom (3.2).

### Shot 2 — Magical transformation: "MASA UNTUK JAGA DIRI! 💗" (4.5–9.0s)

**KEYFRAME 2 (start)**
```
Close-up: the character [ref] in her lavender pyjamas, now smiling softly,
reaches up with one finger to touch a glowing floating pink 3D heart. The food
characters wave goodbye happily in the background and drift out of focus.
Moonlight-blue bedroom. [GLOBAL STYLE BLOCK]
```

**KEYFRAME 2 (end)**
```
The same character [ref], same outfit, standing in a dreamy futuristic
self-care universe: floating pearl-white platforms, lavender and blush-pink
clouds, glowing crystal flowers, gentle aurora in pink and champagne gold, soft
holographic rings in the sky, thousands of tiny glowing particles swirling
around her in a spiral. Serene, magical. [GLOBAL STYLE BLOCK]
```

**MOTION 2** (start + end frame)
```
Her fingertip touches the pink heart, which pulses and releases a ring of light.
A swirling lavender portal opens behind her. The bedroom walls dissolve into
glowing particles that spiral upward, revealing the dreamy self-care universe.
Thousands of particles swirl around her. The camera performs a smooth
180-degree orbit around her during the transformation, ending in front of her as
she opens her eyes and smiles. Seamless, cinematic, no cuts, consistent face
and outfit.
```

**Typography (edit):** 6.8s "MASA UNTUK JAGA DIRI! 💗" appears as a holographic
title: pearl-white text with a lavender outer glow and a thin cyan-pink chromatic
edge, letters scan in left to right with a light sweep (10 frames), a slight
floating bob (±6px over 2s). Position: upper third.

**SFX:** "ting" on the heart touch (4.8), cinematic magical sweep (5.0–6.5),
soft rising shimmer under the orbit, whoosh as the title appears (6.8).

### Shot 3 — Holographic mind map: "RUTIN JAGA DIRI ✨" (9.0–17.0s)

**KEYFRAME 3A (wide)**
```
The character [ref] stands in the self-care universe at the centre of a floating
holographic mind map. Above her head is an empty glowing glassmorphism title
panel. Around her float three large transparent glass bubbles: one top-left,
one top-right, one lower-centre. Each bubble has realistic glass reflections,
iridescent edges and an animated neon lavender outline, and is connected to the
others by glowing lavender light trails. Floating particles. [GLOBAL STYLE BLOCK]
```

**KEYFRAME 3B — inside bubble 1 (wardrobe)**
```
Inside a transparent glass bubble: a beautiful miniature white-and-gold
wardrobe with its doors opening, revealing stylish pastel outfits on tiny
hangers (cream cardigan, lavender dress, pink blazer), a little mirror and a
hat box. Iridescent glass reflections on the bubble surface. [GLOBAL STYLE BLOCK]
```

**KEYFRAME 3C — inside bubble 2 (self-care routine)**
```
Inside a transparent glass bubble: the same character [ref] relaxing with a
pastel headband, a soft face mask and eyes closed, a cup of herbal tea, scented
candles, bath salts and a small book on a fluffy rug. Calm and happy.
[GLOBAL STYLE BLOCK]
```

**KEYFRAME 3D — inside bubble 3 (mirror)**
```
Inside a transparent glass bubble: the same character [ref], same outfit,
smiling confidently at her reflection in an ornate oval champagne-gold mirror
surrounded by soft bulbs and fresh flowers. Warm flattering light.
[GLOBAL STYLE BLOCK]
```
(Show only her face and her reflection. Don't show her body or any body check.)

**MOTION 3A**
```
The camera pulls back and rises slightly as three glass bubbles materialise
around the girl one after another, each gently rotating in 3D with glinting
reflections. Lavender light trails draw themselves between the bubbles.
Particles drift upward. Smooth, satisfying, elegant.
```

**MOTION 3B / 3C / 3D** (one clip per bubble)
```
Slow push-in into the glass bubble, with rack focus from the bubble's glass
surface to the scene inside it. The scene inside animates gently [wardrobe
doors open / she sips tea and smiles / she tucks her hair and smiles at the
mirror]. The bubble slowly rotates; reflections slide across it.
```
In the edit, show each bubble inset as a rack-focus close-up for about 1.6s, then
cut back to the wide shot with that bubble lit. At 16.0s, pull back to the wide
shot with all three bubbles lit and the trails pulsing.

**Typography (edit):**
- 9.3s title "RUTIN JAGA DIRI ✨" in the glass panel above her head (pearl white,
  gold ✨, 3D tilt in, 12 frames).
- 11.0s "🌸 JAGA BADAN", 13.0s "💖 JAGA DIRI", 15.0s "✨ SAYANG DIRI". Each
  label clicks onto its bubble in a frosted-glass pill (white text, 1px lavender
  neon stroke, background blur 20, 15% white fill), scales 80→100% with a soft bounce.

**SFX:** soft "click" when each bubble appears, "ting" when each label lands,
a light glassy shimmer when the trails connect (16.0).

### Shot 4 — Cinematic product reveal: "VTLM 💜" (17.0–23.0s)

**KEYFRAME 4A (ribbon transition)**
```
Full-frame swirling lavender and blush-pink silk ribbons with satin highlights
filling the screen, gold sparkles caught in the folds, soft volumetric light
shining through. [GLOBAL STYLE BLOCK]
```

**KEYFRAME 4B (empty product stage)**
```
Luxurious product stage: an empty floating round glass pedestal with a
champagne-gold rim, hovering above a glossy reflective pearl-lavender floor. A
soft golden spotlight from above. Rotating lavender particles, floating
translucent pink hearts, delicate bokeh, light silk ribbons drifting away at
the edges. The top of the pedestal is empty and clear for a product to be
placed later. Centred composition, the pedestal in the lower-middle of the frame.
[GLOBAL STYLE BLOCK]
```

**MOTION 4**
```
Lavender silk ribbons swirl across the camera and slowly part like curtains,
revealing the empty floating glass pedestal under a golden spotlight. The camera
dollies in slowly with a slight arc to the left; particles rotate around the
pedestal, translucent hearts float upward, soft lens flare from the spotlight.
Nothing appears on the pedestal.
```

**Composite (edit / AE):** at 18.5s, the cut-out **real VTLM pouch** (front only)
fades and scales in on the pedestal (90→100%, 12 frames, ease-out) with a soft
white glow. Keep it upright and centred, filling about 45% of the frame width.
Add a pedestal contact shadow, a floor reflection (flipped, 20% opacity), one
diagonal light sweep across the pouch at 19.5s (a white gradient, screen blend,
30% opacity, 15 frames), and a slow scale of 100→106% to 23.0s. Don't warp,
stretch or recolour the pouch. Grade the plate's lavender to match the scene, but
keep the gold foil gold.

**Typography (edit):**
- 19.0s "VTLM 💜", large (about 150pt equivalent), champagne-gold gradient with a
  thin white highlight bevel, placed **above** the pouch (y ≈ 15–25%). Don't
  overlap the pouch.
- 20.8s "RUTIN PENJAGAAN DIRI ✨" in pearl white with a lavender glow,
  below the VTLM title, in a smaller size.

**SFX:** deep cinematic whoosh (17.0, on the second beat drop), silk swoosh
(17.2–18.2), elegant luxury chime (18.5, the pouch appears), crystal sparkle (19.5, light sweep).

### Shot 5 — Premium shopping moment (23.0–27.0s)

**KEYFRAME 5**
```
Elegant pastel boutique interior: blush-pink walls with arched shelves, pearl-
white marble floor, champagne-gold accents, flowers, soft daylight from tall
windows. The character [ref], same face and hair, now in a cream knit cardigan,
white top and lavender pleated skirt, walks happily holding a cute glossy
YELLOW shopping bag with rope handles (plain, no text). Tiny sparkling stars
around the bag. To her right, an empty small glass display stand with soft
light, left empty for a product. Medium-wide shot. [GLOBAL STYLE BLOCK]
```

**MOTION 5**
```
Smooth tracking shot moving alongside the girl as she walks through the pastel
boutique, swinging the yellow shopping bag happily, then turns toward the
camera and smiles. Parallax between the foreground flowers, her and the shelves.
Tiny stars twinkle around the bag. Natural walk, consistent face and outfit.
```

**Composite:** the real pouch on the empty display stand, or held close to the
camera with her face blurred behind it. The pouch stays fully visible and sharp.

**Typography (edit):** stacked pills on the left, each appearing on a beat:
23.4s "JAGA BADAN 🌸", 24.2s "JAGA DIRI 💖", 25.2s "KERANA DIRI ANDA
BERHARGA ✨" (that one larger, champagne gold).

**SFX:** a light whoosh on the transition, "pop" on each line, a soft sparkle on
the bag stars.

### Shot 6 — CTA end card (27.0–30.0s)

**KEYFRAME 6**
```
Dreamy lavender and blush-pink gradient end-card background with soft bokeh,
floating translucent hearts, gold sparkles and silk ribbons framing the edges.
Lower-centre: an empty floating glass pedestal with a gold rim. A yellow
shopping bag sits beside it, slightly behind. Plenty of clean empty space.
[GLOBAL STYLE BLOCK]
```

**MOTION 6**
```
Very gentle float: particles drift, hearts rise slowly, the bag sparkles. The
camera is nearly locked with a subtle 2% push-in. No new objects appear.
```

**Composite:** the real VTLM pouch on the pedestal (front, centred, about 40% of the frame
width, between y ≈ 38% and 68%).

**Typography (edit):**
- 27.3s "KENALI VTLM DI BEG KUNING 🛍️", bold rounded font, white text on
  a blush-pink rounded pill, gold stroke, at y ≈ 20–30% of the frame.
- 27.8s a **glowing golden arrow** (gold gradient, soft outer glow) sits at the
  **lower left (x ≈ 10–30%, y ≈ 72–80%)**, pointing **down-left** toward where
  TikTok shows the yellow basket / product link above the caption. It pulses
  gently (scale 100→110→100% every 0.6s, glow brightening on each pulse) and
  never overlaps the pouch.

**SFX:** a cute shopping notification sound (27.3), a satisfying magical "ding"
on the arrow (27.8), music resolves and rings out to 30.0.

---

## 6. Typography system

| Use | Font (CapCut / Google Fonts) | Style |
|---|---|---|
| Hook and CTA | **Baloo 2 ExtraBold** or **Fredoka Bold** | ALL CAPS, white fill, 6–8px blush-pink stroke, gold 3D extrusion (offset 0/6px, #C9A45C), soft drop shadow |
| Holographic titles | **Poppins SemiBold** | Pearl white #FFF8FB, lavender outer glow #B79CFF at 60%, letter-spacing +2% |
| Bubble labels / pills | **Poppins Medium** | Frosted glass pill: 15% white plus background blur, 1px neon lavender stroke |
| Brand title "VTLM" | **Cormorant Garamond Bold** or **Playfair Display** (a serif to echo the pack) | Champagne-gold gradient #F3DFA2 → #C9A45C, white highlight |

- **Minimum text size:** the hook at about 110–130px cap height on a 1080×1920
  canvas, labels at about 60px or more. Every line must stay readable on a phone at arm's length.
- **TikTok safe zone:** keep all key text and the product inside x 60–900px and
  y 220–1480px. The right column (≈ 120px) and the bottom ≈ 420px are covered by
  TikTok's buttons and caption. Only the CTA arrow goes into the bottom-left area.
- Emojis: use the platform's colour emoji (Apple style in CapCut) at the same
  height as the text.
- Check the spelling of every string against this list before export:
  `SELALU LAPAR TENGAH MALAM?` · `MASA UNTUK JAGA DIRI!` · `RUTIN JAGA DIRI` ·
  `JAGA BADAN` · `JAGA DIRI` · `SAYANG DIRI` · `VTLM` · `RUTIN PENJAGAAN DIRI` ·
  `KERANA DIRI ANDA BERHARGA` · `KENALI VTLM DI BEG KUNING`

---

## 7. Sound design cue sheet

Music: an upbeat Korean-aesthetic pop instrumental from the TikTok Commercial Music
Library, 110–125 BPM, at −14 LUFS overall. Duck the music by about 3 dB under big SFX.

| Time | Cue | Notes |
|---|---|---|
| 0.0 | Clock tick ×2 + soft sparkle | Music starts on a filtered intro (low-pass) |
| 1.2–2.4 | 4× cute pop (food) + 4× pop (words) | Pitch each pop slightly higher |
| 3.2 | BOOM + whoosh | Music filter opens: **drop 1** |
| 4.8 | Ting (heart touch) | |
| 5.0–6.5 | Magical sweep + rising shimmer | |
| 6.8 | Whoosh (title) | |
| 9.0, 11.0, 13.0, 15.0 | Glass click + ting | One pair per bubble |
| 16.0 | Glass shimmer | Trails connect |
| 17.0 | Deep cinematic whoosh | **Drop 2 / chorus** |
| 17.2–18.2 | Silk swoosh | |
| 18.5 | Luxury chime | Pouch appears |
| 19.5 | Crystal sparkle | Light sweep |
| 23.4 / 24.2 / 25.2 | Pop ×3 | Shopping lines |
| 27.3 | Shopping notification | CTA |
| 27.8 | Magical ding | Arrow |
| 29.5–30.0 | Music ending / ring-out | Clean loop back to the start |

Free SFX sources: the CapCut sound library, Pixabay Sound Effects, Mixkit.

---

## 8. Colour grade

- Palette anchors: lavender #B79CFF, blush pink #F7C6D9, pearl white
  #FFF8FB, champagne gold #E6C687, soft peach #FFD8C2, moonlight blue #8FA8E8.
- Shot 1 is cooler (moonlight blue shadows, pink highlights). Shot 2 onward is warmer and brighter.
- In CapCut: Contrast +8, Highlights −10, Shadows +6, Saturation +5, a slight
  lavender tint in the shadows and peach in the highlights, Glow / Bloom 10–15, film grain
  5. Add a vignette of −8 on the product shots only.
- Text contrast check: put a 25% dark-lavender gradient (#2B1A4A → transparent)
  behind light text when the background is bright.

---

## 9. Quality control checklist

- [ ] Her face, hair, scrunchie and eye colour are the same in every shot. Regenerate
      any clip where her face morphs.
- [ ] Hands: 5 fingers and no fused fingers. Crop or cut around bad hand frames.
- [ ] The pyjamas are the same in shots 1–4. The boutique outfit is the same in shot 5.
- [ ] The pouch is always the real photo plate, front only, never warped, with the
      gold "VTLM" and tagline readable. The back is never shown.
- [ ] No AI-generated text anywhere in the frame (clock, bag, signs): check every frame.
- [ ] All Malay text matches the spelling list. No English words on screen.
- [ ] No eating, scales, body shots, before/after, or "slim / kurus / lapar hilang"
      wording. No health claims.
- [ ] Text and product stay inside the TikTok safe zone, and the arrow doesn't cover the product.
- [ ] No flicker at the cuts, and the hook lands inside the first 1.2s.

---

## 10. Edit and export

1. CapCut project at 1080×1920, 30 fps (60 fps if every clip was generated or
   interpolated at 60).
2. Place the clips in the timeline order from section 4. Transitions: a match-cut whip at 4.5,
   a particle dissolve at 9.0, and a ribbon wipe (shot 4's own animation) at 17.0. Use a
   light flash at 23.0 and a soft zoom-through at 27.0.
3. Add text, stickers, particles (CapCut effects: "Sparkle", "Star trail",
   "Light leak pink") and the SFX following the cue sheet.
4. Export: 4K if the clips were upscaled (otherwise 1080p), 30/60 fps, H.264 or
   HEVC, high bitrate (≥ 20 Mbps for 1080p, ≥ 45 Mbps for 4K).
5. TikTok post: link the VTLM product in TikTok Shop so the yellow basket appears.
   Suggested caption (Malay, no claims):
   `Masa untuk jaga diri 💜 #VTLM #rutinjagadiri #selfcare #fyp #tiktokshopmy`
