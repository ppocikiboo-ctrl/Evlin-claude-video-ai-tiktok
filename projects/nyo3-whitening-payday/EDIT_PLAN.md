# NYO3 Whitening Pycnogenol — Video TikTok Affiliate Payday Sales

Hasil siap (1080×1920, 30 fps, 30 saat, H.264 + AAC, ~-14 LUFS):

| Fail | Guna bila |
|---|---|
| `output/NYO3_Payday_TikTok_1080x1920.mp4` | Promosi Payday NYO3 **sedang aktif** |
| `output/NYO3_TanpaPayday_TikTok_1080x1920.mp4` | Promosi belum disahkan — teks Payday diganti "JOM KENALI NYO3!" / "DAPATKAN DI TIKTOK SHOP!" |

Rakaman asal (16 s, 120 fps) kekal sebagai rakaman utama. Babak dilambatkan
menggunakan bingkai 120 fps asal, jadi gerakan perlahan kekal licin tanpa bingkai janaan AI.

## Garis masa

| Masa | Babak | Rakaman asal | Teks / grafik | Bunyi |
|---|---|---|---|---|
| 0–2 s | Hook | 1.05–2.6 s (kotak depan), zoom masuk | 🔥 GAJI DAH MASUK?! → 💗 PAYDAY SALES NYO3!, kilauan emas/merah jambu, beg membeli-belah di tepi skrin, kilatan cahaya pada kotak | dentingan, mesin wang tunai (0.9 s) |
| 2–6 s | Perbandingan kulit | Gambar jenama yang dilampirkan | ✨ NAK KULIT NAMPAK LEBIH BERSERI? → 💗 KENALI PENJAGAAN KULIT NYO3!, bingkai merah jambu, zoom perlahan, kanta pembesar merentasi baris ke-2, label penafian | desiran, kilauan, pop |
| 6–11 s | Formula | 3.0–5.3 s (papan kapsul) | 🌸 KENALI FORMULA NYO3! + 4 kad kaca: Pycnogenol®, Sodium Hyaluronate, Kolagen Marin (Naticol®), Vitamin E + Zink; garisan bercahaya dari kad ke produk (menjejak gerakan kotak), molekul 3D berputar | pop setiap kad |
| 11–17 s | Infografik | 11.0–15.9 s (sisi kotak + jari menunjuk ikon) | 💧 SOKONGAN HIDRASI KULIT · ✨ NUTRISI UNTUK KULIT BERSERI · 🌸 SOKONGAN KEANJALAN KULIT · 🛡️ PENJAGAAN KULIT DARI DALAM (ikon animasi: titisan air, wajah bercahaya, heliks kolagen, kapsul + perisai); nota "Suplemen makanan · sokongan nutrisi, bukan rawatan" | dentingan setiap manfaat |
| 17–23 s | Paparan produk | 9.8–11.0 s (kotak depan paling tajam) | 💗 NYO3 WHITENING PYCNOGENOL → ✨ PENJAGAAN KULIT BERMULA DARI DALAM; kilauan mengorbit produk, sapuan cahaya pada kotak | kilauan, pop |
| 23–30 s | Penutup | 1.6–2.95 s, produk di tengah | 💗 PAYDAY SALES HARI INI! → ✨ MASA UNTUK UPGRADE RUTIN PENJAGAAN KULIT! → 🛍️ TEKAN BEG KUNING SEKARANG! (butang berdenyut + anak panah ke pautan produk) | mesin wang tunai, klik, dentingan akhir |

Setiap peralihan: kilatan cahaya merah jambu + "zoom punch" + bunyi desiran, dipotong tepat pada rentak 120 BPM.

## Gred warna
Latar biru/ungu asal ditukar kepada rona rose-plum dengan cahaya lembut di tengah dan vignet.
Piksel cerah (kotak, kapsul) dan warna kulit tangan **tidak diubah**, jadi warna serta pantulan
iridesen pembungkusan kekal asli. Ditambah sedikit kontras dan ketajaman.

## Audio
- Muzik latar gaya K-pop/iklan kecantikan (progresi IV–V–iii–vi, 120 BPM) **disintesis sendiri**
  oleh `tools/audio.py` — tiada sampel pihak ketiga, jadi selamat untuk kegunaan komersial.
- Semua SFX (mesin wang tunai, desiran, pop, dentingan, kilauan, klik) juga dijana sendiri.
- Tiada suara latar. Bunyi asal rakaman (bunyi tangan) dibuang.
- Jika mahu lagu trending, gantikan muzik dalam editor TikTok menggunakan **Commercial Music Library**
  (kekalkan volum asal rendah supaya SFX masih kedengaran).

## Pematuhan kandungan
- Gambar perbandingan digunakan **tanpa diubah** (tiada retouch/penukaran tona); hanya dipotong
  untuk membuang tajuk dan **lajur peratus (95.8%, 33.8%, 21.6%, 20%)** — angka itu tidak dipaparkan.
- Label: "Visual perbandingan promosi jenama — bukan bukti hasil pengguna yang disahkan. Hasil individu mungkin berbeza."
- Tiada harga, diskaun, stok terhad atau testimoni dicipta.
- Ayat manfaat berbentuk sokongan nutrisi; tiada dakwaan memutihkan/merawat jeragat/pigmentasi.
- Pembungkusan produk tidak dijana semula — semua dari rakaman asal.

### Perlu disemak sebelum muat naik
1. **Payday Sales** — guna versi Payday hanya jika promosi NYO3 benar-benar aktif di TikTok Shop.
2. Gambar perbandingan jenama ini sendiri membandingkan dengan "produk Glutathione" (perbandingan
   dengan pesaing) — TikTok Shop kadangkala menolak visual "sebelum/selepas" untuk suplemen. Jika
   video ditolak, buang babak 2–6 s (jalankan semula dengan babak itu digantikan rakaman produk).
3. Perkataan "WHITENING" ada pada pembungkusan asal (tidak boleh diubah); kapsyen siaran
   elakkan perkataan "putih"/"memutihkan" — guna "berseri" / "sokongan penjagaan kulit".

## Cadangan kapsyen
> Gaji dah masuk? 💗 Masa untuk upgrade rutin penjagaan kulit dari dalam dengan NYO3 Whitening Pycnogenol ✨ Tekan beg kuning untuk lihat produk! 🛍️
> #NYO3 #PaydaySales #SkincareMalaysia #PenjagaanKulit #TikTokShopMalaysia #Pycnogenol

## Render semula
```bash
cd tools
python3 render.py SUMBER.mp4 ../reference/perbandingan-kulit-jenama.jpg ../output/NYO3_Payday_TikTok_1080x1920.mp4
python3 render.py SUMBER.mp4 ../reference/perbandingan-kulit-jenama.jpg ../output/NYO3_TanpaPayday_TikTok_1080x1920.mp4 --no-payday
python3 render.py SUMBER.mp4 ../reference/perbandingan-kulit-jenama.jpg /tmp/pratonton --preview 1,4,8,13,19,28   # bingkai JPG sahaja
```
Keperluan: Python 3, numpy, Pillow, scipy, ffmpeg, fon Inter + Noto Color Emoji. Masa render ≈ 6 minit.
