"""Prepare cards, hook frames and synthesized whoosh SFX."""
import sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

U = "/root/.claude/uploads/878573dd-f1f2-5804-95d9-dddb669af68e/"
OUT = sys.argv[1]
SR = 44100
rng = np.random.default_rng(7)


def content(name):
    return Image.open(U + name).convert("RGB").crop((0, 428, 1600, 2028))


def card(name, out, size=400, radius=22, border=6):
    im = content(name).resize((size, size), Image.LANCZOS)
    full = size + border * 2
    pad = 24
    canvas = Image.new("RGBA", (full + pad * 2, full + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (pad, pad + 8, pad + full, pad + full + 8), radius + border, fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(shadow)
    frame = Image.new("RGBA", (full, full), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle((0, 0, full - 1, full - 1), radius + border, fill=(255, 255, 255, 255))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius, fill=255)
    frame.paste(im, (border, border), mask)
    canvas.alpha_composite(frame, (pad, pad))
    canvas.save(out)


def fullbleed(name, out):
    im = content(name)  # square 1600 -> fill 1080x1920
    im = im.resize((1920, 1920), Image.LANCZOS).crop((420, 0, 1500, 1920))
    im.save(out, quality=95)


def svf_noise(dur, f0, f1, f2, q=1.2, amp=1.0):
    """Band-passed noise whose centre frequency sweeps f0 -> f1 -> f2."""
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    fc = np.where(t < 0.5, f0 * (f1 / f0) ** (t / 0.5), f1 * (f2 / f1) ** ((t - 0.5) / 0.5))
    x = rng.standard_normal(n)
    low = band = 0.0
    y = np.empty(n)
    damp = 1.0 / q
    for i in range(n):
        f = 2 * np.sin(np.pi * fc[i] / SR)
        high = x[i] - low - damp * band
        band += f * high
        low += f * band
        y[i] = band
    env = np.sin(np.pi * t) ** 1.6
    y = y * env
    return amp * y / (np.abs(y).max() + 1e-9)


def stereo_pan(y, left_to_right=True):
    t = np.linspace(0, 1, len(y))
    p = t if left_to_right else 1 - t
    return np.stack([y * np.cos(p * np.pi / 2), y * np.sin(p * np.pi / 2)], 1)


def save(name, st, gain=0.9):
    st = st / (np.abs(st).max() + 1e-9) * gain
    data = (st * 32767).astype(np.int16)
    with wave.open(f"{OUT}/{name}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data.tobytes())


# Big "whoooosh" for the hook / section changes
save("whoosh_big", stereo_pan(svf_noise(0.75, 250, 2600, 600, q=1.0)
                              + 0.5 * svf_noise(0.75, 500, 5000, 1200, q=2.0)))
# Quick "wip" swish when a card slides in
save("wip_in", stereo_pan(svf_noise(0.32, 900, 6500, 3000, q=1.6), True), 0.8)
# Softer "whoop" when a card slides out
save("whoop_out", stereo_pan(svf_noise(0.28, 4000, 1500, 500, q=1.4), False), 0.6)
# Little pop for the hook text
n = int(0.12 * SR); t = np.arange(n) / SR
pop = np.sin(2 * np.pi * (600 * t + 9000 * t * t)) * np.exp(-t * 35)
save("pop", np.stack([pop, pop], 1), 0.7)

cards = {
    "c_soap5": "a0f6c496-image.jpg",
    "c_layers": "04dd1f5b-image.jpg",
    "c_why": "b153f49c-image.jpg",
    "c_foamfine": "93b8d2a1-image.jpg",
    "c_foam3s": "6a18ff34-image.jpg",
}
for k, v in cards.items():
    card(v, f"{OUT}/{k}.png")
fullbleed("6a18ff34-image.jpg", f"{OUT}/hook_foam.jpg")
fullbleed("93b8d2a1-image.jpg", f"{OUT}/hook_foam2.jpg")
print("done")
