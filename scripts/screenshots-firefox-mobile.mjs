#!/usr/bin/env node

/**
 * Capture mobile viewport screenshots in Firefox and Chromium for cross-browser comparison.
 *
 * Usage:
 *   node scripts/screenshots-firefox-mobile.mjs
 *
 * Output:
 *   screenshots/firefox-mobile/{page}.png
 *   screenshots/chromium-mobile/{page}.png
 */

import { firefox, chromium } from '@playwright/test';
import { spawn } from 'child_process';
import { mkdir } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const PORT = 4322;
const BASE_URL = `http://localhost:${PORT}`;
const TEST_LAMBDA_ENDPOINT = 'https://test-lambda.example.com/contact';

const PAGES = [
  { slug: 'home', path: '/' },
  { slug: 'about', path: '/about/' },
  { slug: 'certifications', path: '/certifications/' },
  { slug: 'contact', path: '/contact/' },
  { slug: 'projects', path: '/projects/' },
];

const MOBILE_VIEWPORT = { width: 375, height: 667 };

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

      const preview = spawn('npm', ['run', 'preview', '--', '--port', String(PORT)], {
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

async function captureWithBrowser(browserType, outputDir) {
  await mkdir(outputDir, { recursive: true });

  const browser = await browserType.launch();
  const context = await browser.newContext({
    viewport: MOBILE_VIEWPORT,
    isMobile: true,
    hasTouch: true,
  });

  for (const { slug, path: pagePath } of PAGES) {
    const page = await context.newPage();
    const url = `${BASE_URL}${pagePath}`;
    const response = await page.goto(url, { waitUntil: 'networkidle' });
    if (!response?.ok()) {
      throw new Error(`Failed to load ${url} (status ${response?.status()})`);
    }
    const filepath = path.join(outputDir, `${slug}.png`);
    await page.screenshot({ path: filepath, fullPage: true });
    console.log(`  ${path.basename(outputDir)}/${slug}.png`);
    await page.close();
  }

  await browser.close();
}

(async () => {
  console.log(`Building site and starting preview on ${BASE_URL}...`);
  const server = await startPreviewServer();

  try {
    await waitForServer(BASE_URL);

    console.log('Capturing Firefox mobile screenshots...');
    await captureWithBrowser(firefox, path.join(ROOT, 'screenshots', 'firefox-mobile'));

    console.log('Capturing Chromium mobile screenshots...');
    await captureWithBrowser(chromium, path.join(ROOT, 'screenshots', 'chromium-mobile'));

    console.log('Done.');
  } finally {
    server.stop();
  }
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
