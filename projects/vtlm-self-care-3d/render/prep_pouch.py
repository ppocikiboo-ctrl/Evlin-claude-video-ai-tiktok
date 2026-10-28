"""Cut the real VTLM pouch out of the reference video frame.

Removes the background (rembg / u2net), straightens the pouch, replaces the
thumb in the lower-left corner with the mirrored right side of the pouch and
trims the outline to a clean rounded rectangle. The printed front (gold VTLM
wordmark and tagline) is never redrawn.

    python3 prep_pouch.py <frame.jpg> assets/vtlm_pouch.png

The frame used is the reference video at 3.5s:
    ffmpeg -ss 3.5 -i reference.mp4 -frames:v 1 -q:v 2 frame.jpg
"""
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw
from rembg import new_session, remove

# Pouch corners in the 1080x1920 frame at 3.5s (TL, TR, BR, BL), measured
# from the minimum-area rectangle of the lavender pixels.
CORNERS = [[267.5, 601.6], [860.7, 620.8], [834.3, 1440.4], [241.1, 1421.3]]
OUT_W, OUT_H = 600, 830


def main(src, dst):
    cut = np.array(remove(Image.open(src), session=new_session("u2net")))
    m = cv2.getPerspectiveTransform(
        np.float32(CORNERS), np.float32([[0, 0], [OUT_W, 0], [OUT_W, OUT_H], [0, OUT_H]]))
    w = cv2.warpPerspective(cut, m, (OUT_W, OUT_H), flags=cv2.INTER_CUBIC).astype(np.float32)

    hsv = cv2.cvtColor(w[..., :3].astype(np.uint8), cv2.COLOR_RGB2HSV)
    h = hsv[..., 0].astype(int)
    skin = (((h < 28) | (h > 168)) | (w[..., 3] < 128)).astype(np.uint8)
    zone = np.zeros_like(skin)
    zone[480:, :260] = 1  # the thumb only covers the lower-left corner
    skin = cv2.dilate(skin * zone, np.ones((25, 25), np.uint8))
    blend = cv2.GaussianBlur(skin.astype(np.float32), (0, 0), 8)[..., None]
    rgb = w[..., :3] * (1 - blend) + w[:, ::-1, :3] * blend
    # Edge pixels rembg left transparent are dark; fill them from the pouch.
    edge = ((w[..., 3] < 230) & (blend[..., 0] < 0.5)).astype(np.uint8)
    edge = cv2.dilate(edge, np.ones((5, 5), np.uint8))
    rgb = cv2.inpaint(rgb.clip(0, 255).astype(np.uint8), edge, 7, cv2.INPAINT_TELEA).astype(np.float32)

    ss = 4
    alpha = Image.new("L", (OUT_W * ss, OUT_H * ss), 0)
    ImageDraw.Draw(alpha).rounded_rectangle(
        [8 * ss, 8 * ss, (OUT_W - 9) * ss, (OUT_H - 9) * ss], radius=30 * ss, fill=255)
    alpha = np.array(alpha.resize((OUT_W, OUT_H), Image.LANCZOS)).astype(np.float32)
    # Follow the real outline where rembg found it (the warp is not exact).
    found = w[..., 3] * (1 - blend[..., 0]) + w[:, ::-1, 3] * blend[..., 0]
    found = cv2.erode((found > 128).astype(np.uint8) * 255, np.ones((7, 7), np.uint8))
    found = cv2.GaussianBlur(found.astype(np.float32), (0, 0), 1.2)
    alpha = np.minimum(alpha, found)
    Image.fromarray(np.dstack([rgb, alpha]).clip(0, 255).astype(np.uint8)).save(dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
