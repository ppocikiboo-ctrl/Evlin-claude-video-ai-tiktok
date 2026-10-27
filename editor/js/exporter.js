/* Export: frame-accurate offline render → WebCodecs H.264 (+ AAC when the
 * browser can encode it) → MP4 via mp4-muxer. Every frame is seeked, graded
 * and composited exactly as in the preview; audio is rendered offline with
 * the same scheduler. Fallback: real-time MediaRecorder capture. */
window.NYO = window.NYO || {};

NYO.Exporter = (function () {
  const W = NYO.OUT_W, H = NYO.OUT_H, FPS = NYO.FPS;

  async function capabilities() {
    const caps = { webcodecs: typeof VideoEncoder !== 'undefined' && typeof Mp4Muxer !== 'undefined', video: null, aac: false, opus: false };
    if (!caps.webcodecs) return caps;
    const candidates = ['avc1.640028', 'avc1.4d0028', 'avc1.42e028', 'avc1.640032', 'avc1.42e032'];
    for (const codec of candidates) {
      for (const hw of ['prefer-hardware', 'no-preference']) {
        try {
          const cfg = { codec, width: W, height: H, bitrate: 12e6, framerate: FPS, hardwareAcceleration: hw, avc: { format: 'avc' } };
          const r = await VideoEncoder.isConfigSupported(cfg);
          if (r.supported) { caps.video = cfg; break; }
        } catch (e) { /* try next */ }
      }
      if (caps.video) break;
    }
    if (typeof AudioEncoder !== 'undefined') {
      try { caps.aac = (await AudioEncoder.isConfigSupported({ codec: 'mp4a.40.2', sampleRate: 48000, numberOfChannels: 2, bitrate: 192000 })).supported; } catch (e) { /* no AAC */ }
      try { caps.opus = (await AudioEncoder.isConfigSupported({ codec: 'opus', sampleRate: 48000, numberOfChannels: 2, bitrate: 192000 })).supported; } catch (e) { /* no Opus */ }
    }
    return caps;
  }

  function seek(video, t) {
    return new Promise((resolve, reject) => {
      let done = false;
      const finish = () => {
        if (done) return; done = true;
        video.removeEventListener('seeked', onSeeked);
        resolve();
      };
      const onSeeked = () => {
        if (video.requestVideoFrameCallback) {
          // Make sure the decoded frame for this position is presented.
          let fired = false;
          video.requestVideoFrameCallback(() => { fired = true; finish(); });
          setTimeout(() => { if (!fired) finish(); }, 120);
        } else finish();
      };
      video.addEventListener('seeked', onSeeked);
      video.currentTime = t;
      setTimeout(() => { if (!done) { done = true; video.removeEventListener('seeked', onSeeked); reject(new Error('Video seek timed out at ' + t.toFixed(3) + 's')); } }, 8000);
    });
  }

  /* opts: { project, video, buffers, bitrate, onProgress(p, msg), signal } */
  async function exportMp4(opts) {
    const { project, video, buffers } = opts;
    const caps = await capabilities();
    if (!caps.webcodecs) throw new Error('This browser has no WebCodecs encoder. Use Chrome or Edge (v113+), or the real-time recording option.');
    if (!caps.video) throw new Error('No H.264 encoder is available in this browser for 1080×1920.');
    const audioCodec = caps.aac ? 'aac' : (caps.opus ? 'opus' : null);

    const progress = opts.onProgress || (() => {});
    progress(0, 'Rendering audio mix…');
    const mix = await NYO.AudioEngine.renderOffline(project, buffers, 48000);

    const muxer = new Mp4Muxer.Muxer({
      target: new Mp4Muxer.ArrayBufferTarget(),
      video: { codec: 'avc', width: W, height: H, frameRate: FPS },
      audio: audioCodec ? { codec: audioCodec, numberOfChannels: 2, sampleRate: 48000 } : undefined,
      fastStart: 'in-memory',
      firstTimestampBehavior: 'offset'
    });

    let encError = null;
    const venc = new VideoEncoder({
      output: (chunk, meta) => muxer.addVideoChunk(chunk, meta),
      error: (e) => { encError = e; }
    });
    const vcfg = Object.assign({}, caps.video, { bitrate: opts.bitrate || 12e6, latencyMode: 'quality' });
    venc.configure(vcfg);

    let aenc = null;
    if (audioCodec) {
      aenc = new AudioEncoder({ output: (chunk, meta) => muxer.addAudioChunk(chunk, meta), error: (e) => { encError = e; } });
      aenc.configure({ codec: audioCodec === 'aac' ? 'mp4a.40.2' : 'opus', sampleRate: 48000, numberOfChannels: 2, bitrate: 192000 });
      const block = 4800;
      const L = mix.getChannelData(0), R = mix.getChannelData(1);
      for (let i = 0; i < mix.length; i += block) {
        const n = Math.min(block, mix.length - i);
        const data = new Float32Array(n * 2);
        data.set(L.subarray(i, i + n), 0);
        data.set(R.subarray(i, i + n), n);
        const ad = new AudioData({ format: 'f32-planar', sampleRate: 48000, numberOfFrames: n, numberOfChannels: 2, timestamp: Math.round(i / 48000 * 1e6), data });
        aenc.encode(ad);
        ad.close();
      }
    }

    // Dedicated full-resolution compositor.
    const canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H;
    const comp = new NYO.Compositor(canvas);

    const wasPaused = video.paused;
    video.pause();
    const total = Math.max(1, Math.round(project.duration * FPS));
    const t0 = performance.now();
    for (let i = 0; i < total; i++) {
      if (opts.signal && opts.signal.aborted) throw new DOMException('Export cancelled', 'AbortError');
      if (encError) throw encError;
      const t = i / FPS;
      // Seek into the middle of the source frame for exact frame mapping.
      await seek(video, Math.min(video.duration - 0.002, t + 0.5 / FPS));
      comp.render(t, project, video, { overlays: true });
      const frame = new VideoFrame(canvas, { timestamp: Math.round(i * 1e6 / FPS), duration: Math.round(1e6 / FPS) });
      venc.encode(frame, { keyFrame: i % (FPS * 2) === 0 });
      frame.close();
      while (venc.encodeQueueSize > 6) await new Promise((r) => setTimeout(r, 4));
      if (i % 3 === 0) {
        const el = (performance.now() - t0) / 1000;
        const eta = el / (i + 1) * (total - i - 1);
        progress((i + 1) / total, `Encoding frame ${i + 1}/${total} · ~${Math.ceil(eta)} s left`);
      }
    }
    await venc.flush();
    if (aenc) await aenc.flush();
    if (encError) throw encError;
    muxer.finalize();
    venc.close(); if (aenc) aenc.close();
    if (!wasPaused) video.play();
    const blob = new Blob([muxer.target.buffer], { type: 'video/mp4' });
    progress(1, 'Done');
    return { blob, audioCodec, videoCodec: vcfg.codec, mix, frames: total, peak: NYO.AudioEngine.peak(mix) };
  }

  /* Real-time fallback: plays the timeline once while recording the canvas
   * and the live mix with MediaRecorder (MP4 if supported, else WebM). */
  async function recordRealtime(opts) {
    const { app } = opts;
    const types = ['video/mp4;codecs=avc1.640028,mp4a.40.2', 'video/mp4;codecs=avc1,mp4a.40.2', 'video/mp4', 'video/webm;codecs=vp9,opus', 'video/webm'];
    const mime = types.find((t) => window.MediaRecorder && MediaRecorder.isTypeSupported(t));
    if (!mime) throw new Error('MediaRecorder is not available in this browser.');
    const canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H;
    const comp = new NYO.Compositor(canvas);
    const stream = canvas.captureStream(FPS);
    const actx = app.audioCtx();
    const dest = actx.createMediaStreamDestination();
    dest.stream.getAudioTracks().forEach((tr) => stream.addTrack(tr));
    const rec = new MediaRecorder(stream, { mimeType: mime, videoBitsPerSecond: 12e6, audioBitsPerSecond: 192000 });
    const chunks = [];
    rec.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
    const video = app.video;
    await seek(video, 0);
    const when = actx.currentTime + 0.15;
    const handle = NYO.AudioEngine.schedule(actx, dest, app.project, 0, when, app.buffers());
    rec.start(250);
    await new Promise((r) => setTimeout(r, 150));
    video.muted = true;
    await video.play();
    await new Promise((resolve) => {
      const tick = () => {
        const t = actx.currentTime - when;
        if (opts.signal && opts.signal.aborted) return resolve();
        comp.render(Math.max(0, t), app.project, video, { overlays: true });
        if (opts.onProgress) opts.onProgress(Math.min(1, t / app.project.duration), `Recording ${t.toFixed(1)} / ${app.project.duration.toFixed(1)} s`);
        if (t >= app.project.duration) return resolve();
        requestAnimationFrame(tick);
      };
      tick();
    });
    video.pause();
    handle.stop();
    await new Promise((r) => { rec.onstop = r; rec.stop(); });
    return { blob: new Blob(chunks, { type: mime.split(';')[0] }), mime };
  }

  return { capabilities, exportMp4, recordRealtime, seek };
})();
