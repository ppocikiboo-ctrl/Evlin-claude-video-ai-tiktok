# Baju kurung sage floral (T60057): mirror selfie (8 s, 9:16)

Edited from the original AI clip (Veo, 8 s, 720x1280, no audio).

- **Video:** [`kurung_sage_mirror_natural.mp4`](kurung_sage_mirror_natural.mp4)
- **Product reference:** [`reference/product-details-T60057.jpg`](reference/product-details-T60057.jpg)
- **Colour before and after:** [`colour-before-after.jpg`](colour-before-after.jpg) (left: original, right: edited)

## Matching the outfit to the product photo

| Detail | Product photo | AI video | Status |
|---|---|---|---|
| Fabric colour | Cool grey-sage | Warmer olive / yellow-green | **Fixed.** Only the green fabric pixels were shifted toward sage, slightly greyer and brighter ([`sage_colour_shift.py`](sage_colour_shift.py)). Skin, walls and the phone are unchanged |
| Print | Small white and blush-pink flowers with thin olive stems | Similar, slightly larger and pinker flowers | Close enough; left as is |
| Neckline | Small **stand (mandarin) collar** with piping, **piped V-shaped yoke seams**, a keyhole slit, and the **pearl button at the bottom of the slit** | Plain round neck with the pearl button at the top | **Not fixed.** Changing the cut of the garment needs a video generator; use the prompt below |
| Skirt waist | Shirred elastic waistband | Covered by the top | No change needed |
| Fabric finish | Soft crepe / chiffon with a slight sheen | Matte cotton look | Left as is |

## Removing the AI look

- Light handheld shake (about 3% zoom so the frame stays full)
- Slightly softer image plus fine moving grain, like phone sensor noise
- Saturation slightly lower, contrast slightly higher
- 30 fps instead of 24 fps
- Very quiet room tone in place of total silence (replace it with a trending sound in TikTok)
- Generator metadata stripped by the re-encode

## Prompt to regenerate with the correct neckline

Use image-to-video (Veo 3 / Kling 2.x). Upload a frame of this video as the first
frame and `reference/product-details-T60057.jpg` as the product reference.

```
Vertical 9:16 iPhone mirror selfie video in a bright modern bedroom, handheld,
natural daylight, real UGC look. A young Malaysian-Asian woman with long wavy
dark hair in a half-up bun holds a burgundy iPhone in front of her face. She
walks toward the mirror, turns sideways to show the fit, then touches the
neckline button.

She wears the EXACT baju kurung from the reference image: a soft grey-sage
crepe with a slight sheen and a dense print of small white and blush-pink
flowers with thin olive-green stems and leaves. The neckline has a small
stand-up mandarin collar edged with thin self-fabric piping. Two piped seams
run from the shoulders down in a V to the center chest. A short keyhole slit
runs down from the collar and closes with a single round pearl button at the
bottom of the slit. Long straight sleeves, a hip-length top, and a long
matching skirt.

Photorealistic, real skin texture, no beauty filter, no cinematic grading,
no slow motion.
```

Negative: `round neckline, collarless, pearl button at the top of the neck,
V-neck without collar, big flowers, olive or yellow-green fabric, cartoon,
CGI, plastic skin, extra fingers, watermark, text`

After generating, run the same edit again (colour shift if needed, then the
natural-look pass).

Before posting, turn on TikTok's **AI-generated content** label.
