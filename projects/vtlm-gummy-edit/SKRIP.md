# VTLM — Skrip, Efek & Caption TikTok

Video siap edit: [`VTLM_edit_final.mp4`](VTLM_edit_final.mp4) (1080x1920, 30fps, ~35 saat; asal ~44 saat).

## Apa yang dibuang
- Semua jeda dan senyap lebih 0.25 saat (permulaan, antara ayat, sebelum "Itu adalah…", dalam "mahu… mendapatkan", sebelum "gula-gula").
- Momen kekok "…yang tu…" (masa awak terlupa senarai pada kad).
- Frasa **"makanan tinggi kalori"**: frasa diet ini mudah dikesan sebagai kandungan pengurusan berat badan.

## Skrip VO (versi yang ada dalam video sekarang)
> Nak yang jimat, korang wajib beli yang ni. Sebab beli 2 balang dapat harga yang lebih berbaloi, apatah lagi kalau grab terus 3!
>
> Untuk penggunaan VTLM ni: ambil 1/2 biji selepas sarapan, lepas tu ambil bersama air suam.
> Minum air juga 3000ml sehari, bersama air limau lagi baik.
>
> Jangan makan selepas jam 8 malam, dan elakkan lobak putih, teh, makanan pedas, makanan bergoreng dan juga minuman berkarbonat.
>
> Itu adalah pantang larang kalau nak hasil yang lebih baik dengan gula-gula VTLM ni.

## Skrip cadangan (kalau nak rakam semula), dengan sudut "shopping baju baru"
Tiada perkataan *kecil, slim, kurus, berat, kilo, lemak, kalori, diet, perut, buang, turun, sebelum/selepas* dan tiada janji hasil.

| Masa | Visual | VO | Teks skrin |
|---|---|---|---|
| 0–3s | Pegang 3 pek ke kamera, zoom masuk | "Korang tahu tak apa rahsia aku makin seronok shopping baju baru sekarang?" | RAHSIA AKU BOLEH **SHOPPING BAJU BARU** |
| 3–7s | Tunjuk 2 pek → 3 pek | "Ni dia, VTLM. Beli 2 lagi jimat, grab terus 3 paling berbaloi!" | BELI 2 = LEBIH JIMAT / GRAB 3 = PALING BERBALOI |
| 7–14s | Tunjuk kad panduan, tunjuk dengan jari | "Cara guna senang je: 1/2 biji lepas sarapan, dengan air suam." | CARA GUNA ① ② |
| 14–18s | Close-up kad | "Minum air 3000ml sehari, campur limau lagi best." | ③ AIR 3000ML SEHARI |
| 18–26s | Senarai pada kad | "Untuk rutin yang lebih teratur, elakkan makan lewat malam, teh, makanan pedas, bergoreng dan minuman bergas." | TIPS RUTIN HARIAN (senarai ✗) |
| 26–30s | Pegang pek, senyum | "Amalkan setiap hari, rasa lebih yakin nak cuba outfit baru!" | AMALKAN SETIAP HARI |
| 30–35s | Pek ke kamera | "Tekan beg kuning sekarang sebelum stok habis!" | TEKAN **BEG KUNING** SEKARANG! |

## Efek visual yang dimasukkan
- **Jump cut + punch-in zoom**: setiap potongan berselang 100% / 112% zoom, dengan push-in perlahan 3%, supaya potongan nampak disengajakan.
- **Color grade**: kontras +6%, saturasi +15%, sharpen ringan, vignette lembut (warna ungu pek jadi lebih menonjol).
- **Caption karaoke** (font Anton, huruf besar): perkataan aktif kuning dan membesar, kata kunci (jimat, berbaloi, 1/2 biji, 3000ML, VTLM) berwarna ungu-merah jambu. Ejaan dibetulkan: "berbaloi", "VTLM", "lobak putih".
- **Hook 0–3s**: "RAHSIA AKU BOLEH SHOPPING BAJU BARU" + "jom tengok cara aku guna" (pop-in).
- **Lencana harga**: "BELI 2 = LEBIH JIMAT" (ungu), "GRAB 3 = PALING BERBALOI!" (kuning).
- **Kad langkah**: CARA GUNA ① ② ③ muncul ikut VO.
- **Senarai ✗** "TIPS RUTIN HARIAN" yang terbina satu demi satu ikut sebutan.
- **CTA penutup**: kotak ungu "TEKAN BEG KUNING SEKARANG!" + "Beli 2 jimat • Grab 3 paling berbaloi".
- **Progress bar** kuning di atas, dan audio dinormalkan ke -14 LUFS (standard TikTok).

## Caption post (copy-paste)
```
Rahsia aku makin seronok shopping baju baru 🛍️💜 Cara guna VTLM senang je, ikut je kad panduan ni!
Beli 2 lagi jimat, grab 3 paling berbaloi 👉 tekan beg kuning sekarang!
#VTLM #gulagula #rutinharian #ootdmalaysia #shoppingbajubaru #tiktokshopmalaysia #racuntiktok
```

## Nota pematuhan TikTok
- Dalam VO dan teks tiada sebutan kecil, slim, kurus, berat badan, lemak, kalori atau janji hasil.
- **Kad panduan dalam footage** ada tertulis "Makanan tinggi kalori" (boleh nampak jika di-pause). Kalau nak lebih selamat, rakam semula bahagian kad dengan jari menutup baris itu.
- Frasa VO asal **"pantang larang… hasil yang lebih baik"** dikekalkan kerana ia samar. Kalau nak lebih selamat, gunakan skrip cadangan di atas ("amalkan setiap hari").
- Perhatian: TikTok menyemak produk suplemen/gummy secara berasingan (kategori produk & kelulusan TikTok Shop), bukan hanya perkataan. Pastikan produk ini lulus untuk kategori tersebut dalam akaun Shop awak.

## Render semula
`python3 build/build.py <video_asal.mp4> output.mp4` (perlukan ffmpeg dengan libass, dan font Anton + Montserrat dalam `fonts/`).
