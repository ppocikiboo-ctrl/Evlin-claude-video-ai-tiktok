# RCH Black Baggy Pants — TikTok Mirror Selfie OOTD (15s, 9:16)

Ultra-realistic TikTok affiliate video: a young Malaysian-Asian woman films a
mirror selfie OOTD on an iPhone, modeling the black RCH baggy pants.

**Product reference (primary visual reference):**
https://drive.google.com/file/d/1QgHfV6v-XTKqvglRsnfNl5urhfuHzwzZ/view

**Project assets folder:**
https://drive.google.com/drive/folders/10zUTEpuNS2McdVVWibpxr_jr9NJHcriM

**Local copy of the front product photo:** [`reference/product-front.jpg`](reference/product-front.jpg)

### Product details (from the front product photo)

| Feature | What the photo shows |
|---|---|
| Fabric | Solid black, lightweight woven track-pant fabric (nylon look) with a soft matte sheen |
| Silhouette | Relaxed high-rise, wide straight legs, full length, hems pooling slightly over the sneakers |
| Waistband | Wide gathered elastic waistband |
| Drawstrings | Black cord with white flecks, tied in a bow at center front, ends hanging to mid-thigh |
| Logo | Small white italic "RCH" inside an oval swoosh outline, on the wearer's left front hip just below the waistband |
| Upper piping | Thin white piping on each leg starts at the waistband near center front, arches outward over the hip and runs straight down the front of the thigh to about the knee |
| Lower piping | A second white piping line on each leg runs down the outer side and sweeps in a gentle S-curve across the lower leg to the hem |
| Knee seam | Horizontal panel seam across each leg at about knee height |
| Pockets | Side slant pockets at the hips (hands fit inside) |

### How the real pants look (from the example phone video)

The example video (frames in [`reference/example-frames.jpg`](reference/example-frames.jpg))
shows the real product in indoor light, which differs a little from the studio photo.
The prompts below follow the real product:

- **Fabric:** thin, lightweight crinkled nylon (windbreaker / taslan type), with
  soft creases and a subtle sheen. In room light it reads as very dark
  charcoal-black, not flat jet black.
- **Piping:** thin white piping with a slight sheen; in shadow it looks light grey.
- **Logo:** a small white embroidered emblem on the wearer's left hip, next to the drawstrings.
- **Back:** plain black, with the side piping visible at the edges.
- **Drape:** the fabric is light, so the wide legs swing and fold easily when moved.

Always attach this image as the **image / product / ingredient reference** in the
video tool. The text prompt alone cannot reproduce the exact piping and logo.

---

## 1. Recommended workflow (best product accuracy)

Video models change the details of clothing much less when they animate a
correct still image than when they generate the clothing from text. Work in
two steps:

1. **Make a keyframe image.** Use an image model that accepts a reference image
   (Nano Banana / Gemini image, GPT-image, Flux Kontext, Seedream). Upload the
   product photo and use **Prompt A**. Generate 4–8 versions and keep the one
   whose pants match the reference exactly: the piping lines, the logo position
   and the drawstrings.
2. **Animate the keyframe.** In an image-to-video tool (Kling 2.x, Veo 3,
   Runway Gen-4, Hailuo, Sora), upload the chosen keyframe as the first frame
   and the product photo as an extra reference if the tool allows one. Then use
   **Prompt B** with the **Negative prompt**.
3. If the tool's maximum clip length is under 15 s, generate the shots in
   section 4 as separate clips, all from the same keyframe, and join them in
   CapCut.

---

## 2. Prompt A — keyframe image

```
Vertical 9:16 photo, authentic iPhone mirror selfie in a bright, clean bedroom
with a full-length mirror. A young Malaysian-Asian woman, about 25 years old,
160 cm tall, slim with natural proportions, long straight dark hair, real skin
texture with visible pores and no beauty filter, natural makeup. She holds an
iPhone in her right hand in front of her chest, partly covering her face, and
the phone's back camera faces the mirror. Her posture is relaxed and confident
and her weight rests on one leg.

Outfit: a fitted white baby tee with short sleeves, a body-hugging slim fit and
plain white cotton with no logo, slightly cropped so it ends at the waistband.
She wears the EXACT black RCH baggy pants from the reference image. Keep their
solid black lightweight crinkled nylon fabric with soft creases and a subtle
sheen, relaxed
high-rise wide straight-leg silhouette, wide gathered elastic waistband and
black drawstrings with white flecks tied in a bow at center front. On each leg,
thin white piping starts at the waistband near center front, arches outward
over the hip and runs straight down the front of the thigh to the knee, and a
second white piping line runs down the outer side and sweeps in a gentle
S-curve across the lower leg to the hem. Keep the horizontal knee seam, the
side slant pockets and the small white italic "RCH" logo in an oval swoosh on
her left front hip just below the waistband. The full-length hems pool
slightly over clean white casual sneakers. Minimal
accessories: small earrings, maybe a thin bracelet.

Modern Korean-inspired casual streetwear. Soft daylight from a window, neutral
warm tones, a slightly imperfect handheld composition, the head-to-toe outfit
fully visible in the mirror. Photorealistic with real-phone image quality.
```

---

## 3. Prompt B — video (15 s, 9:16)

```
15-second vertical 9:16 video, an authentic TikTok OOTD mirror selfie recorded
handheld on an iPhone at 30fps. It looks like real user-generated content:
slight natural hand shake, iPhone auto-exposure, a bright bedroom with soft
window daylight in front of a full-length mirror.

A young Malaysian-Asian woman, about 25 years old, 160 cm tall, slim, with long
straight dark hair and realistic skin texture, wears a fitted white cropped
baby tee (plain, no logo), the exact black RCH baggy pants from the reference
image, and clean white sneakers.

The pants must match the reference exactly in every frame: solid black
lightweight crinkled nylon fabric, relaxed wide straight legs, a wide elastic
waistband with black white-flecked drawstrings tied at center front, white
piping that arches from the waistband over each hip and runs down the front of
each thigh to the knee, a second white piping line curving in an S-shape down
the outer lower leg to the hem, the knee seam, the side slant pockets and the
small white italic "RCH" oval-swoosh logo on her left hip. The piping stays
continuous and the lines stay consistent while the fabric moves.

Action: she holds the phone at chest height facing the mirror. She shifts her
weight, turns her hips left and right to show the wide-leg drape, takes one
small step forward so the fabric swings, tugs the drawstring lightly, turns
around for a quick back view, and turns back with a relaxed smile. Natural,
unposed movement and casual confidence.

Photorealistic with real fabric physics: light nylon with soft crinkles and a
subtle sheen, and the wide legs swing and fold naturally. No cinematic grading, no slow motion, no
camera moves other than her handheld phone.
```

### Negative prompt

```
cartoon, CGI, 3D render, plastic skin, airbrushed, beauty filter, doll face,
extra fingers, deformed hands, distorted phone, phone floating, mirror
reflection mismatch, second person, oversized shirt, jacket, hoodie, crop top
showing midriff gap too large, logo on t-shirt, skinny jeans, leggings, shorts,
grey pants, blue pants, cargo pants, jogger cuffs, tapered legs, missing white
piping, extra stripes, straight side stripes instead of curved front piping,
broken or flickering piping, plain black drawstrings, white drawstrings, wrong
logo, large logo, logo on the wrong hip, text artifacts, changed pocket
position, heels, black shoes, dirty shoes, heavy
jewelry, cinematic color grade, slow motion, drone shot, dolly zoom, watermark,
subtitles
```

---

## 4. Shot list (if generating as separate clips)

| # | Time | Shot | Action | Purpose |
|---|------|------|--------|---------|
| 1 | 0–3 s | Full-body mirror selfie | She steps into frame, adjusts her stance, and tilts the phone slightly | Hook: the full outfit at a glance |
| 2 | 3–6 s | Full body, small hip turns | She turns left, then right, so the wide legs swing | Shows the baggy silhouette and the drape |
| 3 | 6–9 s | Phone tilted down to the waist | Her free hand tugs the white-flecked drawstring and the RCH logo on her left hip is visible | Waistband, drawstrings, logo and piping detail |
| 4 | 9–12 s | Phone tilted down to the legs and sneakers | One step forward, the fabric pools over the sneakers | Front leg piping, lower curved piping, length |
| 5 | 12–15 s | Back to full body | A quick spin to the back view, turns forward, smiles, pose | Back view, then the call-to-action moment |

---

## 4b. Format 2 — hands-on product showcase (matches the example video)

The example video is a faceless "real product" clip: one person holds the
pants up in a bedroom and shows each detail. This style looks very authentic,
and since no face or full body is needed, AI tools get the pants right more
often. Use it as its own post, or cut 3–5 s of it into the mirror selfie video
as B-roll.

**Tip:** your real footage of the pants always beats AI here. If you have the
pants, film this format yourself and use AI only for the mirror selfie.

### Prompt C — showcase video (15 s, 9:16)

```
15-second vertical 9:16 video, authentic handheld phone footage for TikTok,
filmed by a real person in a small bedroom: a light grey curtain on the left,
a white wall, a white drawer cabinet and a black headboard behind, pink bedding
at the bottom edge. Indoor daylight, slightly flat iPhone exposure, small
natural hand shake. No face is shown; only her hands and forearms.

She shows the exact black RCH baggy pants from the reference image. The pants
are thin, lightweight crinkled black nylon with a subtle sheen, a wide
gathered elastic waistband, black drawstrings with white flecks, a small white
embroidered logo on the left hip, thin white piping that arches from the
waistband over each hip and runs down the front of the thigh to the knee, and
a second white piping line that curves in an S-shape down the outer lower leg
to the hem. Wide straight legs, full length.

Action: she starts with the pants folded and held up in one hand, then lets
them unfold so the full length drops. She holds them up by the waistband
against the wall, smooths the leg to show the curved piping, then holds the
waistband at her own waist to show the length and drape. She stretches the
elastic waistband and lets the drawstrings swing, turns the pants to show the
plain back, then gives the leg a light shake so the light nylon swings.

Photorealistic real fabric: crinkles, creases and a soft sheen, with the
piping staying continuous on the moving fabric. No studio lighting, no
cinematic grading, no slow motion.
```

Use the same **Negative prompt** as above, and add: `face, mannequin, hanger,
studio backdrop, flat lay, folded neatly in packaging`.

### Shot list

| # | Time | Shot | Action | Purpose |
|---|------|------|--------|---------|
| 1 | 0–3 s | Pants folded, held up in one hand | She lets the pants unfold and drop to full length | Hook: the reveal |
| 2 | 3–6 s | Full length against the wall | Holds them by the waistband and smooths one leg | Silhouette, arched piping |
| 3 | 6–9 s | Waistband close-up | Stretches the elastic, the drawstrings swing, the logo is visible | Waistband, drawstrings, logo |
| 4 | 9–12 s | Held at her own waist | Lines the waistband up with her waist and shows the length to the floor | Fit and length |
| 5 | 12–15 s | Back view, then a lower leg close-up | Turns the pants around, then shakes the leg so the S-curve piping moves | Back view, lower piping, fabric movement |

---

## 5. TikTok post package

**On-screen text (CapCut, Malay/English mix):**

- 0–3 s: `OOTD ft. seluar baggy RCH 🖤`
- 6–9 s: `Pinggang getah + tali, selesa gila`
- 12–15 s: `Link kat beg kuning 👇`

**Caption:**

```
Seluar baggy RCH ni memang wajib ada 🖤 Wide-leg, pinggang getah, ada piping
putih — padan dengan baby tee & sneakers putih je dah cantik. Tekan beg kuning
untuk beli! 🛒

#ootd #baggypants #seluarbaggy #ootdmalaysia #koreanstyle #streetwear
#tiktokshopmalaysia #fyp
```

**Audio:** a trending lo-fi / K-pop instrumental from TikTok's Commercial Music
Library, which affiliate posts must use.

---

## 6. Product-accuracy QA checklist

Check every generated clip frame by frame before posting:

- [ ] The pants are solid black with no colour shift to grey or navy
- [ ] The wide straight-leg silhouette holds and the legs never taper, cuff or turn skinny
- [ ] The wide elastic waistband is visible and the drawstrings are black with white flecks, tied at center front
- [ ] On **both** legs the white piping arches from the waistband over the hip and runs down the front of the thigh to the knee, continuous and without flicker
- [ ] On **both** legs the second piping line curves down the outer lower leg to the hem
- [ ] The knee seam is visible
- [ ] The white italic "RCH" oval-swoosh logo is small, on her left hip, with no garbled letters
- [ ] The side slant pockets match the reference
- [ ] The tee is white, fitted, cropped at the waistband and has no logo
- [ ] The sneakers are clean and white
- [ ] Hands, fingers, the phone and the mirror reflection look physically correct
- [ ] The skin looks real, not airbrushed

Disclose AI-generated content using TikTok's AI-generated label, which TikTok
requires for realistic AI content.
