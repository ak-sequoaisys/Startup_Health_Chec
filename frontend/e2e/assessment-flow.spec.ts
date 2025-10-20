import { test, expect } from '@playwright/test';

test.describe('Complete Assessment Flow', () => {
  test('should complete full assessment workflow', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByText('Startup Compliance Health Check')).toBeVisible();
    await expect(page.getByText(/Evaluate your HR & labour compliance/i)).toBeVisible();

    await page.getByRole('button', { name: /start assessment/i }).click();

    await expect(page.getByText('Start Your Compliance Assessment')).toBeVisible();

    await page.getByLabel(/email/i).fill('e2e-test@example.com');
    await page.getByLabel(/company name/i).fill('E2E Test Company');
    await page.getByLabel(/industry/i).fill('Technology');
    
    await page.getByRole('combobox', { name: /employee range/i }).click();
    await page.getByRole('option', { name: /11-50 employees/i }).click();

    await page.getByRole('checkbox', { name: /new south wales/i }).click();
    await page.getByRole('checkbox', { name: /victoria/i }).click();

    await page.getByRole('combobox', { name: /business age/i }).click();
    await page.getByRole('option', { name: /1-3 years/i }).click();

    await page.getByLabel(/consent/i).click();

    await page.getByRole('button', { name: /start assessment/i }).click();

    await expect(page.getByText(/question 1 of/i)).toBeVisible({ timeout: 10000 });

    const questionCount = await page.locator('text=/question \\d+ of (\\d+)/i').textContent();
    const totalQuestions = parseInt(questionCount?.match(/of (\d+)/)?.[1] || '0');

    for (let i = 0; i < totalQuestions; i++) {
      await expect(page.getByText(new RegExp(`question ${i + 1} of ${totalQuestions}`, 'i'))).toBeVisible();

      const firstOption = page.locator('input[type="radio"]').first();
      await firstOption.click();

      const nextButton = page.getByRole('button', { name: i === totalQuestions - 1 ? /submit/i : /next/i });
      await nextButton.click();

      if (i < totalQuestions - 1) {
        await page.waitForTimeout(500);
      }
    }

    await expect(page.getByText(/compliance score/i)).toBeVisible({ timeout: 15000 });
    await expect(page.getByText(/overall risk level/i)).toBeVisible();
  });

  test('should allow navigation back and forth between questions', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('button', { name: /start assessment/i }).click();

    await page.getByLabel(/email/i).fill('nav-test@example.com');
    await page.getByLabel(/company name/i).fill('Navigation Test Company');
    
    await page.getByRole('combobox', { name: /employee range/i }).click();
    await page.getByRole('option', { name: /11-50 employees/i }).click();

    await page.getByRole('checkbox', { name: /new south wales/i }).click();
    await page.getByLabel(/consent/i).click();

    await page.getByRole('button', { name: /start assessment/i }).click();

    await expect(page.getByText(/question 1 of/i)).toBeVisible({ timeout: 10000 });

    const firstOption = page.locator('input[type="radio"]').first();
    await firstOption.click();

    await page.getByRole('button', { name: /next/i }).click();

    await expect(page.getByText(/question 2 of/i)).toBeVisible();

    await page.getByRole('button', { name: /previous/i }).click();

    await expect(page.getByText(/question 1 of/i)).toBeVisible();
    await expect(firstOption).toBeChecked();
  });

  test('should display validation errors for incomplete contact form', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('button', { name: /start assessment/i }).click();

    await page.getByRole('button', { name: /start assessment/i }).click();

    const emailInput = page.getByLabel(/email/i);
    await expect(emailInput).toBeFocused();
  });

  test('should show progress indicator during assessment', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('button', { name: /start assessment/i }).click();

    await page.getByLabel(/email/i).fill('progress-test@example.com');
    await page.getByLabel(/company name/i).fill('Progress Test Company');
    
    await page.getByRole('combobox', { name: /employee range/i }).click();
    await page.getByRole('option', { name: /11-50 employees/i }).click();

    await page.getByRole('checkbox', { name: /new south wales/i }).click();
    await page.getByLabel(/consent/i).click();

    await page.getByRole('button', { name: /start assessment/i }).click();

    await expect(page.getByText(/question 1 of/i)).toBeVisible({ timeout: 10000 });

    const progressBar = page.locator('[role="progressbar"]');
    await expect(progressBar).toBeVisible();

    await expect(page.getByText(/complete/i)).toBeVisible();
  });
});

test.describe('Results Display', () => {
  test('should display comprehensive results after assessment', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('button', { name: /start assessment/i }).click();

    await page.getByLabel(/email/i).fill('results-test@example.com');
    await page.getByLabel(/company name/i).fill('Results Test Company');
    
    await page.getByRole('combobox', { name: /employee range/i }).click();
    await page.getByRole('option', { name: /11-50 employees/i }).click();

    await page.getByRole('checkbox', { name: /new south wales/i }).click();
    await page.getByLabel(/consent/i).click();

    await page.getByRole('button', { name: /start assessment/i }).click();

    await expect(page.getByText(/question 1 of/i)).toBeVisible({ timeout: 10000 });

    const questionCount = await page.locator('text=/question \\d+ of (\\d+)/i').textContent();
    const totalQuestions = parseInt(questionCount?.match(/of (\d+)/)?.[1] || '0');

    for (let i = 0; i < totalQuestions; i++) {
      const firstOption = page.locator('input[type="radio"]').first();
      await firstOption.click();

      const nextButton = page.getByRole('button', { name: i === totalQuestions - 1 ? /submit/i : /next/i });
      await nextButton.click();

      if (i < totalQuestions - 1) {
        await page.waitForTimeout(500);
      }
    }

    await expect(page.getByText(/compliance score/i)).toBeVisible({ timeout: 15000 });

    await expect(page.getByText(/category breakdown/i)).toBeVisible();
    await expect(page.getByText(/priority actions/i)).toBeVisible();
  });
});
