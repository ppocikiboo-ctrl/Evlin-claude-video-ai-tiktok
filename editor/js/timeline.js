/* Interactive timeline: ruler/scrub, video thumbnails, caption & label clips
 * (move / trim), sound-effect markers, music bar and tracking keyframes. */
window.NYO = window.NYO || {};

NYO.Timeline = class {
  constructor(app) {
    this.app = app;
    this.heads = document.getElementById('tlHeads');
    this.scroll = document.getElementById('tlScroll');
    this.content = document.getElementById('tlContent');
    this.zoomEl = document.getElementById('tlZoom');
    this.pps = 40;
    this.thumbs = [];
    this.zoomEl.addEventListener('input', () => { this.pps = +this.zoomEl.value; this.render(); });
    this.scroll.addEventListener('scroll', () => { this.heads.scrollTop = this.scroll.scrollTop; });
    new ResizeObserver(() => this.fit()).observe(this.scroll);
  }

  fit() {
    const w = this.scroll.clientWidth - 30;
    const d = this.app.project.duration || 30;
    const pps = Math.max(20, Math.min(240, w / d));
    if (!this._userZoom && (!this._fitted || Math.abs(pps - this.pps) > 0.5)) {
      this.pps = pps; this.zoomEl.value = Math.round(pps); this._fitted = true;
      this.render();
    }
  }

  x(t) { return 10 + t * this.pps; }
  t(x) { return Math.max(0, Math.min(this.app.project.duration, (x - 10) / this.pps)); }

  render() {
    const app = this.app, p = app.project;
    const width = this.x(p.duration) + 40;
    const tracks = [
      { key: 'ruler', name: '' },
      { key: 'video', name: 'Video' },
      { key: 'cap', name: 'Captions' },
      { key: 'lab', name: 'Labels' },
      { key: 'kf', name: 'Keyframes' },
      { key: 'sfx', name: 'Sound FX' },
      { key: 'mus', name: 'Music' }
    ];
    this.heads.innerHTML = tracks.map((tr) => `<div class="tl-head ${tr.key === 'ruler' ? 'ruler' : ''}">${tr.name}</div>`).join('');
    const c = this.content;
    c.innerHTML = '';
    c.style.width = width + 'px';

    // Ruler
    const ruler = document.createElement('div');
    ruler.className = 'tl-ruler';
    const step = this.pps > 90 ? 0.5 : this.pps > 30 ? 1 : 2;
    for (let s = 0; s <= p.duration + 0.001; s += step) {
      const tk = document.createElement('div');
      tk.className = 'tl-tick';
      tk.style.left = this.x(s) + 'px';
      if (Math.abs(s - Math.round(s)) < 0.01) tk.textContent = Math.round(s) + 's';
      ruler.appendChild(tk);
    }
    this.dragScrub(ruler);
    c.appendChild(ruler);

    // Video thumbnails
    const vt = this.track(c);
    const th = document.createElement('div');
    th.className = 'tl-thumbs';
    th.style.left = this.x(0) + 'px';
    th.style.width = (p.duration * this.pps) + 'px';
    if (this.thumbs.length) {
      const per = (p.duration * this.pps) / this.thumbs.length;
      this.thumbs.forEach((cv) => { const cl = document.createElement('canvas'); cl.width = cv.width; cl.height = cv.height; cl.getContext('2d').drawImage(cv, 0, 0); cl.style.width = per + 'px'; th.appendChild(cl); });
    } else {
      th.style.background = 'repeating-linear-gradient(90deg,#2b241d,#2b241d 40px,#241e18 40px,#241e18 80px)';
    }
    vt.appendChild(th);
    this.dragScrub(vt);

    // Captions & labels (overlapping clips stack into lanes)
    const laneTrack = (items, kind, headIndex) => {
      const tr = this.track(c);
      const lanes = [];
      items.slice().sort((a, b) => a.start - b.start).forEach((it) => {
        let i = lanes.findIndex((end) => end <= it.start + 0.001);
        if (i < 0) { i = lanes.length; lanes.push(0); }
        lanes[i] = it.end;
        const el = this.clip(it, kind, it.name);
        if (i) el.style.top = (4 + i * 30) + 'px';
        tr.appendChild(el);
      });
      const hgt = Math.max(34, 4 + lanes.length * 30);
      tr.style.height = hgt + 'px';
      this.heads.children[headIndex].style.height = hgt + 'px';
    };
    laneTrack(p.captions, 'cap', 2);
    laneTrack(p.labels, 'lab', 3);

    // Keyframes of selected label
    const kt = this.track(c);
    const sel = app.selection;
    if (sel && sel.type === 'label') {
      const l = p.labels.find((q) => q.id === sel.id);
      if (l) l.keyframes.forEach((kf, i) => {
        const m = document.createElement('div');
        m.className = 'kf-mark' + (app.selKey === i ? ' sel' : '');
        m.style.left = this.x(kf[0]) + 'px';
        m.title = `Keyframe ${kf[0].toFixed(3)}s`;
        m.addEventListener('pointerdown', (e) => {
          e.stopPropagation();
          app.selKey = i;
          this.dragGeneric(e, (dt) => { kf[0] = Math.max(0, Math.round((kf[0] + dt) * 1000) / 1000); }, () => { NYO.Track.sortKeys(l); app.changed('keyframes'); }, () => app.seek(kf[0]));
        });
        kt.appendChild(m);
      });
    }

    // SFX
    const st = this.track(c);
    p.sfx.forEach((cue) => {
      const T = NYO.sfxTime(p, cue);
      if (T === null) return;
      const m = document.createElement('div');
      m.className = 'sfx-mark' + (sel && sel.type === 'sfx' && sel.id === cue.id ? ' sel' : '') + (cue.link ? ' linked' : '');
      m.style.left = this.x(T) + 'px';
      m.title = `${NYO.SFX_TYPES[cue.type] || cue.type} @ ${T.toFixed(2)}s${cue.link ? ' (linked)' : ''}`;
      m.addEventListener('pointerdown', (e) => {
        e.stopPropagation();
        app.select('sfx', cue.id);
        this.dragGeneric(e, (dt) => {
          if (cue.link) cue.offset = Math.round(((cue.offset || 0) + dt) * 1000) / 1000;
          else cue.t = Math.max(0, Math.round((cue.t + dt) * 1000) / 1000);
        }, () => app.changed('sfx'));
      });
      st.appendChild(m);
    });

    // Music
    const mt = this.track(c);
    const bar = document.createElement('div');
    bar.className = 'music-bar';
    bar.style.left = this.x(0) + 'px';
    bar.style.width = (p.duration * this.pps) + 'px';
    const a = p.audio;
    bar.textContent = a.music === 'generated' ? `Original score · ${a.bpm} BPM · fade-out ${a.fadeOut}s` : a.music === 'file' ? `Music: ${app.musicName || 'uploaded track'}` : 'No music';
    const fo = Math.max(0, a.fadeOut) * this.pps;
    bar.style.maskImage = `linear-gradient(90deg, rgba(0,0,0,.35), #000 ${Math.max(1, a.fadeIn * this.pps)}px, #000 calc(100% - ${fo}px), rgba(0,0,0,.25))`;
    mt.appendChild(bar);

    const ph = document.createElement('div');
    ph.className = 'playhead';
    c.appendChild(ph);
    this.ph = ph;
    this.updatePlayhead();
  }

  track(parent) {
    const d = document.createElement('div');
    d.className = 'tl-track';
    parent.appendChild(d);
    return d;
  }

  clip(el, kind, name) {
    const app = this.app;
    const d = document.createElement('div');
    const sel = app.selection && app.selection.id === el.id;
    d.className = `clip ${kind}` + (sel ? ' sel' : '') + (el.enabled === false ? ' off' : '') + (el.connector === 'tracked' ? ' trk' : '');
    d.style.left = this.x(el.start) + 'px';
    d.style.width = Math.max(8, (el.end - el.start) * this.pps) + 'px';
    d.textContent = name;
    d.title = `${name}  ${el.start.toFixed(2)}–${el.end.toFixed(2)}s`;
    const hl = document.createElement('div'); hl.className = 'h l';
    const hr = document.createElement('div'); hr.className = 'h r';
    d.appendChild(hl); d.appendChild(hr);
    const type = kind === 'cap' ? 'caption' : 'label';
    const snap = (v) => {
      const ph = app.time;
      if (Math.abs(v - ph) * this.pps < 6) return ph;
      return Math.round(v * 20) / 20;
    };
    const begin = (e, mode) => {
      e.stopPropagation();
      app.select(type, el.id);
      const s0 = el.start, e0 = el.end;
      let acc = 0;
      this.dragGeneric(e, (dt) => {
        acc += dt;
        if (mode === 'move') {
          const len = e0 - s0;
          let ns = snap(Math.max(0, Math.min(app.project.duration - len, s0 + acc)));
          el.start = ns; el.end = ns + len;
        } else if (mode === 'l') {
          el.start = snap(Math.max(0, Math.min(el.end - 0.2, s0 + acc)));
        } else {
          el.end = snap(Math.min(app.project.duration, Math.max(el.start + 0.2, e0 + acc)));
        }
        d.style.left = this.x(el.start) + 'px';
        d.style.width = Math.max(8, (el.end - el.start) * this.pps) + 'px';
        app.requestDraw();
      }, () => app.changed(type));
    };
    d.addEventListener('pointerdown', (e) => begin(e, 'move'));
    hl.addEventListener('pointerdown', (e) => begin(e, 'l'));
    hr.addEventListener('pointerdown', (e) => begin(e, 'r'));
    return d;
  }

  dragGeneric(e, onDelta, onEnd, onClick) {
    const startX = e.clientX;
    let lastX = e.clientX, moved = false;
    const move = (ev) => {
      const dx = ev.clientX - lastX;
      if (Math.abs(ev.clientX - startX) > 2) moved = true;
      lastX = ev.clientX;
      if (moved && dx) onDelta(dx / this.pps);
    };
    const up = () => {
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', up);
      if (moved) onEnd && onEnd(); else onClick && onClick();
    };
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', up);
  }

  dragScrub(el) {
    el.addEventListener('pointerdown', (e) => {
      const rect = this.content.getBoundingClientRect();
      const go = (ev) => this.app.seek(this.t(ev.clientX - rect.left));
      go(e);
      const up = () => { window.removeEventListener('pointermove', go); window.removeEventListener('pointerup', up); };
      window.addEventListener('pointermove', go);
      window.addEventListener('pointerup', up);
    });
  }

  updatePlayhead() {
    if (!this.ph) return;
    const x = this.x(this.app.time);
    this.ph.style.left = x + 'px';
    if (this.app.playing) {
      const s = this.scroll;
      if (x > s.scrollLeft + s.clientWidth - 40 || x < s.scrollLeft) s.scrollLeft = x - 60;
    }
  }

  async buildThumbs(video) {
    const n = 16;
    this.thumbs = [];
    const h = 30, w = Math.round(h * video.videoWidth / video.videoHeight);
    for (let i = 0; i < n; i++) {
      await NYO.Exporter.seek(video, (i + 0.5) * video.duration / n).catch(() => {});
      const cv = document.createElement('canvas');
      cv.width = w; cv.height = h;
      cv.getContext('2d').drawImage(video, 0, 0, w, h);
      this.thumbs.push(cv);
    }
    this.render();
  }
};
