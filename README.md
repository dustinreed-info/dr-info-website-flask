# Dustin Reed Info - Static Site

Source code for www.dustinreed.info. A static site built with **Astro + Tailwind CSS**,
deployed to AWS S3 + CloudFront.

Previously a Flask/Jinja2 app on Elastic Beanstalk; now a static-first Astro site
(server-side visitor tracking / analytics removed).

## Tech stack

- [Astro](https://astro.build) - static site generator
- [Tailwind CSS](https://tailwindcss.com) v4 (via `@tailwindcss/vite`)
- The existing `site.css` design is preserved; Tailwind utilities are available
  (imported without preflight in `src/styles/global.css`).

## Structure

```text
src/
├── layouts/BaseLayout.astro     # head + nav + footer shell
├── components/                  # Navbar, Footer
├── pages/                       # index, about, certifications, contact, projects, 404
└── styles/global.css            # Tailwind (no preflight, preserves site.css)
public/
├── static/                      # site.css, icons, images, manifest
└── *.pdf                        # resume + cert downloads
scripts/deploy.js                # build + S3 sync + CloudFront invalidation
.github/workflows/deploy.yml     # auto-deploy on push to main
```

## Local development

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # outputs static site to dist/
npm run preview  # preview the built site
npm test         # run the Playwright e2e suite
```

The first time you run the tests, install the browser: `npx playwright install chromium`.

## Docker

```bash
docker build -t dr-info-static .
docker run --rm -p 8080:80 dr-info-static   # http://localhost:8080
```

## Deploy

See [DEPLOYMENT.md](DEPLOYMENT.md). Quick version:

```bash
cp .env.example .env   # fill in S3_BUCKET, CLOUDFRONT_DIST_ID, S3_REGION
npm run deploy         # builds, then syncs dist/ to S3 + invalidates CloudFront
```

Pushes to `main` deploy automatically via GitHub Actions.
