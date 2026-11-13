import { heygenAuthHeaders, searchSounds, downloadTo } from "/root/.claude/skills/media-use/audio/scripts/lib/heygen.mjs";
const headers = heygenAuthHeaders(); const dir = process.argv[2];
const want = [
 ["whoosh","68ce3485","whoosh-1"],["whoosh","f21dfc94","whoosh-2"],["soft cinematic whoosh swipe","a4855a82","whoosh-3"],
 ["A heavy rubber stamp slammed onto paper on a desk","c35b59ff","stamp-thud"],["A heavy rubber stamp slammed onto paper on a desk","cb87077c","stamp-clack"],
 ["Rapid mechanical typewriter keys typing a short line","fa6fa6ac","typing-1"],["Rapid mechanical typewriter keys typing a short line","420ffbbe","typing-2"],
 ["A short bright pop as a bubble appears","13175e25","pop-1"],["A short bright pop as a bubble appears","9efe59a2","pop-2"],
 ["Paper page turning","9b77ef76","paper"],["A rising cinematic tension riser building up","598ca16b","riser-slam"],["A rising cinematic tension riser building up","762c29b8","riser-short"],
 ["deep cinematic impact boom","7e1cbac7","impact-boom"],["A crisp camera shutter click","618e3c54","shutter"],["Coins and cash register cha-ching","2d6aa30f","cash"],
 ["A soft glassy notification ping","fd8d6893","ping-1"],["A soft glassy notification ping","9eddaec3","ping-2"],
 ["A digital glitch stutter burst","226f9d29","glitch-1"],["A digital glitch stutter burst","0107dd4e","glitch-2"],["A single soft mouse click","cf8c57bb","click"],
 ["A tense low drone sting with a dark hit","ac60d9b0","drone-hit"]];
const cache = {};
for (const [q, pre, name] of want) {
  cache[q] ??= await searchSounds(q, "sound_effects", headers, { limit: 8, minScore: 0.4 });
  const x = cache[q].find(t => t.id.startsWith(pre));
  if (!x) { console.log("MISS", name); continue; }
  const ext = (x.audio_url.split("?")[0].split(".").pop() || "mp3");
  await downloadTo(x.audio_url, `${dir}/${name}.${ext}`); console.log("ok", name, ext, x.duration);
}
