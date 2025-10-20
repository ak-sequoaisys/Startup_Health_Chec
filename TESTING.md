# Testing Documentation

## Overview
This document provides comprehensive information about the testing infrastructure for the Startup Compliance Health Check Tool.

## Test Coverage

### Backend Tests (Python/pytest)
- **Unit Tests**: API endpoint testing
- **Integration Tests**: Full assessment workflow testing
- **Coverage Target**: >80%

### Frontend Tests (TypeScript/Vitest/Playwright)
- **Unit Tests**: Component testing with React Testing Library
- **Integration Tests**: E2E user flow testing with Playwright
- **Accessibility Tests**: WCAG 2.1 AA compliance testing
- **Performance Tests**: FCP, load time, and API response time testing

---

## Running Tests

### Backend Tests

#### Prerequisites
```bash
cd backend
poetry install
```

#### Run All Tests
```bash
poetry run pytest
```

#### Run with Coverage
```bash
poetry run pytest --cov=app --cov-report=html
```

#### Run Specific Test File
```bash
poetry run pytest tests/test_api_endpoints.py
```

#### Run Specific Test
```bash
poetry run pytest tests/test_api_endpoints.py::TestHealthCheck::test_healthz_endpoint
```

#### View Coverage Report
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

### Frontend Tests

#### Prerequisites
```bash
cd frontend
npm install
npm run playwright:install
```

#### Run Unit Tests
```bash
npm test
```

#### Run Unit Tests with UI
```bash
npm run test:ui
```

#### Run Unit Tests with Coverage
```bash
npm run test:coverage
```

#### Run E2E Tests
```bash
npm run test:e2e
```

#### Run E2E Tests with UI
```bash
npm run test:e2e:ui
```

#### Run E2E Tests in Headed Mode
```bash
npm run test:e2e:headed
```

#### Run Accessibility Tests Only
```bash
npm run test:a11y
```

#### Run Performance Tests Only
```bash
npm run test:perf
```

---

## Test Structure

### Backend Test Structure
```
backend/
├── tests/
│   ├── __init__.py
│   ├── test_api_endpoints.py      # API endpoint unit tests
│   └── test_integration.py        # Integration tests
└── pytest.ini                      # Pytest configuration
```

### Frontend Test Structure
```
frontend/
├── src/
│   ├── __tests__/
│   │   └── App.test.tsx           # Component unit tests
│   └── test/
│       └── setup.ts               # Test setup and configuration
├── e2e/
│   ├── assessment-flow.spec.ts    # E2E user flow tests
│   ├── accessibility.spec.ts      # Accessibility tests
│   └── performance.spec.ts        # Performance tests
└── playwright.config.ts           # Playwright configuration
```

---

## Test Categories

### 1. Unit Tests

#### Backend Unit Tests
- **Location**: `backend/tests/test_api_endpoints.py`
- **Purpose**: Test individual API endpoints
- **Coverage**:
  - Health check endpoint
  - Questions retrieval
  - Assessment start
  - Answer submission
  - Assessment computation
  - Lead management
  - Audit logs

#### Frontend Unit Tests
- **Location**: `frontend/src/__tests__/App.test.tsx`
- **Purpose**: Test React components in isolation
- **Coverage**:
  - Intro screen rendering
  - Contact form validation
  - Question navigation
  - Answer selection
  - Error handling

### 2. Integration Tests

#### Backend Integration Tests
- **Location**: `backend/tests/test_integration.py`
- **Purpose**: Test complete workflows
- **Coverage**:
  - Full assessment flow from start to finish
  - Multiple assessment isolation
  - Risk level calculation
  - Answer update workflow
  - Category scoring accuracy
  - Priority actions generation

#### Frontend E2E Tests
- **Location**: `frontend/e2e/assessment-flow.spec.ts`
- **Purpose**: Test complete user journeys
- **Coverage**:
  - Complete assessment workflow
  - Question navigation (forward/backward)
  - Form validation
  - Progress indicator
  - Results display

### 3. Accessibility Tests

- **Location**: `frontend/e2e/accessibility.spec.ts`
- **Purpose**: Ensure WCAG 2.1 AA compliance
- **Coverage**:
  - No accessibility violations on any page
  - Proper form labels
  - Keyboard navigation
  - Screen reader compatibility
  - Color contrast
  - Heading hierarchy
  - Image alt text
  - Link descriptions

### 4. Performance Tests

- **Location**: `frontend/e2e/performance.spec.ts`
- **Purpose**: Validate performance requirements
- **Coverage**:
  - First Contentful Paint (FCP) < 2 seconds
  - Page load time < 5 seconds
  - Assessment submission < 5 seconds
  - Question navigation responsiveness
  - Results page render time
  - Memory leak detection
  - Asset loading efficiency
  - API response times

---

## Continuous Integration

### GitHub Actions Workflow (Recommended)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install
      - name: Run tests
        run: |
          cd backend
          poetry run pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run unit tests
        run: |
          cd frontend
          npm test
      - name: Install Playwright
        run: |
          cd frontend
          npm run playwright:install
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e
```

---

## Test Data

### Mock Data
- **Backend**: Uses in-memory database with fixture data
- **Frontend**: Uses mocked API responses via Vitest mocks

### Test Users
- **Email**: test@example.com, e2e-test@example.com, etc.
- **Company Names**: Test Company, E2E Test Company, etc.

---

## Debugging Tests

### Backend Debugging

#### Run with Verbose Output
```bash
poetry run pytest -v
```

#### Run with Print Statements
```bash
poetry run pytest -s
```

#### Run with Debugger
```bash
poetry run pytest --pdb
```

### Frontend Debugging

#### Debug Unit Tests
```bash
npm run test:ui
```

#### Debug E2E Tests
```bash
npm run test:e2e:headed
```

#### View Playwright Trace
```bash
npx playwright show-trace trace.zip
```

---

## Writing New Tests

### Backend Test Template

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestNewFeature:
    def test_new_endpoint(self):
        """Test description"""
        response = client.get("/api/v1/new-endpoint")
        assert response.status_code == 200
        assert "expected_key" in response.json()
```

### Frontend Unit Test Template

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import MyComponent from '../MyComponent';

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('should handle user interaction', () => {
    render(<MyComponent />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(screen.getByText('Updated Text')).toBeInTheDocument();
  });
});
```

### Frontend E2E Test Template

```typescript
import { test, expect } from '@playwright/test';

test.describe('New Feature', () => {
  test('should complete new workflow', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /action/i }).click();
    await expect(page.getByText('Expected Result')).toBeVisible();
  });
});
```

---

## Test Maintenance

### Regular Tasks
1. **Update test data** when API changes
2. **Add tests** for new features
3. **Update snapshots** when UI changes
4. **Review coverage** reports monthly
5. **Fix flaky tests** immediately

### Best Practices
- Write descriptive test names
- Keep tests independent and isolated
- Use fixtures for common setup
- Mock external dependencies
- Test edge cases and error conditions
- Maintain test documentation

---

## Troubleshooting

### Common Issues

#### Backend Tests Fail with Import Errors
```bash
# Solution: Reinstall dependencies
cd backend
poetry install
```

#### Frontend Tests Fail with Module Not Found
```bash
# Solution: Clear cache and reinstall
cd frontend
rm -rf node_modules
npm install
```

#### Playwright Tests Timeout
```bash
# Solution: Increase timeout in playwright.config.ts
timeout: 30000  # 30 seconds
```

#### Accessibility Tests Fail
```bash
# Solution: Run with headed mode to see violations
npm run test:e2e:headed
```

#### Performance Tests Fail
```bash
# Solution: Ensure backend is running and responsive
# Check network conditions
# Run tests individually to isolate issues
```

---

## Coverage Goals

### Backend
- **Line Coverage**: >80%
- **Branch Coverage**: >75%
- **Function Coverage**: >85%

### Frontend
- **Line Coverage**: >70%
- **Branch Coverage**: >65%
- **Component Coverage**: 100% of critical components

---

## Resources

### Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library Documentation](https://testing-library.com/)
- [Axe Accessibility Testing](https://www.deque.com/axe/)

### Tools
- **Coverage Reports**: `htmlcov/index.html` (backend), `coverage/index.html` (frontend)
- **Playwright UI**: `npm run test:e2e:ui`
- **Vitest UI**: `npm run test:ui`

---

## Contact

For questions about testing:
- Review this documentation
- Check test files for examples
- Consult team members
- Create an issue in the repository
