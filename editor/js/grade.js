/* WebGL colour grader: real per-pixel colour processing (white balance,
 * exposure, tone curve, saturation/vibrance, skin & product protection,
 * light denoise, subtle sharpening, highlight roll-off, vignette). */
window.NYO = window.NYO || {};

NYO.Grader = class {
  constructor() {
    this.canvas = document.createElement('canvas');
    const gl = this.canvas.getContext('webgl', { preserveDrawingBuffer: true, premultipliedAlpha: false, antialias: false });
    if (!gl) throw new Error('WebGL is not available in this browser.');
    this.gl = gl;
    this._init();
  }

  _init() {
    const gl = this.gl;
    const vs = `
      attribute vec2 a_pos;
      varying vec2 v_uv;
      void main() {
        v_uv = vec2(a_pos.x * 0.5 + 0.5, 0.5 - a_pos.y * 0.5);
        gl_Position = vec4(a_pos, 0.0, 1.0);
      }`;
    const fs = `
      precision highp float;
      varying vec2 v_uv;
      uniform sampler2D u_tex;
      uniform vec2 u_texel;
      uniform vec2 u_crop0;
      uniform vec2 u_crop1;
      uniform float u_aspect;
      uniform float u_enabled;
      uniform float u_exposure, u_brightness, u_contrast, u_highlights, u_shadows;
      uniform float u_whites, u_blacks, u_sat, u_vib, u_temp, u_tint;
      uniform float u_cast, u_skin, u_product, u_sharpen, u_denoise, u_vignette, u_rolloff, u_midwarm;

      float luma(vec3 c) { return dot(c, vec3(0.2126, 0.7152, 0.0722)); }

      vec3 rgb2hsv(vec3 c) {
        vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
        vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
        vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
        float d = q.x - min(q.w, q.y);
        float e = 1.0e-10;
        return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
      }

      vec3 sampleTex(vec2 uv) { return texture2D(u_tex, uv).rgb; }

      float shoulder(float x, float k) {
        if (x <= k) return x;
        return k + (1.0 - k) * (1.0 - exp(-(x - k) / (1.0 - k)));
      }

      void main() {
        vec2 uv = mix(u_crop0, u_crop1, v_uv);
        vec3 src = sampleTex(uv);
        if (u_enabled < 0.5) { gl_FragColor = vec4(src, 1.0); return; }
        vec3 c = src;

        // Light edge-preserving noise reduction (3x3 bilateral).
        if (u_denoise > 0.0) {
          vec3 sum = c; float wsum = 1.0;
          for (int i = -1; i <= 1; i++) {
            for (int j = -1; j <= 1; j++) {
              if (i == 0 && j == 0) continue;
              vec3 s = sampleTex(uv + vec2(float(i), float(j)) * u_texel);
              float d = length(s - src);
              float w = exp(-d * d / 0.0072) * ((i != 0 && j != 0) ? 0.6 : 1.0);
              sum += s * w; wsum += w;
            }
          }
          c = mix(c, sum / wsum, u_denoise);
        }

        // Very subtle luminance-only unsharp mask, clamped to avoid halos.
        if (u_sharpen > 0.0) {
          vec3 b = (sampleTex(uv + vec2(1.5, 0.0) * u_texel) + sampleTex(uv - vec2(1.5, 0.0) * u_texel)
                  + sampleTex(uv + vec2(0.0, 1.5) * u_texel) + sampleTex(uv - vec2(0.0, 1.5) * u_texel)) * 0.25;
          float dl = clamp(luma(c) - luma(b), -0.06, 0.06);
          c += dl * u_sharpen;
        }

        vec3 base = clamp(c, 0.0, 1.0);

        // White balance + exposure in linear light.
        vec3 lin = pow(base, vec3(2.2));
        lin *= vec3(1.0 + u_temp * 0.10, 1.0 - u_tint * 0.07, 1.0 - u_temp * 0.13);
        lin *= exp2(u_exposure);
        vec3 p = pow(max(lin, 0.0), vec3(1.0 / 2.2));

        // Levels: blacks / whites.
        float bp = -u_blacks * 0.35;
        float wp = 1.0 - u_whites * 0.35;
        p = (p - bp) / (wp - bp);

        // Shadows (bell around low mids, true blacks stay glossy) and highlights.
        float L = luma(p);
        float ws = smoothstep(0.0, 0.16, L) * (1.0 - smoothstep(0.16, 0.6, L));
        float wh = smoothstep(0.45, 1.0, L);
        float Lt = L + u_shadows * 0.22 * ws + u_highlights * 0.30 * wh;
        p = mix(p + (Lt - L), p * (Lt / max(L, 0.001)), smoothstep(0.05, 0.25, L));

        // Brightness as a midtone gamma (protects whites and blacks).
        p = pow(max(p, 0.0), vec3(1.0 / (1.0 + u_brightness * 0.6)));

        // Natural contrast around a mid-grey pivot.
        p = (p - 0.46) * (1.0 + u_contrast) + 0.46;

        // Warm midtones, clean neutral shadows.
        L = luma(p);
        float wm = smoothstep(0.15, 0.5, L) * (1.0 - smoothstep(0.55, 0.9, L));
        p += vec3(0.018, 0.006, -0.016) * u_midwarm * wm;
        float wsh = 1.0 - smoothstep(0.05, 0.25, L);
        p = mix(p, vec3(L), 0.25 * u_cast * wsh);

        // Cast correction: pull near-neutral bright areas (beige wall, curtain,
        // white box) toward a clean warm ivory, removing yellow/green tints.
        vec3 hsvP = rgb2hsv(clamp(p, 0.0, 1.0));
        float neutralW = (1.0 - smoothstep(0.06, 0.22, hsvP.y)) * smoothstep(0.35, 0.75, L) * u_cast;
        vec3 ivory = vec3(1.0, 0.982, 0.945);
        vec3 ivoryTarget = ivory * (L / luma(ivory));
        p = mix(p, ivoryTarget, neutralW * 0.55);

        // Vibrance (weighted toward muted colours) then saturation.
        L = luma(p);
        float mx = max(p.r, max(p.g, p.b));
        float mn = min(p.r, min(p.g, p.b));
        float sat = mx - mn;
        p = mix(vec3(L), p, 1.0 + u_vib * (1.0 - smoothstep(0.0, 0.5, sat)));
        p = mix(vec3(luma(p)), p, 1.0 + u_sat);

        // Highlight roll-off (soft shoulder).
        vec3 rolled = vec3(shoulder(p.r, 0.80), shoulder(p.g, 0.80), shoulder(p.b, 0.80));
        p = mix(p, rolled, u_rolloff);

        // Skin & product protection: keep the ORIGINAL hue/chroma of skin and
        // of the deep-red packaging / reddish-brown softgels, adopting only the
        // new brightness. Prevents orange/pink skin and shifted product colours.
        vec3 hsvO = rgb2hsv(base);
        float h = hsvO.x;
        float skin = smoothstep(0.015, 0.035, h) * (1.0 - smoothstep(0.10, 0.14, h))
                   * smoothstep(0.10, 0.18, hsvO.y) * (1.0 - smoothstep(0.62, 0.78, hsvO.y))
                   * smoothstep(0.18, 0.30, hsvO.z);
        float redHue = max(1.0 - smoothstep(0.02, 0.05, h), smoothstep(0.92, 0.96, h));
        float product = redHue * smoothstep(0.35, 0.55, hsvO.y);
        float protect = clamp(skin * u_skin + product * u_product, 0.0, 1.0);
        float Lg = luma(p);
        vec3 toneOnly = base * (Lg / max(luma(base), 0.002));
        p = mix(p, toneOnly, protect);

        // Very subtle vignette.
        vec2 d = (v_uv - 0.5) * vec2(u_aspect, 1.0);
        float r = length(d) / length(vec2(u_aspect, 1.0) * 0.5);
        p *= 1.0 - u_vignette * smoothstep(0.45, 1.0, r) * 1.6;

        gl_FragColor = vec4(clamp(p, 0.0, 1.0), 1.0);
      }`;
    const prog = gl.createProgram();
    [[gl.VERTEX_SHADER, vs], [gl.FRAGMENT_SHADER, fs]].forEach(([type, src]) => {
      const s = gl.createShader(type);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
      gl.attachShader(prog, s);
    });
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
    gl.useProgram(prog);
    this.prog = prog;

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, 'a_pos');
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

    this.tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, this.tex);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);

    this.u = {};
    ['u_tex', 'u_texel', 'u_crop0', 'u_crop1', 'u_aspect', 'u_enabled', 'u_exposure', 'u_brightness', 'u_contrast',
      'u_highlights', 'u_shadows', 'u_whites', 'u_blacks', 'u_sat', 'u_vib', 'u_temp', 'u_tint', 'u_cast',
      'u_skin', 'u_product', 'u_sharpen', 'u_denoise', 'u_vignette', 'u_rolloff', 'u_midwarm']
      .forEach((n) => { this.u[n] = gl.getUniformLocation(prog, n); });
  }

  /* Render `source` (video/canvas) graded into an outW×outH canvas.
   * crop = [x0,y0,x1,y1] normalised source region to show. */
  process(source, srcW, srcH, outW, outH, g, crop) {
    const gl = this.gl;
    if (this.canvas.width !== outW || this.canvas.height !== outH) {
      this.canvas.width = outW;
      this.canvas.height = outH;
    }
    gl.viewport(0, 0, outW, outH);
    gl.bindTexture(gl.TEXTURE_2D, this.tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, source);
    const u = this.u;
    const c = crop || [0, 0, 1, 1];
    gl.uniform1i(u.u_tex, 0);
    gl.uniform2f(u.u_texel, 1 / srcW, 1 / srcH);
    gl.uniform2f(u.u_crop0, c[0], c[1]);
    gl.uniform2f(u.u_crop1, c[2], c[3]);
    gl.uniform1f(u.u_aspect, outW / outH);
    gl.uniform1f(u.u_enabled, g.enabled ? 1 : 0);
    gl.uniform1f(u.u_exposure, g.exposure);
    gl.uniform1f(u.u_brightness, g.brightness / 100);
    gl.uniform1f(u.u_contrast, g.contrast / 100);
    gl.uniform1f(u.u_highlights, g.highlights / 100);
    gl.uniform1f(u.u_shadows, g.shadows / 100);
    gl.uniform1f(u.u_whites, g.whites / 100);
    gl.uniform1f(u.u_blacks, g.blacks / 100);
    gl.uniform1f(u.u_sat, g.saturation / 100);
    gl.uniform1f(u.u_vib, g.vibrance / 100);
    gl.uniform1f(u.u_temp, g.temperature / 100);
    gl.uniform1f(u.u_tint, g.tint / 100);
    gl.uniform1f(u.u_cast, g.castCorrection / 100);
    gl.uniform1f(u.u_skin, g.skinProtect / 100);
    gl.uniform1f(u.u_product, g.productProtect / 100);
    gl.uniform1f(u.u_sharpen, g.sharpen / 100 * 1.2);
    gl.uniform1f(u.u_denoise, g.denoise / 100);
    gl.uniform1f(u.u_vignette, g.vignette / 100);
    gl.uniform1f(u.u_rolloff, g.rolloff / 100);
    gl.uniform1f(u.u_midwarm, g.midWarmth / 100);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    return this.canvas;
  }
};
