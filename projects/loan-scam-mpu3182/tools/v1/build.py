"""Generate the HyperFrames project for the loan-scam academic video.

Writes static HTML: index.html (video, music, SFX, scene hosts) and one scene file per
chapter in compositions/. Every timed element is written out in the HTML; the per-scene
script only builds tweens from the data-* attributes it finds.
"""
import json, os, html, sys

S = sys.argv[1]
P = f"{S}/loanscam"
W, H = 1080, 1920
EDL = json.load(open(f"{S}/work/edl.json"))
TALK_DUR = round(EDL["duration"], 3)
TAIL = 4.4                       # end card holds after the last word
TOTAL = round(TALK_DUR + TAIL, 3)
SFXM = json.load(open(f"{S}/work/sfx_meta.json"))
SEC = {s["id"]: s for s in EDL["sections"]}

esc = html.escape

# ----------------------------------------------------------------------------------------------
# Card builders. Times are absolute (film seconds); scenes convert them to local time.
# Inner elements carry data-fx (how they enter) and data-in (seconds after the card starts).
# ----------------------------------------------------------------------------------------------

def chars(text, cls="tw"):
    return "".join(f'<span class="{cls}">{esc(c) if c != " " else "&nbsp;"}</span>' for c in text)

def card(cid, start, end, inner, zone="top", extra_cls="", style=""):
    return dict(id=cid, start=start, end=end, zone=zone,
                html=f'<div id="{cid}" class="clip card zone-{zone} {extra_cls}" data-start="{{L}}" data-duration="{round(end-start,3)}" style="{style}">'
                     f'<div class="card-in">{inner}</div></div>')

def kicker(text, at=0.0, color="red"):
    return f'<div class="kicker k-{color}" data-fx="wipe" data-in="{at}"><span class="kdot"></span>{esc(text)}</div>'

def chapter(cid, start, end, num, title, sub=""):
    """Big slate (2.6 s) + a small dock tab that stays for the rest of the chapter."""
    slate = (f'<div class="slate" data-fx="slate" data-in="0">'
             f'<div class="slate-num" data-fx="rise" data-in="0.05">BAB {num:02d} / 08</div>'
             f'<div class="slate-rule" data-fx="draw" data-in="0.15"></div>'
             f'<div class="slate-title" data-fx="rise" data-in="0.25">{title}</div>'
             + (f'<div class="slate-sub" data-fx="rise" data-in="0.45">{esc(sub)}</div>' if sub else "")
             + '</div>')
    out = [card(cid, start, min(start + 2.9, end), slate, zone="top")]
    dock = (f'<div class="dock" data-fx="dock" data-in="0"><span class="dock-num">{num:02d}</span>'
            f'<span class="dock-t">{esc(sub or title)}</span></div>')
    if end - (start + 2.7) > 1:
        out.append(card(cid + "-dock", start + 2.7, end, dock, zone="dock"))
    return out

def note(cid, start, end, kick, head, body="", zone="top", accent="red", head_size=None):
    hs = f' style="font-size:{head_size}px"' if head_size else ""
    inner = (kicker(kick, 0.0, accent) +
             f'<div class="head"{hs} data-fx="rise" data-in="0.12">{head}</div>' +
             (f'<div class="body" data-fx="rise" data-in="0.3">{body}</div>' if body else ""))
    return card(cid, start, end, f'<div class="paper">{inner}</div>', zone)

def stat(cid, start, end, kick, prefix, to, suffix, label, land, fmt="comma", decimals=0, accent="red", source=""):
    """Counter that lands on `land` (absolute)."""
    inner = (kicker(kick, 0.0, accent) +
             f'<div class="stat"><span class="stat-pre">{esc(prefix)}</span>'
             f'<span class="stat-num" data-fx="count" data-in="0.15" data-to="{to}" data-land="{round(land-start,3)}" data-fmt="{fmt}" data-dec="{decimals}">0</span>'
             f'<span class="stat-suf">{esc(suffix)}</span></div>'
             f'<div class="body" data-fx="rise" data-in="0.35">{label}</div>' +
             (f'<div class="src" data-fx="rise" data-in="0.6">{esc(source)}</div>' if source else ""))
    return card(cid, start, end, f'<div class="paper">{inner}</div>')

def steps(cid, start, end, kick, items, accent="red"):
    """items: (absolute_time, title, sub)"""
    rows = "".join(
        f'<div class="step" data-fx="slide" data-in="{round(t-start,3)}"><div class="step-n">{i+1}</div>'
        f'<div class="step-txt"><div class="step-t">{tt}</div>' + (f'<div class="step-s">{esc(ss)}</div>' if ss else "") + '</div></div>'
        for i, (t, tt, ss) in enumerate(items))
    return card(cid, start, end, f'<div class="paper">{kicker(kick, 0, accent)}<div class="steps">{rows}</div></div>')

def chips(cid, start, end, kick, items, accent="red", head=""):
    row = "".join(f'<span class="chip" data-fx="pop" data-in="{round(t-start,3)}">{esc(x)}</span>' for t, x in items)
    hd = f'<div class="head" data-fx="rise" data-in="0.1" style="font-size:54px">{head}</div>' if head else ""
    return card(cid, start, end, f'<div class="paper">{kicker(kick, 0, accent)}{hd}<div class="chips">{row}</div></div>')

def evidence(cid, start, end, img, label, pos="50% 50%", h=340, w=900, rot=-1.6, pan=None, fit="cover", zone="top", tag="BUKTI"):
    pan_attr = f' data-pan="{pan[0]},{pan[1]}"' if pan else ""
    inner = (f'<div class="photo" data-fx="drop" data-in="0" data-rot="{rot}" style="width:{w}px">'
             f'<div class="tape"></div>' +
             (f'<div class="photo-win" style="height:{h}px"><img class="photo-img pan-img" src="assets/img/{img}"{pan_attr} data-fx="pan" data-in="0"/></div>' if pan else f'<div class="photo-win" style="height:{h}px"><img class="photo-img" src="assets/img/{img}" style="object-fit:{fit};object-position:{pos}"/></div>') +
             f'<div class="photo-cap"><span class="cap-tag">{tag}</span>{esc(label)}</div></div>')
    return card(cid, start, end, inner, zone)

def stamp(text, at_rel, color="red", size=96, rot=-9, x=0, y=0):
    return (f'<div class="stamp st-{color}" data-fx="stamp" data-in="{at_rel}" '
            f'data-rot="{rot}" style="font-size:{size}px;margin-left:{x}px;margin-top:{y}px">{esc(text)}</div>')

def lower(cid, start, end, name, role):
    inner = (f'<div class="lt"><div class="lt-bar" data-fx="draw" data-in="0"></div>'
             f'<div class="lt-name" data-fx="rise" data-in="0.12">{esc(name)}</div>'
             f'<div class="lt-role" data-fx="rise" data-in="0.25">{role}</div></div>')
    return card(cid, start, end, inner, zone="bottom")

def tag_bottom(cid, start, end, text, accent="red"):
    return card(cid, start, end, f'<div class="btag bt-{accent}" data-fx="rise" data-in="0">{text}</div>', zone="bottom")

# ----------------------------------------------------------------------------------------------
# Beats. Times are on the edited timeline (see words_out.json).
# ----------------------------------------------------------------------------------------------
B = {}   # scene id -> list of cards
X = []   # SFX cues: (time_of_hit, name, volume)

def sfx(t, name, vol=0.5):
    X.append((t, name, vol))

# ---- HOOK 0 -> 11.07 -------------------------------------------------------------------------
hook = []
hook.append(card("hk-a", 0.0, 6.40,
    '<div class="paper paper-dark">'
    + kicker("KES #1 · KOTA TINGGI, JOHOR · MEI 2026", 0.0, "amber")
    + '<div class="hk-lbl" data-fx="rise" data-in="0.2">KERUGIAN SEORANG PENGARAH SYARIKAT</div>'
    + '<div class="stat stat-xl"><span class="stat-pre">RM</span><span class="stat-num" data-fx="count" data-in="0.3" data-to="167050" data-land="4.6" data-fmt="comma" data-dec="0">0</span></div>'
    + '<div class="src src-light" data-fx="rise" data-in="0.8">Sumber: Berita RTM, 24/05/2026</div>'
    + '</div>'))
sfx(0.05, "drone-hit", 0.55); sfx(0.25, "typing-2", 0.35); sfx(4.62, "impact-boom", 0.55); sfx(4.7, "cash", 0.30)
hook.append(card("hk-b", 6.40, 8.83,
    '<div class="paper paper-dark">'
    + kicker("KES #3 · MIRI, SARAWAK", 0.0, "amber")
    + '<div class="head head-light" data-fx="rise" data-in="0.1">Rumah mangsa dibaling<br><span class="hl-red">bom petrol.</span></div>'
    + '</div>'))
sfx(6.42, "glitch-1", 0.45); sfx(8.0, "stamp-thud", 0.5)
hook.append(card("hk-c", 8.83, 11.07,
    '<div class="paper paper-dark hk-c">'
    + '<div class="head head-light" data-fx="rise" data-in="0.05" style="font-size:78px">Ini bukan<br>cerita rekaan.</div>'
    + stamp("KES SEBENAR", 1.25, "red", 80, -8, 0, 0)
    + '</div>'))
sfx(10.10, "stamp-clack", 0.55)
sfx(11.07 - SFXM["riser-slam"]["peak"], "riser-slam", 0.28)
B["s-hook"] = hook

# ---- INTRO 11.07 -> 33.0 ---------------------------------------------------------------------
intro = []
intro.append(card("in-title", 11.07, 17.0,
    '<div class="title-card">'
    '<div class="tc-kick" data-fx="rise" data-in="0.05">TUGASAN VIDEO · MPU 3182</div>'
    '<div class="tc-main" data-fx="slam" data-in="0.1">LOAN<br>SCAM</div>'
    '<div class="tc-rule" data-fx="draw" data-in="0.35"></div>'
    '<div class="tc-sub" data-fx="rise" data-in="0.5">Penipuan pinjaman yang tidak wujud: krisis etika di era digital</div>'
    '</div>'))
sfx(11.08, "impact-boom", 0.5)
intro.append(lower("in-lt", 17.1, 24.1, "Evelyn Sofidu",
    "Pelajar · MPU 3182 Penghayatan Etika dan Peradaban 2"))
sfx(17.15, "paper", 0.55)
intro.append(note("in-isu", 24.2, 32.95, "ISU YANG DIBINCANGKAN",
    'Penipuan <span class="hl">pinjaman tidak wujud</span>',
    '<i>Loan scam</i>: tawaran pinjaman palsu yang menyasarkan orang yang terdesak.'))
sfx(24.22, "whoosh-2", 0.4)
B["s-intro"] = intro

# ---- DATA 33.0 -> 75.4 -----------------------------------------------------------------------
data = []
data += chapter("da-ch", 33.0, 75.4, 1, "Data &amp; Fakta", "Data & Fakta")
sfx(33.02, "whoosh-1", 0.45)
data.append(note("da-src", 35.9, 46.4, "SUMBER DATA",
    'Infografik <span class="hl">BERNAMA</span>',
    'Diterbitkan pada <b>4 Ogos 2026</b>. Data rasmi penipuan dalam talian di Malaysia.'))
sfx(35.95, "click", 0.5)
data.append(stat("da-280", 46.5, 53.2, "SKMM · SEJAK 2022", "≈", 280000, "", "kandungan penipuan &amp; iklan palsu <b>diturunkan</b>", 50.5))
sfx(46.52, "whoosh-3", 0.35); sfx(50.55, "pop-2", 0.6)
data.append(stat("da-3b", 53.3, 62.9, "KERUGIAN · TAHUN 2025", "RM", 3, " bilion+", "kerugian akibat penipuan dalam talian", 58.85, fmt="plain"))
sfx(53.32, "whoosh-2", 0.35); sfx(58.9, "cash", 0.4)
data.append(card("da-sasar", 63.0, 75.3,
    '<div class="paper">' + kicker("SASARAN SINDIKET", 0, "red")
    + '<div class="head" data-fx="rise" data-in="0.1" style="font-size:56px">Orang yang sedang <span class="hl">susah</span> &amp; perlukan wang</div>'
    + '<div class="vs">'
    + '<div class="vs-row" data-fx="slide" data-in="4.9"><span class="vs-k">DIJANJI</span><span class="vs-v">Pinjaman mudah &amp; cepat lulus</span></div>'
    + '<div class="vs-row vs-bad" data-fx="slide" data-in="9.0"><span class="vs-k">AKHIRNYA</span><span class="vs-v">Mangsa sendiri hilang wang</span></div>'
    + '</div></div>'))
sfx(63.02, "paper", 0.45); sfx(67.92, "pop-1", 0.5)
sfx(72.05, "stamp-clack", 0.45)
B["s-data"] = data

# ---- JERAT 75.4 -> 115.43 --------------------------------------------------------------------
jer = []
jer += chapter("je-ch", 75.6, 115.43, 2, "Di mana jerat<br>dipasang?", "Di mana jerat dipasang")
sfx(75.62, "whoosh-1", 0.45)
jer.append(card("je-plat", 79.5, 92.2,
    '<div class="paper">' + kicker("IKLAN BERBAYAR DI MEDIA SOSIAL", 0, "red")
    + '<div class="logos">'
    + '<div class="logo-tile" data-fx="pop" data-in="2.9"><div class="logo-crop" style="background-image:url(assets/img/sosmed-logos.jpg);background-position:-30px -107px"></div><span>Facebook</span></div>'
    + '<div class="logo-tile" data-fx="pop" data-in="3.6"><div class="logo-crop" style="background-image:url(assets/img/sosmed-logos.jpg);background-position:-200px -107px"></div><span>Instagram</span></div>'
    + '<div class="logo-tile" data-fx="pop" data-in="4.8"><div class="logo-crop" style="background-image:url(assets/img/sosmed-logos.jpg);background-position:-366px -107px"></div><span>TikTok</span></div>'
    + '</div><div class="body" data-fx="rise" data-in="5.6">Aplikasi yang kita guna <b>setiap hari</b>.</div></div>'))
sfx(79.52, "whoosh-2", 0.35); sfx(82.4, "pop-1", 0.55); sfx(83.1, "pop-2", 0.55); sfx(84.3, "pop-1", 0.55)
jer.append(card("je-ad", 92.3, 104.0,
    '<div class="admock" data-fx="drop" data-in="0">'
    '<div class="ad-top"><div class="ad-logo">B</div><div><div class="ad-name">Pinjaman Peribadi Rasmi</div><div class="ad-spon">Ditaja · Iklan</div></div></div>'
    '<div class="ad-body"><div class="ad-big" data-fx="rise" data-in="0.3">PINJAMAN SEGERA</div>'
    f'<div class="ad-line" data-fx="type" data-in="8.6">{chars("✓ Lulus 24 jam")}</div>'
    f'<div class="ad-line" data-fx="type" data-in="10.2">{chars("✓ Tanpa semakan CTOS")}</div>'
    '<div class="ad-btn" data-fx="rise" data-in="1.2">MOHON SEKARANG</div></div>'
    '<div class="ad-logo-note" data-fx="rise" data-in="2.0">guna logo bank &amp; nama syarikat yang nampak sah</div>'
    + stamp("PALSU", 11.1, "red", 120, -12, 0, 0) +
    '</div>'))
sfx(92.32, "whoosh-3", 0.4); sfx(100.9, "typing-2", 0.4); sfx(102.5, "typing-2", 0.4); sfx(103.45, "stamp-thud", 0.6)
jer.append(card("je-chat", 104.1, 115.3,
    '<div class="paper">' + kicker("KLIK IKLAN → TERUS KE WHATSAPP", 0, "red")
    + '<div class="chat">'
    '<div class="bub bub-in" data-fx="pop" data-in="2.9">Salam. Saya <b>pegawai pinjaman</b>. Boleh saya bantu? 😊</div>'
    '<div class="bub bub-out" data-fx="pop" data-in="4.6">Saya nak mohon pinjaman RM5,000</div>'
    '</div>' + stamp("PEGAWAI TIDAK SAH", 10.3, "red", 64, -6, 0, 0) + '</div>'))
sfx(104.12, "click", 0.5); sfx(107.05, "ping-1", 0.5); sfx(108.75, "ping-2", 0.4); sfx(114.45, "stamp-clack", 0.55)
B["s-jerat"] = jer

# ---- MODUS 115.43 -> 171.8 -------------------------------------------------------------------
mo = []
mo += chapter("mo-ch", 115.45, 171.8, 3, "Bagaimana mangsa<br>ditipu?", "Modus operandi")
sfx(115.47, "whoosh-1", 0.45)
mo.append(steps("mo-steps", 118.4, 134.1, "CORAK PENIPUAN · HAMPIR SAMA SETIAP KES", [
    (121.1, "Minta salinan kad pengenalan", "maklumat peribadi diserahkan"),
    (125.0, "Pinjaman “sudah lulus”", "kadang-kadang dengan surat kelulusan palsu"),
    (131.1, "Barulah minta bayaran", "di sinilah wang mangsa hilang"),
]))
sfx(118.42, "paper", 0.45); sfx(121.12, "pop-2", 0.55); sfx(125.02, "pop-2", 0.55); sfx(131.12, "pop-2", 0.55)
mo.append(chips("mo-fees", 134.2, 140.5, "CONTOH BAYARAN PENDAHULUAN", [
    (135.2, "Yuran guaman"), (136.3, "Insurans"), (137.2, "Yuran CTOS"), (138.7, "Yuran pengaktifan akaun")],
    head="“Bayar dulu, baru wang dikeluarkan”"))
sfx(135.2, "cash", 0.3); sfx(136.3, "pop-1", 0.5); sfx(137.2, "pop-2", 0.5); sfx(138.7, "pop-1", 0.5)
mo.append(card("mo-amt", 140.6, 147.5,
    '<div class="paper">' + kicker("MENURUT POLIS", 0, "red")
    + '<div class="range"><div class="range-a" data-fx="rise" data-in="1.6">RM150–RM200</div>'
      '<div class="range-arrow" data-fx="draw" data-in="3.8"></div>'
      '<div class="range-b" data-fx="slam" data-in="5.6">RIBUAN RINGGIT</div></div>'
      '<div class="body" data-fx="rise" data-in="2.0">setiap bayaran, dan boleh terus meningkat</div></div>'))
sfx(140.62, "whoosh-2", 0.35); sfx(146.2, "impact-boom", 0.4)
mo.append(evidence("mo-keldai", 147.6, 152.85, "keldai-ilustrasi.jpg", "Wang dipindah ke akaun keldai", pos="50% 45%", h=340, rot=1.4))
sfx(147.62, "shutter", 0.45)
mo.append(card("mo-quote", 152.9, 160.6,
    '<div class="paper quote">' + kicker("PENEGASAN JSJK · PDRM", 0, "red")
    + '<div class="q" data-fx="rise" data-in="0.15">Mana-mana pinjaman yang meminta <span class="hl">bayaran pendahuluan</span> ialah</div>'
    + stamp("PENIPUAN", 7.0, "red", 104, -7, 0, 0) + '</div>'))
sfx(152.92, "paper", 0.45); sfx(159.95, "stamp-thud", 0.6)
mo.append(evidence("mo-poster", 160.7, 171.75, "poster-tipu-pinjaman.jpg", "Tanda-tanda scammer · JSJK", pos="50% 0%", h=340, w=860, rot=-1.2, pan=(-2, -52)))
sfx(160.72, "shutter", 0.4)
mo.append(tag_bottom("mo-cakna", 161.0, 171.7, '<b>CAKNA:</b> tanpa semak CTOS? tanpa yuran guaman? <span class="hl-red">Itu tanda bahaya.</span>'))
sfx(164.6, "pop-1", 0.45)
B["s-modus"] = mo

# ---- KES 171.8 -> 218.3 ----------------------------------------------------------------------
ks = []
ks += chapter("ks-ch", 171.8, 218.3, 4, "Kes sebenar", "Kes sebenar")
sfx(171.82, "whoosh-1", 0.45); sfx(172.0, "drone-hit", 0.3)
ks.append(evidence("ks-rtm", 174.6, 184.6, "berita-rtm.jpg", "Berita RTM · 24/05/2026", pos="50% 12%", h=340, w=900, rot=-1.4, pan=(-12, -42)))
sfx(174.62, "shutter", 0.5)
ks.append(tag_bottom("ks-rtm-t", 177.6, 184.5, 'Rugi <b class="hl-red">RM167,050</b> · iklan pinjaman <b>RM500,000</b> di Facebook'))
sfx(178.0, "cash", 0.3)
nine = "".join(f'<div class="acct" data-fx="pop" data-in="{round(1.2+i*0.32,2)}"><div class="acct-ic"></div><div class="acct-n">{i+1}</div></div>' for i in range(9))
ks.append(card("ks-nine", 184.7, 194.8,
    '<div class="paper">' + kicker("WANG DIPINDAHKAN KE…", 0, "red")
    + '<div class="head" data-fx="rise" data-in="0.1" style="font-size:60px"><span class="hl">9 akaun berbeza</span>, nama berbeza</div>'
    + f'<div class="accts">{nine}</div></div>'))
sfx(184.72, "whoosh-3", 0.35)
for i in range(9): sfx(184.7 + 1.2 + i * 0.32 + 0.02, "click", 0.32)
ks.append(card("ks-besut", 194.9, 207.9,
    '<div class="paper">' + kicker("KES #2 · BESUT, TERENGGANU · SEPT 2026", 0, "red")
    + '<div class="hk-lbl dark" data-fx="rise" data-in="2.6">PENGUSAHA BOT PELANCONG RUGI</div>'
    + f'<div class="stat"><span class="stat-pre">RM</span><span class="stat-num" data-fx="count" data-in="3.0" data-to="135800" data-land="{round(201.9-194.9,2)}" data-fmt="comma" data-dec="0">0</span></div>'
    + '<div class="mini-row"><span class="mini" data-fx="pop" data-in="9.6">Iklan di TikTok</span><span class="mini mini-red" data-fx="pop" data-in="11.1">18× pindahan wang</span></div>'
    + '</div>'))
sfx(194.92, "paper", 0.45); sfx(201.95, "impact-boom", 0.45); sfx(204.5, "pop-1", 0.5); sfx(206.0, "pop-2", 0.55)
ks.append(card("ks-miri", 208.0, 218.2,
    '<div class="paper paper-dark">' + kicker("KES #3 · MIRI, SARAWAK", 0, "amber")
    + '<div class="threat"><div class="th-row" data-fx="slide" data-in="0.9"><span class="th-ic">!</span><span>Mangsa pinjaman palsu &amp; along <b>diugut melalui WhatsApp</b></span></div>'
    + '<div class="th-row th-hot" data-fx="slide" data-in="6.6"><span class="th-ic">!</span><span>Rumah mangsa <b>dibaling bom petrol</b></span></div></div>'
    + '</div>'))
sfx(208.02, "glitch-2", 0.4); sfx(214.65, "glitch-1", 0.4); sfx(216.95, "impact-boom", 0.5)
B["s-kes"] = ks

# ---- KESAN 218.3 -> 244.77 -------------------------------------------------------------------
ke = []
ke += chapter("ke-ch", 218.4, 244.77, 5, "Kesan kepada<br>mangsa", "Kesan kepada mangsa")
sfx(218.42, "whoosh-1", 0.45)
ke.append(card("ke-3", 221.2, 244.7,
    '<div class="paper">' + kicker("KESANNYA SANGAT BERAT", 0, "red")
    + '<div class="impact-rows">'
    + '<div class="ir" data-fx="slide" data-in="2.0"><span class="ir-k">KEWANGAN</span><span class="ir-v">hutang asal → <b>hutang lebih besar</b></span></div>'
    + '<div class="ir" data-fx="slide" data-in="8.5"><span class="ir-k">EMOSI</span><span class="ir-v">malu · tertekan · <b>salahkan diri</b></span></div>'
    + '<div class="ir ir-hot" data-fx="slide" data-in="14.2"><span class="ir-k">KEPERCAYAAN</span><span class="ir-v"><b>hilang</b>, termasuk pada institusi kewangan yang sah</span></div>'
    + '</div></div>'))
sfx(221.22, "paper", 0.45); sfx(223.2, "pop-2", 0.5); sfx(229.7, "pop-2", 0.5); sfx(235.4, "impact-boom", 0.4)
B["s-kesan"] = ke

# ---- ETIKA 244.77 -> 347.47 ------------------------------------------------------------------
et = []
et += chapter("et-ch", 244.9, 347.47, 6, "Etika &amp;<br>Peradaban", "Etika & peradaban")
sfx(244.92, "whoosh-1", 0.45)
et.append(card("et-punca", 249.5, 261.6,
    '<div class="paper">' + kicker("SOALAN TUGASAN · 2 PUNCA KERUNTUHAN ETIKA", 0, "red")
    + '<div class="two">'
    + '<div class="two-c" data-fx="pop" data-in="5.8"><div class="two-n">01</div><div class="two-t">Sikap<br>tamak</div></div>'
    + '<div class="two-c" data-fx="pop" data-in="7.5"><div class="two-n">02</div><div class="two-t">Pengabaian<br>tanggungjawab</div></div>'
    + '</div><div class="body" data-fx="rise" data-in="9.6">Kedua-duanya jelas dalam <i>loan scam</i>.</div></div>'))
sfx(249.52, "paper", 0.45); sfx(255.3, "pop-1", 0.55); sfx(257.0, "pop-2", 0.55)
et.append(note("et-tamak", 261.7, 268.95, "01 · SIKAP TAMAK → SINDIKET",
    'Sanggup ambil wang orang yang <span class="hl">sedang susah</span>'))
sfx(261.72, "whoosh-2", 0.35)
et.append(note("et-abai", 269.0, 279.5, "02 · ABAI TANGGUNGJAWAB → PEMILIK AKAUN KELDAI",
    'Sewa akaun demi <span class="hl">wang mudah</span>',
    'tanpa peduli wang siapa yang masuk, dan siapa yang menjadi mangsa.'))
sfx(269.02, "whoosh-3", 0.35)
et.append(evidence("et-jerat", 279.6, 286.8, "jerat-keldai.jpg", "Jerat sindiket keldai akaun · CCID", pos="50% 8%", h=340, w=880, rot=1.2, pan=(0, -42)))
sfx(279.62, "shutter", 0.4)
et.append(note("et-gelap", 286.9, 296.2, "KONSEP MODUL",
    '<span class="hl">Ekonomi gelap</span>',
    'Aktiviti di luar kawalan pihak berkuasa, sering dikaitkan dengan sindiket jenayah.'))
sfx(286.92, "paper", 0.45); sfx(290.4, "ping-1", 0.4)
et.append(steps("et-nilai", 296.3, 327.6, "PERADABAN · 3 NILAI ASAS YANG TERHAKIS", [
    (302.2, "Empati", "mangsa dilihat sebagai sumber wang, bukan manusia"),
    (307.6, "Kesopanan &amp; kesusilaan", "mangsa diugut, dimalukan, gambar keluarga digunakan"),
    (318.3, "Kepercayaan", "asas perpaduan masyarakat majmuk"),
]))
sfx(296.32, "whoosh-2", 0.35); sfx(302.2, "pop-2", 0.55); sfx(307.6, "pop-2", 0.55); sfx(318.3, "pop-2", 0.55)
et.append(card("et-curiga", 327.7, 340.2,
    '<div class="paper">' + kicker("BAGAIMANA KEPERCAYAAN RUNTUH", 0, "red")
    + '<div class="steps">'
    + '<div class="step" data-fx="slide" data-in="0.6"><div class="step-n">›</div><div class="step-txt"><div class="step-t">Menyamar sebagai pegawai bank</div></div></div>'
    + '<div class="step" data-fx="slide" data-in="3.3"><div class="step-n">›</div><div class="step-txt"><div class="step-t">Guna bahasa &amp; logat mangsa</div></div></div>'
    + '<div class="step" data-fx="slide" data-in="5.7"><div class="step-n">›</div><div class="step-txt"><div class="step-t">Guna akaun rakyat pelbagai kaum</div></div></div>'
    + '</div><div class="verdict" data-fx="slam" data-in="10.0">Rakyat mula curiga sesama sendiri</div></div>'))
sfx(327.72, "paper", 0.4); sfx(328.3, "click", 0.45); sfx(331.0, "click", 0.45); sfx(333.4, "click", 0.45); sfx(337.7, "impact-boom", 0.35)
et.append(card("et-rukun", 340.3, 347.4,
    '<div class="paper paper-dark quote">' + kicker("RUKUN NEGARA · PRINSIP KE-5", 0, "amber")
    + '<div class="q q-light" data-fx="rise" data-in="0.2">Kesopanan dan Kesusilaan</div>'
    + '<div class="body body-light" data-fx="rise" data-in="4.4">…hanya tinggal <span class="hl-amber">slogan</span>?</div></div>'))
sfx(340.32, "whoosh-3", 0.35); sfx(346.6, "drone-hit", 0.3)
B["s-etika"] = et

# ---- UNDANG 347.47 -> 423.43 -----------------------------------------------------------------
un = []
un += chapter("un-ch", 347.6, 423.43, 7, "Penyelesaian", "Undang-undang")
sfx(347.62, "whoosh-1", 0.45); sfx(347.7, "ping-2", 0.35)
un.append(note("un-1", 350.6, 354.7, "CADANGAN 01", 'Penguatkuasaan <span class="hl">undang-undang</span>'))
sfx(350.62, "pop-1", 0.5)
un.append(card("un-s233", 354.8, 363.8,
    '<div class="paper">' + kicker("SKMM MENGGUNAKAN", 0, "red")
    + f'<div class="law" data-fx="type" data-in="1.4">{chars("Seksyen 233")}</div>'
    + '<div class="body" data-fx="rise" data-in="2.8">Akta Komunikasi dan Multimedia 1998</div>'
    + '<div class="body" data-fx="rise" data-in="5.5">untuk <b>menurunkan</b> kandungan &amp; iklan palsu</div></div>'))
sfx(354.82, "paper", 0.4); sfx(356.2, "typing-2", 0.4)
un.append(card("un-96", 363.9, 373.0,
    '<div class="paper">' + kicker("DARI SEGI ANGKA", 0, "red")
    + '<div class="ring-row"><div class="ring" data-fx="ring" data-in="2.9" data-to="96"><svg viewBox="0 0 120 120"><circle class="ring-bg" cx="60" cy="60" r="50"/><circle class="ring-fg" cx="60" cy="60" r="50"/></svg>'
    + f'<div class="ring-num"><span class="stat-num" data-fx="count" data-in="2.9" data-to="96" data-land="{round(367.6-363.9,2)}" data-fmt="plain" data-dec="0">0</span>%</div></div>'
    + '<div class="ring-txt" data-fx="rise" data-in="4.3">permohonan <b>berjaya</b> menurunkan kandungan penipuan</div></div></div>'))
sfx(363.92, "whoosh-2", 0.35); sfx(367.65, "ping-1", 0.45)
un.append(steps("un-lemah", 373.1, 395.0, "NAMUN · 3 KELEMAHAN", [
    (379.3, "Reaktif", "kandungan diturunkan selepas ada mangsa"),
    (388.3, "Mudah buka akaun &amp; iklan baru", "sebaik sahaja yang lama diturunkan"),
], accent="red"))
sfx(373.12, "paper", 0.4); sfx(379.3, "pop-2", 0.55); sfx(388.3, "pop-2", 0.55)
un.append(card("un-bars", 395.1, 407.6,
    '<div class="paper">' + kicker("3 · KES DI BAWAH SEKSYEN 233", 0, "red")
    + '<div class="bars">'
    + '<div class="bar-row"><span class="bar-k">Disiasat</span><div class="bar-track"><div class="bar bar-ink" data-fx="grow" data-in="5.3" data-w="100"></div></div>'
    + f'<span class="bar-v stat-num" data-fx="count" data-in="5.3" data-to="462" data-land="{round(401.8-395.1,2)}" data-fmt="plain" data-dec="0">0</span></div>'
    + '<div class="bar-row"><span class="bar-k">Ke mahkamah</span><div class="bar-track"><div class="bar bar-red" data-fx="grow" data-in="10.3" data-w="4.8"></div></div>'
    + f'<span class="bar-v bar-v-red stat-num" data-fx="count" data-in="10.3" data-to="22" data-land="{round(405.9-395.1,2)}" data-fmt="plain" data-dec="0">0</span></div>'
    + '</div><div class="src" data-fx="rise" data-in="1.5">Sumber: Infografik BERNAMA</div></div>'))
sfx(395.12, "whoosh-3", 0.35); sfx(401.85, "pop-2", 0.55); sfx(405.95, "stamp-clack", 0.5)
un.append(card("un-vs", 407.7, 417.7,
    '<div class="paper">' + kicker("MAKSUDNYA, SEKSYEN 233…", 0, "red")
    + '<div class="vs">'
    + '<div class="vs-row vs-good" data-fx="slide" data-in="3.8"><span class="vs-k">✓ BERKESAN</span><span class="vs-v">menyekat kandungan</span></div>'
    + '<div class="vs-row vs-bad" data-fx="slide" data-in="5.2"><span class="vs-k">✕ LEMAH</span><span class="vs-v">menghukum dalang, ramai di luar negara</span></div>'
    + '</div></div>'))
sfx(407.72, "paper", 0.4); sfx(411.5, "ping-2", 0.4); sfx(412.9, "glitch-1", 0.35)
un.append(card("un-verdict", 417.8, 423.4,
    '<div class="paper quote">' + kicker("KESIMPULAN SAYA", 0, "red")
    + '<div class="q" data-fx="rise" data-in="0.3">Undang-undang ini <span class="hl">perlu</span>…</div>'
    + stamp("TIDAK MENCUKUPI", 3.9, "red", 74, -6, 0, 0) + '</div>'))
sfx(417.82, "whoosh-2", 0.35); sfx(421.75, "stamp-thud", 0.6)
B["s-undang"] = un

# ---- LITERASI 423.43 -> 473.0 ----------------------------------------------------------------
li = []
li.append(note("li-1", 423.6, 429.4, "CADANGAN 02", 'Literasi <span class="hl">digital</span>'))
sfx(423.62, "whoosh-1", 0.45)
li.append(card("li-dock", 423.6, 473.0, '<div class="dock" data-fx="dock" data-in="0"><span class="dock-num">07</span><span class="dock-t">Literasi digital</span></div>', zone="dock"))
li.append(steps("li-3", 429.5, 446.7, "INGAT 3 PERKARA MUDAH", [
    (432.0, "Pinjaman sah TIDAK minta bayaran pendahuluan", ""),
    (436.9, "Semak no. telefon &amp; akaun bank", "portal Semak Mule PDRM · semakmule.rmp.gov.my"),
    (444.1, "Sudah tertipu? Hubungi NSRC segera", "supaya wang boleh disekat"),
]))
sfx(429.52, "paper", 0.4); sfx(432.0, "pop-2", 0.55); sfx(436.9, "pop-2", 0.55); sfx(444.1, "pop-2", 0.55)
li.append(evidence("li-nsrc", 446.8, 453.7, "nsrc-997.png", "NSRC · Pusat Respons Scam · 997", pos="50% 50%", h=340, w=900, rot=-1.0, fit="contain", tag="RUJUK"))
sfx(446.82, "shutter", 0.4); sfx(447.5, "ping-1", 0.5)
li.append(evidence("li-share", 453.8, 459.6, "3-cara-elak.jpg", "Kongsi dengan ibu bapa & warga emas", pos="50% 16%", h=340, w=860, rot=1.3, tag="KONGSI"))
sfx(453.82, "shutter", 0.35)
li.append(card("li-rumah", 459.7, 472.9,
    '<div class="paper">' + kicker("SEBAGAI BAKAL GURU", 0, "red")
    + '<div class="head" data-fx="rise" data-in="0.2" style="font-size:54px">Literasi digital paling berkesan bila bermula dari…</div>'
    + '<div class="two">'
    + '<div class="two-c" data-fx="pop" data-in="8.1"><div class="two-n">⌂</div><div class="two-t">Rumah</div></div>'
    + '<div class="two-c" data-fx="pop" data-in="9.8"><div class="two-n">✎</div><div class="two-t">Bilik darjah</div></div>'
    + '</div><div class="body" data-fx="rise" data-in="10.7"><b>sebelum</b> seseorang menjadi mangsa.</div></div>'))
sfx(459.72, "paper", 0.4); sfx(467.8, "pop-1", 0.55); sfx(469.5, "pop-2", 0.55)
B["s-literasi"] = li

# ---- INTEGRITI 473.0 -> 519.9 ----------------------------------------------------------------
ig = []
ig.append(note("ig-1", 473.1, 481.3, "CADANGAN 03 · PALING PENTING", 'Integriti <span class="hl">diri</span>'))
sfx(473.12, "whoosh-1", 0.45)
ig.append(card("ig-dock", 473.1, 519.9, '<div class="dock" data-fx="dock" data-in="0"><span class="dock-num">07</span><span class="dock-t">Integriti diri</span></div>', zone="dock"))
links = "".join(f'<div class="link l{i}" data-fx="pop" data-in="{round(0.4+i*0.25,2)}">{t}</div>' for i, t in enumerate(["SINDIKET", "AKAUN KELDAI", "MANGSA"]))
ig.append(card("ig-chain", 481.4, 491.85,
    '<div class="paper">' + kicker("SINDIKET TAK BOLEH BERGERAK TANPA AKAUN KELDAI", 0, "red")
    + f'<div class="chain" data-fx="none" data-in="0">{links}<div class="chain-cut" data-fx="cut" data-in="{round(491.1-481.4,2)}"></div></div>'
    + '<div class="body" data-fx="rise" data-in="3.0">Jika rakyat <b>menolak</b> tawaran sewa / jual akaun bank…</div>'
    + '<div class="verdict" data-fx="slam" data-in="9.7">rantaian ini pasti terputus</div></div>'))
sfx(481.42, "paper", 0.4); sfx(491.1, "glitch-1", 0.45); sfx(491.15, "impact-boom", 0.5)
ig.append(evidence("ig-hukum", 491.9, 497.7, "keldai-didakwa.png", "Pemilik akaun keldai boleh didakwa", pos="50% 40%", h=340, w=860, rot=-1.2))
sfx(491.92, "shutter", 0.4)
ig.append(tag_bottom("ig-10", 493.0, 497.7, 'Hukuman sehingga <b class="hl-red">10 tahun penjara</b>'))
sfx(495.8, "stamp-clack", 0.5)
ig.append(card("ig-tuhan", 497.8, 512.9,
    '<div class="paper">' + kicker("TOLAK BUKAN KERANA TAKUT DIHUKUM", 0, "red")
    + '<div class="q" data-fx="rise" data-in="4.6" style="font-size:58px">Prinsip <span class="hl">Kepercayaan kepada Tuhan</span></div>'
    + '<div class="body" data-fx="rise" data-in="8.5">Setiap perbuatan tetap dipertanggungjawabkan, <b>walaupun tiada siapa yang melihat.</b></div></div>'))
sfx(497.82, "whoosh-2", 0.35); sfx(502.4, "ping-2", 0.4)
ig.append(note("ig-orang", 513.0, 519.8, "KITA MENOLAK KERANA SEDAR…",
    'Perbuatan itu <span class="hl">menyakiti</span> &amp; <span class="hl">merugikan</span> orang lain'))
sfx(513.02, "paper", 0.4)
B["s-integriti"] = ig

# ---- PENUTUP 519.9 -> 554.4 ------------------------------------------------------------------
pe = []
pe += chapter("pe-ch", 520.0, 554.4, 8, "Penutup", "Penutup")
sfx(520.02, "whoosh-1", 0.45)
pe.append(card("pe-krisis", 522.9, 535.9,
    '<div class="paper">' + kicker("LOAN SCAM BUKAN SEKADAR JENAYAH KEWANGAN", 0, "red")
    + '<div class="head" data-fx="rise" data-in="2.8">Ia adalah <span class="hl">krisis etika</span></div>'
    + '<div class="mini-row"><span class="mini" data-fx="pop" data-in="6.4">sikap tamak</span><span class="mini" data-fx="pop" data-in="7.2">abai tanggungjawab</span></div>'
    + '<div class="body" data-fx="rise" data-in="9.3">yang menghakis kepercayaan masyarakat majmuk kita.</div></div>'))
sfx(522.92, "paper", 0.4); sfx(525.7, "stamp-clack", 0.4); sfx(529.4, "pop-1", 0.5); sfx(530.1, "pop-2", 0.5)
plates = "".join(f'<div class="plate p{i}" data-fx="plate" data-in="{a}"><span class="plate-n">{i+1}</span>{t}</div>'
                 for i, (a, t) in enumerate([(5.1, "Undang-undang yang tegas"), (6.8, "Rakyat yang celik digital"), (9.0, "Individu yang berintegriti")]))
pe.append(card("pe-3", 536.0, 546.9,
    '<div class="paper">' + kicker("3 LAPISAN YANG BERGERAK BERSAMA", 0, "red") + f'<div class="plates">{plates}</div></div>'))
sfx(536.02, "whoosh-3", 0.35); sfx(541.1, "pop-2", 0.55); sfx(542.8, "pop-2", 0.55); sfx(545.0, "pop-2", 0.55)
pe.append(card("pe-msia", 547.0, 553.1,
    '<div class="paper paper-dark">' + kicker("HANYA DENGAN CARA INI", 0, "amber")
    + '<div class="head head-light" data-fx="rise" data-in="1.2">Malaysia kekal <span class="hl-amber">lestari</span><br>&amp; <span class="hl-amber">bertamadun</span>.</div></div>'))
sfx(552.25, "impact-boom", 0.4)
B["s-penutup"] = pe

# ---- END CARD (full frame, after she finishes speaking) --------------------------------------
END_START = 553.15
endc = [card("ed-card", END_START, TOTAL,
    '<div class="endcard" data-fx="fade" data-in="0">'
    '<div class="ec-k" data-fx="rise" data-in="0.3">SEKIAN, TERIMA KASIH</div>'
    '<div class="ec-t" data-fx="slam" data-in="0.45">LOAN SCAM</div>'
    '<div class="ec-rule" data-fx="draw" data-in="0.7"></div>'
    '<div class="ec-n" data-fx="rise" data-in="0.9">Evelyn Sofidu</div>'
    '<div class="ec-c" data-fx="rise" data-in="1.05">MPU 3182 · Penghayatan Etika dan Peradaban 2<br>Pensyarah: Puan Rusniyati</div>'
    '<div class="ec-src" data-fx="rise" data-in="1.4">RUJUKAN: Infografik BERNAMA (4 Ogos 2026) · Berita RTM · JSJK PDRM · SKMM · NSRC 997 · Majlis Keselamatan Negara</div>'
    '</div>', zone="full")]
sfx(END_START + 0.47, "stamp-thud", 0.45)
B["s-end"] = endc

SCENES = [  # id, start, end
    ("s-hook", 0.0, SEC["hook3"]["end"]),
    ("s-intro", SEC["intro"]["start"], SEC["intro"]["end"]),
    ("s-data", SEC["data"]["start"], SEC["data"]["end"]),
    ("s-jerat", SEC["jerat"]["start"], SEC["jerat"]["end"]),
    ("s-modus", SEC["modus"]["start"], SEC["modus"]["end"]),
    ("s-kes", SEC["kes"]["start"], SEC["kes"]["end"]),
    ("s-kesan", SEC["kesan"]["start"], SEC["kesan"]["end"]),
    ("s-etika", SEC["etika"]["start"], SEC["etika"]["end"]),
    ("s-undang", SEC["undang"]["start"], SEC["undang"]["end"]),
    ("s-literasi", SEC["literasi"]["start"], SEC["literasi"]["end"]),
    ("s-integriti", SEC["integriti"]["start"], SEC["integriti"]["end"]),
    ("s-penutup", SEC["penutup"]["start"], END_START),
    ("s-end", END_START, TOTAL),
]

# ----------------------------------------------------------------------------------------------
CSS = open(f"{S}/work/scene.css").read()
ENGINE = open(f"{S}/work/engine.js").read()

os.makedirs(f"{P}/compositions", exist_ok=True)
hosts = []
hud = f"""<template>
<style>
#s-hud {{ position:absolute; inset:0; pointer-events:none; }}
#s-hud .hud-bar {{ position:absolute; left:0; top:0; height:8px; width:{W}px; background:#E5383B; transform-origin:0 50%; }}
#s-hud .hud-tag {{ position:absolute; right:40px; top:48px; font:600 26px/1 'IBM Plex Mono', monospace; letter-spacing:.12em; color:#EFE8DA;
  background:rgba(13,23,38,.72); padding:10px 14px; border:1px solid rgba(239,232,218,.35); }}
#s-hud .hud-tag b {{ color:#E5383B; }}
</style>
<div id="s-hud" data-composition-id="s-hud" data-width="{W}" data-height="{H}" data-duration="{round(END_START,3)}">
  <div id="hud-bar" class="clip hud-bar" data-start="0" data-duration="{round(END_START,3)}"></div>
  <div id="hud-tag" class="clip hud-tag" data-start="11.2" data-duration="{round(END_START-11.2,3)}"><b>●</b> FAIL KES · LOAN SCAM</div>
</div>
<script>
(function(){{
const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#hud-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {round(END_START,3)}, ease: "none" }}, 0);
tl.fromTo("#hud-tag", {{ opacity: 0, y: -10 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 11.2);
window.__timelines = window.__timelines || {{}};
window.__timelines["s-hud"] = tl;
}})();
</script>
</template>
"""
os.makedirs(f"{P}/compositions", exist_ok=True)
open(f"{P}/compositions/s-hud.html", "w").write(hud)
hosts.append(f'<div id="s-hud" class="clip" data-composition-id="s-hud" data-composition-src="compositions/s-hud.html" data-start="0" '
             f'data-duration="{round(END_START,3)}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:8"></div>')
for sid, s0, s1 in SCENES:
    cards = B[sid]
    body = []
    for c in cards:
        st = max(c["start"], s0); en = min(c["end"], s1)
        if en - st < 0.2:
            continue
        local = round(st - s0, 3)
        h = c["html"].replace('data-start="{L}"', f'data-start="{local}"')
        h = h.replace(f'data-duration="{round(c["end"]-c["start"],3)}"', f'data-duration="{round(en-st,3)}"', 1)
        body.append(h)
    dur = round(s1 - s0, 3)
    doc = f"""<template>
<style>
#{sid} {{ position:absolute; inset:0; }}
{CSS.replace('#ROOT', '#' + sid)}
</style>
<div id="{sid}" data-composition-id="{sid}" data-width="{W}" data-height="{H}" data-duration="{dur}" data-layout-allow-overlap>
{chr(10).join(body)}
</div>
<script>
(function(){{
{ENGINE.replace('__SID__', sid)}
}})();
</script>
</template>
"""
    open(f"{P}/compositions/{sid}.html", "w").write(doc)
    hosts.append(f'<div id="{sid}" class="clip" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                 f'data-start="{round(s0,3)}" data-duration="{dur}" data-track-index="2" data-track-kind="graphics" '
                 f'data-width="{W}" data-height="{H}" style="z-index:5"></div>')

# ---- punch-ins on the talking head: alternate framing on chapter starts and big beats ----------
PUNCH = [(0.0, 1.10), (6.40, 1.0), (8.83, 1.13), (11.07, 1.0), (33.0, 1.06), (46.5, 1.0), (63.0, 1.07), (75.6, 1.0),
         (92.3, 1.06), (104.1, 1.0), (115.45, 1.07), (134.2, 1.0), (152.9, 1.08), (160.7, 1.0), (171.8, 1.07),
         (184.7, 1.0), (208.0, 1.08), (218.4, 1.0), (235.4, 1.08), (244.9, 1.0), (269.0, 1.06), (286.9, 1.0),
         (317.5, 1.07), (327.7, 1.0), (340.3, 1.08), (347.6, 1.0), (373.1, 1.06), (395.1, 1.0), (417.8, 1.08),
         (423.6, 1.0), (444.1, 1.06), (453.8, 1.0), (473.1, 1.07), (481.4, 1.0), (491.1, 1.08), (497.8, 1.0),
         (513.0, 1.06), (520.0, 1.0), (536.0, 1.05), (547.0, 1.09)]

# ---- SFX audio elements ------------------------------------------------------------------------
aud = []
X.sort()
lanes = []  # end time per SFX lane, so no lane holds two overlapping sounds
for i, (t, name, vol) in enumerate(X):
    if vol <= 0: continue
    if name not in SFXM: raise SystemExit("unknown sfx " + name)
    m = SFXM[name]
    start = max(0.0, round(t - m["peak"] + 1/30, 3))  # land the peak one frame after the picture
    lane = next((k for k, end in enumerate(lanes) if end <= start), None)
    if lane is None:
        lanes.append(0); lane = len(lanes) - 1
    lanes[lane] = start + m["dur"] + 0.01
    aud.append(f'<audio id="fx{i:03d}" class="clip" src="assets/sfx/{name}.mp3" data-start="{start}" data-duration="{m["dur"]}" '
               f'data-volume="{vol}" data-track-index="{10 + lane}" data-audio-group="sfx"></audio>')

# ---- music bed with ducking lane -----------------------------------------------------------------
# bed is built by ffmpeg (bgm/bed.wav) at about -20 LUFS; voice sits ~-16 LUFS.
UNDER = 0.25   # under the voice: bed sits ~12 dB below speech
pts = [{"t": 0, "v": 0.45}, {"t": 0.6, "v": UNDER}]
pts += [{"t": round(TALK_DUR - 1.2, 2), "v": UNDER}, {"t": round(TALK_DUR + 0.2, 2), "v": 0.95}, {"t": TOTAL, "v": 0.95}]
auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": pts}]}).replace('"', "&quot;")
fx = json.dumps({"version": 1, "nodes": [{"type": "highpass", "id": "b1", "label": "Clear low end for the voice", "params": {"frequency": 110}},
                                          {"type": "peaking", "id": "b2", "label": "Make room for speech", "params": {"frequency": 2500, "gain": -4, "q": 0.8}}]}).replace('"', "&quot;")
voice_fx = json.dumps({"version": 1, "nodes": [{"type": "peaking", "id": "v1", "label": "Clarity", "params": {"frequency": 3200, "gain": 2, "q": 1}},
                                               {"type": "limiter", "id": "v2", "label": "Catch peaks", "params": {"limit": -1}}]}).replace('"', "&quot;")

index = f"""<!doctype html>
<html lang="ms">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<script src="assets/vendor/gsap.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:#0D1726; }}
#main {{ position:relative; width:{W}px; height:{H}px; overflow:hidden; background:#0D1726; }}
#talk-wrap {{ position:absolute; inset:0; transform-origin:50% 52%; }}
#talk {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
#grade {{ position:absolute; inset:0; pointer-events:none; z-index:2;
  background: linear-gradient(180deg, rgba(13,23,38,.55) 0%, rgba(13,23,38,0) 34%, rgba(13,23,38,0) 72%, rgba(13,23,38,.50) 100%); }}
#hud {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; z-index:8; pointer-events:none; }}
#hud-bar {{ position:absolute; left:0; top:0; height:8px; width:{W}px; background:#E5383B; transform-origin:0 50%; }}
#hud-tag {{ position:absolute; right:40px; top:48px; font:600 26px/1 'IBM Plex Mono', monospace; letter-spacing:.12em; color:#EFE8DA;
  background:rgba(13,23,38,.72); padding:10px 14px; border:1px solid rgba(239,232,218,.35); }}
#hud-tag b {{ color:#E5383B; }}
</style>
</head>
<body>
<div id="main" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}" data-fps="30">
  <div id="talk-wrap">
    <video id="talk" class="clip" src="assets/talk.mp4" data-start="0" data-duration="{TALK_DUR}" data-track-index="0"
      data-has-audio="true" data-volume="1" data-audio-group="voice" data-fx-chain="{voice_fx}"></video>
  </div>
  <div id="grade"></div>
  {chr(10).join('  ' + h for h in hosts)}
  <audio id="bed" class="clip" src="assets/bgm/bed.wav" data-start="0" data-duration="{TOTAL}" data-track-index="9"
    data-volume="1" data-audio-group="music" data-automation="{auto}" data-fx-chain="{fx}"></audio>
  {chr(10).join('  ' + a for a in aud)}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
"""
prev = None
for t, sc in PUNCH:
    if prev is None:
        index += f'tl.set("#talk-wrap", {{ scale: {sc} }}, 0);\n'
    else:
        # hard punch on the cut (a jump-cut feel), not a slow zoom
        index += f'tl.set("#talk-wrap", {{ scale: {sc} }}, {t});\n'
    prev = sc
index += f"""tl.to("#talk-wrap", {{ scale: 1.03, duration: 2.2, ease: "power2.inOut" }}, {round(TALK_DUR - 2.4, 2)});
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
open(f"{P}/index.html", "w").write(index)
json.dump({"total": TOTAL, "talk": TALK_DUR, "sfx": len(aud), "scenes": [s[0] for s in SCENES]}, open(f"{S}/work/build_info.json", "w"))
print("total", TOTAL, "sfx", len(aud), "cards", sum(len(v) for v in B.values()))
