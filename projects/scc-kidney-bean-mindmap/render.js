// Renders scene.html frame by frame and pipes PNGs into ffmpeg.
// usage: node render.js <base-url> <out.mp4> [--preview t1,t2,...  (writes PNG stills instead)]
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

(async () => {
  const [base, out, flag, list] = process.argv.slice(2);
  const tl = JSON.parse(fs.readFileSync(path.join(__dirname, "timeline.json"), "utf8"));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on("pageerror", e => { console.error("page error:", e); process.exit(1); });
  await page.goto(`${base}/scene.html`);
  await page.evaluate(() => window.ready);
  const canvas = await page.$("canvas");

  if (flag === "--preview") {
    for (const t of list.split(",").map(Number)) {
      await page.evaluate(t => window.renderFrame(t), t);
      await canvas.screenshot({ path: `${out}/preview_${t.toFixed(2)}.png` });
    }
  } else {
    const n = Math.round(tl.duration * tl.fps);
    const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(tl.fps), "-i", "-",
      "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", out], { stdio: ["pipe", "inherit", "inherit"] });
    for (let i = 0; i < n; i++) {
      await page.evaluate(t => window.renderFrame(t), i / tl.fps);
      const buf = await canvas.screenshot({ type: "png" });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
      if (i % 60 === 0) console.log(`frame ${i}/${n}`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on("close", r));
  }
  await browser.close();
})();
