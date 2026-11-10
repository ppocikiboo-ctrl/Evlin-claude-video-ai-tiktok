# Breast Volume Boost & Firm Patch — sarikata video

4 klip review (dialek Sabah) dengan sarikata gaya TikTok:
teks tebal putih, perkataan yang sedang disebut menyala **kuning**, kata kunci **pink**,
dan setiap baris baru muncul dengan animasi "pop".

**Suntingan (versi 2):**
- Jeda senyap & momen janggal dibuang automatik (senyap > 0.25s dipotong, simpan 0.08s nafas).
- Ucapan dipercepat **1.15x** (pic suara kekal) supaya lebih yakin & lantang.
- Punch-in zoom 1.1x berselang-seli setiap potongan, supaya jump cut nampak bertenaga.
- Audio dinormalkan ke -14 LUFS (kuat & jelas untuk TikTok).
- Sarikata diselaraskan semula dengan Whisper pada audio yang sudah disunting.

| Klip | Asal | Selepas |
|---|---|---|
| 1 | 10.7s | 6.5s |
| 2 | 9.6s | 7.2s |
| 3 | 13.3s | 9.6s |
| 4 | 13.1s | 8.8s |

| Klip | Video siap | Sarikata |
|---|---|---|
| 1 | [output/01-vv1-sarikata.mp4](output/01-vv1-sarikata.mp4) | [.srt](01-vv1.srt) |
| 2 | [output/02-vv2-sarikata.mp4](output/02-vv2-sarikata.mp4) | [.srt](02-vv2.srt) |
| 3 | [output/03-vv3-sarikata.mp4](output/03-vv3-sarikata.mp4) | [.srt](03-vv3.srt) |
| 4 | [output/04-v44-sarikata.mp4](output/04-v44-sarikata.mp4) | [.srt](04-v44.srt) |

Fail `.srt` boleh diimport terus ke CapCut jika mahu ubah gaya sendiri.

Untuk ubah perkataan: edit `CLIPS`; untuk laju / potongan: `SPEED`, `MIN_GAP`, `EXTRA_CUTS`
dalam `build_subs.py` (perlu `ffmpeg` dan `pip install faster-whisper`), kemudian
`python3 build_subs.py <folder_video_asal>`.
