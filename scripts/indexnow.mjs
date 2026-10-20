#!/usr/bin/env node
/**
 * Push URLs to IndexNow (Bing, Yandex, Seznam, Naver… share submissions), so a new or
 * changed page is crawled within hours instead of whenever the sitemap is next read.
 *
 *   npm run indexnow -- https://docs.membase.com/build/ [more URLs…]
 *   npm run indexnow            # no arguments: every URL in the live sitemap
 *
 * Run it after the deploy is live: IndexNow fetches the key file from the site to verify
 * the submission, and crawls the URLs straight away. The key is the file in public/ named
 * `<key>.txt` whose content is the key itself.
 */
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const SITE_URL = (process.env.DOCS_SITE_URL ?? 'https://docs.membase.com').replace(/\/$/, '');
const host = new URL(SITE_URL).host;

const publicDir = join(import.meta.dirname, '..', 'public');
const key = readdirSync(publicDir)
  .filter(f => /^[a-f0-9]{8,128}\.txt$/i.test(f))
  .map(f => f.slice(0, -4))
  .find(k => readFileSync(join(publicDir, `${k}.txt`), 'utf8').trim() === k);
if (!key) {
  console.error('No IndexNow key file in public/ (expected <key>.txt containing the key).');
  process.exit(1);
}

const locs = async url => [...(await (await fetch(url)).text()).matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1]);

let urls = process.argv.slice(2);
if (!urls.length) {
  // Astro writes a sitemap index pointing at numbered sitemaps; the pages are in those.
  for (const sitemap of await locs(`${SITE_URL}/sitemap-index.xml`)) urls.push(...(await locs(sitemap)));
}
const foreign = urls.filter(u => new URL(u).host !== host);
if (!urls.length || foreign.length) {
  console.error(urls.length ? `Only ${host} URLs can be submitted with this key:\n  ${foreign.join('\n  ')}` : 'No URLs to submit.');
  process.exit(1);
}

const res = await fetch('https://api.indexnow.org/indexnow', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json; charset=utf-8' },
  body: JSON.stringify({ host, key, keyLocation: `${SITE_URL}/${key}.txt`, urlList: urls }),
});
// 200 = accepted, 202 = accepted, key validation pending. Anything else is a failure.
console.log(`IndexNow ${res.status} ${res.statusText} — ${urls.length} URL(s)`);
for (const u of urls) console.log(`  ${u}`);
if (res.status !== 200 && res.status !== 202) {
  console.error(await res.text());
  process.exit(1);
}
