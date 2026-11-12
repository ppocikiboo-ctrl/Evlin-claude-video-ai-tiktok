/* Compositor: draws one finished frame (graded footage + animated captions +
 * tracked labels) at any time t. Used by both the live preview and export,
 * so the export matches the preview frame for frame. All layout values are
 * authored on a 1080×1920 canvas and scaled. */
window.NYO = window.NYO || {};

(function () {
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const ease = {
    outCubic: (x) => 1 - Math.pow(1 - x, 3),
    inOutSine: (x) => -(Math.cos(Math.PI * x) - 1) / 2,
    outBack: (x) => { const c1 = 1.5, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
    outQuint: (x) => 1 - Math.pow(1 - x, 5)
  };
  NYO.ease = ease;

  const FONT_FAMILY = {
    serif: "'Playfair Display', 'Times New Roman', serif",
    sans: "'Poppins', 'Helvetica Neue', Arial, sans-serif"
  };
  NYO.fontString = function (ln, size) {
    return `${ln.italic ? 'italic ' : ''}${ln.weight || 400} ${size}px ${FONT_FAMILY[ln.font] || FONT_FAMILY.serif}`;
  };

  function hexA(hex, a) {
    const h = hex.replace('#', '');
    const n = parseInt(h.length === 3 ? h.split('').map((c) => c + c).join('') : h, 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  }
  NYO.hexA = hexA;

  NYO.Compositor = class {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.grader = new NYO.Grader();
      this.hit = { captions: [], labels: [] };
    }

    /* Placement of the source frame inside the 9:16 output. */
    videoRect(project, vw, vh, t) {
      const W = this.canvas.width, H = this.canvas.height;
      const lay = project.layout;
      const s = (lay.fit === 'fill' ? Math.max(W / vw, H / vh) : Math.min(W / vw, H / vh)) * (lay.zoom || 1) * this.punchZoom(project, t);
      const w = vw * s, h = vh * s;
      return { x: (W - w) / 2, y: (H - h) / 2 + (lay.offsetY || 0) * H, w, h };
    }

    /* Zoom "punch" on section changes: the frame starts slightly pushed in
     * and settles back, like a cut-zoom in an edit. */
    punchZoom(project, t) {
      const fx = project.fx;
      if (!fx || !fx.punches || t == null) return 1;
      let z = 1;
      fx.punches.forEach((p) => {
        const d = p.dur || 0.45, k = (t - p.t) / d;
        if (k >= 0 && k < 1) z *= 1 + (p.amount || 0.06) * (1 - ease.outCubic(k));
      });
      return z;
    }

    drawFx(t, project) {
      const fx = project.fx;
      if (!fx) return;
      const ctx = this.ctx, S = this.S, W = this.canvas.width, H = this.canvas.height;
      (fx.flashes || []).forEach((f) => {
        const k = (t - f.t) / (f.dur || 0.18);
        if (k >= 0 && k < 1) {
          ctx.save();
          ctx.globalAlpha = (f.alpha || 0.5) * (1 - k) * (1 - k);
          ctx.fillStyle = f.color || '#FFFFFF';
          ctx.fillRect(0, 0, W, H);
          ctx.restore();
        }
      });
      const ch = fx.chapters ? fx.chapters.concat([project.duration]) : null;
      if (ch && ch.length > 1) {
        // Segmented chapter bar (story-style) below the TikTok top tabs.
        const x0 = 60, x1 = NYO.OUT_W - 60, y = fx.chapterY || 170, gap = 10, hgt = 6;
        const end = ch[ch.length - 1];
        const total = x1 - x0 - gap * (ch.length - 2);
        const a = clamp(t / 0.3, 0, 1) * clamp((project.duration - t) / 0.3, 0, 1);
        ctx.save();
        ctx.globalAlpha = a;
        let x = x0;
        for (let i = 0; i < ch.length - 1; i++) {
          const w = total * (ch[i + 1] - ch[i]) / (end - ch[0]);
          const p = clamp((t - ch[i]) / (ch[i + 1] - ch[i]), 0, 1);
          ctx.fillStyle = 'rgba(255,255,255,0.38)';
          ctx.beginPath(); ctx.roundRect(x * S, y * S, w * S, hgt * S, 3 * S); ctx.fill();
          if (p > 0) {
            ctx.fillStyle = fx.chapterColor || '#FFFFFF';
            ctx.beginPath(); ctx.roundRect(x * S, y * S, w * p * S, hgt * S, 3 * S); ctx.fill();
          }
          x += w + gap;
        }
        ctx.restore();
      }
    }

    render(t, project, video, opts) {
      opts = opts || {};
      const ctx = this.ctx, W = this.canvas.width, H = this.canvas.height;
      const S = W / NYO.OUT_W;
      this.S = S;
      ctx.save();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.globalAlpha = 1;
      ctx.filter = 'none';
      ctx.fillStyle = project.layout.ivory || '#EFE6DA';
      ctx.fillRect(0, 0, W, H);

      const hasVideo = video && video.readyState >= 2 && video.videoWidth > 0;
      this.rect = null;
      if (hasVideo) {
        const vw = video.videoWidth, vh = video.videoHeight;
        const r = this.videoRect(project, vw, vh, t);
        this.rect = r;
        // Visible region (clip to canvas) → crop in source space.
        const vx0 = Math.max(0, r.x), vy0 = Math.max(0, r.y);
        const vx1 = Math.min(W, r.x + r.w), vy1 = Math.min(H, r.y + r.h);
        const crop = [(vx0 - r.x) / r.w, (vy0 - r.y) / r.h, (vx1 - r.x) / r.w, (vy1 - r.y) / r.h];
        const ow = Math.max(2, Math.round(vx1 - vx0)), oh = Math.max(2, Math.round(vy1 - vy0));
        const graded = this.grader.process(video, vw, vh, ow, oh, project.grade, crop);

        if (project.layout.fit !== 'fill' && project.layout.background === 'blur' && (vy0 > 0 || vx0 > 0)) {
          // Soft blurred extension of the same graded footage to fill 9:16.
          const cs = Math.max(W / ow, H / oh) * 1.08;
          ctx.save();
          ctx.filter = `blur(${Math.round(36 * S)}px)`;
          ctx.drawImage(graded, (W - ow * cs) / 2, (H - oh * cs) / 2, ow * cs, oh * cs);
          ctx.restore();
          ctx.fillStyle = hexA(project.layout.ivory || '#EFE6DA', 0.28);
          ctx.fillRect(0, 0, W, H);
        }
        ctx.drawImage(graded, vx0, vy0, ow, oh);

        if (opts.compare === 'split' || opts.compare === 'before') {
          const sx = opts.compare === 'before' ? W : clamp(opts.split == null ? 0.5 : opts.split, 0, 1) * W;
          ctx.save();
          ctx.beginPath(); ctx.rect(0, 0, sx, H); ctx.clip();
          ctx.drawImage(video, crop[0] * vw, crop[1] * vh, (crop[2] - crop[0]) * vw, (crop[3] - crop[1]) * vh, vx0, vy0, ow, oh);
          ctx.restore();
          if (opts.compare === 'split') {
            ctx.fillStyle = 'rgba(255,255,255,0.9)';
            ctx.fillRect(sx - 1 * S, 0, 2 * S, H);
            ctx.font = `500 ${Math.round(22 * S)}px ${FONT_FAMILY.sans}`;
            ctx.textBaseline = 'top';
            ctx.fillStyle = 'rgba(0,0,0,0.55)';
            ctx.textAlign = 'right'; ctx.fillText('BEFORE', sx - 14 * S, 120 * S);
            ctx.textAlign = 'left'; ctx.fillText('AFTER', sx + 14 * S, 120 * S);
          }
        }
      } else {
        const g = ctx.createLinearGradient(0, 0, 0, H);
        g.addColorStop(0, '#F6EFE5'); g.addColorStop(1, '#E7D9C6');
        ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
        ctx.fillStyle = 'rgba(120,96,60,0.55)';
        ctx.font = `400 ${Math.round(34 * S)}px ${FONT_FAMILY.sans}`;
        ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText('Upload your original MP4 to begin', W / 2, H * 0.55);
      }

      this.hit = { captions: [], labels: [] };
      if (opts.overlays !== false) {
        project.labels.forEach((l) => { if (l.enabled !== false) this.drawLabel(t, l, project, opts); });
        project.captions.forEach((c) => { if (c.enabled !== false) this.drawCaption(t, c, opts); });
        this.drawFx(t, project);
      }
      if (opts.safeZones) this.drawSafeZones();
      ctx.restore();
    }

    drawSafeZones() {
      const ctx = this.ctx, S = this.S, W = this.canvas.width, H = this.canvas.height;
      ctx.save();
      ctx.fillStyle = 'rgba(255,60,90,0.12)';
      ctx.fillRect(0, 0, W, 130 * S);
      ctx.fillRect(0, H - 380 * S, W, 380 * S);
      ctx.fillRect(W - 140 * S, 130 * S, 140 * S, H - 510 * S);
      ctx.strokeStyle = 'rgba(255,60,90,0.55)'; ctx.setLineDash([8 * S, 6 * S]); ctx.lineWidth = 2 * S;
      ctx.strokeRect(0 + 40 * S, 130 * S, W - 180 * S, H - 510 * S);
      ctx.restore();
    }

    /* ---------------- captions ---------------- */

    layoutLines(c) {
      // Break each line into rows of styled word runs that fit maxWidth.
      const ctx = this.ctx, S = this.S;
      const maxW = (c.maxWidth || 0.86) * NYO.OUT_W;
      const rows = [];
      c.lines.forEach((ln, li) => {
        const size = ln.size;
        const ind = ln.check ? size * 1.35 : 0;
        const lineMax = maxW - ind;
        ctx.font = NYO.fontString(ln, size);
        if ('letterSpacing' in ctx) ctx.letterSpacing = `${(ln.tracking || 0)}px`;
        const words = ln.text.split(/(\s+)/).filter((w) => w.length);
        const tokens = [];
        words.forEach((w) => {
          const hl = ln.highlight && w.replace(/[^\p{L}\p{N}.]/gu, '') === ln.highlight.replace(/[^\p{L}\p{N}.]/gu, '') && ln.highlight.length > 0;
          tokens.push({ text: w, hl: hl, w: ctx.measureText(w).width, space: /^\s+$/.test(w) });
        });
        let row = { line: ln, li, tokens: [], w: 0, size, ind, first: true };
        tokens.forEach((tk) => {
          if (!tk.space && row.w + tk.w > lineMax && row.tokens.length) {
            while (row.tokens.length && row.tokens[row.tokens.length - 1].space) row.w -= row.tokens.pop().w;
            rows.push(row);
            row = { line: ln, li, tokens: [], w: 0, size, ind };
          }
          if (tk.space && !row.tokens.length) return;
          row.tokens.push(tk); row.w += tk.w;
        });
        if (row.tokens.length) rows.push(row);
      });
      if ('letterSpacing' in ctx) ctx.letterSpacing = '0px';
      return rows;
    }

    drawCaption(t, c, opts) {
      if (t < c.start - 0.001 || t > c.end + 0.001) return;
      const ctx = this.ctx, S = this.S, W = this.canvas.width;
      const rows = this.layoutLines(c);
      if (!rows.length) return;
      const lh = (r) => r.size * (r.line.lineHeight || (r.line.font === 'sans' ? 1.45 : 1.25)) * (r.line.chip && r.first ? 1.3 : 1);
      const totalH = rows.reduce((a, r) => a + lh(r), 0);
      const cx = c.x * NYO.OUT_W, cy = c.y * NYO.OUT_H;
      rows.forEach((r) => { r.full = r.w + (r.ind || 0) + (r.line.chip ? r.size * 1.1 : 0); });
      const blockW = Math.max.apply(null, rows.map((r) => r.full));
      const life = t - c.start, left = c.end - t;
      const outP = clamp(left / (c.outDur || 0.5), 0, 1);
      const inP0 = clamp(life / (c.inDur || 0.8), 0, 1);

      // Hit box for direct manipulation in the preview.
      this.hit.captions.push({ id: c.id, x: (cx - blockW / 2 - 20) * S, y: (cy - totalH / 2 - 20) * S, w: (blockW + 40) * S, h: (totalH + 40) * S });

      // Backdrop: feathered warm scrim for legibility over bright footage.
      if (c.backdrop === 'scrim') {
        const a = (c.backdropOpacity == null ? 0.34 : c.backdropOpacity) * ease.outCubic(inP0) * ease.inOutSine(outP);
        if (a > 0.003) {
          ctx.save();
          ctx.translate(cx * S, cy * S);
          ctx.scale((blockW / 2 + 150) * S, (totalH / 2 + 95) * S);
          const g = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);
          g.addColorStop(0, `rgba(38,26,18,${a})`);
          g.addColorStop(0.55, `rgba(38,26,18,${a * 0.72})`);
          g.addColorStop(1, 'rgba(38,26,18,0)');
          ctx.fillStyle = g;
          ctx.beginPath(); ctx.arc(0, 0, 1, 0, Math.PI * 2); ctx.fill();
          ctx.restore();
        }
      }

      if (c.backdrop === 'glass') {
        // Frosted panel: real blur of the footage underneath + warm dark tint.
        const a = ease.outCubic(inP0) * ease.inOutSine(outP);
        if (a > 0.003) {
          const pw = blockW + 80, ph = totalH + 44, px = cx - pw / 2, py = cy - ph / 2 + (1 - ease.outCubic(inP0)) * 14;
          ctx.save();
          ctx.globalAlpha = a;
          ctx.beginPath(); ctx.roundRect(px * S, py * S, pw * S, ph * S, 22 * S); ctx.clip();
          ctx.filter = `blur(${Math.round(16 * S)}px)`;
          ctx.drawImage(this.canvas, (px - 24) * S, (py - 24) * S, (pw + 48) * S, (ph + 48) * S, (px - 24) * S, (py - 24) * S, (pw + 48) * S, (ph + 48) * S);
          ctx.filter = 'none';
          ctx.fillStyle = `rgba(32,22,16,${c.backdropOpacity == null ? 0.42 : c.backdropOpacity})`;
          ctx.fillRect(px * S, py * S, pw * S, ph * S);
          ctx.restore();
          ctx.save();
          ctx.globalAlpha = a * 0.7;
          ctx.strokeStyle = hexA(NYO.PALETTE.gold, 0.6); ctx.lineWidth = 1.2 * S;
          ctx.beginPath(); ctx.roundRect((px + 0.5) * S, (py + 0.5) * S, (pw - 1) * S, (ph - 1) * S, 22 * S); ctx.stroke();
          ctx.restore();
        }
      }

      if (c.backdrop === 'box') {
        // Solid editorial card that wipes in from the left.
        const a = ease.inOutSine(outP);
        const wp = ease.outQuint(clamp(inP0 * 1.25, 0, 1));
        if (a > 0.003 && wp > 0.002) {
          const padX = c.boxPadX || 38, padY = c.boxPadY || 30;
          const pw = blockW + padX * 2, ph = totalH + padY * 2, px = cx - pw / 2, py = cy - ph / 2;
          ctx.save();
          ctx.globalAlpha = a * (c.backdropOpacity == null ? 0.94 : c.backdropOpacity);
          ctx.shadowColor = 'rgba(0,0,0,0.28)'; ctx.shadowBlur = 24 * S; ctx.shadowOffsetY = 6 * S;
          ctx.fillStyle = c.backdropColor || '#FFFFFF';
          ctx.beginPath(); ctx.roundRect(px * S, py * S, pw * wp * S, ph * S, (c.boxRadius || 18) * S); ctx.fill();
          if (c.accentColor) {
            ctx.shadowColor = 'transparent';
            ctx.globalAlpha = a;
            ctx.fillStyle = c.accentColor;
            ctx.beginPath(); ctx.roundRect(px * S, py * S, 9 * S, ph * S, [(c.boxRadius || 18) * S, 0, 0, (c.boxRadius || 18) * S]); ctx.fill();
          }
          ctx.restore();
        }
      }

      let y = cy - totalH / 2;
      let segIndex = 0;
      let wordIndex = 0;
      const rowX = (r) => (c.align === 'left' ? cx - blockW / 2 : cx - r.full / 2) + (r.ind || 0) + (r.line.chip ? r.size * 0.55 : 0);
      rows.forEach((r, ri) => {
        const h = lh(r);
        const baseY = y + h / 2;
        y += h;
        const ln = r.line;
        const anim = c.anim;
        const delay = (ln.delay || 0);
        if (anim === 'stagger' && ln.text.indexOf('•') >= 0) {
          // Each "•"-separated item enters on its own beat.
          const parts = [];
          let cur = [];
          r.tokens.forEach((tk) => { if (tk.text === '•') { parts.push(cur); parts.push([tk]); cur = []; } else cur.push(tk); });
          parts.push(cur);
          let x = cx - r.w / 2;
          parts.forEach((p) => {
            const pw = p.reduce((a, tk) => a + tk.w, 0);
            const isDot = p.length === 1 && p[0].text === '•';
            const d = delay + (isDot ? (segIndex - 0.5) : segIndex) * 0.45;
            if (!isDot) segIndex++;
            const st = this.animState('stagger', life - d, c.inDur, outP, t);
            if (st.alpha > 0.002) {
              this.drawTokens(p, ln, x, baseY + st.dy, st, cx, baseY);
              if (!isDot && life - d > 0 && life - d < 0.9) this.drawSparkle(x + pw - 6, baseY - r.size * 0.55, (life - d) / 0.9, ln.highlightColor || NYO.PALETTE.gold);
            }
            x += pw;
          });
          return;
        }
        if (anim === 'wordPop') {
          // Kinetic type: each word pops in on its own beat.
          let x = rowX(r);
          r.tokens.forEach((tk) => {
            if (tk.space) { x += tk.w; return; }
            const d = delay + wordIndex * (c.wordGap || 0.09);
            wordIndex++;
            const st = this.animState('wordPop', life - d, c.inDur, outP, t - c.start);
            if (ln.bounce) st.dy += Math.sin(Math.max(0, life) * 7) * 7;
            if (st.alpha > 0.002) this.drawTokens([tk], ln, x, baseY + st.dy, st, x + tk.w / 2, baseY, life - d, c);
            x += tk.w;
          });
          return;
        }
        const lineIdx = r.li;
        const d = delay + (anim === 'stagger' ? ri * 0.35 : 0) + (anim === 'checklist' ? lineIdx * (c.stagger || 0.38) : 0);
        const st = this.animState(anim, life - d, c.inDur, outP, t - c.start);
        if (ln.bounce) st.dy += Math.sin(Math.max(0, life) * 7) * 7;
        if (st.alpha <= 0.002) return;
        const x0 = rowX(r) + (st.dx || 0);
        if (ln.check && r.first) this.drawCheck(x0 - r.ind + r.size * 0.5, baseY + st.dy, r.size, life - d, st.alpha, ln.checkColor || '#B3122E');
        this.drawTokens(r.tokens, ln, x0, baseY + st.dy, st, anim === 'punch' ? cx : x0 + r.w / 2, baseY, life - d, c);
      });
    }

    animState(anim, life, inDur, outP, sinceStart) {
      inDur = inDur || 0.8;
      const inP = clamp(life / inDur, 0, 1);
      const o = ease.inOutSine(outP);
      const s = { alpha: 0, dx: 0, dy: 0, scale: 1, blur: 0, clip: 1, spacing: 0 };
      if (life < 0) return s;
      switch (anim) {
        case 'slideUp':
          s.alpha = ease.outCubic(Math.min(1, inP * 1.3)) * o;
          s.dy = (1 - ease.outQuint(inP)) * 70 - (1 - o) * 14;
          break;
        case 'reveal':
          s.alpha = ease.outCubic(inP) * o;
          s.clip = ease.outCubic(inP);
          s.blur = (1 - ease.outCubic(inP)) * 8;
          s.dy = (1 - ease.outCubic(inP)) * 18 - (1 - o) * 10;
          break;
        case 'stagger':
          s.alpha = ease.outCubic(inP) * o;
          s.dy = (1 - ease.outCubic(inP)) * 34 - (1 - o) * 12;
          break;
        case 'cinematic':
          s.alpha = ease.inOutSine(inP) * o;
          s.dy = 14 - Math.min(1, Math.max(0, sinceStart) / 4) * 26;
          s.spacing = Math.min(1, Math.max(0, sinceStart) / 4) * 1.6;
          s.blur = (1 - ease.outCubic(inP)) * 3 + (1 - o) * 3;
          break;
        case 'punch':
          s.alpha = Math.min(1, inP * 4) * o;
          s.scale = 1 + 0.5 * (1 - ease.outBack(inP)) + (1 - o) * 0.06;
          s.blur = (1 - Math.min(1, inP * 2.5)) * 6;
          break;
        case 'wordPop':
          s.alpha = Math.min(1, inP * 3) * o;
          s.scale = 0.55 + 0.45 * ease.outBack(inP);
          s.dy = (1 - ease.outCubic(inP)) * 16 - (1 - o) * 10;
          break;
        case 'checklist':
          s.alpha = ease.outCubic(inP) * o;
          s.dx = (1 - ease.outQuint(inP)) * -46;
          s.dy = -(1 - o) * 10;
          break;
        case 'fadeUpZoom':
        default:
          s.alpha = ease.outCubic(inP) * o;
          s.dy = (1 - ease.outCubic(inP)) * 36 - (1 - o) * 12;
          s.scale = 0.965 + 0.035 * ease.outCubic(inP) + Math.max(0, sinceStart) * 0.0045;
          break;
      }
      return s;
    }

    drawTokens(tokens, ln, x0, y, st, cx, baseY, life, cap) {
      const ctx = this.ctx, S = this.S;
      ctx.save();
      ctx.globalAlpha = clamp(st.alpha, 0, 1);
      if (st.blur > 0.3) ctx.filter = `blur(${(st.blur * S).toFixed(1)}px)`;
      ctx.translate(cx * S, baseY * S);
      ctx.scale(st.scale * S, st.scale * S);
      ctx.translate(-cx, -baseY);
      if (st.clip < 1) {
        const h = ln.size * 1.6;
        ctx.beginPath();
        ctx.rect(x0 - 40, y + h / 2 - h * st.clip, 3000, h * st.clip + 4);
        ctx.clip();
      }
      ctx.font = NYO.fontString(ln, ln.size);
      const extra = st.spacing || 0;
      if ('letterSpacing' in ctx) ctx.letterSpacing = `${(ln.tracking || 0) + extra}px`;
      ctx.textBaseline = 'middle';
      ctx.textAlign = 'left';
      const shadowOn = ln.shadow != null ? ln.shadow : !(cap && cap.backdrop === 'box');
      if (shadowOn) {
        ctx.shadowColor = 'rgba(30,18,10,0.45)';
        ctx.shadowBlur = 16;
        ctx.shadowOffsetY = 2;
      }
      // Re-centre if extra tracking widened the row.
      let total = 0;
      tokens.forEach((tk) => { total += ctx.measureText(tk.text).width; });
      const orig = tokens.reduce((a, tk) => a + tk.w, 0);
      let x = x0 - (total - orig) / 2;
      if (ln.chip) {
        // Pill-shaped section tag behind the line.
        const pad = ln.size * 0.55;
        ctx.save();
        ctx.shadowColor = 'transparent';
        ctx.fillStyle = ln.chipColor || '#B3122E';
        ctx.beginPath(); ctx.roundRect(x - pad, y - ln.size * 0.8, total + pad * 2, ln.size * 1.6, ln.size * 0.8); ctx.fill();
        ctx.restore();
      }
      tokens.forEach((tk) => {
        const w = ctx.measureText(tk.text).width;
        if (!tk.space) {
          if (tk.hl && ln.hlStyle === 'box') {
            // Keyword marker: solid box wipes in behind the word.
            const p = life == null ? 1 : ease.outCubic(clamp((life - 0.12) / 0.28, 0, 1));
            ctx.save();
            ctx.shadowColor = 'transparent';
            ctx.fillStyle = ln.highlightColor || '#B3122E';
            ctx.beginPath(); ctx.roundRect(x - ln.size * 0.09, y - ln.size * 0.66, (w + ln.size * 0.18) * p, ln.size * 1.3, ln.size * 0.12); ctx.fill();
            ctx.restore();
            ctx.fillStyle = p > 0.5 ? (ln.hlTextColor || '#FFFFFF') : ln.color;
            ctx.fillText(tk.text, x, y);
          } else if (tk.hl) {
            ctx.fillStyle = ln.highlightColor || NYO.PALETTE.gold;
            ctx.fillText(tk.text, x, y);
            // One soft champagne light sweep across the highlighted word.
            if (life != null && life > 0.5 && life < 1.6) {
              const p = (life - 0.5) / 1.1;
              const gx = x - 60 + (w + 120) * p;
              const g = ctx.createLinearGradient(gx - 50, 0, gx + 50, 0);
              g.addColorStop(0, 'rgba(255,249,240,0)');
              g.addColorStop(0.5, 'rgba(255,249,240,0.85)');
              g.addColorStop(1, 'rgba(255,249,240,0)');
              ctx.save();
              ctx.shadowColor = 'transparent';
              ctx.globalCompositeOperation = 'source-atop';
              ctx.fillStyle = g;
              ctx.fillText(tk.text, x, y);
              ctx.restore();
            }
          } else {
            ctx.fillStyle = ln.color;
            ctx.fillText(tk.text, x, y);
          }
        }
        x += w;
      });
      ctx.restore();
    }

    drawCheck(x, y, size, life, alpha, color) {
      // Round badge that pops, then a tick that draws itself.
      const ctx = this.ctx, S = this.S;
      const pop = ease.outBack(clamp(life / 0.3, 0, 1));
      const tick = ease.outCubic(clamp((life - 0.12) / 0.3, 0, 1));
      const r = size * 0.48 * pop;
      if (r <= 0.5) return;
      ctx.save();
      ctx.globalAlpha = clamp(alpha, 0, 1);
      ctx.scale(S, S);
      ctx.fillStyle = color;
      ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#FFFFFF'; ctx.lineWidth = size * 0.11; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      const p1 = [x - size * 0.2, y + size * 0.01], p2 = [x - size * 0.05, y + size * 0.16], p3 = [x + size * 0.22, y - size * 0.14];
      const l1 = Math.hypot(p2[0] - p1[0], p2[1] - p1[1]), l2 = Math.hypot(p3[0] - p2[0], p3[1] - p2[1]);
      let len = (l1 + l2) * tick;
      if (len > 0) {
        ctx.beginPath(); ctx.moveTo(p1[0], p1[1]);
        const k1 = Math.min(1, len / l1);
        ctx.lineTo(p1[0] + (p2[0] - p1[0]) * k1, p1[1] + (p2[1] - p1[1]) * k1);
        len -= l1;
        if (len > 0) { const k2 = Math.min(1, len / l2); ctx.lineTo(p2[0] + (p3[0] - p2[0]) * k2, p2[1] + (p3[1] - p2[1]) * k2); }
        ctx.stroke();
      }
      ctx.restore();
    }

    drawSparkle(x, y, p, color) {
      // Small four-point glint that blooms and fades (p: 0..1).
      const ctx = this.ctx, S = this.S;
      const a = Math.sin(Math.PI * clamp(p, 0, 1));
      const r = 7 + 12 * ease.outCubic(p);
      ctx.save();
      ctx.translate(x * S, y * S);
      ctx.rotate(p * 0.6);
      ctx.globalAlpha = a * 0.9;
      ctx.fillStyle = NYO.PALETTE.ivory;
      ctx.shadowColor = color; ctx.shadowBlur = 10 * S;
      ctx.beginPath();
      for (let i = 0; i < 8; i++) {
        const ang = i * Math.PI / 4, rr = (i % 2 ? r * 0.18 : r) * S;
        ctx.lineTo(Math.cos(ang) * rr, Math.sin(ang) * rr);
      }
      ctx.closePath(); ctx.fill();
      ctx.restore();
    }

    /* ---------------- labels ---------------- */

    anchorFor(label, t) {
      if (label.connector !== 'tracked' || !this.rect) return null;
      const s = NYO.Track.sample(label, t);
      if (!s) return null;
      const S = this.S, r = this.rect;
      return { x: (r.x + s.x * r.w) / S, y: (r.y + s.y * r.h) / S, alpha: s.alpha };
    }

    drawLabel(t, l, project, opts) {
      if (t < l.start - 0.001 || t > l.end + 0.001) return;
      const ctx = this.ctx, S = this.S;
      const life = t - l.start, left = l.end - t;
      const inP = clamp(life / (l.inDur || 0.55), 0, 1);
      const outP = clamp(left / (l.outDur || 0.4), 0, 1);
      let alpha = ease.inOutSine(outP);

      let dot = null, cardPt;
      if (l.connector === 'tracked') {
        const a = this.anchorFor(l, t);
        if (!a) return;
        alpha *= a.alpha;
        if (alpha <= 0.002) return;
        dot = { x: a.x + (l.dotDx || 0), y: a.y + (l.dotDy || 0) };
        // Card follows a short trailing average of the anchor: natural float.
        let sx = 0, sy = 0, n = 0;
        [0.14, 0.1, 0.06, 0.03, 0].forEach((dt) => {
          const q = this.anchorFor(l, t - dt);
          if (q && q.alpha > 0.5) { sx += q.x; sy += q.y; n++; }
        });
        const base = n ? { x: sx / n, y: sy / n } : a;
        cardPt = { x: base.x + (l.dotDx || 0) + l.cardDx, y: base.y + (l.dotDy || 0) + l.cardDy };
      } else {
        if (alpha <= 0.002) return;
        cardPt = { x: l.freeX * NYO.OUT_W, y: l.freeY * NYO.OUT_H };
      }
      cardPt.y += Math.sin((t + l.start) * 1.7) * 3;

      // Card geometry (authored units).
      const padX = 22, padY = 14;
      const tl = { font: l.titleFont || 'serif', weight: l.titleWeight || 500, size: l.titleSize, italic: false, tracking: 0.5 };
      const sl = { font: 'sans', weight: l.subWeight || 300, size: l.subSize, italic: false, tracking: 2.2 };
      const solid = l.cardStyle === 'solid';
      ctx.save();
      ctx.font = NYO.fontString(tl, tl.size);
      if ('letterSpacing' in ctx) ctx.letterSpacing = '0.5px';
      const tw = ctx.measureText(l.title).width;
      ctx.font = NYO.fontString(sl, sl.size);
      if ('letterSpacing' in ctx) ctx.letterSpacing = '2.2px';
      const sw = l.subtitle ? ctx.measureText(l.subtitle).width : 0;
      ctx.restore();
      const cw = Math.max(tw, sw) + padX * 2 + (l.connector === 'tracked' ? 0 : 26);
      const ch = tl.size * 1.2 + (l.subtitle ? sl.size * 1.5 : 0) + padY * 2;

      let cx0, cy0; // top-left
      if (l.connector === 'tracked') {
        // cardPt is the card corner nearest the dot (bottom-inner by default).
        const leftSide = l.side === 'left';
        cx0 = leftSide ? cardPt.x - cw : cardPt.x;
        cy0 = l.cardDy <= 0 ? cardPt.y - ch : cardPt.y;
      } else {
        cx0 = cardPt.x - cw / 2; cy0 = cardPt.y - ch / 2;
      }
      // Keep inside the TikTok-safe region.
      cx0 = clamp(cx0, 40, NYO.OUT_W - 60 - cw);
      cy0 = clamp(cy0, 140, NYO.OUT_H - 400 - ch);

      this.hit.labels.push({ id: l.id, x: cx0 * S, y: cy0 * S, w: cw * S, h: ch * S, dot: dot ? { x: dot.x * S, y: dot.y * S } : null });

      // Entrance timeline: dot pops → line draws → card fades/slides in.
      const dotP = l.connector === 'tracked' ? clamp(life / 0.28, 0, 1) : 1;
      const lineP = l.connector === 'tracked' ? clamp((life - 0.12) / 0.45, 0, 1) : 1;
      const cardP = l.connector === 'tracked' ? clamp((life - 0.3) / Math.max(0.2, (l.inDur || 0.55)), 0, 1) : inP;
      const accent = l.accent || NYO.PALETTE.gold;

      ctx.save();
      ctx.scale(S, S);
      ctx.globalAlpha = alpha;

      if (dot) {
        // Connector: dot → card's near bottom/top edge, then along the card edge.
        const leftSide = l.side === 'left';
        const edgeY = l.cardDy <= 0 ? cy0 + ch : cy0;
        const nearX = leftSide ? cx0 + cw : cx0;
        const farX = leftSide ? cx0 : cx0 + cw;
        const pts = [[dot.x, dot.y], [nearX, edgeY], [farX, edgeY]];
        const seg1 = Math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]);
        const seg2 = Math.abs(pts[2][0] - pts[1][0]);
        let len = (seg1 + seg2) * ease.outCubic(lineP);
        ctx.strokeStyle = accent;
        ctx.lineWidth = 1.6;
        ctx.lineCap = 'round';
        ctx.shadowColor = hexA(accent, 0.55); ctx.shadowBlur = 6;
        ctx.beginPath();
        ctx.moveTo(pts[0][0], pts[0][1]);
        if (len > 0) {
          const k1 = Math.min(1, len / Math.max(1, seg1));
          ctx.lineTo(pts[0][0] + (pts[1][0] - pts[0][0]) * k1, pts[0][1] + (pts[1][1] - pts[0][1]) * k1);
          len -= seg1;
          if (len > 0) ctx.lineTo(pts[1][0] + (pts[2][0] - pts[1][0]) * Math.min(1, len / Math.max(1, seg2)), edgeY);
        }
        ctx.stroke();
        // Tracking dot: small, softly glowing, never larger than the capsule.
        const pulse = 0.5 + 0.5 * Math.sin(life * 4.2);
        const pr = ease.outBack(dotP);
        ctx.shadowBlur = 0;
        ctx.fillStyle = hexA(accent, 0.22 * pr);
        ctx.beginPath(); ctx.arc(dot.x, dot.y, (9 + pulse * 4) * pr, 0, Math.PI * 2); ctx.fill();
        ctx.shadowColor = hexA(accent, 0.8); ctx.shadowBlur = 8;
        ctx.fillStyle = NYO.PALETTE.ivory;
        ctx.beginPath(); ctx.arc(dot.x, dot.y, 4.2 * pr, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = accent; ctx.lineWidth = 1.4; ctx.shadowBlur = 0;
        ctx.beginPath(); ctx.arc(dot.x, dot.y, 5.6 * pr, 0, Math.PI * 2); ctx.stroke();
      }

      // Card: frosted glass (real backdrop blur of the frame underneath).
      const ca = ease.outCubic(cardP);
      if (ca > 0.002) {
        const slide = (1 - ca) * 14;
        const x = cx0, y = cy0 + slide, rad = 16;
        ctx.globalAlpha = alpha * ca;
        if (solid) {
          ctx.save();
          ctx.shadowColor = 'rgba(0,0,0,0.3)'; ctx.shadowBlur = 16; ctx.shadowOffsetY = 4;
          ctx.fillStyle = l.cardColor || '#B3122E';
          ctx.beginPath(); ctx.roundRect(x, y, cw, ch, 12); ctx.fill();
          ctx.restore();
        } else {
          ctx.save();
          ctx.beginPath(); ctx.roundRect(x, y, cw, ch, rad); ctx.clip();
          ctx.setTransform(1, 0, 0, 1, 0, 0);
          ctx.filter = `blur(${Math.round(12 * S)}px)`;
          ctx.drawImage(this.canvas, (x - 20) * S, (y - 20) * S, (cw + 40) * S, (ch + 40) * S, (x - 20) * S, (y - 20) * S, (cw + 40) * S, (ch + 40) * S);
          ctx.restore();
          ctx.fillStyle = 'rgba(32,22,16,0.44)';
          ctx.beginPath(); ctx.roundRect(x, y, cw, ch, rad); ctx.fill();
        }
        ctx.strokeStyle = hexA(solid ? '#FFFFFF' : accent, solid ? 0.35 : 0.65); ctx.lineWidth = 1.2;
        ctx.beginPath(); ctx.roundRect(x + 0.5, y + 0.5, cw - 1, ch - 1, solid ? 12 : rad); ctx.stroke();

        ctx.textBaseline = 'alphabetic';
        ctx.shadowColor = solid ? 'transparent' : 'rgba(20,12,6,0.35)'; ctx.shadowBlur = 6;
        const tx = x + padX + (l.connector === 'tracked' ? 0 : 26);
        if (l.connector !== 'tracked') {
          // Small gold marker + hairline for untracked cards.
          ctx.fillStyle = accent;
          ctx.beginPath(); ctx.arc(x + padX + 6, y + padY + tl.size * 0.62, 4, 0, Math.PI * 2); ctx.fill();
        }
        ctx.font = NYO.fontString(tl, tl.size);
        if ('letterSpacing' in ctx) ctx.letterSpacing = '0.5px';
        ctx.fillStyle = l.titleColor;
        ctx.fillText(l.title, tx, y + padY + tl.size * 0.95);
        if (l.subtitle) {
          ctx.font = NYO.fontString(sl, sl.size);
          if ('letterSpacing' in ctx) ctx.letterSpacing = '2.2px';
          ctx.fillStyle = l.subColor;
          ctx.fillText(l.subtitle, tx, y + padY + tl.size * 1.2 + sl.size * 1.15);
        }
      }
      ctx.restore();
    }
  };
})();
