#!/usr/bin/env node

/**
 * Capture full-page screenshots of all site pages at desktop and mobile viewports.
 *
 * Usage:
 *   node scripts/screenshots.mjs [before|after|both]
 *   npm run screenshots              # defaults to after
 *   npm run screenshots -- before
 *   npm run screenshots -- after
 *   npm run screenshots -- both
 *   npm run screenshots:both
 *
 * Output: screenshots/{before|after}/{page}-{desktop|mobile}.png
 */

import { chromium } from '@playwright/test';
import { spawn } from 'child_process';
import { mkdir } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const PORT = 4321;
const BASE_URL = `http://localhost:${PORT}`;
const TEST_LAMBDA_ENDPOINT = 'https://test-lambda.example.com/contact';

const PAGES = [
  { slug: 'home', path: '/' },
  { slug: 'about', path: '/about/' },
  { slug: 'certifications', path: '/certifications/' },
  { slug: 'contact', path: '/contact/' },
  { slug: 'projects', path: '/projects/' },
  { slug: '404', path: '/404.html' },
];

const VIEWPORTS = {
  desktop: { width: 1280, height: 800 },
  mobile: { width: 375, height: 667 },
};

const VALID_SETS = new Set(['before', 'after', 'both']);

function usage() {
  console.error('Usage: node scripts/screenshots.mjs [before|after|both]');
  process.exit(1);
}

function resolveTargets(arg) {
  if (!arg) {
    console.log(
      'No target specified, defaulting to after. Use: npm run screenshots -- before|after',
    );
    return ['after'];
  }
  if (!VALID_SETS.has(arg)) {
    usage();
  }
  return arg === 'both' ? ['before', 'after'] : [arg];
}

async function waitForServer(url, timeoutMs = 120_000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(url);
      if (res.ok || res.status === 404) return;
    } catch {
      // server not ready yet
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(`Server did not become ready at ${url} within ${timeoutMs}ms`);
}

function startPreviewServer() {
  return new Promise((resolve, reject) => {
    const child = spawn('npm', ['run', 'build'], {
      cwd: ROOT,
      stdio: 'inherit',
      env: { ...process.env, PUBLIC_LAMBDA_ENDPOINT: TEST_LAMBDA_ENDPOINT },
      shell: true,
    });

    child.on('error', reject);
    child.on('exit', (code) => {
      if (code !== 0) {
        reject(new Error(`npm run build exited with code ${code}`));
        return;
      }

      const preview = spawn('npm', ['run', 'preview'], {
        cwd: ROOT,
        stdio: 'inherit',
        env: { ...process.env, PUBLIC_LAMBDA_ENDPOINT: TEST_LAMBDA_ENDPOINT },
        shell: true,
      });

      preview.on('error', reject);

      resolve({
        stop: () => {
          preview.kill('SIGTERM');
        },
      });
    });
  });
}

async function captureScreenshots(setName) {
  const outputDir = path.join(ROOT, 'screenshots', setName);
  await mkdir(outputDir, { recursive: true });

  console.log(`Building site and starting preview on ${BASE_URL}...`);
  const server = await startPreviewServer();

  try {
    await waitForServer(BASE_URL);
    console.log(`Capturing screenshots to ${outputDir}/`);

    const browser = await chromium.launch();
    const context = await browser.newContext();

    for (const { slug, path: pagePath } of PAGES) {
      for (const [viewportName, size] of Object.entries(VIEWPORTS)) {
        const page = await context.newPage();
        await page.setViewportSize(size);
        const url = `${BASE_URL}${pagePath}`;
        const response = await page.goto(url, { waitUntil: 'networkidle' });
        if (!response?.ok()) {
          throw new Error(`Failed to load ${url} (status ${response?.status()})`);
        }
        const filename = `${slug}-${viewportName}.png`;
        const filepath = path.join(outputDir, filename);
        await page.screenshot({ path: filepath, fullPage: true });
        console.log(`  ${filename}`);
        await page.close();
      }
    }

    await browser.close();
    console.log(`Done — ${PAGES.length * Object.keys(VIEWPORTS).length} images in ${outputDir}/`);
  } finally {
    server.stop();
  }
}

const targets = resolveTargets(process.argv[2]);

(async () => {
  for (const setName of targets) {
    await captureScreenshots(setName);
  }
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
