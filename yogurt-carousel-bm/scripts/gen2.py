import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
S = sys.argv[1]
B = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
MD = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'

def med(a, box):
    x0, y0, x1, y1 = box
    return tuple(int(v) for v in np.median(a[y0:y1, x0:x1].reshape(-1, 3), axis=0))

def ctext(d, cx, cy, s, font, fill):
    w = d.textlength(s, font=font); bb = font.getbbox(s)
    d.text((cx - w / 2, cy - (bb[1] + bb[3]) / 2), s, font=font, fill=fill)

def offers(im):
    a = np.array(im); d = ImageDraw.Draw(im)
    bg = med(a, (130, 560, 150, 600))
    for box in [(220, 412, 410, 458), (140, 602, 495, 714), (688, 412, 878, 458), (602, 602, 972, 714)]:
        d.rectangle(box, fill=bg)
    fl = ImageFont.truetype(MD, 28); fb = ImageFont.truetype(SB, 36)
    ctext(d, 315, 436, 'tawaran A', fl, (110, 110, 110)); ctext(d, 783, 436, 'tawaran B', fl, (110, 110, 110))
    ctext(d, 315, 637, 'beg + jam', fb, (25, 25, 25)); ctext(d, 315, 682, 'RM49', fb, (25, 25, 25))
    ctext(d, 783, 637, 'beg RM49', fb, (25, 25, 25)); ctext(d, 783, 682, '+ jam PERCUMA', fb, (46, 125, 60))

def price(im, badge):
    a = np.array(im); d = ImageDraw.Draw(im)
    pb = med(a, (300, 460, 330, 530))
    d.rectangle((420, 455, 680, 540), fill=pb)
    ctext(d, 550, 497, 'RM100', ImageFont.truetype(SB, 54), (40, 40, 45))
    d.rectangle((390, 612, 710, 684), fill=(12, 12, 12))
    ctext(d, 549, 648, 'beli sekarang', ImageFont.truetype(SB, 40), (255, 255, 255))
    if badge:
        red = med(a, (670, 385, 690, 415))
        d.rounded_rectangle((636, 356, 944, 442), radius=43, fill=red)
        ctext(d, 790, 398, 'tinggal 3 lagi', ImageFont.truetype(SB, 34), (255, 255, 255))

# slide: (blank_until, title, size, extra)
SL = {
 9: (340, "Itulah framing effect. Orang beli cara ia disampaikan.", 44, None),
 10: (430, "Apa lagi?", 60, None),
 11: (330, "Beg dan jam tangan RM49. Atau beg RM49, jam tangan PERCUMA?", 44, offers),
 12: (430, "Jam percuma la. Mestilah.", 48, None),
 13: (430, "Harga sama. Barang sama.", 48, None),
 14: (430, "Tapi 'percuma' rasa lebih untung.", 46, None),
 15: (430, "Itulah bundle pricing.", 48, None),
 16: (430, "Dan yang terakhir?", 52, None),
 17: (330, "Butang tulis 'beli sekarang'. Anda terus beli?", 44, lambda im: price(im, False)),
 18: (430, "Tak. Nanti-nanti la beli.", 48, None),
 19: (330, "Sekarang tulis 'tinggal 3 lagi'.", 48, lambda im: price(im, True)),
 20: (430, "…saya beli sekarang juga.", 48, None),
 21: (430, "Kenapa?", 60, None),
 22: (430, "Sebab takut terlepas.", 48, None),
 23: (340, "Scarcity. Takut terlepas (FOMO) buat orang cepat bertindak.", 44, None),
 24: (340, "Jadi produk tak pernah berubah. Cuma cara saya sampaikan.", 44, None),
 25: (480, "Follow untuk lagi!", 56, None),
}
TEXTY = {11: 215, 17: 215, 19: 215, 25: 350}

def wrap(d, text, font, maxw):
    words = text.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def layer(im, i):
    L = im.convert('L')
    m = L.point(lambda v: 255 if v > 212 else 0)
    seeds = [(0, 0), (1099, 0), (0, 1463), (1099, 1463), (550, 5), (5, 700), (1094, 700)]
    for seed in seeds:
        if m.getpixel(seed) == 255: ImageDraw.floodfill(m, seed, 128)
    if i not in (11, 17, 19, 25):
        for (x0, x1, y0, y1) in [(760, 830, 1150, 1460), (225, 270, 1100, 1460)]:
            for y in range(y0, y1, 6):
                for x in range(x0, x1):
                    if m.getpixel((x, y)) == 255: ImageDraw.floodfill(m, (x, y), 128)
    arr = np.array(m)
    return arr

def to_rgba(im, m):
    bg = (m == 128)
    bgimg = Image.fromarray((bg * 255).astype('uint8'))
    near = np.array(bgimg.filter(ImageFilter.MaxFilter(5))) > 0
    band = near & ~bg
    l = np.array(im.convert('L')).astype(float)
    alpha = np.where(bg, 0, 255).astype(float)
    rgb = np.array(im).astype(float)
    soft = band & (l > 165)
    alpha[soft] = np.clip((255 - l[soft]) / (255 - 165), 0, 1) * 255
    rgb[soft] = np.minimum(rgb[soft], 150)
    return Image.fromarray(np.dstack([rgb, alpha]).astype('uint8'), 'RGBA')

def pockets(m, card_zone):
    """flood-fill large white pockets (>1500px) not inside card zone"""
    img = Image.fromarray(m.copy())
    h, w = m.shape
    seen = np.zeros_like(m, bool)
    ys, xs = np.where(m == 255)
    for y, x in zip(ys[::97], xs[::97]):
        if seen[y, x] or np.array(img)[y, x] != 255: continue
        if card_zone and y < card_zone: continue
        tmp = img.copy(); ImageDraw.floodfill(tmp, (int(x), int(y)), 77)
        t = np.array(tmp) == 77; seen |= t
        n = t.sum()
        ty, tx = np.where(t)
        # skip eyes/collars (small) ; pockets between limbs are tall & thin and large
        if n > 1500 and n < 60000:
            img = tmp.point(lambda v: 128 if v == 77 else v)
    return np.array(img)

for i, (blank, title, size, extra) in SL.items():
    im = Image.open(f'{S}/crop2/{i}.png').convert('RGB')
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1100, blank), fill='white')
    d.line((1098, 0, 1098, 1464), fill='white', width=6)
    if extra: extra(im)
    # video layer
    m = layer(im, i)
    to_rgba(im, m).save(f'{S}/vid/layer_{i}.png')
    # static slide
    st = im.copy(); d = ImageDraw.Draw(st)
    f = ImageFont.truetype(B, size); lines = wrap(d, title, f, 900); lh = int(size * 1.25)
    cy = TEXTY.get(i, 290); y = cy - lh * len(lines) / 2
    for l in lines:
        w = d.textlength(l, font=f); d.text(((1100 - w) / 2, y), l, font=f, fill=(17, 17, 17)); y += lh
    st.resize((1080, 1440), Image.LANCZOS).save(f'{S}/out/slide_{i}.png')
print('ok')
