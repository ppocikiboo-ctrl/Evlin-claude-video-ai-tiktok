import { heygenAuthHeaders, searchSounds } from "/root/.claude/skills/media-use/audio/scripts/lib/heygen.mjs";
const headers = heygenAuthHeaders();
for (const q of process.argv.slice(2)) {
  const r = await searchSounds(q, process.env.T || "music", headers, { limit: 8, minScore: process.env.MIN ? Number(process.env.MIN) : undefined });
  console.log("## " + q);
  for (const x of r) console.log(JSON.stringify({ id:x.id, name:x.name||x.title, dur:x.duration, score:x.score, tags:x.tags, desc:(x.description||"").slice(0,90), url:(x.audio_url||"").slice(0,60) }));
}
