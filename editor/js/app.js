/* Editor application: state, playback clock, preview interaction, panels. */
window.NYO = window.NYO || {};

(function () {
  const $ = (id) => document.getElementById(id);
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const fmt = (t) => {
    const m = Math.floor(t / 60), s = t - m * 60;
    return `${String(m).padStart(2, '0')}:${s.toFixed(2).padStart(5, '0')}`;
  };

  function h(tag, attrs, children) {
    const el = document.createElement(tag);
    if (attrs) Object.entries(attrs).forEach(([k, v]) => {
      if (k === 'class') el.className = v;
      else if (k === 'text') el.textContent = v;
      else if (k === 'html') el.innerHTML = v;
      else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
      else if (v === true) el.setAttribute(k, '');
      else if (v !== false && v != null) el.setAttribute(k, v);
    });
    (children || []).forEach((c) => { if (c != null) el.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return el;
  }

  const app = {
    project: NYO.loadProjectLocal() || NYO.defaultProject(),
    time: 0,
    playing: false,
    selection: null,
    selKey: -1,
    tab: 'text',
    compare: 'off',
    split: 0.5,
    clickToKey: false,
    hq: false,
    musicBuffer: null,
    originalBuffer: null,
    musicName: '',
    videoName: '',
    exportAbort: null,

    init() {
      this.video = $('video');
      this.trackVideo = $('trackVideo');
      this.canvas = $('preview');
      this.comp = new NYO.Compositor(this.canvas);
      this.timeline = new NYO.Timeline(this);
      this.bindUI();
      this.renderPanel();
      this.timeline.render();
      const fonts = ['500 40px "Playfair Display"', 'italic 400 40px "Playfair Display"', '300 30px Poppins', '400 30px Poppins', '500 30px Poppins'];
      Promise.all(fonts.map((f) => document.fonts.load(f))).then(() => this.requestDraw());
      this.requestDraw();
      this.loop();
    },

    /* ---------- audio ---------- */
    audioCtx() {
      if (!this._actx) this._actx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 48000 });
      if (this._actx.state === 'suspended') this._actx.resume();
      return this._actx;
    },
    buffers() { return { music: this.musicBuffer, original: this.originalBuffer }; },

    /* ---------- playback ---------- */
    play() {
      if (this.playing) return;
      if (this.time >= this.project.duration - 0.02) this.time = 0;
      const ctx = this.audioCtx();
      const when = ctx.currentTime + 0.08;
      this.audioHandle = NYO.AudioEngine.schedule(ctx, ctx.destination, this.project, this.time, when, this.buffers());
      this.clock = { ctxT: when, t: this.time };
      this.playing = true;
      $('btnPlay').textContent = '❚❚';
      if (this.hasVideo()) {
        this.video.currentTime = this.time;
        this.video.play().catch(() => {});
      }
    },
    pause() {
      if (!this.playing) return;
      this.playing = false;
      $('btnPlay').textContent = '▶';
      if (this.audioHandle) { this.audioHandle.stop(); this.audioHandle = null; }
      this.video.pause();
      this.seek(this.time);
    },
    toggle() { this.playing ? this.pause() : this.play(); },
    restartAudio() {
      if (!this.playing) return;
      this.pause(); this.play();
    },
    seek(t) {
      t = clamp(t, 0, this.project.duration);
      this.time = t;
      if (this.playing) { this.pause(); this.time = t; }
      if (this.hasVideo()) {
        // Show the source frame that covers time t.
        const target = Math.min(this.video.duration - 0.002, t + 0.5 / NYO.FPS);
        if (Math.abs(this.video.currentTime - target) > 0.001) this.video.currentTime = target;
      }
      this.requestDraw();
      this.timeline.updatePlayhead();
      this.updateTimecode();
      if (this.tab === 'labels') this.refreshKeyTable();
    },
    step(frames) {
      const f = Math.round(this.time * NYO.FPS) + frames;
      this.seek(f / NYO.FPS);
    },
    hasVideo() { return this.video.readyState >= 1 && this.video.videoWidth > 0; },

    loop() {
      const tick = () => {
        if (this.playing) {
          const ctx = this._actx;
          this.time = this.clock.t + (ctx.currentTime - this.clock.ctxT);
          if (this.time < this.clock.t) this.time = this.clock.t;
          if (this.time >= this.project.duration) {
            this.time = this.project.duration;
            this.pause();
          } else if (this.hasVideo() && !this.video.paused && Math.abs(this.video.currentTime - this.time) > 0.12) {
            this.video.currentTime = this.time; // resync to the audio clock
          }
          this.timeline.updatePlayhead();
          this.updateTimecode();
          this.dirty = true;
        }
        if (this.dirty) { this.dirty = false; this.draw(); }
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    },
    requestDraw() { this.dirty = true; },
    draw() {
      const want = this.hq ? [1080, 1920] : [540, 960];
      if (this.canvas.width !== want[0]) { this.canvas.width = want[0]; this.canvas.height = want[1]; }
      this.comp.render(this.time, this.project, this.hasVideo() ? this.video : null, {
        compare: this.holdBefore ? 'before' : this.compare,
        split: this.split,
        safeZones: this.project.view && this.project.view.safeZones
      });
      // Editing guides (preview only).
      const ctx = this.comp.ctx;
      const sel = this.selection;
      if (sel && sel.type === 'label') {
        const l = this.project.labels.find((q) => q.id === sel.id);
        if (l && l.connector === 'tracked' && this.comp.rect) {
          const s = NYO.Track.sample(l, this.time);
          const r = this.comp.rect;
          const ki = NYO.Track.keyAt(l, this.time);
          if (s) {
            ctx.save();
            ctx.strokeStyle = ki >= 0 ? '#ffffff' : 'rgba(255,255,255,0.6)';
            ctx.setLineDash(ki >= 0 ? [] : [4, 3]);
            ctx.lineWidth = 1.5;
            const x = r.x + s.x * r.w, y = r.y + s.y * r.h;
            ctx.beginPath(); ctx.arc(x, y, 14 * this.comp.S * 2, 0, Math.PI * 2); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(x - 6, y); ctx.lineTo(x + 6, y); ctx.moveTo(x, y - 6); ctx.lineTo(x, y + 6); ctx.stroke();
            ctx.restore();
          }
        }
      }
      if (sel && sel.type === 'caption') {
        const hb = this.comp.hit.captions.find((q) => q.id === sel.id);
        if (hb) { ctx.save(); ctx.strokeStyle = 'rgba(214,183,122,0.8)'; ctx.setLineDash([5, 4]); ctx.strokeRect(hb.x, hb.y, hb.w, hb.h); ctx.restore(); }
      }
    },
    updateTimecode() {
      $('timecode').textContent = `${fmt(this.time)} · f${Math.round(this.time * NYO.FPS)} / ${fmt(this.project.duration)}`;
    },

    /* ---------- model changes ---------- */
    changed(kind, opts) {
      opts = opts || {};
      NYO.saveProjectLocal(this.project);
      this.requestDraw();
      if (!opts.noTimeline) this.timeline.render();
      if (!opts.noPanel) this.renderPanel();
      if (kind === 'audio' || kind === 'sfx') {
        clearTimeout(this._audioT);
        this._audioT = setTimeout(() => this.restartAudio(), 250);
      }
    },
    select(type, id) {
      this.selection = { type, id };
      this.selKey = -1;
      const want = type === 'caption' ? 'text' : type === 'label' ? 'labels' : type === 'sfx' ? 'audio' : this.tab;
      if (want !== this.tab) this.setTab(want); else this.renderPanel();
      this.timeline.render();
      this.requestDraw();
    },
    setTab(tab) {
      this.tab = tab;
      document.querySelectorAll('.tab').forEach((b) => b.classList.toggle('active', b.dataset.tab === tab));
      this.renderPanel();
    },
    toast(msg, ms) {
      const t = $('toast');
      t.textContent = msg; t.classList.add('show');
      clearTimeout(this._toastT);
      this._toastT = setTimeout(() => t.classList.remove('show'), ms || 3200);
    },

    /* ---------- media loading ---------- */
    async loadVideo(file) {
      if (!file) return;
      this.pause();
      if (this.videoURL) URL.revokeObjectURL(this.videoURL);
      this.videoURL = URL.createObjectURL(file);
      this.videoName = file.name;
      this.video.src = this.videoURL;
      this.trackVideo.src = this.videoURL;
      this.video.muted = true; // original audio is muted; it can be mixed back in via Audio › Original audio
      await new Promise((res, rej) => {
        this.video.onloadeddata = res;
        this.video.onerror = () => rej(new Error('This browser cannot decode the video. Use an H.264 MP4 in Chrome or Edge.'));
      }).catch((e) => { this.toast(e.message, 6000); throw e; });
      const v = this.video, dur = Math.round(v.duration * 1000) / 1000;
      const matches = NYO.matchesBundledFootage(v.videoWidth, v.videoHeight, v.duration);
      if (matches) {
        this.project.duration = dur;
        this.toast('Original footage recognised: measured softgel tracking keyframes applied.', 4500);
      } else {
        if (Math.abs(dur - this.project.duration) > 0.05) NYO.retimeProject(this.project, dur);
        this.project.labels.forEach((l) => { if (l.connector === 'tracked') l.keyframes = []; });
        this.toast(`Timeline adapted to ${dur.toFixed(2)} s. This is a different clip, so tracking keyframes were cleared: set them in Labels & Tracking.`, 7000);
      }
      this.project.source = { name: file.name, width: v.videoWidth, height: v.videoHeight, duration: dur };
      this.changed('video');
      this.seek(Math.min(this.time, dur));
      $('dropHint').style.display = 'none';
      // Decode the original soundtrack (muted by default, available in the mix).
      file.arrayBuffer().then((ab) => this.audioCtx().decodeAudioData(ab)).then((b) => { this.originalBuffer = b; }).catch(() => { this.originalBuffer = null; });
      await new Promise((r) => { if (this.trackVideo.readyState >= 2) r(); else this.trackVideo.onloadeddata = r; });
      this.timeline.buildThumbs(this.trackVideo);
    },
    async loadMusic(file) {
      if (!file) return;
      try {
        const ab = await file.arrayBuffer();
        this.musicBuffer = await this.audioCtx().decodeAudioData(ab);
        this.musicName = file.name;
        this.project.audio.music = 'file';
        this.changed('audio');
        this.toast(`Music loaded: ${file.name} (${this.musicBuffer.duration.toFixed(1)} s)`);
      } catch (e) {
        this.toast('Could not decode that audio file.', 4000);
      }
    },

    /* ---------- UI bindings ---------- */
    bindUI() {
      $('videoFile').addEventListener('change', (e) => this.loadVideo(e.target.files[0]));
      $('loadProject').addEventListener('change', async (e) => {
        const f = e.target.files[0]; if (!f) return;
        try {
          const p = JSON.parse(await f.text());
          if (p.version !== 1) throw new Error('Unsupported project file');
          this.project = p; this.selection = null;
          this.changed('project');
          this.toast('Project opened.');
        } catch (err) { this.toast('Could not open project: ' + err.message, 5000); }
        e.target.value = '';
      });
      $('saveProject').addEventListener('click', () => {
        const blob = new Blob([JSON.stringify(this.project, null, 2)], { type: 'application/json' });
        this.download(blob, 'ageless-nyo3-project.json');
      });
      $('resetProject').addEventListener('click', () => {
        if (!confirm('Restore the default Ageless by NYO3 edit? Your current text, timing and settings will be replaced.')) return;
        const src = this.project.source;
        this.project = NYO.defaultProject();
        if (this.hasVideo()) {
          const v = this.video;
          if (NYO.matchesBundledFootage(v.videoWidth, v.videoHeight, v.duration)) this.project.duration = Math.round(v.duration * 1000) / 1000;
          else { NYO.retimeProject(this.project, Math.round(v.duration * 1000) / 1000); this.project.labels.forEach((l) => { if (l.connector === 'tracked') l.keyframes = []; }); }
          this.project.source = src;
        }
        this.selection = null;
        this.changed('project');
      });
      document.querySelectorAll('.tab').forEach((b) => b.addEventListener('click', () => this.setTab(b.dataset.tab)));
      $('btnPlay').addEventListener('click', () => this.toggle());
      $('btnPrev').addEventListener('click', () => this.step(-1));
      $('btnNext').addEventListener('click', () => this.step(1));
      $('btnStart').addEventListener('click', () => this.seek(0));
      $('compareMode').addEventListener('change', (e) => { this.compare = e.target.value; this.requestDraw(); });
      $('safeZones').checked = !!(this.project.view && this.project.view.safeZones);
      $('safeZones').addEventListener('change', (e) => { this.project.view = this.project.view || {}; this.project.view.safeZones = e.target.checked; this.changed('view', { noPanel: true, noTimeline: true }); });
      $('addCaption').addEventListener('click', () => this.addCaption());
      $('addLabel').addEventListener('click', () => this.addLabel());
      $('addSfx').addEventListener('click', () => this.addSfx());
      $('tlZoom').addEventListener('input', () => { this.timeline._userZoom = true; });

      this.video.addEventListener('seeked', () => this.requestDraw());
      this.video.addEventListener('loadeddata', () => this.requestDraw());

      const wrap = $('previewWrap');
      wrap.addEventListener('dragover', (e) => { e.preventDefault(); wrap.classList.add('drag'); });
      wrap.addEventListener('dragleave', () => wrap.classList.remove('drag'));
      wrap.addEventListener('drop', (e) => {
        e.preventDefault(); wrap.classList.remove('drag');
        const f = [...e.dataTransfer.files].find((x) => x.type.startsWith('video/'));
        if (f) this.loadVideo(f);
      });

      this.bindPreviewPointer();

      window.addEventListener('keydown', (e) => {
        if (/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) return;
        if (e.code === 'Space') { e.preventDefault(); this.toggle(); }
        else if (e.code === 'ArrowLeft') { e.preventDefault(); this.step(e.shiftKey ? -10 : -1); }
        else if (e.code === 'ArrowRight') { e.preventDefault(); this.step(e.shiftKey ? 10 : 1); }
        else if (e.code === 'Home') this.seek(0);
        else if (e.code === 'End') this.seek(this.project.duration);
        else if (e.code === 'KeyK') this.keyframeAtPlayhead();
        else if (e.code === 'KeyB' && !this.holdBefore) { this.holdBefore = true; this.requestDraw(); }
        else if ((e.code === 'Delete' || e.code === 'Backspace') && this.selection && this.selection.type === 'label') this.deleteKeyAtPlayhead();
      });
      window.addEventListener('keyup', (e) => { if (e.code === 'KeyB') { this.holdBefore = false; this.requestDraw(); } });
    },

    canvasPoint(e) {
      const r = this.canvas.getBoundingClientRect();
      return { x: (e.clientX - r.left) / r.width * this.canvas.width, y: (e.clientY - r.top) / r.height * this.canvas.height };
    },

    bindPreviewPointer() {
      this.canvas.addEventListener('pointerdown', (e) => {
        const p = this.canvasPoint(e);
        const S = this.comp.S;
        const sel = this.selection;
        // 1) Click-to-keyframe for the selected tracked label.
        if (this.clickToKey && sel && sel.type === 'label' && this.comp.rect) {
          const l = this.project.labels.find((q) => q.id === sel.id);
          if (l) {
            const r = this.comp.rect;
            const set = (pt) => {
              NYO.Track.setKey(l, Math.round(this.time * NYO.FPS) / NYO.FPS, clamp((pt.x - r.x) / r.w, 0, 1), clamp((pt.y - r.y) / r.h, 0, 1));
              this.requestDraw();
            };
            set(p);
            this.dragOnCanvas(e, (pt) => set(pt), () => this.changed('keyframes'));
            return;
          }
        }
        // 2) Labels (cards): drag to reposition.
        const lh = [...this.comp.hit.labels].reverse().find((b) => p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h);
        if (lh) {
          const l = this.project.labels.find((q) => q.id === lh.id);
          this.select('label', l.id);
          let last = p;
          this.dragOnCanvas(e, (pt) => {
            const dx = (pt.x - last.x) / S, dy = (pt.y - last.y) / S; last = pt;
            if (l.connector === 'tracked') { l.cardDx = Math.round(l.cardDx + dx); l.cardDy = Math.round(l.cardDy + dy); }
            else { l.freeX = clamp(l.freeX + dx / NYO.OUT_W, 0, 1); l.freeY = clamp(l.freeY + dy / NYO.OUT_H, 0, 1); }
            this.requestDraw();
          }, () => this.changed('label'));
          return;
        }
        // 3) Captions: drag to reposition.
        const ch = [...this.comp.hit.captions].reverse().find((b) => p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h);
        if (ch) {
          const c = this.project.captions.find((q) => q.id === ch.id);
          this.select('caption', c.id);
          let last = p;
          this.dragOnCanvas(e, (pt) => {
            c.x = clamp(c.x + (pt.x - last.x) / S / NYO.OUT_W, 0.05, 0.95);
            c.y = clamp(c.y + (pt.y - last.y) / S / NYO.OUT_H, 0.03, 0.97);
            last = pt; this.requestDraw();
          }, () => this.changed('caption'));
          return;
        }
        // 4) Split compare: drag the divider.
        if (this.compare === 'split') {
          const set = (pt) => { this.split = clamp(pt.x / this.canvas.width, 0, 1); this.requestDraw(); };
          set(p); this.dragOnCanvas(e, set);
        }
      });
    },
    dragOnCanvas(e, onMove, onEnd) {
      this.canvas.setPointerCapture(e.pointerId);
      const move = (ev) => onMove(this.canvasPoint(ev));
      const up = () => {
        this.canvas.removeEventListener('pointermove', move);
        this.canvas.removeEventListener('pointerup', up);
        onEnd && onEnd();
      };
      this.canvas.addEventListener('pointermove', move);
      this.canvas.addEventListener('pointerup', up);
    },

    /* ---------- add / remove ---------- */
    addCaption() {
      const t = this.time;
      const c = {
        id: NYO.uid('c'), name: 'New caption', start: Math.round(t * 100) / 100, end: Math.min(this.project.duration, t + 3),
        x: 0.5, y: 0.3, anim: 'fadeUpZoom', inDur: 0.8, outDur: 0.5, backdrop: 'scrim', backdropOpacity: 0.34, maxWidth: 0.84,
        lines: [NYO.line('Your text here', { size: 58 })]
      };
      this.project.captions.push(c);
      this.select('caption', c.id);
      this.changed('caption');
    },
    addLabel() {
      const t = this.time;
      const l = {
        id: NYO.uid('l'), name: 'New label', title: 'DAY CARE ☀️', subtitle: 'Morning Routine',
        start: Math.round(t * 100) / 100, end: Math.min(this.project.duration, t + 3), connector: 'tracked', target: 'red', side: 'left',
        freeX: 0.5, freeY: 0.4, cardDx: -70, cardDy: -150, dotDx: -36, dotDy: 0, keyframes: [],
        titleSize: 40, subSize: 22, titleColor: NYO.PALETTE.ivory, subColor: NYO.PALETTE.gold, accent: NYO.PALETTE.gold,
        inDur: 0.55, outDur: 0.4, maxGap: 0.6, enabled: true
      };
      this.project.labels.push(l);
      this.select('label', l.id);
      this.clickToKey = true;
      this.changed('label');
      this.toast('New tracked label: click the softgel in the preview to set keyframes, or use Auto-track.', 5000);
    },
    addSfx() {
      const cue = { id: NYO.uid('x'), type: 'sparkle', link: null, offset: 0, t: Math.round(this.time * 1000) / 1000, gain: 0.5 };
      this.project.sfx.push(cue);
      this.select('sfx', cue.id);
      this.changed('sfx');
    },

    /* ---------- keyframes ---------- */
    selLabel() {
      const s = this.selection;
      return s && s.type === 'label' ? this.project.labels.find((l) => l.id === s.id) : null;
    },
    keyframeAtPlayhead() {
      const l = this.selLabel();
      if (!l || l.connector !== 'tracked') return this.toast('Select a tracked label first.');
      const s = NYO.Track.sample(l, this.time) || { x: 0.5, y: 0.5 };
      NYO.Track.setKey(l, Math.round(this.time * NYO.FPS) / NYO.FPS, s.x, s.y);
      this.changed('keyframes');
      this.toast(`Keyframe set at ${this.time.toFixed(3)} s. Drag in the preview with click-to-keyframe on to correct it.`);
    },
    deleteKeyAtPlayhead() {
      const l = this.selLabel(); if (!l) return;
      const i = NYO.Track.keyAt(l, this.time);
      if (i >= 0) { l.keyframes.splice(i, 1); this.changed('keyframes'); }
    },

    download(blob, name) {
      const a = h('a', { href: URL.createObjectURL(blob), download: name });
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 60000);
    },

    /* ---------- panels ---------- */
    renderPanel() {
      const body = $('tabBody');
      const st = body.scrollTop;
      body.innerHTML = '';
      const builder = { text: this.panelText, labels: this.panelLabels, color: this.panelColor, audio: this.panelAudio, layout: this.panelLayout, export: this.panelExport }[this.tab];
      builder.call(this, body);
      body.scrollTop = st;
    },

    // Generic field helpers. `obj[key]` is edited live.
    num(obj, key, opts) {
      opts = opts || {};
      const inp = h('input', { type: 'number', step: opts.step || 0.01, min: opts.min, max: opts.max, value: obj[key] });
      inp.addEventListener('input', () => {
        const v = parseFloat(inp.value); if (isNaN(v)) return;
        obj[key] = opts.min != null ? Math.max(opts.min, opts.max != null ? Math.min(opts.max, v) : v) : v;
        if (opts.after) opts.after();
        this.changed(opts.kind || 'edit', { noPanel: true, noTimeline: !opts.timeline });
      });
      inp.addEventListener('change', () => { if (opts.timeline) this.timeline.render(); });
      return inp;
    },
    txt(obj, key, opts) {
      opts = opts || {};
      const inp = h(opts.area ? 'textarea' : 'input', opts.area ? { rows: 2 } : { type: 'text' });
      inp.value = obj[key] || '';
      inp.addEventListener('input', () => { obj[key] = inp.value; this.changed(opts.kind || 'edit', { noPanel: true, noTimeline: !opts.timeline }); });
      return inp;
    },
    sel(obj, key, options, opts) {
      opts = opts || {};
      const s = h('select', null, options.map(([v, label]) => h('option', { value: v, text: label })));
      s.value = obj[key] == null ? '' : obj[key];
      s.addEventListener('change', () => {
        obj[key] = s.value === '' && opts.nullable ? null : (opts.number ? +s.value : s.value);
        if (opts.after) opts.after();
        this.changed(opts.kind || 'edit', { noPanel: !opts.panel, noTimeline: !opts.timeline });
      });
      return s;
    },
    color(obj, key, kind) {
      const c = h('input', { type: 'color', value: obj[key] });
      c.addEventListener('input', () => { obj[key] = c.value; this.changed(kind || 'edit', { noPanel: true, noTimeline: true }); });
      return c;
    },
    check(obj, key, label, opts) {
      opts = opts || {};
      const c = h('input', { type: 'checkbox' });
      c.checked = !!obj[key];
      c.addEventListener('change', () => { obj[key] = c.checked; this.changed(opts.kind || 'edit', { noPanel: !opts.panel, noTimeline: !opts.timeline }); });
      return h('label', { class: 'chk' }, [c, ' ' + label]);
    },
    slider(label, obj, key, min, max, step, opts) {
      opts = opts || {};
      const out = h('output', { text: (+obj[key]).toFixed(step < 1 ? 2 : 0) + (opts.unit || '') });
      const r = h('input', { type: 'range', min, max, step, value: obj[key] });
      r.addEventListener('input', () => {
        obj[key] = +r.value;
        out.textContent = (+r.value).toFixed(step < 1 ? 2 : 0) + (opts.unit || '');
        if (opts.after) opts.after();
        this.changed(opts.kind || 'edit', { noPanel: true, noTimeline: !opts.timeline });
      });
      r.addEventListener('dblclick', () => { if (opts.reset != null) { obj[key] = opts.reset; r.value = opts.reset; r.dispatchEvent(new Event('input')); } });
      return h('div', { class: 'slider', title: opts.title || '' }, [h('label', { text: label }), r, out]);
    },
    row(label, input) { return h('div', { class: 'row' }, [h('label', { text: label }), input]); },
    field(label, input) { return h('div', { class: 'field' }, [h('span', { text: label }), input]); },
    section(title, children, note) {
      return h('div', { class: 'section' }, [h('h3', { text: title }), note ? h('p', { class: 'note', html: note }) : null].concat(children));
    },

    listOf(items, type, metaFn) {
      return h('div', { class: 'list' }, items.map((it) => {
        const sel = this.selection && this.selection.id === it.id;
        const cb = h('input', { type: 'checkbox' });
        cb.checked = it.enabled !== false;
        cb.addEventListener('click', (e) => e.stopPropagation());
        cb.addEventListener('change', () => { it.enabled = cb.checked; this.changed(type); });
        return h('div', { class: 'list-item' + (sel ? ' sel' : '') + (it.enabled === false ? ' off' : ''), onclick: () => { this.select(type, it.id); this.seek(it.start + 0.6 > it.end ? it.start : it.start + Math.min(1.2, (it.end - it.start) / 2)); } }, [cb, h('span', { text: it.name }), h('span', { class: 'meta', text: metaFn(it) })]);
      }));
    },

    panelText(body) {
      const p = this.project;
      body.appendChild(this.section('Captions', [
        this.listOf(p.captions, 'caption', (c) => `${c.start.toFixed(1)}–${c.end.toFixed(1)}s`),
        h('div', { class: 'btn-row' }, [
          h('button', { class: 'btn btn-sm', text: '+ Add caption', onclick: () => this.addCaption() }),
          h('button', { class: 'btn btn-sm', text: 'Duplicate', onclick: () => {
            const c = this.selection && p.captions.find((q) => q.id === this.selection.id); if (!c) return;
            const d = JSON.parse(JSON.stringify(c)); d.id = NYO.uid('c'); d.name += ' copy'; p.captions.push(d); this.select('caption', d.id); this.changed('caption');
          } }),
          h('button', { class: 'btn btn-sm btn-danger', text: 'Delete', onclick: () => {
            if (!this.selection || this.selection.type !== 'caption') return;
            p.captions = p.captions.filter((q) => q.id !== this.selection.id);
            p.sfx.forEach((s) => { if (s.link === this.selection.id) { s.t = NYO.sfxTime(p, s) || 0; s.link = null; } });
            this.selection = null; this.changed('caption');
          } })
        ])
      ], 'Click a caption to edit it. Drag it in the preview to reposition; drag/trim it on the timeline to retime.'));

      const c = this.selection && this.selection.type === 'caption' && p.captions.find((q) => q.id === this.selection.id);
      if (!c) return;
      const tl = { kind: 'caption', timeline: true, step: 1 / 30 };
      body.appendChild(this.section('Selected caption', [
        this.row('Name', this.txt(c, 'name', { kind: 'caption', timeline: true })),
        h('div', { class: 'row3' }, [
          this.field('Start (s)', this.num(c, 'start', Object.assign({ min: 0 }, tl))),
          this.field('End (s)', this.num(c, 'end', Object.assign({ min: 0 }, tl))),
          this.field('Animation', this.sel(c, 'anim', [['fadeUpZoom', 'Fade · rise · zoom'], ['slideUp', 'Slide up'], ['reveal', 'Cinematic reveal'], ['stagger', 'Staggered'], ['cinematic', 'Slow cinematic']], { kind: 'caption' }))
        ]),
        h('div', { class: 'row3' }, [
          this.field('In (s)', this.num(c, 'inDur', { min: 0.05, step: 0.05 })),
          this.field('Out (s)', this.num(c, 'outDur', { min: 0.05, step: 0.05 })),
          this.field('Backdrop', this.sel(c, 'backdrop', [['scrim', 'Soft scrim'], ['glass', 'Frosted glass panel'], ['none', 'None']]))
        ]),
        this.slider('Position X', c, 'x', 0.05, 0.95, 0.005),
        this.slider('Position Y', c, 'y', 0.03, 0.97, 0.005),
        this.slider('Max width', c, 'maxWidth', 0.4, 0.95, 0.01),
        this.slider('Scrim opacity', c, 'backdropOpacity', 0, 0.8, 0.01)
      ]));

      const lines = h('div');
      c.lines.forEach((ln, i) => {
        lines.appendChild(h('div', { class: 'line-card' }, [
          h('div', { class: 'hdr' }, [h('span', { text: `Line ${i + 1}` }), h('button', { class: 'btn btn-sm btn-ghost btn-danger', text: 'Remove', onclick: () => { c.lines.splice(i, 1); this.changed('caption'); } })]),
          this.txt(ln, 'text', { area: true }),
          h('div', { class: 'row3' }, [
            this.field('Font', this.sel(ln, 'font', [['serif', 'Playfair Display'], ['sans', 'Poppins']])),
            this.field('Weight', this.sel(ln, 'weight', [[300, 'Light 300'], [400, 'Regular 400'], [500, 'Medium 500'], [600, 'Semibold 600']], { number: true })),
            this.field('Size (px @1080)', this.num(ln, 'size', { min: 12, max: 160, step: 1 }))
          ]),
          h('div', { class: 'row3' }, [
            this.field('Colour', this.color(ln, 'color')),
            this.field('Letter spacing', this.num(ln, 'tracking', { step: 0.5 })),
            this.field('Delay (s)', this.num(ln, 'delay', { min: 0, step: 0.05 }))
          ]),
          h('div', { class: 'row3' }, [
            this.field('Highlight word', this.txt(ln, 'highlight')),
            this.field('Highlight colour', this.color(ln, 'highlightColor')),
            this.field('Style', this.check(ln, 'italic', 'Italic'))
          ]),
          h('div', { class: 'btn-row' }, Object.entries(NYO.PALETTE).map(([n, v]) => h('button', { class: 'btn btn-sm', text: n, style: `border-color:${v}`, onclick: () => { ln.color = v; this.changed('caption'); } })))
        ]));
      });
      body.appendChild(this.section('Lines', [lines, h('button', { class: 'btn btn-sm', text: '+ Add line', onclick: () => { c.lines.push(NYO.line('New line', { font: 'sans', weight: 300, size: 32 })); this.changed('caption'); } })], 'Palette: champagne gold #D6B77A · ivory #FFF9F0 · soft rose #E8B7BE.'));
    },

    panelLabels(body) {
      const p = this.project;
      const matches = this.hasVideo() && NYO.matchesBundledFootage(this.video.videoWidth, this.video.videoHeight, this.video.duration);
      body.appendChild(this.section('Labels', [
        this.listOf(p.labels, 'label', (l) => `${l.connector === 'tracked' ? '⌖ ' + l.keyframes.length + ' kf · ' : ''}${l.start.toFixed(1)}–${l.end.toFixed(1)}s`),
        h('div', { class: 'btn-row' }, [
          h('button', { class: 'btn btn-sm', text: '+ Add label', onclick: () => this.addLabel() }),
          h('button', { class: 'btn btn-sm', text: 'Duplicate', onclick: () => {
            const l = this.selLabel(); if (!l) return;
            const d = JSON.parse(JSON.stringify(l)); d.id = NYO.uid('l'); d.name += ' copy'; p.labels.push(d); this.select('label', d.id); this.changed('label');
          } }),
          h('button', { class: 'btn btn-sm btn-danger', text: 'Delete', onclick: () => {
            const l = this.selLabel(); if (!l) return;
            p.labels = p.labels.filter((q) => q.id !== l.id);
            p.sfx.forEach((s) => { if (s.link === l.id) { s.link = null; s.t = l.start + (s.offset || 0); } });
            this.selection = null; this.changed('label');
          } })
        ])
      ], '<b>How tracking works here:</b> the red &amp; black softgel keyframes were <i>measured from your clip</i> by template matching (frame by frame). In the editor, <b>Auto-track</b> runs the same kind of matcher in your browser from any keyframe you set. It stops and tells you when it loses the object. Every keyframe stays editable.<br><br>In your footage the blister pack is only on screen at <b>≈0.9–2.7 s</b> and <b>≈29.0–30.1 s</b>. Scenes 4–5 (12–22 s) show the box, so those two are floating cards without a softgel connector.'));

      const l = this.selLabel();
      if (!l) return;
      const tl = { kind: 'label', timeline: true, step: 1 / 30 };
      body.appendChild(this.section('Selected label', [
        this.row('Name', this.txt(l, 'name', { kind: 'label', timeline: true })),
        h('div', { class: 'row2' }, [this.field('Title', this.txt(l, 'title')), this.field('Subtitle', this.txt(l, 'subtitle'))]),
        h('div', { class: 'row3' }, [
          this.field('Start (s)', this.num(l, 'start', Object.assign({ min: 0 }, tl))),
          this.field('End (s)', this.num(l, 'end', Object.assign({ min: 0 }, tl))),
          this.field('Connector', this.sel(l, 'connector', [['tracked', 'Tracked line + dot'], ['none', 'Card only']], { kind: 'label', panel: true, timeline: true }))
        ]),
        h('div', { class: 'row3' }, [
          this.field('Target', this.sel(l, 'target', [['red', 'Red softgel (DAY)'], ['black', 'Black softgel (NIGHT)'], ['other', 'Other']])),
          this.field('Card side', this.sel(l, 'side', [['left', 'Left'], ['right', 'Right']])),
          this.field('Title size', this.num(l, 'titleSize', { min: 16, max: 90, step: 1 }))
        ]),
        h('div', { class: 'row3' }, [
          this.field('Title colour', this.color(l, 'titleColor')),
          this.field('Subtitle colour', this.color(l, 'subColor')),
          this.field('Line / dot', this.color(l, 'accent'))
        ]),
        l.connector === 'tracked' ? h('div', null, [
          this.slider('Card offset X', l, 'cardDx', -400, 400, 1),
          this.slider('Card offset Y', l, 'cardDy', -400, 400, 1),
          this.slider('Dot offset X', l, 'dotDx', -120, 120, 1, { title: 'Moves the dot off the capsule so it never covers it' }),
          this.slider('Dot offset Y', l, 'dotDy', -120, 120, 1)
        ]) : h('div', null, [
          this.slider('Position X', l, 'freeX', 0.05, 0.95, 0.005),
          this.slider('Position Y', l, 'freeY', 0.05, 0.95, 0.005)
        ])
      ]));

      if (l.connector !== 'tracked') return;
      const prog = h('div', { class: 'progress' }, [h('div')]);
      const status = h('div', { class: 'status' });
      const runTrack = async (dir) => {
        if (!this.hasVideo()) return this.toast('Upload the video first.');
        this.pause();
        const from = Math.round(this.time * NYO.FPS) / NYO.FPS;
        const to = dir > 0 ? Math.min(l.end + 0.2, this.project.duration) : Math.max(l.start - 0.2, 0);
        if (Math.abs(to - from) < 1 / NYO.FPS) return this.toast('Move the playhead inside the label range first.');
        if (!NYO.Track.sample(l, from)) return this.toast('Set a keyframe on the softgel at the playhead first (click-to-keyframe).');
        if (NYO.Track.keyAt(l, from) < 0) { const s = NYO.Track.sample(l, from); NYO.Track.setKey(l, from, s.x, s.y); }
        status.textContent = 'Tracking…';
        const abort = new AbortController();
        this._trackAbort = abort;
        try {
          const res = await NYO.Track.autoTrack(this.trackVideo, l, from, to, {
            signal: abort.signal,
            onProgress: (f, t, sc) => { prog.firstChild.style.width = (f * 100).toFixed(1) + '%'; status.textContent = `Tracking ${t.toFixed(2)} s · match ${sc.toFixed(2)}`; }
          });
          status.textContent = res.lostAt != null
            ? `Tracked ${res.written} keyframes. Lost the object at ${res.lostAt.toFixed(2)} s (moved out of view, blurred or covered). Add a keyframe after that point and continue.`
            : `Tracked ${res.written} keyframes to ${to.toFixed(2)} s.`;
        } catch (e) { status.textContent = 'Tracking failed: ' + e.message; }
        this.changed('keyframes');
      };
      const kb = h('button', { class: 'btn btn-sm' + (this.clickToKey ? ' btn-gold' : ''), text: this.clickToKey ? '⌖ Click-to-keyframe: ON' : '⌖ Click-to-keyframe: OFF', onclick: () => { this.clickToKey = !this.clickToKey; this.renderPanel(); } });
      body.appendChild(this.section('Motion tracking', [
        h('div', { class: 'btn-row' }, [
          kb,
          h('button', { class: 'btn btn-sm', text: 'Key at playhead (K)', onclick: () => this.keyframeAtPlayhead() }),
          h('button', { class: 'btn btn-sm', text: 'Delete key', onclick: () => this.deleteKeyAtPlayhead() })
        ]),
        h('div', { class: 'btn-row' }, [
          h('button', { class: 'btn btn-sm', text: '◀ Prev key', onclick: () => { const k = l.keyframes.filter((q) => q[0] < this.time - 0.01).pop(); if (k) this.seek(k[0]); } }),
          h('button', { class: 'btn btn-sm', text: 'Next key ▶', onclick: () => { const k = l.keyframes.find((q) => q[0] > this.time + 0.01); if (k) this.seek(k[0]); } }),
          h('button', { class: 'btn btn-sm', text: 'Auto-track ◀ backward', onclick: () => runTrack(-1) }),
          h('button', { class: 'btn btn-sm', text: 'Auto-track forward ▶', onclick: () => runTrack(1) }),
          h('button', { class: 'btn btn-sm btn-ghost', text: 'Stop', onclick: () => this._trackAbort && this._trackAbort.abort() })
        ]),
        prog, status,
        h('div', { class: 'btn-row' }, [
          h('button', { class: 'btn btn-sm', text: 'Load measured ' + (l.target === 'black' ? 'black' : 'red') + ' softgel track', disabled: !matches || l.target === 'other', title: matches ? '' : 'Only for the original clip this preset was measured on', onclick: () => { l.keyframes = NYO.BUNDLED_TRACK[l.target === 'black' ? 'black' : 'red'].map((k) => k.slice()); this.changed('keyframes'); } }),
          h('button', { class: 'btn btn-sm btn-danger', text: 'Clear keys in label range', onclick: () => { l.keyframes = l.keyframes.filter((k) => k[0] < l.start - 0.3 || k[0] > l.end + 0.3); this.changed('keyframes'); } })
        ]),
        this.slider('Max key gap (s)', l, 'maxGap', 0.1, 3, 0.05, { title: 'Gaps longer than this hide the label (object off screen)' }),
        h('div', { class: 'kf-wrap' }, [this.keyTable(l)])
      ], 'With <b>Click-to-keyframe</b> on, click or drag the capsule in the preview to set its position at the current frame. Step with ←/→. Keyframes are softgel centres; the dot offset keeps the dot beside the capsule, never on top of it.'));
    },
    keyTable(l) {
      const tb = h('tbody');
      l.keyframes.forEach((kf, i) => {
        const tr = h('tr', { class: Math.abs(kf[0] - this.time) < 0.5 / NYO.FPS ? 'cur' : '', onclick: () => this.seek(kf[0]) }, [
          h('td', { text: kf[0].toFixed(3) + 's' }), h('td', { text: (kf[1] * 100).toFixed(1) + '%' }), h('td', { text: (kf[2] * 100).toFixed(1) + '%' }),
          h('td', null, [h('button', { class: 'btn btn-sm btn-ghost', text: '✕', onclick: (e) => { e.stopPropagation(); l.keyframes.splice(i, 1); this.changed('keyframes'); } })])
        ]);
        tb.appendChild(tr);
      });
      this._keyTable = h('table', { class: 'kf-table' }, [h('thead', null, [h('tr', null, [h('th', { text: 'Time' }), h('th', { text: 'X' }), h('th', { text: 'Y' }), h('th')])]), tb]);
      return this._keyTable;
    },
    refreshKeyTable() {
      if (!this._keyTable || !this._keyTable.isConnected) return;
      const l = this.selLabel(); if (!l) return;
      [...this._keyTable.tBodies[0].rows].forEach((tr, i) => {
        const kf = l.keyframes[i];
        tr.className = kf && Math.abs(kf[0] - this.time) < 0.5 / NYO.FPS ? 'cur' : '';
      });
    },

    panelColor(body) {
      const g = this.project.grade;
      const presetSel = h('select', null, Object.entries(NYO.GRADE_PRESETS).map(([k, v]) => h('option', { value: k, text: v.name })));
      presetSel.value = g.preset || 'warm-ivory';
      presetSel.addEventListener('change', () => { Object.assign(g, NYO.GRADE_PRESETS[presetSel.value].values); g.preset = presetSel.value; this.changed('grade'); });
      const D = NYO.GRADE_PRESETS['warm-ivory'].values;
      const s = (label, key, min, max, step, unit, title) => this.slider(label, g, key, min, max, step, { unit, reset: D[key], title, kind: 'grade' });
      const cmp = h('select', null, [['off', 'After (graded)'], ['split', 'Before | After split'], ['before', 'Before (original)']].map(([v, t]) => h('option', { value: v, text: t })));
      cmp.value = this.compare;
      cmp.addEventListener('change', () => { this.compare = cmp.value; $('compareMode').value = cmp.value; this.requestDraw(); });
      body.appendChild(this.section('Grade', [
        this.row('Preset', presetSel),
        this.row('Enabled', this.check(g, 'enabled', 'Apply colour grade', { kind: 'grade' })),
        this.row('Compare', cmp)
      ], 'Real per-pixel processing on the GPU (WebGL), not a coloured overlay. Double-click a slider to reset it. Hold <b>B</b> to see the original.'));
      body.appendChild(this.section('Light', [
        s('Exposure', 'exposure', -1, 1, 0.01, ' EV'),
        s('Brightness', 'brightness', -50, 50, 1, '%'),
        s('Contrast', 'contrast', -50, 50, 1, '%'),
        s('Highlights', 'highlights', -100, 100, 1, '%'),
        s('Shadows', 'shadows', -100, 100, 1, '%', 'Lifts low-mids while keeping true blacks (black softgels) deep'),
        s('Whites', 'whites', -50, 50, 1, '%'),
        s('Blacks', 'blacks', -50, 50, 1, '%'),
        s('Highlight roll-off', 'rolloff', 0, 100, 1, '%')
      ]));
      body.appendChild(this.section('Colour', [
        s('Temperature', 'temperature', -50, 50, 1, '', 'Positive = warmer'),
        s('Tint', 'tint', -50, 50, 1, '', 'Positive = magenta, negative = green'),
        s('Warm midtones', 'midWarmth', 0, 100, 1, '%'),
        s('Saturation', 'saturation', -50, 50, 1, '%'),
        s('Vibrance', 'vibrance', -50, 50, 1, '%'),
        s('Cast cleanup', 'castCorrection', 0, 100, 1, '%', 'Pulls near-neutral bright areas (beige wall, curtain) to clean warm ivory and neutralises shadows'),
        s('Skin protect', 'skinProtect', 0, 100, 1, '%', 'Keeps original skin hue: no orange/pink shift, no whitening'),
        s('Product protect', 'productProtect', 0, 100, 1, '%', 'Keeps the deep-red packaging and reddish-brown softgels true to the original')
      ]));
      body.appendChild(this.section('Finish', [
        s('Sharpening', 'sharpen', 0, 100, 1, '%'),
        s('Noise reduction', 'denoise', 0, 100, 1, '%'),
        s('Vignette', 'vignette', 0, 30, 1, '%')
      ]));
    },

    panelAudio(body) {
      const a = this.project.audio, p = this.project;
      const musicFile = h('input', { type: 'file', accept: 'audio/*', hidden: true });
      musicFile.addEventListener('change', () => this.loadMusic(musicFile.files[0]));
      body.appendChild(this.section('Background music', [
        this.row('Source', this.sel(a, 'music', [['generated', 'Original score (built-in)'], ['file', 'My licensed track'], ['none', 'None']], { kind: 'audio', panel: true, timeline: true })),
        a.music === 'file' ? h('div', { class: 'btn-row' }, [h('label', { class: 'btn btn-sm' }, ['Upload music…', musicFile]), h('span', { class: 'note', text: this.musicName || 'No file loaded' })]) : null,
        a.music === 'file' ? this.slider('Start offset', a, 'musicOffset', 0, 120, 0.1, { unit: ' s', kind: 'audio' }) : null,
        a.music === 'generated' ? this.slider('Tempo (BPM)', a, 'bpm', 95, 105, 1, { kind: 'audio', timeline: true }) : null,
        this.slider('Fade in', a, 'fadeIn', 0, 4, 0.1, { unit: ' s', kind: 'audio', timeline: true }),
        this.slider('Fade out', a, 'fadeOut', 0, 6, 0.1, { unit: ' s', kind: 'audio', timeline: true })
      ], 'The built-in score is composed and synthesised in code for this project: dreamy electric piano, ambient pads, a soft beat and bell arpeggios, no vocals. It contains no third-party samples, so there is nothing to license. To use a track from TikTok\'s Commercial Music Library or another licence you hold, choose “My licensed track”.'));
      body.appendChild(this.section('Mix', [
        this.slider('Master', a, 'master', 0, 1.2, 0.01, { kind: 'audio' }),
        this.slider('Music', a, 'musicVolume', 0, 1.2, 0.01, { kind: 'audio' }),
        this.slider('Sound FX', a, 'sfxVolume', 0, 1.5, 0.01, { kind: 'audio' }),
        this.slider('Original audio', a, 'originalVolume', 0, 1, 0.01, { kind: 'audio', title: 'Muted (0) per the brief' }),
        h('div', { class: 'btn-row' }, [h('button', { class: 'btn btn-sm', text: 'Download mix (WAV)', onclick: async () => {
          this.toast('Rendering audio…');
          const buf = await NYO.AudioEngine.renderOffline(this.project, this.buffers());
          this.download(NYO.AudioEngine.encodeWav(buf), 'ageless-nyo3-mix.wav');
          this.toast(`Mix rendered · peak ${(20 * Math.log10(NYO.AudioEngine.peak(buf) || 1e-6)).toFixed(1)} dBFS`);
        } })])
      ], 'The master bus has a gentle compressor and a limiter, so the mix does not clip.'));

      const linkOpts = [['', '— none (absolute time) —']].concat(p.captions.map((c) => [c.id, 'Caption: ' + c.name]), p.labels.map((l) => [l.id, 'Label: ' + l.name]));
      const list = h('div');
      p.sfx.slice().sort((x, y) => (NYO.sfxTime(p, x) || 0) - (NYO.sfxTime(p, y) || 0)).forEach((cue) => {
        const sel = this.selection && this.selection.type === 'sfx' && this.selection.id === cue.id;
        const T = NYO.sfxTime(p, cue);
        list.appendChild(h('div', { class: 'line-card', style: sel ? 'border-color: var(--gold)' : '' }, [
          h('div', { class: 'hdr' }, [
            h('span', { text: `${T == null ? 'disabled element' : T.toFixed(2) + ' s'} · ${NYO.SFX_TYPES[cue.type]}` }),
            h('span', null, [
              h('button', { class: 'btn btn-sm btn-ghost', text: '▶', title: 'Preview', onclick: () => NYO.AudioEngine.previewSfx(this.audioCtx(), p, cue.type, cue.gain) }),
              h('button', { class: 'btn btn-sm btn-ghost', text: 'Go', onclick: () => T != null && this.seek(Math.max(0, T - 0.3)) }),
              h('button', { class: 'btn btn-sm btn-ghost btn-danger', text: '✕', onclick: () => { p.sfx = p.sfx.filter((q) => q !== cue); this.changed('sfx'); } })
            ])
          ]),
          h('div', { class: 'row3' }, [
            this.field('Sound', this.sel(cue, 'type', Object.entries(NYO.SFX_TYPES), { kind: 'sfx', panel: true, timeline: true })),
            this.field('Synced to', this.sel(cue, 'link', linkOpts, { nullable: true, kind: 'sfx', panel: true, timeline: true, after: () => {
              if (cue.link) { const el = p.captions.concat(p.labels).find((e) => e.id === cue.link); cue.offset = Math.round(((cue.t || 0) - el.start) * 1000) / 1000; if (Math.abs(cue.offset) > 10) cue.offset = 0; }
              else cue.t = T || 0;
            } })),
            cue.link ? this.field('Offset (s)', this.num(cue, 'offset', { step: 0.01, kind: 'sfx', timeline: true })) : this.field('Time (s)', this.num(cue, 't', { min: 0, step: 0.01, kind: 'sfx', timeline: true }))
          ]),
          this.slider('Level', cue, 'gain', 0, 1.2, 0.01, { kind: 'sfx' })
        ]));
      });
      body.appendChild(this.section('Sound effects', [
        h('div', { class: 'btn-row' }, [h('button', { class: 'btn btn-sm', text: '+ Add at playhead', onclick: () => this.addSfx() })]),
        list
      ], 'Cues linked to a caption or label move with it on the timeline. All effects are synthesised, soft and low-passed (no harsh highs).'));
    },

    panelLayout(body) {
      const lay = this.project.layout;
      const src = this.project.source;
      body.appendChild(this.section('Frame', [
        this.row('Fit', this.sel(lay, 'fit', [['fit', 'Fit: preserve the full original frame'], ['fill', 'Fill: crop to 9:16']], { kind: 'layout' })),
        this.row('Background', this.sel(lay, 'background', [['blur', 'Soft blurred extension'], ['ivory', 'Solid warm ivory']], { kind: 'layout' })),
        this.row('Ivory colour', this.color(lay, 'ivory', 'layout')),
        this.slider('Zoom', lay, 'zoom', 1, 1.3, 0.005, { kind: 'layout' }),
        this.slider('Vertical offset', lay, 'offsetY', -0.1, 0.1, 0.001, { kind: 'layout' })
      ], src ? `Source: ${src.name} · ${src.width}×${src.height} · ${src.duration.toFixed(2)} s. Output: 1080×1920 (9:16) · 30 fps. Your clip is a little wider than 9:16, so <b>Fit</b> keeps every pixel and fills the small top and bottom bands; <b>Fill</b> crops about 7% from the sides.` : 'Upload your MP4 to see its details.'));
      const hq = h('input', { type: 'checkbox' });
      hq.checked = this.hq;
      hq.addEventListener('change', () => { this.hq = hq.checked; this.requestDraw(); });
      body.appendChild(this.section('Preview', [
        h('label', { class: 'chk' }, [hq, ' Full-resolution preview (1080×1920)']),
        h('div', { class: 'btn-row' }, [h('button', { class: 'btn btn-sm', text: 'Fit timeline to video length', onclick: () => {
          if (!this.hasVideo()) return this.toast('Upload the video first.');
          NYO.retimeProject(this.project, Math.round(this.video.duration * 1000) / 1000); this.changed('layout');
        } })])
      ]));
    },

    panelExport(body) {
      const capsBox = h('div', { class: 'caps', text: 'Checking encoder support…' });
      NYO.Exporter.capabilities().then((c) => {
        capsBox.innerHTML = `
          <div>${c.webcodecs ? '<span class="ok">✓</span>' : '<span class="no">✕</span>'} WebCodecs + MP4 muxer</div>
          <div>${c.video ? '<span class="ok">✓</span> H.264 video (' + c.video.codec + ')' : '<span class="no">✕</span> H.264 encoder'}</div>
          <div>${c.aac ? '<span class="ok">✓</span> AAC audio' : '<span class="no">✕</span> AAC encoder in this browser' + (c.opus ? ' (Opus will be used instead)' : '')}</div>`;
        if (!c.aac && c.video) capsBox.innerHTML += '<p class="note warn">This browser cannot encode AAC, so the MP4 will carry Opus audio. TikTok accepts it, but if you need strict H.264 + AAC, export in Chrome or Edge on Windows/macOS, or run the ffmpeg command below.</p>';
      });
      const bitrate = { v: 12e6 };
      const br = h('select', null, [[8e6, '8 Mbps'], [12e6, '12 Mbps (recommended)'], [16e6, '16 Mbps']].map(([v, t]) => h('option', { value: v, text: t })));
      br.value = 12e6;
      br.addEventListener('change', () => { bitrate.v = +br.value; });
      const prog = h('div', { class: 'progress' }, [h('div')]);
      const status = h('div', { class: 'status' });
      const result = h('div');
      const setP = (p, msg) => { prog.firstChild.style.width = (p * 100).toFixed(1) + '%'; status.textContent = msg; };
      const exportBtn = h('button', { class: 'btn btn-gold', text: 'Export MP4 · 1080×1920 · 30 fps' });
      const cancelBtn = h('button', { class: 'btn', text: 'Cancel', disabled: true });
      const rtBtn = h('button', { class: 'btn btn-sm', text: 'Real-time recording (fallback)' });
      const wavBtn = h('button', { class: 'btn btn-sm', text: 'Download audio mix (WAV)' });
      const busy = (b) => { exportBtn.disabled = b; rtBtn.disabled = b; cancelBtn.disabled = !b; };

      exportBtn.addEventListener('click', async () => {
        if (!this.hasVideo()) return this.toast('Upload your original MP4 first.');
        this.pause();
        busy(true); result.innerHTML = '';
        const abort = new AbortController(); this.exportAbort = abort;
        const t0 = performance.now();
        try {
          const r = await NYO.Exporter.exportMp4({ project: this.project, video: this.video, buffers: this.buffers(), bitrate: bitrate.v, signal: abort.signal, onProgress: setP });
          const secs = ((performance.now() - t0) / 1000).toFixed(0);
          const name = 'ageless-nyo3-tiktok-1080x1920.mp4';
          const url = URL.createObjectURL(r.blob);
          this.lastExport = r;
          result.appendChild(h('p', { class: 'note', html: `Rendered ${r.frames} frames in ${secs} s · ${(r.blob.size / 1048576).toFixed(1)} MB · video ${r.videoCodec} · audio ${r.audioCodec ? r.audioCodec.toUpperCase() : 'none'} · audio peak ${(20 * Math.log10(r.peak || 1e-6)).toFixed(1)} dBFS` }));
          result.appendChild(h('a', { class: 'btn btn-gold', href: url, download: name, text: '⬇ Download ' + name }));
          setP(1, 'Export complete.');
        } catch (e) {
          setP(0, e.name === 'AbortError' ? 'Export cancelled.' : 'Export failed: ' + e.message);
        }
        busy(false);
        this.seek(this.time);
      });
      cancelBtn.addEventListener('click', () => this.exportAbort && this.exportAbort.abort());
      rtBtn.addEventListener('click', async () => {
        if (!this.hasVideo()) return this.toast('Upload your original MP4 first.');
        this.pause(); busy(true); result.innerHTML = '';
        const abort = new AbortController(); this.exportAbort = abort;
        try {
          const r = await NYO.Exporter.recordRealtime({ app: this, signal: abort.signal, onProgress: setP });
          const ext = r.mime.includes('mp4') ? 'mp4' : 'webm';
          result.appendChild(h('p', { class: 'note', text: `Recorded in real time as ${r.mime}. ${ext === 'webm' ? 'Convert with the ffmpeg command below for an H.264/AAC MP4.' : ''}` }));
          result.appendChild(h('a', { class: 'btn btn-gold', href: URL.createObjectURL(r.blob), download: 'ageless-nyo3-realtime.' + ext, text: '⬇ Download recording' }));
          setP(1, 'Recording complete.');
        } catch (e) { setP(0, 'Recording failed: ' + e.message); }
        busy(false);
      });
      wavBtn.addEventListener('click', async () => {
        const buf = await NYO.AudioEngine.renderOffline(this.project, this.buffers());
        this.download(NYO.AudioEngine.encodeWav(buf), 'ageless-nyo3-mix.wav');
      });

      body.appendChild(this.section('Export', [
        capsBox,
        this.row('Video bitrate', br),
        h('div', { class: 'btn-row' }, [exportBtn, cancelBtn]),
        prog, status, result
      ], 'Frame-accurate offline render: every one of the source frames is seeked, graded and composited at 1080×1920, then encoded with your browser\'s H.264 encoder (WebCodecs) and muxed to MP4 with synchronised audio. Rendering is not tied to real time, and the result matches the preview exactly.'));
      body.appendChild(this.section('Alternatives', [
        h('div', { class: 'btn-row' }, [rtBtn, wavBtn]),
        h('p', { class: 'note', html: 'Strict H.264 + AAC from any export (ffmpeg):<br><code>ffmpeg -i export.mp4 -c:v copy -c:a aac -b:a 192k -movflags +faststart final.mp4</code><br>From a WebM recording:<br><code>ffmpeg -i rec.webm -r 30 -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k final.mp4</code>' })
      ]));
    }
  };

  NYO.app = app;
  window.addEventListener('DOMContentLoaded', () => app.init());
})();
