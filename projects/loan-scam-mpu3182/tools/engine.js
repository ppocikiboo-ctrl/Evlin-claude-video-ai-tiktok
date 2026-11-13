// Builds this scene's tweens from the data-* attributes written in the HTML.
// Each .card is a timed clip; its .card-in child enters and exits, and every [data-fx]
// element inside enters at card start + data-in. Nothing here depends on wall-clock time.
const root = document.getElementById("__SID__");
const tl = gsap.timeline({ paused: true });
const num = (v, d) => (v === undefined || v === "" ? d : parseFloat(v));
const fmt = (v, f, dec) => {
  const n = dec > 0 ? v.toFixed(dec) : String(Math.round(v));
  return f === "comma" ? n.replace(/\B(?=(\d{3})+(?!\d))/g, ",") : n;
};

root.querySelectorAll(".card").forEach((card) => {
  const s = num(card.dataset.start, 0);
  const e = s + num(card.dataset.duration, 1);
  const inner = card.querySelector(".card-in");
  const fromY = card.classList.contains("zone-bottom") ? 26 : card.classList.contains("zone-full") ? 0 : -26;
  tl.fromTo(inner, { opacity: 0, y: fromY }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, s);
  if (e - s > 0.9) tl.to(inner, { opacity: 0, y: fromY * 0.6, duration: 0.3, ease: "power2.in" }, e - 0.32);
  tl.set(inner, { visibility: "hidden" }, e - 0.01);

  card.querySelectorAll("[data-fx]").forEach((el) => {
    const t = s + num(el.dataset.in, 0);
    const fx = el.dataset.fx;
    if (t >= e - 0.05) return;
    if (fx === "rise") tl.fromTo(el, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, t);
    else if (fx === "fade") tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power1.out" }, t);
    else if (fx === "wipe") tl.fromTo(el, { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: 0.5, ease: "power3.out" }, t);
    else if (fx === "draw") tl.fromTo(el, { scaleX: 0 }, { scaleX: 1, duration: 0.55, ease: "power2.out" }, t);
    else if (fx === "slide") tl.fromTo(el, { opacity: 0, x: -44 }, { opacity: 1, x: 0, duration: 0.42, ease: "power3.out" }, t);
    else if (fx === "pop") tl.fromTo(el, { opacity: 0, scale: 0.55 }, { opacity: 1, scale: 1, duration: 0.38, ease: "back.out(2.2)" }, t);
    else if (fx === "slam") tl.fromTo(el, { opacity: 0, scale: 1.55 }, { opacity: 1, scale: 1, duration: 0.26, ease: "power4.out" }, t);
    else if (fx === "slate") tl.fromTo(el, { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: 0.45, ease: "power3.inOut" }, t);
    else if (fx === "dock") tl.fromTo(el, { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }, t);
    else if (fx === "plate") tl.fromTo(el, { opacity: 0, y: 40, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.6)" }, t);
    else if (fx === "drop") {
      const r = num(el.dataset.rot, 0);
      tl.fromTo(el, { opacity: 0, y: -70, rotation: r + 5 }, { opacity: 1, y: 0, rotation: r, duration: 0.5, ease: "power3.out" }, t);
    } else if (fx === "stamp") {
      const r = num(el.dataset.rot, -8);
      tl.fromTo(el, { opacity: 0, scale: 2.6, rotation: r - 6 }, { opacity: 1, scale: 1, rotation: r, duration: 0.17, ease: "power4.in" }, t - 0.17);
      tl.fromTo(inner, { x: 0 }, { x: 7, duration: 0.05, yoyo: true, repeat: 3, ease: "none" }, t);
    } else if (fx === "type") {
      const cs = el.querySelectorAll(".tw");
      tl.fromTo(cs, { opacity: 0 }, { opacity: 1, duration: 0.01, stagger: 0.045, ease: "none" }, t);
    } else if (fx === "count") {
      const to = num(el.dataset.to, 0), land = s + num(el.dataset.land, 1), dec = num(el.dataset.dec, 0), f = el.dataset.fmt;
      const o = { v: 0 };
      el.textContent = fmt(0, f, dec);
      tl.fromTo(o, { v: 0 }, { v: to, duration: Math.max(0.3, land - t), ease: "power2.out",
        onUpdate: () => { el.textContent = fmt(o.v, f, dec); } }, t);
    } else if (fx === "pan") {
      const p = (el.dataset.pan || "0,0").split(",").map(parseFloat);
      tl.fromTo(el, { yPercent: p[0] }, { yPercent: p[1], duration: Math.max(0.5, e - t), ease: "sine.inOut" }, t);
    } else if (fx === "ring") {
      const fg = el.querySelector(".ring-fg");
      tl.fromTo(fg, { strokeDashoffset: 314.16 }, { strokeDashoffset: 314.16 * (1 - num(el.dataset.to, 0) / 100), duration: 0.8, ease: "power2.out" }, t);
    } else if (fx === "grow") {
      tl.fromTo(el, { scaleX: 0 }, { scaleX: num(el.dataset.w, 100) / 100, duration: 0.8, ease: "power3.out" }, t);
    } else if (fx === "cut") {
      tl.fromTo(el, { opacity: 0, scaleY: 0, rotation: 18 }, { opacity: 1, scaleY: 1, rotation: 18, duration: 0.14, ease: "power4.out" }, t);
      const ls = card.querySelectorAll(".link");
      if (ls.length === 3) {
        tl.to(ls[0], { x: -26, duration: 0.3, ease: "power3.out" }, t + 0.05);
        tl.to(ls[2], { x: 26, duration: 0.3, ease: "power3.out" }, t + 0.05);
        tl.to(ls[1], { opacity: 0.35, y: 18, rotation: -6, duration: 0.35, ease: "power3.out" }, t + 0.05);
      }
    }
  });
});

window.__timelines = window.__timelines || {};
window.__timelines["__SID__"] = tl;
