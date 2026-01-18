# Testing Suite - The Gauntlet

## Overview

The Gauntlet is an automated test suite that validates the Multifamily Deep Research Engine's ability to correctly evaluate investment opportunities and enforce the "Secret Sauce" criteria.

## Test Philosophy

The engine's purpose is to **prevent "deal fever"** by enforcing institutional discipline. The Gauntlet ensures the AI doesn't approve bad deals just because an investor is excited about them.

## Test Cases

### 1. The Ghost Town Test
**Purpose**: Verify population threshold enforcement

**Input**: Property in a town with <10,000 population (e.g., Marfa, TX)

**Expected Output**:
- MSA Criterion `msa_1` (Population Size) = RED
- Overall recommendation: NO-GO
- Reasoning clearly states population falls below 400k threshold

**Pass Criteria**: Engine correctly rejects the deal

---

### 2. The War Zone Test
**Purpose**: Verify crime rate threshold enforcement

**Input**: Property in high-crime neighborhood

**Expected Output**:
- Sub-Market Criterion `sub_1` (Crime Rate) = RED
- Reasoning states crime rates exceed MSA average
- Source cites FBI UCR or similar

**Pass Criteria**: Engine flags crime risk appropriately

---

### 3. The Context Override Test
**Purpose**: Verify user-uploaded documents override market data

**Input**:
- Property in high-tax market (e.g., Houston: 2.9% county rate)
- User uploads Tax Abatement Agreement showing 0% rate for 10 years

**Expected Output**:
- Sub-Market Criterion `sub_12` (Taxes/Fees) = GREEN
- `override_applied` = `true`
- `override_document` = "Chapter_353_Tax_Abatement_2023.pdf"
- Source cites user document, not county rate

**Pass Criteria**: Engine uses abatement data instead of county rate

---

### 4. The Completeness Check
**Purpose**: Verify heat map contains all 30 criteria

**Expected Output**:
- Array length = 30
- IDs: `msa_1` through `msa_16` (16 items)
- IDs: `sub_1` through `sub_14` (14 items)
- No duplicate IDs
- All required fields present

**Pass Criteria**: JSON structure matches schema exactly

---

### 5. The Goldilocks Test - Amenities
**Purpose**: Verify distance-based logic for amenities

**Test Cases**:
- **Too Close** (<0.25 miles): RED (noise, traffic)
- **Goldilocks** (1-2 miles): GREEN (walkable, quiet)
- **Too Far** (>2 miles): YELLOW/RED (car-dependent)

**Pass Criteria**: Engine applies Goldilocks principle correctly

---

### 6. The Goldilocks Test - Vacancy Rate
**Purpose**: Verify vacancy rate sweet spot logic

**Test Cases**:
- **Too Low** (<3%): YELLOW (overheated market)
- **Goldilocks** (4-6%): GREEN (healthy equilibrium)
- **Too High** (>7%): RED (oversupply)

**Pass Criteria**: Engine recognizes both extremes are bad

---

### 7. The Recommendation Logic Test
**Purpose**: Verify final recommendation thresholds

**Test Cases**:
- **>5 RED flags**: NO-GO recommendation
- **3-5 RED flags**: CAUTION recommendation
- **≤2 RED flags**: PROCEED recommendation

**Pass Criteria**: Correct recommendation for each scenario

---

## Running the Tests

### Prerequisites
```bash
pip install pytest
```

### Run All Tests
```bash
pytest tests/test_gauntlet.py -v
```

### Run Individual Test
```bash
pytest tests/test_gauntlet.py::TestGauntlet::test_ghost_town_rejection -v
```

### Run with Coverage
```bash
pytest tests/test_gauntlet.py --cov=app --cov-report=html
```

## Test Data

Sample test data is provided in `tests/test_data/`:
- `sample_tax_abatement.txt`: Chapter 353 tax abatement agreement
- Additional test documents can be added as needed

## Integration Testing

For full end-to-end testing with the n8n workflow:

1. Set the n8n webhook URL:
```bash
export N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/analyze-property
```

2. Run integration tests:
```bash
pytest tests/test_gauntlet.py --integration
```

## CI/CD Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: Run Gauntlet Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r tests/requirements.txt
      - name: Run Gauntlet
        run: pytest tests/test_gauntlet.py -v
```

## Expected Results

All tests should pass:
```
tests/test_gauntlet.py::TestGauntlet::test_ghost_town_rejection PASSED
tests/test_gauntlet.py::TestGauntlet::test_war_zone_crime_flag PASSED
tests/test_gauntlet.py::TestGauntlet::test_context_override_tax_abatement PASSED
tests/test_gauntlet.py::TestGauntlet::test_completeness_check PASSED
tests/test_gauntlet.py::TestGauntlet::test_goldilocks_logic_amenities PASSED
tests/test_gauntlet.py::TestGauntlet::test_vacancy_rate_goldilocks PASSED
tests/test_gauntlet.py::TestGauntlet::test_recommendation_logic PASSED

======================== 7 passed in 0.05s =========================
```

## Debugging Failed Tests

If a test fails:

1. **Check Heat Map JSON**: Ensure all 30 items are present
2. **Verify Status Values**: Only GREEN/YELLOW/RED are valid
3. **Check Override Logic**: User docs should take precedence
4. **Review Reasoning**: Must be >20 characters and specific
5. **Validate Sources**: Must include citation details

## Adding New Tests

To add a new test case:

1. Create a new method in `TestGauntlet` class
2. Name it `test_<descriptive_name>`
3. Use `self._create_mock_heat_map()` to generate base data
4. Modify relevant criteria based on test scenario
5. Assert expected outcomes
6. Add documentation to this README

## Maintenance

Tests should be updated when:
- Criteria thresholds change
- New criteria are added (beyond 30)
- Override logic is enhanced
- Recommendation thresholds are adjusted

## Contact

For issues with the test suite, contact the development team.
