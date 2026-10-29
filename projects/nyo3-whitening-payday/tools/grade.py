"""Colour grade: moves the blue/violet backdrop to a rose-plum tone while
leaving skin and the white packaging untouched."""
import numpy as np
from PIL import Image, ImageFilter

ROSE = np.array([255, 160, 196], np.float32)
W, H = 1080, 1920

_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((_xx - W * 0.5) / W) ** 2 + ((_yy - H * 0.38) / H) ** 2)
VIGNETTE = np.clip(1.0 - 0.55 * np.clip(_r - 0.25, 0, None) ** 1.4, 0.6, 1)[..., None]
GLOW = (np.exp(-(_r / 0.42) ** 2) * 0.10)[..., None] * np.array([255, 205, 220], np.float32)


def grade(frame):
    f = frame.astype(np.float32)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    blueness = (b - np.maximum(r, g)) / 255.0
    m = np.clip((blueness - 0.04) / 0.24, 0, 1)
    m = m * m * (3 - 2 * m)
    # protect the packaging: bright pixels keep their original (iridescent) colour
    m *= np.clip((165 - np.minimum(np.minimum(r, g), b)) / 45.0, 0, 1)
    v = np.clip(b / 255.0, 0, 1) ** 0.85
    tgt = v[..., None] * ROSE * 0.92 + 6
    f = f * (1 - m[..., None]) + tgt * m[..., None]
    # gentle lift + contrast, warm champagne bias in highlights
    f = (f / 255.0) ** 0.94 * 255.0
    f = (f - 128) * 1.06 + 132
    f[..., 0] *= 1.02
    f[..., 2] *= 0.985
    f = f * VIGNETTE + GLOW
    out = np.clip(f, 0, 255).astype(np.uint8)
    im = Image.fromarray(out).filter(ImageFilter.UnsharpMask(radius=2.2, percent=55, threshold=2))
    return np.asarray(im)


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        a = np.asarray(Image.open(p).convert("RGB"))
        Image.fromarray(np.hstack([a, grade(a)])).resize((1080, 960)).save(p.replace(".png", "_g.jpg"))
