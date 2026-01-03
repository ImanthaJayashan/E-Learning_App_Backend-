# Write-Sense Frontend

Small React + Vite frontend for the Write-Sense e-learning project.

## Quick Overview

- **Stack:** React, TypeScript, Vite, Tailwind CSS, Framer Motion
- **Purpose:** Frontend for tutorials and interactive learning experiences

## Prerequisites

- Node.js (recommend 16+ or 18+)
- npm (or use yarn/pnpm)

## Install

```bash
npm install
```

## Available scripts

- `npm run dev` — start development server (Vite)
- `npm run build` — build production assets
- `npm run preview` — locally preview production build

## Project structure

- index.html
- package.json
- vite.config.ts
- postcss.config.js
- tailwind.config.js
- src/
  - App.tsx
  - main.tsx
  - style.css
  - components/
    - Navbar.tsx
    - PrimaryButton.tsx
  - pages/
    - Landing.tsx
    - Tutorials.tsx
- public/
  - answers/

## Local development

1. Install deps: `npm install`
2. Start dev server: `npm run dev`
3. Open the URL shown by Vite (usually http://localhost:5173)

## Building for production

```bash
npm run build
npm run preview
```

## Notes

- The project uses Vite + React plugin; TypeScript types are included in `devDependencies`.
- If you plan to add backend integration, add environment variable handling (example: `.env`) and update fetch endpoints accordingly.

## Next steps (suggestions)

- Add a `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` for collaboration.
- Add tests and a CI workflow (GitHub Actions) to run lints/tests on PRs.

---
Generated README by developer assistant.
