# Loan Scam — video tugasan MPU 3182 (HyperFrames)

Video akademik 9:16 (1080×1920) untuk MPU 3182 Penghayatan Etika dan Peradaban 2,
pensyarah Puan Rusniyati. Topik: penipuan pinjaman tidak wujud (*loan scam*).

**Status (13 Nov 2026):** edit versi 1 siap sampai preview. Pelajar akan **retake**
rakaman (mata nampak membaca, banyak bahagian awkward) dan hantar esok. Semua rekaan,
animasi, SFX dan muzik di sini diguna semula untuk rakaman baru.

## Sumber

- Rakaman asal (versi 1): Drive folder `1g0PfGazYyGAaYaRwvRlvJ6NDEpegJ_de`
  (Video 1, Video 2, Video 3; ~190–245 MB setiap satu, 1080×1920 HEVC ~30 fps).
- Gambar: Drive folder `1Nyx2yUOv3D6cKdfOQpR00_casYYIsAGO` (sudah disalin ke `hyperframes/assets/img/`).
- Muat turun video besar: `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`
  (host `drive.usercontent.google.com` dan `drive.google.com` sudah dibenarkan dalam environment).
- Muzik & SFX: katalog HeyGen (login `npx hyperframes auth login --device`, dengan `NODE_USE_ENV_PROXY=1`).
  Fail sudah ada dalam `hyperframes/assets/bgm/*.mp3` dan `hyperframes/assets/sfx/`.

## Keputusan yang dipersetujui

- Susunan: **Video 1 → Video 3 → Video 2** (V3 = kes sebenar/kesan/etika, V2 = penyelesaian + penutup).
- Hook (±11 s): "Pada Mei 2026, seorang pengarah syarikat di Kota Tinggi kerugian RM167,050"
  → "rumah mangsa dibaling bom petrol" → "Ini bukan cerita rekaan." + cop KES SEBENAR.
- Nama di skrin: **Evelyn Sofidu**; pensyarah **Puan Rusniyati**.
- NSRC = **997** (rakaman v1 kedengaran "999" — retake perlu sebut 997).
- Gambar `5-cara-lapor` (Indonesia/Okezone) **tidak digunakan**.
- Muka mesti bersih: grafik hanya zon atas (y 150–600) dan bawah (y ≥ 1470). Muka ±y 640–1400.
- Muzik ~12 dB di bawah suara (bed `data-volume` lane = 0.25), suara dinormalkan ke −16 LUFS.

## Rekaan — "Fail Kes / Dossier"

Kertas krim `#EFE8DA`, dakwat `#0D1726`, merah amaran `#E5383B`, amber `#F4B942`.
Tajuk Playfair Display 900, label IBM Plex Mono, nombor Oswald/League Gothic, badan Inter.
8 bab: 01 Data & Fakta · 02 Di mana jerat dipasang · 03 Modus operandi · 04 Kes sebenar ·
05 Kesan kepada mangsa · 06 Etika & peradaban · 07 Penyelesaian (undang-undang, literasi digital,
integriti diri) · 08 Penutup. Kad tamat dengan rujukan.

## Paip kerja (tools/)

| Langkah | Fail |
| --- | --- |
| Transcribe (faster-whisper large-v3-turbo, `ms`, word timestamps) | `tools/transcribe.py` |
| Cari pause / perkataan meleret | `tools/gaps.py` |
| Senarai potongan (VAD + bahagian editorial) → `edl.json`, `words_out.json` | `tools/edit.py` (jadual `SECTIONS`) |
| Render track percakapan, potongan tepat frame | `tools/render_cut.py` → `assets/talk.mp4` |
| Bina bed muzik ikut bab | `tools/build_bed.sh` → `assets/bgm/bed.wav` |
| Jana HyperFrames (index + 13 scene + HUD, 74 kad, ~144 SFX) | `tools/build.py` + `scene.css` + `engine.js` |
| Cari / muat turun muzik & SFX HeyGen | `tools/music.mjs`, `dlmusic.mjs`, `dlsfx.mjs` |

Sebelum `edit.py`: setiap sumber dijadikan CFR 30 fps (`ffmpeg -vf fps=30 … crf 15`) dan audio
dinormalkan (`highpass 75, acompressor, loudnorm I=-16`) ke `cfr/<v>_v.mp4` dan `cfr/<v>_a.wav`.
Jalan skrip dengan direktori kerja (scratchpad) sebagai argumen; `build.py` menulis ke `<S>/loanscam`.

## Untuk rakaman baru (esok)

1. Muat turun rakaman baru → transcribe → baca transcript.
2. Kemas kini `SECTIONS` dalam `tools/edit.py` (masa sumber setiap bab, potongan ulang/take buruk).
3. Jalankan `edit.py` → `render_cut.py`.
4. **Tetapkan semula semua masa beat dalam `tools/build.py`** (masa output) ikut `words_out.json` baru —
   kandungan kad kekal, cuma masa berubah. Juga masa bab untuk `build_bed.sh`.
5. `build.py` → `npx hyperframes check` → snapshot → preview draf → minta kelulusan → render penuh.

Data v1 yang disimpan: `data/transcript_v*.json`, `data/edl.json`, `data/words_out.json`,
`data/sfx_meta.json` (titik puncak SFX), `data/contact-sheet-*.jpg` (storyboard preview v1).
