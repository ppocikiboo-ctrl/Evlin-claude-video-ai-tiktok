# Sunset beach: grey crop tee + white pleated shorts (12.8 s, 9:16)

Edited from the original AI clip (13.25 s, 720x1280, two clips joined at 24 and 30 fps).

- **Video:** [`sunset_shorts_natural.mp4`](sunset_shorts_natural.mp4)
- **Teeth before and after:** [`teeth_before_after.jpg`](teeth_before_after.jpg) (left: original, right: fixed)

## Teeth fix

When her lips part (about 1.5–6.4 s), the AI teeth were blurry and broken by dark
gaps, so they looked gappy.

[`teeth_fix.py`](teeth_fix.py) runs on every frame:

1. MediaPipe Face Landmarker finds the inner-lip contour.
2. When the lips are open, it fills the mouth opening with one even row of upper
   teeth. The fill colour comes from her cheek skin under the sunset light, pushed
   toward ivory, and is smoothed over time so it does not flicker.
3. It adds soft shading: a slight shadow under the upper lip, a darker biting
   edge, darker mouth corners, and faint separations between the teeth.

Frames with closed lips are left untouched.

Run it with `python3 teeth_fix.py in_30fps.mp4 out.mp4 face_landmarker.task`.
The video must be constant 30 fps first, and the model comes from
https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task

## Removing the AI look

| AI tell in the original | Fix |
|---|---|
| A 0.5 s dissolve (6.43–6.93 s) where two faces overlap, like a ghost | Replaced it with a hard cut |
| Mixed 24 and 30 fps | Converted all of it to 30 fps |
| A perfectly smooth, cinematic camera | Light handheld shake |
| Too clean and too sharp | Slightly softer image plus fine moving grain |
| An oversaturated sunset | Saturation lowered by 12% |
| Generator metadata | Stripped by the re-encode |

The original audio is kept and cut at the same point as the video.

Before posting, turn on TikTok's **AI-generated content** label.
