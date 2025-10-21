import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility Tests', () => {
  test('intro page should not have accessibility violations', async ({ page }) => {
    await page.goto('/');
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('contact form should not have accessibility violations', async ({ page }) => {
    await page.goto('/');
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('assessment questions should not have accessibility violations', async ({ page }) => {
    await page.goto('/');
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    await page.getByLabel(/email/i).fill('a11y-test@example.com');
    await page.getByLabel(/company name/i).fill('A11y Test Company');
    
    await page.getByRole('combobox', { name: /employee range/i }).click();
    await page.getByRole('option', { name: /11-50 employees/i }).click();
    
    await page.getByRole('checkbox', { name: /new south wales/i }).click();
    await page.getByLabel(/consent/i).click();
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    await expect(page.getByText(/question 1 of/i)).toBeVisible({ timeout: 10000 });
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('form inputs should have proper labels', async ({ page }) => {
    await page.goto('/');
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    const emailInput = page.getByLabel(/email/i);
    await expect(emailInput).toBeVisible();
    
    const companyInput = page.getByLabel(/company name/i);
    await expect(companyInput).toBeVisible();
    
    const employeeRangeSelect = page.getByRole('combobox', { name: /employee range/i });
    await expect(employeeRangeSelect).toBeVisible();
  });

  test('buttons should have accessible names', async ({ page }) => {
    await page.goto('/');
    
    const startButton = page.getByRole('button', { name: /start assessment/i });
    await expect(startButton).toBeVisible();
    
    await startButton.click();
    
    const backButton = page.getByRole('button', { name: /back/i });
    await expect(backButton).toBeVisible();
    
    const submitButton = page.getByRole('button', { name: /start assessment/i });
    await expect(submitButton).toBeVisible();
  });

  test('checkboxes should have proper labels and be keyboard accessible', async ({ page }) => {
    await page.goto('/');
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    const nswCheckbox = page.getByRole('checkbox', { name: /new south wales/i });
    await expect(nswCheckbox).toBeVisible();
    
    await nswCheckbox.focus();
    await page.keyboard.press('Space');
    await expect(nswCheckbox).toBeChecked();
    
    const consentCheckbox = page.getByLabel(/consent/i);
    await expect(consentCheckbox).toBeVisible();
    
    await consentCheckbox.focus();
    await page.keyboard.press('Space');
    await expect(consentCheckbox).toBeChecked();
  });

  test('radio buttons should be keyboard accessible', async ({ page }) => {
    await page.goto('/');
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    await page.getByLabel(/email/i).fill('keyboard-test@example.com');
    await page.getByLabel(/company name/i).fill('Keyboard Test Company');
    
    await page.getByRole('combobox', { name: /employee range/i }).click();
    await page.getByRole('option', { name: /11-50 employees/i }).click();
    
    await page.getByRole('checkbox', { name: /new south wales/i }).click();
    await page.getByLabel(/consent/i).click();
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    await expect(page.getByText(/question 1 of/i)).toBeVisible({ timeout: 10000 });
    
    const firstRadio = page.locator('input[type="radio"]').first();
    await firstRadio.focus();
    await page.keyboard.press('Space');
    await expect(firstRadio).toBeChecked();
  });

  test('page should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/');
    
    const h1 = page.locator('h1, [role="heading"][aria-level="1"]');
    await expect(h1).toHaveCount(1);
  });

  test('images should have alt text', async ({ page }) => {
    await page.goto('/');
    
    const images = page.locator('img');
    const count = await images.count();
    
    for (let i = 0; i < count; i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute('alt');
      expect(alt).toBeTruthy();
    }
  });

  test('links should have descriptive text', async ({ page }) => {
    await page.goto('/');
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    await page.getByLabel(/email/i).fill('link-test@example.com');
    await page.getByLabel(/company name/i).fill('Link Test Company');
    
    await page.getByRole('combobox', { name: /employee range/i }).click();
    await page.getByRole('option', { name: /11-50 employees/i }).click();
    
    await page.getByRole('checkbox', { name: /new south wales/i }).click();
    await page.getByLabel(/consent/i).click();
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    await expect(page.getByText(/question 1 of/i)).toBeVisible({ timeout: 10000 });
    
    const links = page.locator('a');
    const count = await links.count();
    
    for (let i = 0; i < count; i++) {
      const link = links.nth(i);
      const text = await link.textContent();
      const ariaLabel = await link.getAttribute('aria-label');
      
      expect(text || ariaLabel).toBeTruthy();
    }
  });

  test('color contrast should meet WCAG AA standards', async ({ page }) => {
    await page.goto('/');
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa'])
      .analyze();

    const contrastViolations = accessibilityScanResults.violations.filter(
      v => v.id === 'color-contrast'
    );
    
    expect(contrastViolations).toEqual([]);
  });
});
