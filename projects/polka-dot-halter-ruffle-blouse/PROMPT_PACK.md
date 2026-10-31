# Polka Dot Halter Ruffle Blouse — TikTok Mirror Selfie OOTD (8s, 9:16, silent)

Ultra-realistic TikTok affiliate video: the woman from the reference mirror
selfie films a casual OOTD in her bedroom mirror, modelling the cream-white
polka dot halter blouse with tiered ruffles. Front, ruffle detail, back view,
final pose. No audio.

**References (attach all three in the video tool):**

| File | Role |
|---|---|
| [`reference/model-mirror-selfie.png`](reference/model-mirror-selfie.png) | Model, outfit, phone, bedroom. Use as the **first frame / start image** |
| [`reference/product-front.jpg`](reference/product-front.jpg) | Blouse front: neckline gathers, ruffle tiers, hem finish |
| [`reference/product-back.jpg`](reference/product-back.jpg) | Blouse back: neck bow, open upper back, smocked panel, peplum |

> Only use the model photo if it is you, or if the person in it has agreed to
> appear in an AI-generated ad. TikTok also requires the AI-generated content
> label on realistic AI videos.

---

## 0. Read first: three problems in the references

These three things make the generated clip fail if you don't deal with them
before you prompt.

1. **The bow is in two different places.** In the mirror selfie the big bow is
   tied **at the front of the throat**. In the back product photo the ties make
   a bow **at the back of the neck**, with long tails hanging down the spine.
   The ties can be done either way, but one video can only show one. If you
   don't choose, the model makes the bow jump between front and back
   mid-turn.
   - **Option A (recommended, matches the back photo):** first edit the
     selfie so the bow is at the back of the neck (Prompt A below). The front
     neckline then becomes the gathered halter band from the front product
     photo.
   - **Option B (no edit, matches the selfie):** keep the bow at the front.
     In the back view, the plain halter ties run around the neck and there
     is **no** bow at the back. Use the Option B lines marked below.
2. **Her hair covers the whole back.** Her half-up hair falls to her waist and
   would hide the smocking and the bow. The action script has her sweep her
   hair over one shoulder before she turns. Don't drop that step.
3. **The shoulder bag strap crosses her back.** The black bag on her shoulder
   would cover part of the smocked panel and look messy in the turn. Remove
   it in the keyframe (Prompt A does this), or at least expect the strap
   in the back view.

Also:
- Video models don't know an "iPhone 18". Describe what the photo shows: **a
  burgundy / deep wine-red iPhone with a matching glossy case and a triple
  camera**. That keeps the colour stable.
- The phone covers most of her face in the selfie. Keep it that way the whole
  time. It is realistic, and it is the easiest way to keep her identity stable
  through the turn.

---

## 1. Product details (from the three reference images)

| Feature | What the references show |
|---|---|
| Fabric | Sheer, lightweight cream / off-white chiffon (slightly crinkled georgette look), soft drape, a little see-through on the lower tiers |
| Print | Small, evenly spaced black pin dots across the whole blouse, including the ties |
| Neckline | Halter. Fabric is gathered tightly into a narrow band at the neck and fans out in soft vertical folds |
| Neck ties | Long chiffon ties of the same dotted fabric. In the back photo: a large soft bow at the nape, two long tails hanging to mid-back |
| Front | A long draped panel from the neck falls into **three cascading ruffle tiers**. The tiers are uneven and asymmetric, flowing more to one side |
| Hem finish | Narrow white rolled / merrow edge on every ruffle, slightly wavy (lettuce look) |
| Waist | Elastic shirring at the natural waist in the front, so the top cinches, then flares |
| Sides / shoulders | Cut-in halter armholes. Shoulders and arms bare |
| Back | Open upper back (bare skin between the shoulder blades). Below it, a **wide panel of horizontal elastic smocking (shirring)** across the mid-back, then a gathered peplum ruffle to the hem |
| Length | Ends at the high hip, overlapping the top of the skirt by a few cm |
| Fit | Fitted through the smocked waist, loose and floaty above and below |

Outfit and scene from the mirror selfie (keep these unchanged):

| Item | Detail |
|---|---|
| Hair | Very long dark-brown hair, half-up with a small messy bun on top, loose waves to the waist |
| Skirt | Black pleated mini skirt, knife pleats, matte cotton twill |
| Shoes | Chunky white platform sneakers, white crew socks |
| Jewellery | Thin silver chain bracelet on the wrist of her free hand |
| Nails | Long almond nails, nude-pink |
| Phone | Burgundy iPhone in a matching glossy case, triple camera, held up in front of her face |
| Room | Beige floor-to-ceiling wardrobe on the left, dark-wood door with a silver lever handle on the right, white quilted bed, grey velvet bench edge, light glossy tile floor, beige shag rug corner, grey frame of the full-length mirror visible at the edges |
| Light | Soft warm indoor ceiling light, even exposure |

---

## 2. Recommended workflow

Video models keep clothing much more accurate when they animate a correct
still than when they invent the clothes from text.

1. **Prepare the start frame.**
   - Option A: edit the mirror selfie with Prompt A in an image editor that
     takes reference images (Nano Banana / Gemini image, GPT-image, Flux
     Kontext, Seedream). Give it all three images. Make 4–6 versions and keep
     the one where the blouse matches the product photos best.
   - Option B: use the mirror selfie as it is.
2. **Animate.** Use an image-to-video tool that can do 8 s:
   - **Veo 3 / 3.1:** 8 s clips natively, so the best fit. It adds sound by
     default, so strip it afterwards (step 3).
   - **Kling 2.x:** 5 s or 10 s. Generate 10 s and trim to 8 s.
   - Runway Gen-4, Hailuo, Sora: use the start frame + Prompt B, and cut to 8 s.

   Add `product-back.jpg` as an extra reference image if the tool allows it
   (Kling "elements", Veo "ingredients", Runway references). That is what makes
   the back view right.
3. **Make it silent.** Most tools can't output a clip with no audio track.
   Remove it after download:

   ```bash
   ffmpeg -i input.mp4 -an -c:v copy -t 8 ootd_silent.mp4
   ```

   (`-an` drops the audio track, `-t 8` cuts to exactly 8 s, and
   `-c:v copy` leaves the video untouched.) CapCut: tap the clip, then
   **Volume → 0**, or **Extract audio → delete**.
4. **If the turn breaks** (bow jumps, smocking melts, arm twists), use the
   fallback in section 5.

---

## 3. Prompt A — start-frame edit (Option A only)

```
Edit the first image (mirror selfie). Keep everything the same: the same
woman, face, skin, body, pose, hair, the burgundy iPhone held in front of her
face, the black pleated mini skirt, white crew socks, chunky white platform
sneakers, silver bracelet, bedroom, mirror, lighting and camera angle.

Change only these things:
1. The blouse must exactly match the product reference images: sheer
   cream-white chiffon with small evenly spaced black pin dots, a halter
   neckline gathered into a narrow band at the neck, a long draped front panel
   falling into three uneven cascading ruffle tiers with narrow white rolled
   edges, elastic shirring at the waist, cut-in halter armholes, ending at the
   high hip over the top of the skirt.
2. There is NO bow at the front of the throat. The halter ties go around the
   neck and are tied in a soft bow at the back of the neck (not visible from
   the front, except perhaps the tip of a tie tail behind her shoulder).
3. Remove the black shoulder bag and its strap.

Photorealistic, real phone photo quality, real skin texture, no smoothing.
```

---

## 4. Prompt B — video (8 s, 9:16, silent)

Paste this as one block. The time markers help Veo and Kling keep the order of
the actions.

```
8-second vertical 9:16 video, one continuous shot. An authentic TikTok OOTD
mirror selfie recorded on a phone in a bedroom. It looks like real
user-generated content, not an advert: handheld, mostly steady, with very
slight natural hand movement, phone auto-exposure, soft warm indoor ceiling
light. No cuts, no zoom, no camera moves other than her hand. No music, no
voice, no sound.

Start exactly from the first frame. The same woman as in the reference: very
long dark-brown wavy hair, half-up with a small bun on top, slim, natural
proportions, real skin texture. She holds a burgundy iPhone with a matching
glossy case and a triple camera in front of her face the whole time, so her
face stays mostly hidden behind the phone. She wears the black pleated mini
skirt, white crew socks and chunky white platform sneakers from the
reference, and a thin silver bracelet.

THE BLOUSE must match the product reference images exactly in every frame:
sheer, lightweight cream-white chiffon with small evenly spaced black pin
dots; a halter neckline gathered into a narrow band at the neck; a long
draped front panel falling into three uneven cascading ruffle tiers with
narrow white rolled, slightly wavy edges; elastic shirring at the waist; bare
shoulders. The back: open upper back with bare skin, a halter bow tied at the
back of the neck with two long dotted tails hanging down, a wide horizontally
smocked elastic panel across the mid-back, and a gathered peplum ruffle below
it. The dots stay small, black and evenly spaced; the ruffles keep their
number and shape.

0–2 s: She stands relaxed in front of the full-length mirror, weight on one
leg. With her free hand she lightly fluffs the lowest ruffle tier, then lets
it fall. Small natural sway, subtle breathing. The front of the blouse is
fully visible.

2–4 s: She shifts her weight to the other leg and turns her upper body
slightly to one side, so the side silhouette and the cinched waist show. Her
fingertips lift the edge of a ruffle tier a little and let it go; the light
chiffon floats and settles. Then she sweeps her long hair over her front
shoulder with her free hand, clearing her back.

4–6 s: She turns slowly around to show her back to the mirror, keeping the
phone raised over her shoulder and pointed at the mirror, looking back toward
the phone. The mirror clearly shows the bow at the back of her neck with its
long tails, the bare upper back, the smocked elastic panel and the peplum
ruffle. Her shoulders and arms move naturally; the arm with the phone bends
comfortably over her shoulder.

6–8 s: She turns back to a relaxed three-quarter front pose, phone in front
of her face again. She smooths the front ruffles once with her free hand, the
tiers settle, and she ends in a casual, confident OOTD pose with the blouse
clearly visible in the final frame.

Background stays identical the whole time: beige floor-to-ceiling wardrobe on
the left, dark-wood door with a silver lever handle on the right, white quilted
bed, light glossy tiled floor with soft reflections, grey mirror frame at the
edges. The reflection in the mirror is physically correct.

Photorealistic, real chiffon physics: sheer, light, floaty, moving a moment
after her body moves. Real hair movement. No beauty filter, no slow motion,
no cinematic grading, no text, no subtitles, no watermark.
```

**Option B (bow at the front):** make three changes to the prompt.
- In THE BLOUSE paragraph, replace `a halter bow tied at the back of the neck
  with two long dotted tails hanging down` with `the plain dotted halter ties
  running around the back of the neck, with no bow at the back`. Then add
  `a large soft dotted chiffon bow tied at the front of the throat` to the
  front description.
- In 4–6 s, replace `the bow at the back of her neck with its long tails` with
  `the halter ties around the back of her neck`.
- Add `bow at the back of the neck` to the negative prompt.

### Negative prompt

```
cartoon, CGI, 3D render, AI look, plastic skin, airbrushed, beauty filter,
doll face, changing face, different woman, extra fingers, distorted hands,
twisted arms, broken wrist, unnatural body twist, rubbery limbs, extra limbs,
distorted phone, phone changing colour, black phone, silver phone, white
phone, floating phone, phone disappearing, warped mirror, mirror reflection
mismatch, second person, opaque fabric, thick fabric, satin, white blouse
without dots, large polka dots, red dots, missing dots, dots changing size,
stripes, flowers, missing ruffles, extra ruffle tiers, flat blouse,
off-shoulder top, sleeves, straps, closed back, missing smocking, plain back,
missing neck bow, bow jumping between front and back, blouse changing during
turn, hair covering the back, shoulder bag, long skirt, jeans, shorts, heels,
black shoes, background change, new furniture, flickering, morphing, jump cut,
scene transition, zoom, camera rotation, slow motion, cinematic colour grade,
text, subtitles, captions, watermark, logo, music, voice, sound effects
```

---

## 5. Fallback if the 180° turn breaks

A full turn in 2 s, while holding a phone at a mirror, is where video models
fail most often (the arm twists, the bow jumps, the smocking turns to mush).
If 3–4 generations all fail:

- **Quarter-turn version:** in the 4–6 s block, replace the turn with: `She
  turns her body about 135 degrees away from the mirror and looks back over
  her shoulder, so the mirror shows her back at an angle: the neck bow, the
  bare upper back and the smocked panel.` This is easier to anatomise and still
  shows the back.
- **Two clips:** make clip 1 (0–4 s, front + details) from the start frame.
  Then make a separate back-view still with Prompt A, using `product-back.jpg`
  for the back, and animate it as clip 2 (back view, turning to the front).
  Join them in CapCut with a hard cut on the turn. TikTok mirror videos often
  cut on a spin, so it still looks natural.

---

## 6. Shot list

| # | Time | Action | What it must show |
|---|------|--------|-------------------|
| 1 | 0–2 s | Relaxed front pose, fluffs the lowest ruffle | Full front: halter neck, three ruffle tiers, the dots |
| 2 | 2–4 s | Weight shift, side turn, lifts a ruffle edge, sweeps hair forward | Silhouette, cinched waist, sheer floaty fabric |
| 3 | 4–6 s | Turns her back to the mirror, phone over her shoulder | Neck bow + tails, open upper back, smocked panel, peplum |
| 4 | 6–8 s | Turns back to three-quarter, smooths the ruffles, final pose | Blouse clearly visible in the final frame |

---

## 7. TikTok post package

The video itself is silent. TikTok affiliate posts still need a sound, so add
one in the TikTok app from the **Commercial Music Library**, or post it with
the volume at 0.

**On-screen text (add in CapCut / TikTok, not in the AI prompt):**

- 0–2 s: `Blouse polka dot paling comel 🤍🖤`
- 4–6 s: `Belakang smocked + ikat reben 🎀`
- 6–8 s: `Link kat beg kuning 👇`

**Caption:**

```
Top polka dot halter ni cantik sangat 🤍 Ruffle berlapis depan, belakang
smocked getah + ikat reben — padan dengan skirt pleated hitam & sneakers
putih. Tekan beg kuning untuk beli! 🛒

#ootd #polkadot #halterneck #ruffletop #ootdmalaysia #koreanstyle
#tiktokshopmalaysia #fyp
```

---

## 8. Product-accuracy QA checklist

Check every clip frame by frame before you post:

- [ ] The blouse is cream-white, sheer chiffon, not opaque or satin
- [ ] The dots are small, black and evenly spaced in every frame, including the ties
- [ ] The halter neckline is gathered into a narrow band; shoulders are bare
- [ ] Three uneven ruffle tiers at the front, with narrow white rolled edges
- [ ] Elastic shirring cinches the waist
- [ ] The bow is in **one** place for the whole clip (back for Option A, front for Option B)
- [ ] Back view: open upper back, wide horizontal smocked panel, peplum ruffle
- [ ] Her hair is swept aside so the back is visible during the turn
- [ ] The blouse doesn't change shape, length or ruffle count during the turn
- [ ] The phone stays burgundy with a triple camera, and stays in front of her face
- [ ] Hands, fingers, arms and the mirror reflection look physically correct
- [ ] The skirt is a black pleated mini; the shoes are chunky white sneakers with white socks
- [ ] The bedroom doesn't change: wardrobe, door, bed, floor
- [ ] Exactly 8 s, 9:16, **no audio track** (check: `ffprobe ootd_silent.mp4` lists only a video stream)
- [ ] The skin looks real, not airbrushed
