"""TikTok-style re-edit of the NYO3 Daily Probiotic handheld showcase clip.

Usage: python3 make_edit.py <original.mp4> <output.mp4>

Cuts the dead parts of the original (the slow white flash and fade to black),
adds punch-in zooms, flash cuts, a colour pop, pop-up text in Malay, whoosh/pop
sound effects and a "tekan beg kuning" call to action.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

YELLOW = (255, 214, 0, 255)
RED = (255, 45, 85, 255)
TEAL = (0, 200, 190, 255)
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

# (source start, source end) in seconds of the original clip.
SEGMENTS = [
    (0.00, 1.90),  # bottle drops into hand / flip  -> hook
    (2.20, 5.90),  # front label
    (7.70, 9.15),  # back: ingredients
    (10.20, 12.60),  # back: description + directions -> CTA
]


def emoji_img(ch, size):
    font = ImageFont.truetype(EMOJI, 109)
    img = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((0, 0), ch, font=font, embedded_color=True)
    img = img.crop(img.getbbox())
    return img.resize((size, int(size * img.height / img.width)), Image.LANCZOS)


def text_card(parts, size, fill=WHITE, box=None, stroke=10, pad=(34, 18),
              font=FONT, radius=26, emoji=None):
    """Render a single line of text, optionally on a rounded colour box."""
    f = ImageFont.truetype(font, size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = tmp.textbbox((0, 0), parts, font=f, stroke_width=0 if box else stroke)
    tw, th = r - l, b - t
    em = emoji_img(emoji, int(size * 1.05)) if emoji else None
    ew = em.width + 16 if em else 0
    cw, ch = tw + ew + pad[0] * 2, max(th, em.height if em else 0) + pad[1] * 2
    img = Image.new("RGBA", (cw + 20, ch + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if box:
        # drop shadow then box
        d.rounded_rectangle((14, 16, cw + 14, ch + 16), radius, fill=(0, 0, 0, 110))
        d.rounded_rectangle((6, 6, cw + 6, ch + 6), radius, fill=box)
        d.text((6 + pad[0] - l, 6 + (ch - th) // 2 - t), parts, font=f, fill=fill)
    else:
        d.text((6 + pad[0] - l, 6 + (ch - th) // 2 - t), parts, font=f, fill=fill,
               stroke_width=stroke, stroke_fill=BLACK)
    if em:
        img.alpha_composite(em, (6 + pad[0] + tw + 16, 6 + (ch - em.height) // 2))
    return img


def stack(cards, gap=14, align="center"):
    w = max(c.width for c in cards)
    h = sum(c.height for c in cards) + gap * (len(cards) - 1)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for c in cards:
        x = (w - c.width) // 2 if align == "center" else 0
        img.alpha_composite(c, (x, y))
        y += c.height + gap
    return img


def build_overlays(d):
    """Return a list of (png, out_start, out_end, x, y) overlays."""
    cut = [0.0]
    for s, e in SEGMENTS:
        cut.append(cut[-1] + (e - s))
    ov = []

    def add(img, name, t0, t1, x, y):
        p = os.path.join(d, name + ".png")
        img.save(p)
        if x == "c":
            x = (W - img.width) // 2
        ov.append((p, t0, t1, x, y))

    # 1. Hook
    add(text_card("PERUT SELALU", 92), "hook1", 0.05, cut[1], "c", 250)
    add(text_card("KEMBUNG?", 150, fill=YELLOW, emoji="\U0001F62B"), "hook2", 0.20, cut[1], "c", 370)
    add(text_card("jangan scroll dulu", 50, box=RED, font=FONT_BOLD, emoji="\U0001F447"),
        "hook3", 0.55, cut[1], "c", 580)

    # 2. Front label + key specs
    t = cut[1]
    add(text_card("NYO3 Daily Probiotic", 66, box=WHITE, fill=BLACK, emoji="\U0001F1F3\U0001F1F4"),
        "title", t + 0.05, cut[2], "c", 230)
    specs = [("57 BILION CFU", YELLOW, BLACK), ("7 STRAIN PROBIOTIK", TEAL, BLACK),
             ("60 KAPSUL", RED, WHITE)]
    for i, (s, bg, fg) in enumerate(specs):
        add(text_card(s, 54, box=bg, fill=fg), f"spec{i}", t + 0.6 + i * 0.55, cut[2],
            60, 400 + i * 118)

    # 3. Benefits (from the back label)
    t = cut[2]
    add(stack([text_card("Bantu kurangkan", 72),
               text_card("KEMBUNG & SEMBELIT", 84, fill=YELLOW)]), "benefit",
        t + 0.05, cut[3], "c", 230)

    # 4. Directions + CTA
    t = cut[3]
    add(text_card("1-2 kapsul sehari je", 70, box=WHITE, fill=BLACK, emoji="\U0001F48A"),
        "dose", t + 0.05, cut[4] - 1.1, "c", 250)
    add(stack([text_card("TEKAN BEG KUNING", 96, fill=YELLOW),
               text_card("sebelum stok habis!", 58, box=RED, font=FONT_BOLD, emoji="\U0001F6D2")]),
        "cta", cut[4] - 1.1, cut[4] + 1.0, "c", 260)
    return ov, cut


def zoom_expr(dur, punch):
    # quick punch-in at the cut that eases out, plus a slow push-in.
    p = f"{punch}*pow(max(0\\,1-t/0.28)\\,2)"
    return f"(1.04+{p}+0.07*t/{dur})"


def main(src, out):
    d = tempfile.mkdtemp()
    ovs, cut = build_overlays(d)
    total = cut[-1]

    inputs = ["-i", src]
    for p, *_ in ovs:
        inputs += ["-loop", "1", "-framerate", str(FPS), "-i", p]

    fc = []
    vlabels, alabels = [], []
    for i, (s, e) in enumerate(SEGMENTS):
        dur = e - s
        z = zoom_expr(dur, 0.0 if i == 0 else 0.22)
        fc.append(
            f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS,fps={FPS},"
            f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame,"
            f"crop={W}:{H},setsar=1[v{i}]")
        fc.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS[a{i}]")
        vlabels.append(f"[v{i}]")
        alabels.append(f"[a{i}]")
    fc.append(f"{''.join(vlabels)}concat=n={len(SEGMENTS)}:v=1:a=0[vc]")
    fc.append(f"{''.join(alabels)}concat=n={len(SEGMENTS)}:v=0:a=1[ac]")

    # colour pop + white flash on every cut + vignette
    flash = "+".join(f"between(t\\,{c:.3f}\\,{c + 0.07:.3f})" for c in cut[1:-1])
    fc.append(
        "[vc]eq=contrast=1.10:saturation=1.30:brightness=0.015:gamma=0.98,"
        "unsharp=5:5:0.6,vignette=PI/5,"
        f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.85:t=fill:enable='{flash}'[vg]")

    last = "vg"
    for k, (p, t0, t1, x, y) in enumerate(ovs, start=1):
        fade = f"fade=t=in:st={t0}:d=0.12:alpha=1"
        fc.append(f"[{k}:v]format=rgba,trim=0:{total},setpts=PTS-STARTPTS,{fade}[o{k}]")
        # slide up 40px while fading in
        ye = f"{y}+40*max(0\\,1-(t-{t0})/0.15)"
        fc.append(f"[{last}][o{k}]overlay=x={x}:y='{ye}':enable='between(t,{t0},{t1})'[l{k}]")
        last = f"l{k}"

    # SFX: whoosh on cuts, pop when text appears
    sfx = []
    for j, c in enumerate(cut[1:-1]):
        fc.append(
            f"anoisesrc=d=0.35:c=pink:a=0.9:r=44100,bandpass=f=1800:w=1600,"
            f"volume='0.9*sin(PI*t/0.35)':eval=frame,afade=t=out:st=0.2:d=0.15,"
            f"aformat=channel_layouts=stereo,adelay={int(max(0, c - 0.18) * 1000)}|"
            f"{int(max(0, c - 0.18) * 1000)}[w{j}]")
        sfx.append(f"[w{j}]")
    for k, (p, t0, *_rest) in enumerate(ovs):
        ms = int(t0 * 1000)
        fc.append(
            f"aevalsrc='0.35*sin(2*PI*(520+900*t)*t)*exp(-28*t)':d=0.12:s=44100,"
            f"aformat=channel_layouts=stereo,adelay={ms}|{ms}[p{k}]")
        sfx.append(f"[p{k}]")
    fc.append(f"[ac]volume=1.6[ao]")
    fc.append(f"[ao]{''.join(sfx)}amix=inputs={len(sfx) + 1}:normalize=0:duration=first,"
              f"alimiter=limit=0.95[aout]")

    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc),
           "-map", f"[{last}]", "-map", "[aout]", "-t", f"{total:.3f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(f"wrote {out} ({total:.2f}s)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
