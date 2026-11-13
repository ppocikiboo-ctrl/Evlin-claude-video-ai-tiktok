import { heygenAuthHeaders, searchSounds, downloadTo } from "/root/.claude/skills/media-use/audio/scripts/lib/heygen.mjs";
const headers = heygenAuthHeaders();
const [q, id, out] = process.argv.slice(2);
const r = await searchSounds(q, "music", headers, { limit: 8 });
const x = r.find(t => t.id === id); await downloadTo(x.audio_url, out); console.log("ok", out);
