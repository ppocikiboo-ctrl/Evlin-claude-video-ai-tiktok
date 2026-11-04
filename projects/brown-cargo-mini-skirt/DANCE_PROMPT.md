# Format: Dance OOTD (gaya video tarian TikTok), tanpa sound

Berdasarkan video contoh (tarian ~13 s, kemudian outro TikTok): perempuan
berdiri di bilik tidur, telefon atas tripod di paras dada, menari tarian
tangan yang comel sambil memperagakan pakaian. Bunyi tidak disalin.

## Apa yang membuat video contoh menjadi

| Unsur | Dalam video contoh |
|---|---|
| Kamera | Kamera depan telefon atas tripod, statik, paras dada, sedikit sudut rendah. Bukan mirror selfie |
| Bingkai | Separuh badan hingga bawah lutut, badan di tengah, pakaian penuh kelihatan |
| Cahaya | Lampu LED biru di belakang katil + cahaya siang lembut dari langsir, kulit tetap natural |
| Latar | Bilik tidur moden: langsir kelabu dari siling ke lantai, katil dengan headboard berlapik, cadar kelabu-putih, lantai kayu |
| Gerakan | Tarian tangan pantas ikut rentak: berpusing masuk ke frame, goyang bahu, sentuh rambut, silang tangan di dada (X), tapak tangan terbuka di tepi muka, penumbuk comel, tunjuk jari ke atas, wink, akhir dengan pose "jari cakar" bersilang depan dada |
| Ekspresi | Ceria dan nakal: senyum, muncung, kenyit mata, lip-sync |
| Pakaian | Badan bergoyang supaya kain bergerak, pakaian sentiasa jelas |
| Rentak | Satu gerakan tiap ~1 saat, tiada potongan |

## Perkara penting untuk model anda

Dalam video contoh, muka kelihatan. Gambar model anda pula semua mirror
selfie dengan telefon menutup muka, jadi Veo tak tahu rupa muka sebenar dan
akan **reka muka baharu**. Pilih satu:

- **A. Muka kelihatan:** guna gambar model dengan muka jelas menghadap
  kamera sebagai first frame. Gunakan hanya jika itu anda atau model sudah
  izinkan.
- **B. Tanpa muka (disyorkan, kekal gaya akaun anda):** tarian dalam mirror
  selfie. Satu tangan pegang telefon menutup muka, satu tangan lagi menari.
  Prompt B di bawah.

## Cara dalam Google Flow

1. Mod **Frames to Video**, model **Veo 3.1**, aspect ratio **9:16**.
2. First frame: gambar model (A: muka jelas; B: mirror selfie sedia ada).
3. Paste prompt. Veo jana 8 s. Untuk ~14 s macam contoh, tekan **Extend**
   dan guna prompt sambungan.
4. Buang bunyi: CapCut → Volume 0, atau
   `ffmpeg -i in.mp4 -an -c:v copy out_silent.mp4`. Kemudian letak lagu
   trending dari Commercial Music Library dalam TikTok.

## Prompt A — muka kelihatan, kamera tripod (8 s)

```
8-second vertical 9:16 video, one continuous shot, starting exactly from the
uploaded first frame. An authentic TikTok dance video filmed with a phone's
front camera on a tripod at chest height, slightly low angle. The camera is
completely static: no zoom, no pan, no cuts. Framing from head to just below
the knees, her outfit fully visible and centred.

The same young woman as in the first frame, unchanged: same face, hair, body
and outfit. She wears [OUTFIT: dark chocolate-brown fitted cropped polo tee
with an open V collar and the dark chocolate-brown cotton twill cargo mini
skirt with two front flap pockets, silver button, side slits], white chunky
sneakers. The outfit keeps the exact colour, shape and details in every
frame.

Setting: modern bedroom, light grey floor-to-ceiling curtains, a bed with a
padded headboard and grey-white bedding, light wood floor. Soft daylight
through the curtains plus a cool blue LED glow behind the bed. Natural skin.

She dances a cute, energetic TikTok hand-choreography to an upbeat beat, one
move about every second, moving her hips and shoulders so the outfit moves:
0–1 s: spins into frame from the side and lands facing the camera with a
smile.
1–2 s: shoulder bounce, tucks her hair behind her ear.
2–3 s: crosses both forearms in an X in front of her chest.
3–4 s: opens both palms beside her face with a playful surprised face.
4–5 s: two cute fists near her chin, little pout, hip sway.
5–6 s: crosses her arms with both index fingers pointing out, then winks.
6–7 s: points one finger up, the other hand on her hip, side step.
7–8 s: ends with both hands in a "claw" gesture crossed in front of her
chest, big cheeky smile, holds the pose.

Expressions: cheerful and playful, smiling, pouting, winking, lip-syncing.
Real hair and fabric movement. Photorealistic, real skin texture, no beauty
filter, no slow motion, no cinematic grading, no text, no subtitles, no
watermark, no TikTok logo. No speech.

Avoid: changing face, different outfit, outfit changing colour, extra
fingers, distorted hands, merged fingers, twisted arms, camera movement,
zoom, jump cut, morphing, flickering, background change.
```

## Prompt B — tanpa muka, tarian mirror selfie (8 s)

```
8-second vertical 9:16 video, one continuous shot, starting exactly from the
uploaded first frame. An authentic TikTok OOTD mirror dance video. She holds
the same burgundy phone in front of her face with her right hand the WHOLE
time, so her face is never revealed. The view is the phone's reflection in
the full-length mirror, handheld but steady. No zoom, no cuts.

Keep everything exactly as in the first frame: same woman, hair, body,
bedroom and outfit [dark chocolate-brown fitted cropped polo tee with an open
V collar, dark chocolate-brown cotton twill cargo mini skirt with two front
flap pockets, silver button, side slits, white chunky sneakers]. The outfit
keeps its exact colour, shape and details in every frame.

She dances a cute, upbeat TikTok hand-choreography with her free left hand
and her body, one move about every second:
0–1 s: hip sway to the beat, shoulder bounce.
1–2 s: free hand sweeps her hair back over her shoulder.
2–3 s: free hand open palm next to the phone, playful head tilt.
3–4 s: small cute fist near her chin, knee pop.
4–5 s: points down at the skirt pockets, then turns her hips left.
5–6 s: turns her hips right, pats the skirt pocket.
6–7 s: points one finger up with a little bounce.
7–8 s: ends with a "claw" hand gesture beside the phone, weight on one leg,
holds the pose.

Real hair and fabric movement; the twill skirt is firm and moves only a
little. Photorealistic, no beauty filter, no slow motion, no text, no
subtitles, no watermark. No speech.

Avoid: revealing her face, phone moving away from her face, phone changing
colour, extra fingers, distorted hands, warped mirror, outfit changing,
background change, morphing, flickering, jump cut.
```

## Prompt sambungan (Extend, +6 s)

```
Continue the same shot with no cut, same camera, same woman, same outfit,
same room. She continues the same playful hand-choreography: a quick wave of
both hands, a heart shape with her fingers, a little spin showing the outfit
from the side, and ends facing forward with a cheeky smile and a peace sign,
holding the final pose. No speech, no text.
```
(Untuk Prompt B, tukar `a heart shape with her fingers` jadi
`a half heart with her free hand` dan tambah `phone stays covering her face`.)

## Tips supaya tarian nampak real

- Gerakan tangan pantas sering buat jari rosak. Jana 3–4 versi dan pilih
  yang tangan paling bersih.
- Kalau pakaian berubah semasa berpusing, buang pusingan dan ganti dengan
  `side step`.
- Jangan salin muka, nama atau watermark pencipta video asal. Ambil gaya
  sahaja.
- Hidupkan label **AI-generated content** semasa post.
