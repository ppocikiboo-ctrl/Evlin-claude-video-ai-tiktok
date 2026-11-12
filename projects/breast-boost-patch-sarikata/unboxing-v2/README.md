# Video unboxing — VERSI 2 (gaya edit berbeza)

**Video siap:** [output/unboxing-v2.mp4](output/unboxing-v2.mp4) (32.1s)

Footage sama dengan [versi 1](../unboxing/), tetapi gaya edit lain sama sekali supaya sesuai dipos sebagai video kedua.

| | Versi 1 | **Versi 2** |
|---|---|---|
| Font sarikata | Sarikata asal dari app | **Anton** (tinggi, huruf besar) atas jalur *frosted glass* |
| Animasi sarikata | — | Perkataan muncul **satu demi satu**, terbaru **hijau lime**, kata kunci **coral** |
| Teknik hook | Ayat terus "Benda yang asyik lalu FYP" + zoom melantun | **Flash-forward**: buka dengan babak "pakai baju pun orang tak nampak?!" + teks soalan gaya cop + glitch, kemudian **pita REWIND** ke awal cerita |
| Tukar babak | Kilat putih | **Whip-slide** (kabur gerakan) |
| Zoom | Punch-in statik | **Ken Burns** (push-in / pull-out perlahan) |
| Warna | Terang | **Hangat + grain filem + vignette** |
| Overlay | Label pink / kuning | **Sticker miring** masuk dari kanan + **progress bar pink** |
| Penutup | Label CTA atas video | **Kad CTA penuh** 2.6s: MAHU CUBA? / TEKAN BEG KUNING (berdenyut) / HARGA PROMO SEKARANG! + anak panah ke link produk |
| Bunyi | Whoosh, pop turun, ketik, ka-ching | **Impact boom, swish pendek, bloop naik, sparkle, ketuk kayu, riser, coin, pita rewind + tape-stop** |

Jalur frosted glass juga menutup sarikata lama yang sudah tercetak dalam video asal.

Font: Anton & Poppins (SIL Open Font License, lihat `fonts/`).

Guna: `python3 edit_v2.py <klip1_hook.mp4> <klip2_cta.mp4>` (perlu `ffmpeg` dan `faster-whisper`).
