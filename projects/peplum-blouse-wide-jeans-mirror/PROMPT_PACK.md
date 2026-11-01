# Polka-dot peplum blouse + wide-leg jeans: mirror selfie OOTD (8 s, 9:16)

**Keyframe / reference:** [`reference/keyframe.png`](reference/keyframe.png)

## How to use

- **Tool:** image-to-video (Veo 3, Kling 2.x, Hailuo, Runway Gen-4).
- **First frame:** upload `reference/keyframe.png`.
- **Settings:** 8 s, 9:16, audio **off** (in Veo, also put "silent" in the prompt
  because Veo adds sound by default).
- **Takes:** generate 3–4 and keep the one where the jeans, hands and phone stay
  correct.

The original prompt says "bedroom windows", but the image shows a bright
minimalist room, not a bedroom. A mismatch like this makes the model change the
background, so the prompt below describes the room as it really is.

## Prompt

```
Ultra-realistic 8-second vertical 9:16 mirror selfie OOTD video, animated
from the reference image. Authentic handheld iPhone footage at 30fps with
very slight natural hand shake. Same framing as the reference: full body,
head to shoes, the camera is the phone in her hand.

Scene (unchanged from the reference): a bright, minimalist white room with a
tall white wall panel and a large white board leaning behind her, tall
windows on both sides showing green trees and city buildings, a white floor
lamp on the left, a potted bird-of-paradise plant in a white pot on the
right, a light oak wooden floor. Warm natural sunlight from the windows
casts soft leaf shadows on the wall and floor.

Subject (unchanged from the reference): a slim woman in a black hijab. She
holds a dark burgundy iPhone in front of her face with one hand and wears a
rose-gold watch on that wrist. She wears a white chiffon blouse with tiny
black polka dots, a gathered round neckline, long balloon sleeves with
smocked cuffs, a smocked elastic waist and a two-tier ruffled peplum. A
small black shoulder bag hangs from her shoulder on the left side of the
frame. She wears high-rise, wide-leg, full-length jeans in a light-to-medium
faded blue wash with subtle whiskering and vertical fading, the hems
reaching the floor, and white pointed-toe shoes.

Action, in one continuous shot:
0–3 s: she takes two slow, small, natural steps toward the mirror, and the
wide jean legs swing softly with each step.
3–5.5 s: with her free hand she gently brushes down the front of her thigh
over the jeans, and the denim creases and settles.
5.5–8 s: she turns her body about 30 degrees to the side so the sunlight
rakes across the jeans, showing the denim texture, side seam stitching, the
faded wash and the fabric folds, then she holds the pose.

The phone stays in front of her face for the entire video; her face is never
visible. The mirror reflection stays stable and consistent. The jeans keep
exactly the same colour, wash, wide-leg cut, high rise and full length in
every frame. The blouse, hijab, bag, watch and shoes stay exactly the same.
Realistic body proportions, natural walking weight shift and real fabric
physics.

Real smartphone image quality: natural exposure, true colours, slight
sensor grain. No cinematic grading, no slow motion, no zoom, no camera cuts.

Completely silent video: no audio, music, dialogue, voice-over or sound
effects.
```

## Negative prompt

```
face visible, phone lowered, phone moving away from face, second person,
changed background, bedroom, bed, changing lighting, skinny jeans, straight
or tapered jeans, cropped jeans, ripped jeans, dark indigo jeans, black
jeans, different denim wash, jeans changing colour, shorts, skirt, blouse
changing pattern, large polka dots, missing ruffles, removed bag, sneakers,
extra fingers, deformed hands, fused fingers, floating phone, warped mirror,
body distortion, elongated legs, sliding feet, morphing, flicker, zoom,
camera cut, slow motion, cinematic, CGI, 3D render, plastic skin, cartoon,
text, subtitles, watermark, music, audio
```

## QA before posting

- [ ] The phone covers her face in every frame
- [ ] The jeans keep the same light faded wash, wide leg, high rise and floor length
- [ ] The free hand that brushes the jeans has five normal fingers, with no fusing
- [ ] The feet step forward and never slide
- [ ] The bag, watch and polka-dot ruffled blouse stay the same throughout
- [ ] The windows, plant, lamp and leaning board do not move or morph
- [ ] There is no audio track (or the audio is silent)

After generating, run the natural-look pass (light handheld shake, grain,
30 fps, metadata strip) the same way as the other clips, and turn on TikTok's
**AI-generated content** label.
