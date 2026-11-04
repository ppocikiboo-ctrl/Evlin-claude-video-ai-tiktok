# SCC White Kidney Bean + L-Carnitine Candy — sarikata TikTok

Sarikata (Bahasa Melayu) untuk video affiliate SCC (32.6 s, 1080×1920).
Video asal tidak diubah: saiz, potongan, audio dan paparan sama. Hanya sarikata ditambah.

| Fail | Guna |
|---|---|
| `sarikata.srt` | Teks biasa dengan masa. Import ke CapCut atau TikTok. |
| `sarikata.ass` | Gaya TikTok: Inter Black, putih dengan outline hitam, kata kunci kuning, animasi pop. Digunakan untuk membakar sarikata ke video. |

Bakar semula ke video asal:

```
ffmpeg -i video-asal.mp4 -vf "ass=sarikata.ass" -c:v libx264 -preset slow -crf 16 \
  -pix_fmt yuv420p -fps_mode passthrough -c:a copy -movflags +faststart scc-sarikata.mp4
```

Sarikata diletak di tengah bawah (MarginV 560), di atas kawasan butang dan kapsyen TikTok.
