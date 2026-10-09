# Membase Docs

Source for **[docs.membase.io](https://docs.membase.io)** — built with [Starlight](https://starlight.astro.build) and deployed to GitHub Pages on every push to `main` (`.github/workflows/deploy.yml`).

Pages live in `src/content/docs/`; the sidebar is defined in `astro.config.mjs`.

Content was imported from the `membase-ai` docs in `membase-suites` (`docs/developer` +
`docs/user-guide`, `main` at 2026-10-02), the source of the former GitBook at
`noah-gao.gitbook.io/membase-user-guide`. Page URLs match that GitBook, so its links move
over by swapping the host. Images are in `public/images/`.

```bash
nvm use          # Node 22 (.nvmrc)
npm install
npm run dev      # http://localhost:4321
npm run build    # -> dist/
```
