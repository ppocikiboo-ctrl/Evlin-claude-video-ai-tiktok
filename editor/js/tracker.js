/* Motion tracking: keyframe interpolation and an in-browser point tracker
 * (normalised cross-correlation template matching, frame by frame). */
window.NYO = window.NYO || {};

NYO.Track = {
  sortKeys(label) {
    label.keyframes.sort((a, b) => a[0] - b[0]);
  },

  /* Interpolated point (source-normalised) at time t, plus a coverage alpha
   * that fades the label out where no keyframes exist (object off screen). */
  sample(label, t) {
    const k = label.keyframes;
    if (!k || !k.length) return null;
    const maxGap = label.maxGap || 0.6;
    const fadeLen = 0.12;
    if (t <= k[0][0]) {
      const d = k[0][0] - t;
      return { x: k[0][1], y: k[0][2], alpha: 1 - Math.min(1, Math.max(0, (d - 0.03) / fadeLen)) };
    }
    const last = k[k.length - 1];
    if (t >= last[0]) {
      const d = t - last[0];
      return { x: last[1], y: last[2], alpha: 1 - Math.min(1, Math.max(0, (d - 0.03) / fadeLen)) };
    }
    let i = 0;
    let lo = 0, hi = k.length - 1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      if (k[mid][0] <= t) { i = mid; lo = mid + 1; } else hi = mid - 1;
    }
    const a = k[i], b = k[i + 1];
    const gap = b[0] - a[0];
    if (gap > maxGap) {
      // Object not tracked in this gap: hold nearest key briefly, then hide.
      const da = t - a[0], db = b[0] - t;
      const near = da < db ? a : b;
      const d = Math.min(da, db);
      return { x: near[1], y: near[2], alpha: 1 - Math.min(1, Math.max(0, (d - 0.03) / fadeLen)) };
    }
    const p0 = k[Math.max(0, i - 1)], p3 = k[Math.min(k.length - 1, i + 2)];
    const u = (t - a[0]) / gap;
    const cr = (q0, q1, q2, q3) => {
      const u2 = u * u, u3 = u2 * u;
      return 0.5 * ((2 * q1) + (-q0 + q2) * u + (2 * q0 - 5 * q1 + 4 * q2 - q3) * u2 + (-q0 + 3 * q1 - 3 * q2 + q3) * u3);
    };
    // Fall back to linear across segments whose neighbours are beyond a gap.
    const okPrev = (a[0] - p0[0]) <= maxGap, okNext = (p3[0] - b[0]) <= maxGap;
    const q0 = okPrev ? p0 : a, q3 = okNext ? p3 : b;
    return { x: cr(q0[1], a[1], b[1], q3[1]), y: cr(q0[2], a[2], b[2], q3[2]), alpha: 1 };
  },

  setKey(label, t, x, y) {
    const k = label.keyframes;
    const tol = 0.5 / NYO.FPS;
    const ex = k.find((kf) => Math.abs(kf[0] - t) < tol);
    const tt = Math.round(t * 1000) / 1000;
    if (ex) { ex[0] = tt; ex[1] = x; ex[2] = y; } else k.push([tt, x, y]);
    NYO.Track.sortKeys(label);
  },

  keyAt(label, t) {
    const tol = 0.5 / NYO.FPS;
    return label.keyframes.findIndex((kf) => Math.abs(kf[0] - t) < tol);
  },

  /* Automatic point tracking from the keyframe/interpolated point at fromT
   * toward toT (either direction). Seeks the given video frame by frame,
   * matches a luminance patch, and writes keyframes. Stops when confidence
   * drops below `minScore` (object lost / occluded) and reports it. */
  async autoTrack(video, label, fromT, toT, opts) {
    opts = opts || {};
    const fps = NYO.FPS;
    const dir = toT >= fromT ? 1 : -1;
    const start = NYO.Track.sample(label, fromT);
    if (!start) throw new Error('Set a keyframe on the softgel first (click it in the preview), then auto-track.');
    const scale = Math.min(1, 480 / video.videoWidth);
    const W = Math.round(video.videoWidth * scale), H = Math.round(video.videoHeight * scale);
    const cv = document.createElement('canvas');
    cv.width = W; cv.height = H;
    const cx = cv.getContext('2d', { willReadFrequently: true });
    const tw = Math.max(12, Math.round(30 * W / 480)), th = Math.max(10, Math.round(24 * W / 480));
    const R = Math.round(22 * W / 480);
    const minScore = opts.minScore || 0.55;

    const gray = () => {
      const d = cx.getImageData(0, 0, W, H).data;
      const g = new Float32Array(W * H);
      for (let i = 0, j = 0; i < g.length; i++, j += 4) g[i] = 0.299 * d[j] + 0.587 * d[j + 1] + 0.114 * d[j + 2];
      return g;
    };
    const seek = (t) => new Promise((resolve) => {
      const done = () => { video.removeEventListener('seeked', done); resolve(); };
      video.addEventListener('seeked', done);
      video.currentTime = Math.min(video.duration - 0.001, Math.max(0, t + 0.25 / fps));
    });
    const patch = (g, x, y) => {
      const p = new Float32Array(tw * th);
      const x0 = Math.round(x - tw / 2), y0 = Math.round(y - th / 2);
      for (let j = 0; j < th; j++) for (let i = 0; i < tw; i++) {
        const xx = Math.min(W - 1, Math.max(0, x0 + i)), yy = Math.min(H - 1, Math.max(0, y0 + j));
        p[j * tw + i] = g[yy * W + xx];
      }
      return p;
    };
    const stats = (p) => {
      let m = 0; for (let i = 0; i < p.length; i++) m += p[i];
      m /= p.length;
      let v = 0; for (let i = 0; i < p.length; i++) v += (p[i] - m) * (p[i] - m);
      return { m, s: Math.sqrt(v) || 1 };
    };

    let x = start.x * W, y = start.y * H;
    await seek(fromT);
    cx.drawImage(video, 0, 0, W, H);
    let tpl = patch(gray(), x, y);
    let n = Math.round(Math.abs(toT - fromT) * fps);
    const startFrame = Math.round(fromT * fps);
    const written = [];
    let lostAt = null;
    for (let step = 1; step <= n; step++) {
      if (opts.signal && opts.signal.aborted) break;
      const t = (startFrame + dir * step) / fps;
      if (t < 0 || t > video.duration) break;
      await seek(t);
      cx.drawImage(video, 0, 0, W, H);
      const g = gray();
      const ts = stats(tpl);
      let best = -2, bx = x, by = y;
      for (let dy = -R; dy <= R; dy += 1) {
        for (let dx = -R; dx <= R; dx += 1) {
          const px = Math.round(x + dx), py = Math.round(y + dy);
          const x0 = px - (tw >> 1), y0 = py - (th >> 1);
          if (x0 < 0 || y0 < 0 || x0 + tw >= W || y0 + th >= H) continue;
          let sm = 0;
          for (let j = 0; j < th; j++) { const row = (y0 + j) * W + x0; for (let i = 0; i < tw; i++) sm += g[row + i]; }
          const mean = sm / (tw * th);
          let num = 0, den = 0;
          for (let j = 0; j < th; j++) {
            const row = (y0 + j) * W + x0;
            for (let i = 0; i < tw; i++) {
              const a = g[row + i] - mean;
              num += a * (tpl[j * tw + i] - ts.m);
              den += a * a;
            }
          }
          const sc = num / ((Math.sqrt(den) || 1) * ts.s);
          if (sc > best) { best = sc; bx = px; by = py; }
        }
      }
      if (best < minScore) { lostAt = t; break; }
      x = bx; y = by;
      const np = patch(g, x, y);
      for (let i = 0; i < tpl.length; i++) tpl[i] = tpl[i] * 0.85 + np[i] * 0.15;
      if (step % 2 === 0 || step === n) {
        NYO.Track.setKey(label, t, x / W, y / H);
        written.push(t);
      }
      if (opts.onProgress) opts.onProgress(step / n, t, best);
    }
    return { written: written.length, lostAt };
  }
};
