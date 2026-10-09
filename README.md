# Membase Docs

Source for **[docs.membase.io](https://docs.membase.io)** — built with [Starlight](https://starlight.astro.build) and deployed to GitHub Pages on every push to `main` (`.github/workflows/deploy.yml`).

Pages live in `src/content/docs/`; the sidebar is defined in `astro.config.mjs`.

```bash
nvm use          # Node 22 (.nvmrc)
npm install
npm run dev      # http://localhost:4321
npm run build    # -> dist/
```
