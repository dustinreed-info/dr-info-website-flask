import { test, expect } from '@playwright/test';

const pages = [
  { path: '/', title: 'Home - Dustin Reed', heading: 'Dustin Reed' },
  { path: '/about/', title: 'About - Dustin Reed', heading: 'About This Website' },
  { path: '/certifications/', title: 'Certifications - Dustin Reed', heading: 'Certifications' },
  { path: '/contact/', title: 'Contact - Dustin Reed', heading: 'Get In Touch' },
  { path: '/projects/', title: 'Projects - Dustin Reed', heading: 'My Projects' },
];

test.describe('pages', () => {
  for (const { path, title, heading } of pages) {
    test(`${path} loads with correct title and heading`, async ({ page }) => {
      const response = await page.goto(path);
      expect(response?.ok()).toBeTruthy();
      await expect(page).toHaveTitle(title);
      await expect(page.getByRole('heading', { name: heading }).first()).toBeVisible();
    });
  }
});

test.describe('navigation', () => {
  test('navbar has the expected links', async ({ page }) => {
    await page.goto('/');
    const nav = page.locator('.nav-menu');

    for (const href of ['/about/', '/certifications/', '/projects/', '/contact/']) {
      await expect(nav.locator(`a[href="${href}"]`)).toHaveCount(1);
    }

    const resume = nav.getByRole('link', { name: 'Resume' });
    await expect(resume).toHaveAttribute('href', '/Resume-Reed-Dustin.pdf');
  });
});

test.describe('assets', () => {
  const badges = ['/static/aws-cda-badge.png', '/static/aws-csa-badge.png'];

  test('certification badge images load', async ({ page }) => {
    await page.goto('/certifications/');
    for (const src of badges) {
      const img = page.locator(`img[src="${src}"]`);
      await expect(img).toBeVisible();
      await img.scrollIntoViewIfNeeded();
      await expect
        .poll(async () => img.evaluate((el: HTMLImageElement) => el.naturalWidth))
        .toBeGreaterThan(0);
    }
  });

  test('badge assets respond 200', async ({ request }) => {
    for (const src of badges) {
      const res = await request.get(src);
      expect(res.status()).toBe(200);
    }
  });

  test('site.css responds 200', async ({ request }) => {
    const res = await request.get('/static/site.css');
    expect(res.status()).toBe(200);
  });
});

test.describe('404', () => {
  test('unknown path renders the 404 page', async ({ page }) => {
    await page.goto('/does-not-exist');
    await expect(page.getByText('could not be found')).toBeVisible();
  });
});
