import { test, expect } from '@playwright/test';

test.describe('Performance Tests', () => {
  test('First Contentful Paint should be under 2 seconds', async ({ page }) => {
    await page.goto('/');
    
    const performanceMetrics = await page.evaluate(() => {
      const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paintEntries = performance.getEntriesByType('paint');
      const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint');
      
      return {
        fcp: fcp?.startTime || 0,
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
        loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
      };
    });

    console.log('Performance Metrics:', performanceMetrics);
    
    expect(performanceMetrics.fcp).toBeLessThan(2000);
  });

  test('Page load time should be reasonable', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    console.log('Page Load Time:', loadTime, 'ms');
    
    expect(loadTime).toBeLessThan(5000);
  });

  test('Assessment submission should complete within 5 seconds', async ({ page }) => {
    await page.goto('/');
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    await page.getByLabel(/email/i).fill('perf-test@example.com');
    await page.getByLabel(/company name/i).fill('Performance Test Company');
    
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
        await page.waitForTimeout(100);
      }
    }
    
    const startSubmit = Date.now();
    await expect(page.getByText(/compliance score/i)).toBeVisible({ timeout: 15000 });
    const submitTime = Date.now() - startSubmit;
    
    console.log('Assessment Submission Time:', submitTime, 'ms');
    
    expect(submitTime).toBeLessThan(5000);
  });

  test('Question navigation should be responsive', async ({ page }) => {
    await page.goto('/');
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    await page.getByLabel(/email/i).fill('nav-perf-test@example.com');
    await page.getByLabel(/company name/i).fill('Nav Performance Test Company');
    
    await page.getByRole('combobox', { name: /employee range/i }).click();
    await page.getByRole('option', { name: /11-50 employees/i }).click();
    
    await page.getByRole('checkbox', { name: /new south wales/i }).click();
    await page.getByLabel(/consent/i).click();
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    await expect(page.getByText(/question 1 of/i)).toBeVisible({ timeout: 10000 });
    
    const firstOption = page.locator('input[type="radio"]').first();
    await firstOption.click();
    
    const startNav = Date.now();
    await page.getByRole('button', { name: /next/i }).click();
    await expect(page.getByText(/question 2 of/i)).toBeVisible();
    const navTime = Date.now() - startNav;
    
    console.log('Question Navigation Time:', navTime, 'ms');
    
    expect(navTime).toBeLessThan(500);
  });

  test('Results page should render within 5 seconds', async ({ page }) => {
    await page.goto('/');
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    await page.getByLabel(/email/i).fill('results-perf-test@example.com');
    await page.getByLabel(/company name/i).fill('Results Performance Test Company');
    
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
        await page.waitForTimeout(100);
      }
    }
    
    const startRender = Date.now();
    await expect(page.getByText(/compliance score/i)).toBeVisible({ timeout: 15000 });
    await expect(page.getByText(/category breakdown/i)).toBeVisible();
    await expect(page.getByText(/priority actions/i)).toBeVisible();
    const renderTime = Date.now() - startRender;
    
    console.log('Results Page Render Time:', renderTime, 'ms');
    
    expect(renderTime).toBeLessThan(5000);
  });

  test('Application should not have memory leaks during navigation', async ({ page }) => {
    await page.goto('/');
    
    const initialMetrics = await page.evaluate(() => {
      if (performance.memory) {
        return {
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          totalJSHeapSize: performance.memory.totalJSHeapSize,
        };
      }
      return null;
    });
    
    for (let i = 0; i < 5; i++) {
      await page.getByRole('button', { name: /start assessment/i }).click();
      await page.getByRole('button', { name: /back/i }).click();
    }
    
    const finalMetrics = await page.evaluate(() => {
      if (performance.memory) {
        return {
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          totalJSHeapSize: performance.memory.totalJSHeapSize,
        };
      }
      return null;
    });
    
    if (initialMetrics && finalMetrics) {
      const memoryIncrease = finalMetrics.usedJSHeapSize - initialMetrics.usedJSHeapSize;
      const percentIncrease = (memoryIncrease / initialMetrics.usedJSHeapSize) * 100;
      
      console.log('Memory Increase:', memoryIncrease, 'bytes', `(${percentIncrease.toFixed(2)}%)`);
      
      expect(percentIncrease).toBeLessThan(50);
    }
  });

  test('Images and assets should load efficiently', async ({ page }) => {
    await page.goto('/');
    
    const resourceTimings = await page.evaluate(() => {
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
      return resources.map(resource => ({
        name: resource.name,
        duration: resource.duration,
        size: resource.transferSize,
        type: resource.initiatorType,
      }));
    });
    
    const images = resourceTimings.filter(r => r.type === 'img' || r.name.match(/\.(jpg|jpeg|png|gif|svg|webp)$/i));
    
    images.forEach(image => {
      console.log(`Image: ${image.name}, Duration: ${image.duration}ms, Size: ${image.size} bytes`);
      expect(image.duration).toBeLessThan(2000);
    });
  });

  test('API calls should complete within reasonable time', async ({ page }) => {
    await page.goto('/');
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    await page.getByLabel(/email/i).fill('api-perf-test@example.com');
    await page.getByLabel(/company name/i).fill('API Performance Test Company');
    
    await page.getByRole('combobox', { name: /employee range/i }).click();
    await page.getByRole('option', { name: /11-50 employees/i }).click();
    
    await page.getByRole('checkbox', { name: /new south wales/i }).click();
    await page.getByLabel(/consent/i).click();
    
    const apiStartTime = Date.now();
    
    const responsePromise = page.waitForResponse(response => 
      response.url().includes('/api/v1/assessments/start') && response.status() === 200
    );
    
    await page.getByRole('button', { name: /start assessment/i }).click();
    
    const response = await responsePromise;
    const apiTime = Date.now() - apiStartTime;
    
    console.log('API Response Time:', apiTime, 'ms');
    
    expect(apiTime).toBeLessThan(3000);
    expect(response.status()).toBe(200);
  });
});
