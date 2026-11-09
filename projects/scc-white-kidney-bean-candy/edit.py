#!/usr/bin/env python3
"""Edit the SCC White Kidney Bean candy talking video for TikTok.

What it does:
  * cuts the long pauses (found with ffmpeg silencedetect) and speeds speech up 1.15x
  * jump-cut punch-in zooms, light colour grade, white flash on each cut
  * hook, benefit pills, buyer-review cards, soft "kiasan" conclusion, CTA,
    disclaimer and a progress bar, all rendered as PNG overlays with Pillow

Usage: python3 edit.py <input.mp4> <output.mp4>
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
W, H, FPS = 1080, 1920, 30
SPEED = 1.15

# Speech kept from the source (seconds), padded around the silences.
# The first long take is split in two only to give it a second punch-in.
SEGMENTS = [(0.43, 7.00), (7.00, 14.47), (17.11, 19.89), (20.29, 22.78),
            (23.22, 27.77), (29.61, 33.09), (33.65, 35.57)]
ZOOMS = [1.00, 1.10, 1.00, 1.12, 1.00, 1.10, 1.04]

PINK = (233, 30, 99)
DEEP = (120, 20, 70)
WHITE = (255, 255, 255)
YELLOW = (255, 214, 0)


def font(path, size):
    return ImageFont.truetype(path, size)


def text_card(lines, size=78, fg=WHITE, bg=PINK, pad=(44, 26), radius=36,
              highlight=None, fpath=FONT_BLACK, max_w=980):
    """Rounded card with centred multi-line text. `highlight` = word drawn yellow."""
    f = font(fpath, size)
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    sizes = [d.textbbox((0, 0), ln, font=f) for ln in lines]
    lw = [b[2] - b[0] for b in sizes]
    lh = int(size * 1.22)
    cw = min(max(lw) + pad[0] * 2, max_w + pad[0] * 2)
    ch = lh * len(lines) + pad[1] * 2
    img = Image.new("RGBA", (cw + 40, ch + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((24, 28, cw + 16, ch + 20), radius, fill=(0, 0, 0, 110))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(10)))
    dr = ImageDraw.Draw(img)
    if bg is not None:
        dr.rounded_rectangle((20, 20, cw + 20, ch + 20), radius, fill=bg + (255,))
    y = 20 + pad[1]
    for ln, w in zip(lines, lw):
        x = 20 + (cw - w) // 2
        if highlight and highlight in ln:
            pre, post = ln.split(highlight, 1)
            for part, col in ((pre, fg), (highlight, YELLOW), (post, fg)):
                dr.text((x, y), part, font=f, fill=col, stroke_width=0 if bg else 6,
                        stroke_fill=(0, 0, 0))
                x += dr.textlength(part, font=f)
        else:
            dr.text((x, y), ln, font=f, fill=fg, stroke_width=0 if bg else 6,
                    stroke_fill=(0, 0, 0))
        y += lh
    return img


def review_card(path, crop_top=0, crop_bottom=0, label="REVIEW SEBENAR PEMBELI"):
    src = Image.open(path).convert("RGB")
    src = src.crop((0, crop_top, src.width, src.height - crop_bottom))
    tw = 940
    src = src.resize((tw, int(src.height * tw / src.width)), Image.LANCZOS)
    hf = font(FONT_BLACK, 40)
    head_h = 78
    cw, ch = tw + 40, src.height + head_h + 40
    img = Image.new("RGBA", (cw + 40, ch + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((24, 30, cw + 16, ch + 22), 34, fill=(0, 0, 0, 120))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(12)))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle((20, 20, cw + 20, ch + 20), 34, fill=WHITE + (255,))
    dr.rounded_rectangle((20, 20, cw + 20, 20 + head_h), 34, fill=PINK + (255,))
    dr.rectangle((20, 20 + head_h - 34, cw + 20, 20 + head_h), fill=PINK + (255,))
    tl = dr.textlength(label, font=hf)
    stars_w = 5 * 40
    x0 = 20 + (cw - tl - stars_w - 20) / 2
    dr.text((x0, 38), label, font=hf, fill=WHITE)
    sx = x0 + tl + 20
    for i in range(5):  # draw stars as polygons (no emoji font needed)
        cx, cy, r = sx + 20 + i * 40, 59, 17
        import math
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.45
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        dr.polygon(pts, fill=YELLOW)
    img.paste(src, (40, 20 + head_h + 20))
    return img


def progress_bar():
    img = Image.new("RGBA", (W, 14), PINK + (255,))
    return img


def build_overlays(tmp):
    """Returns list of (png, start, end, x, y, anim) on the FINAL timeline."""
    ov = []

    def add(name, img, t0, t1, y, x=None, anim="up"):
        p = os.path.join(tmp, name + ".png")
        img.save(p)
        ov.append((p, t0, t1, (W - img.width) // 2 if x is None else x, y, anim))

    # HOOK — craving + baju baru
    add("hook1", text_card(["Craving tengah malam", "tak boleh tahan?"], size=82,
                           highlight="Craving"), 0.0, 3.0, 230, anim="pop")
    add("hook2", text_card(["Baju baru dah beli...", "tapi zip tak naik?"], size=82,
                           bg=DEEP, highlight="zip tak naik?"), 3.0, 6.2, 230, anim="pop")
    add("hook_sub", text_card(["Tengok ni dulu sebelum scroll"], size=46, bg=None),
        0.3, 6.2, 1560, anim="up")
    # product + benefits
    add("prod", text_card(["SCC White Kidney Bean", "+ L-Carnitine Candy"], size=54,
                          fg=DEEP, bg=WHITE), 6.2, 10.6, 200, anim="pop")
    add("pill1", text_card(["Bantu kawal selera"], size=56, bg=PINK), 6.6, 10.6, 1420, anim="left")
    add("pill2", text_card(["1/2 tablet sehari je"], size=56, bg=DEEP), 7.4, 10.6, 1560, anim="left")
    # real reviews
    add("rev1", review_card(os.path.join(HERE, "reference/review-1.jpg"), crop_bottom=30), 10.6, 14.2, 170, anim="up")
    add("rev2", review_card(os.path.join(HERE, "reference/review-2.jpg"), crop_top=110,
                            label="DAH BELI KALI KE-5"), 14.2, 17.4, 170, anim="up")
    # soft / figurative conclusion
    add("kias1", text_card(["Bila selera dah 'jinak'...", "pinggang pun ikut 'senyap'"],
                           size=66, highlight="'jinak'"), 17.4, 20.8, 230, anim="pop")
    add("kias2", text_card(["Baju lama terasa longgar,", "baju baru pun berani pakai"],
                           size=66, bg=DEEP, highlight="longgar,"), 20.8, 23.8, 230, anim="pop")
    # CTA
    add("cta", text_card(["KLIK BEG KUNING", "& cuba sendiri!"], size=86, fg=(30, 30, 30),
                         bg=YELLOW), 23.8, 99, 230, anim="pop")
    add("cta_sub", text_card(["Jom mula jaga selera hari ini"], size=44, bg=None),
        24.0, 99, 1540, anim="up")
    add("disc", text_card(["Hasil berbeza mengikut individu.", "Amalkan pemakanan seimbang & minum air secukupnya."],
                          size=28, bg=(0, 0, 0), fpath=FONT_BOLD, pad=(22, 10), radius=16),
        17.4, 99, 1730, anim="none")
    return ov


def main(src, out):
    tmp = tempfile.mkdtemp()
    final_len = sum(b - a for a, b in SEGMENTS) / SPEED
    ov = build_overlays(tmp)
    bar = os.path.join(tmp, "bar.png")
    progress_bar().save(bar)

    inputs = ["-i", src]
    fc = []
    # 1) cut + jump-zoom + grade per segment
    cut_times = []
    acc = 0.0
    for i, ((a, b), z) in enumerate(zip(SEGMENTS, ZOOMS)):
        cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
        fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,crop={cw}:{ch}:(iw-{cw})/2:(ih-{ch})/2,"
                  f"scale={W}:{H},setsar=1[v{i}]")
        fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d=0.02,afade=t=out:st={b - a - 0.03:.3f}:d=0.03[a{i}]")
        cut_times.append(acc / SPEED)
        acc += b - a
    n = len(SEGMENTS)
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    flash = "+".join(f"between(t,{t:.3f},{t + 0.08:.3f})" for t in cut_times[1:])
    fc.append(f"[vc]setpts=PTS/{SPEED},fps={FPS},"
              f"eq=contrast=1.06:saturation=1.18:brightness=0.02:gamma=0.98,"
              f"unsharp=5:5:0.6,vignette=PI/6,"
              f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.55:t=fill:enable='{flash}'[v_base]")
    fc.append(f"[ac]atempo={SPEED},loudnorm=I=-14:TP=-1.5:LRA=11[aout]")

    # 2) overlays
    last = "v_base"
    for k, (png, t0, t1, x, y, anim) in enumerate(ov):
        t1 = min(t1, final_len)
        d = t1 - t0
        idx = k + 1
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", png]
        fade = f"fade=t=in:st=0:d=0.2:alpha=1,fade=t=out:st={max(d - 0.2, 0):.3f}:d=0.2:alpha=1"
        if t1 >= final_len - 0.01:
            fade = "fade=t=in:st=0:d=0.2:alpha=1"
        if anim == "pop":  # scale-in pop
            fc.append(f"[{idx}:v]format=rgba,{fade},setpts=PTS-STARTPTS+{t0}/TB[o{k}]")
            ye = f"{y}-40*max(0\\,1-(t-{t0})/0.18)*sin(PI*min(1\\,(t-{t0})/0.18))"
            xe = f"{x}"
        elif anim == "left":
            fc.append(f"[{idx}:v]format=rgba,{fade},setpts=PTS-STARTPTS+{t0}/TB[o{k}]")
            xe = f"{x}-300*max(0\\,1-(t-{t0})/0.25)"
            ye = f"{y}"
        elif anim == "up":
            fc.append(f"[{idx}:v]format=rgba,{fade},setpts=PTS-STARTPTS+{t0}/TB[o{k}]")
            xe = f"{x}"
            ye = f"{y}+90*max(0\\,1-(t-{t0})/0.25)"
        else:
            fc.append(f"[{idx}:v]format=rgba,{fade},setpts=PTS-STARTPTS+{t0}/TB[o{k}]")
            xe, ye = f"{x}", f"{y}"
        fc.append(f"[{last}][o{k}]overlay=x='{xe}':y='{ye}':eof_action=pass:"
                  f"enable='between(t,{t0},{t1})'[l{k}]")
        last = f"l{k}"
    # 3) progress bar
    inputs += ["-loop", "1", "-framerate", str(FPS), "-i", bar]
    fc.append(f"[{last}][{len(ov) + 1}:v]overlay=x='-W+W*t/{final_len:.3f}':y=H-14:shortest=1,"
              f"format=yuv420p[vout]")

    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc),
           "-map", "[vout]", "-map", "[aout]", "-t", f"{final_len:.3f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(f"done: {out}  ({final_len:.1f}s)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
