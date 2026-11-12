import json, subprocess, sys
V=sys.argv[1]; OUT=sys.argv[2]
# keep segments on the original timeline (pauses, "yang tu" filler, and "makanan tinggi kalori" removed)
SEG=[(0.48,4.17),(4.37,7.80),(9.12,16.48),(17.02,22.80),(23.07,28.12),(29.89,30.94),
     (31.72,33.28),(34.92,36.80),(37.46,39.74),(40.08,41.42),(42.27,43.72)]
starts=[];t=0
for a,b in SEG: starts.append(t); t+=b-a
TOTAL=t
def m(x):
    for (a,b),s in zip(SEG,starts):
        if a-0.15<=x<=b+0.15: return s+min(max(x,a),b)-a
    raise ValueError(x)
# word list with corrected spelling; keep only words inside kept segments
words=[]
for seg in json.load(open("tr_large.json")):
    for w in seg["words"]:
        mid=(w["s"]+w["e"])/2
        if w["w"].strip()=="gula": words.append([42.27,42.50,"gula"]); continue
        if any(a<=mid<=b for a,b in SEG):
            words.append([w["s"],w["e"],w["w"].strip()])
fix={"balai":"baloi","berbalai":"berbaloi","BTLM":"VTLM","lepak":"lobak","1":"1","per":"/","3000ml":"3000ML","-gula":"-gula"}
drop={"Yang","tu"}  # filler around 29.6
ws=[]
for s,e,w in words:
    if 29.5<s<29.9 and w in drop: continue
    ws.append((m(s),m(e),fix.get(w,w)))
# merge "1 / 2" and "gula -gula"
out=[];i=0
while i<len(ws):
    s,e,w=ws[i]
    if w=="1" and i+2<len(ws) and ws[i+1][2]=="/": out.append((s,ws[i+2][1],"1/2")); i+=3; continue
    if w=="-gula": ps,pe,pw=out.pop(); out.append((ps,e,pw+"-gula")); i+=1; continue
    out.append((s,e,w)); i+=1
ws=out
HL={"jimat","wajib","2","baloi","berbaloi","3","1/2","biji","sarapan","suam","3000ML","limau","8","malam","VTLM","pantang","larang","baik"}
def ts(x):
    h=int(x//3600); x-=h*3600; mm=int(x//60); x-=mm*60; return f"{h}:{mm:02d}:{x:05.2f}"
# group into chunks of <=3 words, break at segment boundary or gap
chunks=[];cur=[]
for w in ws:
    if cur and (len(cur)>=3 or w[0]-cur[-1][1]>0.25 or cur[-1][2].endswith(",")):
        chunks.append(cur); cur=[]
    cur.append(w)
chunks.append(cur)
ev=[]
for k,c in enumerate(chunks):
    st=c[0][0]; en=chunks[k+1][0][0] if k+1<len(chunks) else c[-1][1]+0.3
    en=min(en,c[-1][1]+0.6)
    # karaoke style: active word yellow, others white
    for j,w in enumerate(c):
        ws_=w[0] if j else st; we=c[j+1][0] if j+1<len(c) else en
        txt=" ".join(("{\\c&H00E5FF&}" if q is w else ("{\\c&H00E5FF&}" if q[2].strip(",") in HL else "{\\c&HFFFFFF&}"))+q[2].upper().rstrip(",")+"{\\c&HFFFFFF&}" for q in c)
        # active word gets pop scale
        txt=" ".join((("{\\c&H38F2FF&\\fscx112\\fscy112}" if q is w else ("{\\c&HF6A2D9&}" if q[2].strip(",") in HL else "{\\c&HFFFFFF&}"))+q[2].upper().rstrip(",")+"{\\c&HFFFFFF&\\fscx100\\fscy100}") for q in c)
        ev.append(f"Dialogue: 1,{ts(ws_)},{ts(we)},Cap,,0,0,0,,{txt}")
# overlays (times in NEW timeline)
def O(st,en,style,txt,extra=""):
    ev.append(f"Dialogue: 2,{ts(st)},{ts(en)},{style},,0,0,0,,{extra}{txt}")
pop="{\\fad(120,150)\\fscx60\\fscy60\\t(0,180,\\fscx100\\fscy100)}"
# hook
O(0,3.4,"Hook","RAHSIA AKU BOLEH\\N{\\c&H38F2FF&}SHOPPING BAJU BARU",pop)
O(0.25,3.4,"Tag","jom tengok cara aku guna 👇".replace("👇",""),"{\\fad(200,150)}")
# price callout
s_b=m(2.6);O(s_b,m(7.6),"Badge","BELI 2 = LEBIH JIMAT",pop)
O(m(6.9),m(7.8),"Badge2","GRAB 3 = PALING BERBALOI!",pop)
# usage steps
O(m(9.12),m(16.48),"Step","CARA GUNA",pop)
O(m(11.2),m(16.48),"Card","① 1/2 BIJI SELEPAS SARAPAN",pop)
O(m(14.4),m(16.48),"Card2","② BERSAMA AIR SUAM",pop)
O(m(17.02),m(21.08),"Step","CARA GUNA",pop)
O(m(17.4),m(21.08),"Card","③ AIR 3000ML SEHARI",pop)
O(m(19.9),m(21.08),"Card2","+ AIR LIMAU LAGI BAIK",pop)
# lifestyle tips list builds up
O(m(21.1),m(33.28),"Step","TIPS RUTIN HARIAN",pop)
items=[(21.1,"✗ MAKAN LEPAS 8 MALAM"),(25.96,"✗ LOBAK PUTIH"),(26.84,"✗ TEH"),(27.18,"✗ MAKANAN PEDAS"),(29.89,"✗ BERGORENG"),(32.0,"✗ MINUMAN BERGAS")]
for k,(t0,txt) in enumerate(items):
    ev.append(f"Dialogue: 2,{ts(m(t0))},{ts(m(33.28))},List,,0,0,0,,{{\\pos(70,{560+k*92})\\fad(100,150)\\move(20,{560+k*92},70,{560+k*92},0,160)}}{{\\c&H6B6BFF&}}✗{{\\c&HFFFFFF&}}{txt[1:]}")
O(m(34.92),m(39.74),"Step","AMALKAN SETIAP HARI ✓".replace("✓",""),pop)
# CTA end card
cta_s=m(40.08)
O(cta_s,TOTAL,"CtaBox","\\h",(r"{\fad(150,0)\p1}m 0 0 l 920 0 920 330 0 330{\p0}"))
O(cta_s,TOTAL,"Cta","TEKAN {\\c&H38F2FF&}BEG KUNING{\\c&HFFFFFF&}\\NSEKARANG!",pop)
O(cta_s+0.3,TOTAL,"CtaSub","Beli 2 jimat  •  Grab 3 paling berbaloi","{\\fad(200,0)}")
hdr="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Anton,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,7,3,2,60,60,520,1
Style: Hook,Anton,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,8,4,8,50,50,250,1
Style: Tag,Montserrat,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,4,2,8,50,50,520,1
Style: Badge,Anton,74,&H00FFFFFF,&H00FFFFFF,&H00B0249B,&H00B0249B,0,0,0,0,100,100,1,0,3,18,0,8,60,60,250,1
Style: Badge2,Anton,74,&H00202020,&H00202020,&H0038F2FF,&H0038F2FF,0,0,0,0,100,100,1,0,3,18,0,8,60,60,390,1
Style: Step,Anton,66,&H0038F2FF,&H0038F2FF,&H00000000,&H64000000,0,0,0,0,100,100,3,0,1,6,3,8,60,60,230,1
Style: Card,Anton,70,&H00FFFFFF,&H00FFFFFF,&H00B0249B,&H00B0249B,0,0,0,0,100,100,1,0,3,16,0,8,60,60,340,1
Style: Card2,Anton,66,&H00202020,&H00202020,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,1,0,3,16,0,8,60,60,460,1
Style: List,Anton,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,1,0,1,6,3,7,70,60,0,1
Style: CtaBox,Arial,10,&HC0B0249B,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,80,0,0,1
Style: Cta,Anton,112,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,7,3,8,50,50,300,1
Style: CtaSub,Montserrat,44,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,4,2,8,50,50,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
# CtaBox position
ev=[e.replace("CtaBox,,0,0,0,,{","CtaBox,,0,0,0,,{\\pos(80,270)") for e in ev]
open("fx.ass","w").write(hdr+"\n".join(ev)+"\n")
# video graph: alternating punch-in zoom per segment + slow push, color grade, progress bar
fc=[]
for k,(a,b) in enumerate(SEG):
    z=1.0 if k%2==0 else 1.12
    d=b-a
    fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30,"
              f"scale=w='trunc(1080*{z}*(1+0.03*t/{d:.3f})/2)*2':h=-2:eval=frame,crop=1080:1920,setsar=1[v{k}]")
    fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d-0.03:.3f}:d=0.03[a{k}]")
fc.append("".join(f"[v{k}][a{k}]" for k in range(len(SEG)))+f"concat=n={len(SEG)}:v=1:a=1[cv][ca]")
fc.append(f"[cv]eq=contrast=1.06:saturation=1.15:brightness=0.01,unsharp=5:5:0.6,vignette=PI/6,"
          f"drawbox=x=0:y=0:w=1080:h=12:color=black@0.35:t=fill,"
          f"drawbox=x=0:y=0:w='1080*t/{TOTAL:.3f}':h=12:color=0xFFF238@1:t=fill,"
          f"ass=fx.ass:fontsdir=fonts[vo]")
fc.append("[ca]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=9[ao]")
open("fc.txt","w").write(";\n".join(fc))
cmd=["ffmpeg","-v","error","-y","-i",V,"-filter_complex_script","fc.txt","-map","[vo]","-map","[ao]",
     "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-r","30",
     "-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart",OUT]
subprocess.run(cmd,check=True); print("TOTAL",TOTAL)
