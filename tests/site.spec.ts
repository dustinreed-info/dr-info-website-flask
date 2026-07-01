import { test, expect } from '@playwright/test';
import { TEST_LAMBDA_ENDPOINT } from './constants';

const MOBILE_VIEWPORT = { width: 375, height: 667 };
const DESKTOP_VIEWPORT = { width: 1280, height: 720 };

async function fillContactForm(page: import('@playwright/test').Page) {
  await page.locator('#name').fill('Test User');
  await page.locator('#email').fill('test@example.com');
  await page.locator('#subject').fill('Test Subject');
  await page.locator('#message').fill('Test message for Playwright.');
}

async function mockContactSubmission(
  page: import('@playwright/test').Page,
  status: number,
) {
  await page.route(`**/${new URL(TEST_LAMBDA_ENDPOINT).host}/**`, async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: status === 200 ? '{}' : JSON.stringify({ error: 'Server error' }),
      });
      return;
    }
    await route.continue();
  });
}

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

  test('mobile nav toggle opens menu and navigates', async ({ page }) => {
    await page.setViewportSize(MOBILE_VIEWPORT);
    await page.goto('/');

    const navToggle = page.locator('#nav-toggle');
    const navMenu = page.locator('#nav-menu');

    await expect(navToggle).toBeVisible();
    await expect(navMenu).not.toHaveClass(/active/);

    await navToggle.click();
    await expect(navMenu).toHaveClass(/active/);

    await navMenu.getByRole('link', { name: 'About' }).click();
    await expect(page).toHaveURL('/about/');
    await expect(page.getByRole('heading', { name: 'About This Website' }).first()).toBeVisible();
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

test.describe('contact form', () => {
  test('renders Lambda-backed form fields', async ({ page }) => {
    await page.goto('/contact/');

    const form = page.locator('#contact-form');
    await expect(form).toBeVisible();
    await expect(form).not.toHaveAttribute('action', /mailto:/);

    for (const field of ['name', 'email', 'subject', 'message']) {
      await expect(form.locator(`[name="${field}"]`)).toBeVisible();
    }

    await expect(form.locator('#submit-btn')).toBeVisible();
  });

  test('shows success alert on successful submission', async ({ page }) => {
    await mockContactSubmission(page, 200);
    await page.goto('/contact/');
    await fillContactForm(page);

    const submitPromise = page.waitForRequest(
      (req) => req.method() === 'POST' && req.url().includes('test-lambda.example.com'),
    );
    await page.locator('#submit-btn').click();
    const submitRequest = await submitPromise;

    expect(submitRequest.postDataJSON()).toMatchObject({
      name: 'Test User',
      email: 'test@example.com',
      subject: 'Test Subject',
      message: 'Test message for Playwright.',
    });

    const successAlert = page.locator('#form-success');
    await expect(successAlert).toBeVisible();
    await expect(successAlert).toContainText('Success!');
    await expect(page.locator('#form-error')).toHaveClass(/hidden/);
  });

  test('shows error alert on failed submission', async ({ page }) => {
    await mockContactSubmission(page, 500);
    await page.goto('/contact/');
    await fillContactForm(page);
    await page.locator('#submit-btn').click();

    const errorAlert = page.locator('#form-error');
    await expect(errorAlert).toBeVisible();
    await expect(errorAlert).toContainText('Error!');
    await expect(errorAlert).toContainText('Failed to send message');
    await expect(page.locator('#form-success')).toHaveClass(/hidden/);
  });
});

test.describe('visual snapshots', () => {
  test('home page desktop', async ({ page }) => {
    await page.setViewportSize(DESKTOP_VIEWPORT);
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Dustin Reed' }).first()).toBeVisible();
    await expect(page).toHaveScreenshot('home-desktop.png');
  });

  test('home page mobile', async ({ page }) => {
    await page.setViewportSize(MOBILE_VIEWPORT);
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Dustin Reed' }).first()).toBeVisible();
    await expect(page).toHaveScreenshot('home-mobile.png');
  });

  test('contact page desktop', async ({ page }) => {
    await page.setViewportSize(DESKTOP_VIEWPORT);
    await page.goto('/contact/');
    await expect(page.getByRole('heading', { name: 'Get In Touch' }).first()).toBeVisible();
    await expect(page).toHaveScreenshot('contact-desktop.png');
  });

  test('contact page mobile', async ({ page }) => {
    await page.setViewportSize(MOBILE_VIEWPORT);
    await page.goto('/contact/');
    await expect(page.getByRole('heading', { name: 'Get In Touch' }).first()).toBeVisible();
    await expect(page).toHaveScreenshot('contact-mobile.png');
  });
});

test.describe('404', () => {
  test('unknown path renders the 404 page', async ({ page }) => {
    await page.goto('/does-not-exist');
    await expect(page.getByText('could not be found')).toBeVisible();
  });
});
