# VBGV (purple pouch) — TikTok hand-held product video (8 s, 9:16)

Short, faceless TikTok affiliate clips for the VBGV tablet pouch, made with AI
image and video tools. They copy the format of this account's best-selling
videos: a hand holding the pouch in room light, a text overlay, 5–8 seconds.

**Product reference:** [`reference/product-listing.jpg`](reference/product-listing.jpg)
(the TikTok Shop listing image). **Account data:** [`reference/top-videos-oct.jpg`](reference/top-videos-oct.jpg).

---

## 0. Kenapa format ini (data 1–26 Okt 2026)

| Video | Panjang | Views | Item terjual | GMV |
|---|---|---|---|---|
| "Paduuu #bvgv" (1 Okt) | 8 s | 4.4K | 97 | RM5.3K |
| "Jgn lepas kan peluang" (11 Okt) | 5 s | 2.2K | 10 | RM778 |
| "#fypシ" (28 Sep) | 8 s | 119 | 9 | RM462.94 |

- Video VBGV terbaik: **~RM1.20 GMV bagi setiap view**, dan **~2.2% penonton beli**.
  Penukaran ini sangat tinggi, maka produk ini memang menjual.
- Semua video yang menjual ialah **5–8 saat**, menunjukkan **tangan + pek sebenar** dan
  **teks atas skrin**. Tiada muka, tiada voiceover.
- Kesimpulan: jangan buat video panjang. Buat **banyak video pendek** dengan gaya yang sama.

---

## 1. ⚠️ Peraturan wajib sebelum post

Produk ini ialah tablet kecantikan/kesihatan, jadi risikonya lebih tinggi
daripada produk fesyen.

1. **Semak nombor pendaftaran KKM (MAL / NOT)** pada pek, kemudian cari di laman
   NPRA (quest3plus.bpfk.gov.my). Jika tiada, **jangan promosi**. Pil kurus yang tidak
   berdaftar sering dirampas KKM dan TikTok boleh tutup akaun affiliate.
2. **Jangan banding dengan Mounjaro** (atau ubat preskripsi lain). Itu dakwaan
   perubatan, dan Mounjaro ialah tanda dagangan syarikat lain.
3. **Jangan buat dakwaan hasil** yang tidak diluluskan, seperti "turun X kg",
   "kurus cepat", "putih dalam seminggu" atau "makan 1/2 biji takut kurus sangat".
   Iklan produk kesihatan di Malaysia memerlukan kelulusan iklan (nombor **KKLIU**).
   Guna hanya ayat yang ada dalam kelulusan seller.
4. **Jangan guna AI untuk buat testimoni palsu** atau gambar before/after. Video AI
   dalam pek ini hanya menunjukkan **produk**, bukan hasil pada badan seseorang.
5. Hidupkan label **"AI-generated content"** semasa post di TikTok.

---

## 2. Butiran produk (daripada gambar listing)

| Ciri | Rupa |
|---|---|
| Pek | Stand-up zip pouch, foil metalik ungu lavender, bucu bulat, kira-kira saiz tapak tangan |
| Zip | Garisan zip-lock melintang dekat bahagian atas, takuk koyak kecil di tepi kiri atas |
| Logo | "VBGV" huruf serif emas besar di tengah atas |
| Tagline | "Make yourself more beautiful" huruf serif emas kecil di bawah logo |
| Tablet | Tablet bujur ungu lavender pucat, matte, ada garis belah di tengah |

**Dalam video sebenar** (thumbnail), pek nampak **ungu lebih gelap / ungu kebiruan**
dalam cahaya bilik, dan foil memantulkan cahaya. Prompt di bawah mengikut rupa sebenar ini
supaya video nampak seperti dirakam sendiri.

---

## 3. Cara buat (workflow)

1. **Gambar keyframe:** guna model imej yang terima gambar rujukan (Nano Banana / Gemini,
   GPT-image, Flux Kontext, Seedream). Upload `product-listing.jpg` dan guna **Prompt A**.
   Hasilkan 4–8 gambar dan pilih yang logo "VBGV" paling tepat.
2. **Video:** guna image-to-video (Kling, Veo 3, Hailuo, Runway). Jadikan keyframe itu
   frame pertama dan guna **Prompt B, C atau D** bersama **Negative prompt**.
3. **CapCut:** tambah teks atas skrin (bahagian 6), lagu trending dan pin produk.
4. **Tip terbaik:** kalau awak ada pek sebenar, rakam sendiri 5 saat dengan telefon.
   Video sebenar sentiasa lebih dipercayai daripada AI. Guna AI untuk variasi latar sahaja.

---

## 4. Prompt A — keyframe image

```
Vertical 9:16 photo, authentic smartphone snapshot. A woman's hand with natural
short nails and real skin texture holds a small stand-up zip pouch close to the
camera. The pouch is the EXACT product from the reference image: metallic
lavender-purple foil with soft reflections and small crinkles, rounded corners,
a horizontal zip-lock line near the top with a small tear notch on the upper
left edge, the word "VBGV" in large gold serif capital letters centered on the
upper half, and the tagline "Make yourself more beautiful" in small gold serif
letters directly below it. In indoor light the foil reads as a deeper
violet-purple with a slight blue tint.

Background: slightly out of focus, a cozy Malaysian home, a light grey textured
sofa or bedsheet, warm evening room light from a ceiling lamp. Slightly
imperfect handheld framing, the pouch fills about half of the frame and the
logo is sharp and readable. Photorealistic, real-phone image quality, no beauty
filter.
```

---

## 5. Prompt video (8 s, 9:16)

### Prompt B — "Tunjuk pek" (paling dekat dengan video terlaris)

```
8-second vertical 9:16 video, authentic handheld smartphone footage for TikTok,
30fps, slight natural hand shake, phone auto-exposure. Indoor home, warm room
light, background of a light grey textured sofa slightly out of focus.

A woman's hand (no face visible) holds the exact VBGV pouch from the reference:
metallic violet-purple foil, rounded corners, zip-lock line near the top, large
gold serif "VBGV" logo with the small gold tagline "Make yourself more
beautiful" below. The logo stays sharp, correctly spelled and does not change
shape in any frame.

Action: she brings the pouch toward the camera, tilts it slowly left and right
so light glides across the foil, then turns it to show the back for one second
and turns it to the front again, holding it still in the center of the frame
for the last two seconds.

Photorealistic with real foil physics: soft crinkles, natural reflections. No
cinematic grading, no slow motion, no camera moves other than the handheld
phone.
```

### Prompt C — "Buka pek" (unboxing / ASMR)

```
8-second vertical 9:16 video, authentic handheld smartphone footage, top-down
view of a white bedside table in warm morning light with a clear glass of
water and a small potted plant. Two hands hold the exact VBGV pouch from the
reference (metallic violet-purple foil, gold serif "VBGV" logo and small gold
tagline "Make yourself more beautiful"). She pulls the zip-lock open with a
soft crinkle, tips the pouch, and three pale lavender oval tablets with a
center score line roll into her open palm. She holds her palm still toward the
camera for two seconds next to the pouch. Realistic hands with five fingers,
natural nails. Photorealistic, no cinematic grading, no slow motion.
```

### Prompt D — "Stok baru sampai" (promo / urgency)

```
8-second vertical 9:16 video, authentic handheld smartphone footage. A brown
cardboard shipping box opened on a light wooden floor in a bright Malaysian
living room, daylight from a window. Inside the box are about ten identical
VBGV pouches from the reference (metallic violet-purple foil, gold serif
"VBGV" logo, small gold tagline below), stacked loosely. A hand reaches in,
lifts one pouch to the camera, tilts it so the foil shines, and places it on
top of the stack. Every pouch shows the same correct logo. Photorealistic, real
phone quality, no cinematic grading, no slow motion.
```

### Negative prompt

```
cartoon, CGI, 3D render, illustration, plastic look, extra fingers, deformed
hands, six fingers, melted pouch, warped logo, misspelled logo, VBVG, BVGV,
random letters, extra text, text artifacts, wrong color pouch, pink pouch,
silver pouch, matte paper bag, bottle, jar, box packaging, capsules, white
pills, colored pills other than pale lavender, face, person's body, weight
scale, measuring tape, before and after, syringe, injection pen, medical
setting, watermark, subtitles, cinematic color grade, slow motion, drone shot
```

---

## 5b. Format 2 — AI presenter dalam kereta (selfie, 10 s)

Keyframe sedia ada: [`reference/presenter-car-keyframe.png`](reference/presenter-car-keyframe.png),
iaitu watak AI perempuan, rambut lepas, baju-T coklat, pegang pek VBGV dalam kereta.
Upload gambar ini sebagai **frame pertama** dalam Kling / Veo 3 / Hailuo.

**Peraturan format ini:** watak ini AI, jadi dia **tidak boleh** bercakap seolah-olah
dia sudah guna produk ("effect dia macam...", "saya dah turun..."). Dia hanya
memperkenalkan produk dan promo. Jangan ambil video creator lain lalu tukar muka,
kerana itu melanggar hak cipta dan merupakan deepfake orang sebenar.

### Prompt E — video

```
10-second vertical 9:16 video, authentic front-camera selfie footage filmed
handheld on a phone inside a parked car on an overcast day, daylight from the
side windows, black car interior and seat belt visible. Use the reference image
as the first frame and keep the same young woman exactly: long loose dark-brown
hair with a small half-up bun, brown eyes, natural glowing skin, fitted brown
ribbed t-shirt. She holds the exact VBGV pouch from the reference in her left
hand: vivid violet-purple matte pouch, zip-lock near the top, gold serif "VBGV"
logo, sharp and correctly spelled in every frame.

Action: she looks into the camera and talks casually, raises the pouch next to
her cheek, taps the logo with one finger, turns the pouch to show the back for
a moment, then brings it back beside her face and gives a small smile and a
nod. Natural lip movement, natural blinking, slight arm-held camera shake.
Photorealistic, real phone quality, no beauty filter, no cinematic grading,
no slow motion.
```

### Skrip voiceover / lip-sync (Bahasa Melayu santai, ~9 s)

> "Korang, ni la VBGV yang korang selalu tanya tu. Pek ungu ni. Hari ni ada
> promo, so kalau nak, tekan beg kuning bawah tu cepat sebelum habis."

- Guna hanya jika promo itu benar. Jangan tambah dakwaan kurus/putih atau Mounjaro.
- Teks atas skrin: **"Pek ungu ni yang korang cari 💜"**.
- Negative prompt: guna yang sama seperti di atas, **tetapi buang** perkataan `face`
  dan `person's body`, dan tambah `hijab, different woman, face changing, extra arm`.

### Skrip promosi + hook (5 variasi, ~10 s setiap satu)

Struktur: **Hook (0–2 s)** untuk hentikan scroll → **Isi (2–7 s)** tunjuk produk →
**CTA (7–10 s)** suruh tekan beg kuning. Hook bermain dengan rasa ingin tahu, FOMO
dan bukti sosial, bukan dengan janji hasil pada badan.

Sebelum guna, semak tanda *(jika benar)*: harga promo, logo halal JAKIM pada pek,
dan jumlah jualan mesti betul pada hari awak post.

| # | Hook (teks atas skrin + ayat pertama) | Skrip penuh (lip-sync) |
|---|---|---|
| 1 | **"Stop scroll kejap!"** | "Stop scroll kejap! Ni la pek ungu yang viral tu, VBGV. Ramai DM tanya mana nak beli. Link dah ada, tekan beg kuning bawah ni." |
| 2 | **"Korang dah try belum yang ungu ni?"** | "Korang dah try belum yang ungu ni? VBGV. Pek dia kecik, senang bawak dalam beg. Tengah promo hari ni, tekan beg kuning sebelum harga naik balik." *(promo jika benar)* |
| 3 | **"Jangan beli lagi kalau…"** | "Jangan beli lagi kalau tak check harga promo hari ni dulu. VBGV ni tengah murah kat TikTok Shop. Tekan beg kuning, tengok sendiri harga dia." *(promo jika benar)* |
| 4 | **"Sold out minggu lepas, dah restock!"** | "Pek ungu ni sold out minggu lepas, sekarang dah restock. VBGV. Stok terhad, jadi kalau nak, checkout sekarang kat beg kuning." *(sold out & restock jika benar)* |
| 5 | **"Ramai checkout bulan ni, ni sebabnya"** | "Bulan ni je dah ramai checkout benda ni. VBGV, versi halal, pek ungu ni. Nak tahu kenapa ramai pilih, tekan beg kuning, baca review pembeli sendiri." *(halal jika ada logo JAKIM)* |

**Tip hook:**
- 2 saat pertama paling penting. Letak hook sebagai **teks besar di tengah atas** dan
  sebut dengan suara pada masa yang sama.
- Uji **satu hook bagi setiap video**. Selepas 3 hari, kekalkan hook yang dapat paling banyak
  item terjual.
- Akhiri video dengan pek dipegang dekat muka dan teks **"Tekan beg kuning 🛒"**.

**Jangan masukkan** dalam skrip: "turun X kg", "kurus", "putih", "effect macam
Mounjaro/cucuk", "saya dah guna" (watak AI), atau angka promo yang tidak betul.

---

## 6. Teks atas skrin, caption & hashtag

Teks atas skrin (pilih satu bagi setiap video, 1–2 baris):

| Untuk | Teks |
|---|---|
| Prompt B | "Benda kecik ni la yang ramai cari 💜" |
| Prompt B | "Pek ungu ni sold out minggu lepas… dah restock!" *(guna hanya jika benar)* |
| Prompt C | "Rutin pagi saya, simple je 💜" |
| Prompt C | "Satu pek ada berapa biji? Jom tengok" |
| Prompt D | "Stok baru sampai! Promo hari ni je ‼️" *(guna hanya jika promo benar)* |
| Prompt D | "Jangan lepaskan peluang, tekan beg kuning 🛒" |

**Caption:** pendek, seperti video terlaris awak. Contoh: `Paduuu 💜 #vbgv`,
`Promo hari ni je ‼️ #vbgv`.

**Hashtag:** `#vbgv #fyp #fypシ #rutinpagi #tiktokshopmalaysia #promotiktokshop`.
Jangan guna hashtag kurus atau ubat seperti `#kurus` atau `#mounjaro`.

---

## 7. Pelan posting (14 hari)

- **2 video sehari**, setiap satu dengan latar atau sudut berbeza (B, C, D bergilir).
- Ulang format terbaik ("Paduuu") dengan **hook yang lain** setiap kali.
- Selepas 7 hari, semak **Attr. GMV / views** setiap video. Teruskan gaya yang melebihi
  RM0.50 bagi setiap view dan hentikan gaya yang di bawah RM0.10.
