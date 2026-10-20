# Membase Docs

Source for **[docs.membase.com](https://docs.membase.com)** — built with [Starlight](https://starlight.astro.build) and deployed to GitHub Pages on every push to `main` (`.github/workflows/deploy.yml`).

Pages live in `src/content/docs/`; the sidebar is defined in `astro.config.mjs`.

This repo is the source of truth for the Membase docs — edit pages here. **Read [CLAUDE.md](CLAUDE.md)
first** — the site is Starlight, not GitBook, and `npm run check` enforces the format. Images are in
`public/images/`. (Content was first imported from `membase-suites` `docs/developer` +
`docs/user-guide`, which also fed the former GitBook; page URLs match that GitBook.)

```bash
nvm use          # Node 22 (.nvmrc)
npm install
npm run dev      # http://localhost:4321
npm run build    # -> dist/
npm run indexnow # after a deploy is live: push every page (or the URLs you pass) to IndexNow
```
