# Testing Guide

## Testing Strategy

Bowling HQ uses comprehensive testing across all layers:

## Unit Tests

### Backend (Python)

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_sessions.py

# Run specific test
pytest tests/test_sessions.py::test_create_session

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto
```

### Frontend (JavaScript)

```bash
# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- Sessions.test.js
```

## Integration Tests

```bash
# Run API integration tests
pytest tests/integration/

# Run with specific marker
pytest -m integration

# Run with database
pytest -m integration --db
```

## End-to-End Tests

```bash
# Run E2E tests (requires app running)
npm run test:e2e

# Run specific E2E scenario
npm run test:e2e -- --spec=tests/e2e/session.spec.js

# Run headless
npm run test:e2e -- --headless
```

## Test Structure

### Backend Test Example

```python
# tests/test_sessions.py
import pytest
from app.models import Session

@pytest.fixture
def client():
    # Setup test client
    pass

class TestSessions:
    def test_create_session(self, client):
        # Arrange
        data = {"date": "2026-07-08", "score": 185}
        
        # Act
        response = client.post("/api/sessions", json=data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["score"] == 185
```

### Frontend Test Example

```javascript
// tests/Sessions.test.js
import { render, screen } from '@testing-library/react';
import Sessions from '../components/Sessions';

describe('Sessions Component', () => {
  it('renders session list', () => {
    render(<Sessions />);
    expect(screen.getByText(/sessions/i)).toBeInTheDocument();
  });
});
```

## Code Coverage

### Targets

- **Backend**: 80% minimum
- **Frontend**: 75% minimum
- **Critical paths**: 95% minimum

### Generate Coverage Report

```bash
# Python
pytest --cov=app --cov-report=html
# Open htmlcov/index.html

# JavaScript
npm test -- --coverage --watchAll=false
```

## Continuous Integration

### GitHub Actions Workflow

See `.github/workflows/tests.yml` for:
- Running tests on push
- Running tests on pull requests
- Coverage reporting
- Linting and formatting checks

## Performance Testing

```bash
# Load testing with k6
k6 run tests/load/sessions.js

# Stress testing
k6 run tests/load/stress.js

# Soak testing
k6 run tests/load/soak.js
```

## Security Testing

```bash
# Dependency vulnerabilities
npm audit
pip audit

# Static security scanning
bandit -r app/

# SQL injection testing
pytest -m sql_injection
```

## Test Data

### Seeds

```bash
# Create test database
pytest --fixtures db-seed

# Reset test data
python scripts/seed_test_data.py
```

### Factories

```python
# Use factory_boy for test data
from tests.factories import SessionFactory

session = SessionFactory(score=185)
```

## Debugging Tests

```bash
# Run single test with debugging
pytest -s -v tests/test_sessions.py::test_create_session

# Drop into debugger on failure
pytest --pdb

# Verbose output
pytest -vv
```

## Test Markers

```python
# Mark tests
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.unit

# Run only marked tests
pytest -m unit
pytest -m "not slow"
```

## Best Practices

1. **Arrange-Act-Assert**: Structure all tests clearly
2. **DRY**: Use fixtures and factories to avoid duplication
3. **Isolation**: Tests should not depend on each other
4. **Clarity**: Test names should describe what's being tested
5. **Speed**: Unit tests should be fast; group slow tests
6. **Coverage**: Aim for high coverage but focus on critical paths
7. **Maintenance**: Keep tests updated with code changes

## Test Categories

### Unit Tests
- Fast (milliseconds)
- Test individual functions
- Mock external dependencies
- ~70% of test suite

### Integration Tests
- Medium speed (seconds)
- Test component interaction
- Use real database in test environment
- ~20% of test suite

### End-to-End Tests
- Slow (minutes)
- Test full user workflows
- Run against staging environment
- ~10% of test suite

## Continuous Testing

```bash
# Watch mode - rerun tests on file changes
pytest-watch

# JavaScript watch
npm test -- --watch
```

---

**This is a comprehensive testing guide for future implementation.**
