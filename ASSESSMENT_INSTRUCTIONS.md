# Take-Home Test: Web Verifier Skills

**Time:** 3–5 hours  
**Deliverable:** A small repo (JS/TS preferred; Python ok) with verifiers + README  
**Rule:** Do not scrape at scale; just implement verification logic.

---

## What is a "verifier" here?

A verifier is code that returns **pass/fail + extracted evidence** given:
- The final page URL
- Optionally the final page HTML (snapshot)
- The task constraints

---

# Task 1 — URL Verifier (Specific + Simple)

### Goal
Implement a function that verifies whether a user ended on the correct search results page using the **URL only**.

### URL Format (real, public)
GitHub issue search pages, example:
```
https://github.com/search?q=repo%3Amicrosoft%2Fplaywright+is%3Aissue+is%3Aopen+label%3Abug&type=issues
```

### Inputs

**Task constraints:**
- repo = `microsoft/playwright`
- type = `issues`
- state = `open`
- label = `bug`

**Final URL candidates (you must verify):**

| # | URL | Expected |
|---|-----|----------|
| 1 | `https://github.com/search?q=repo%3Amicrosoft%2Fplaywright+is%3Aissue+is%3Aopen+label%3Abug&type=issues` | ✅ PASS |
| 2 | `https://github.com/search?q=repo%3Amicrosoft%2Fplaywright+is%3Apr&type=issues` | ❌ FAIL |
| 3 | `https://github.com/search?q=repo%3Amicrosoft%2Fplaywright+is%3Aissue+label%3Adocumentation&type=issues` | ❌ FAIL |
| 4 | `https://github.com/search?q=label%3Abug+is%3Aopen+repo%3Amicrosoft%2Fplaywright+is%3Aissue&type=issues` | ✅ PASS (order shouldn't matter) |
| 5 | `https://github.com/search?q=repo:microsoft/playwright+is:issue+is:open+label:bug&type=issues` | ✅ PASS (unencoded colons) |

### Clarifications
- **Order of query parameters should NOT matter**
- **URL encoding variations must be handled** (`%3A` = `:` = `%3a`)
- **Extra parameters are acceptable** if all required ones are present
- Return `success: false` if required constraints are missing

### Output Example
```json
{
  "success": true,
  "reason": "URL query contains repo:microsoft/playwright, is:issue, is:open, label:bug, type=issues",
  "evidence": {
    "repo": "microsoft/playwright",
    "type": "issues",
    "tokensFound": ["repo:microsoft/playwright", "is:issue", "is:open", "label:bug"]
  }
}
```

**What this tests:** URL decoding, query parsing, robust matching, edge cases.

---

# Task 2 — DOM Verifier on a Real Page (Specific + Core Skill)

### Goal
Verify the page state by extracting facts from the DOM.

**Use this public URL (stable page):**
```
https://en.wikipedia.org/wiki/Taj_Mahal
```

### What to verify (task constraints)
- Page title must **contain** "Taj Mahal"
- The infobox must **contain** Location = "Agra" (case-insensitive, partial match OK)

### URLs to Test

| # | URL | Expected |
|---|-----|----------|
| 1 | `https://en.wikipedia.org/wiki/Taj_Mahal` | ✅ PASS |
| 2 | `https://en.wikipedia.org/wiki/Eiffel_Tower` | ❌ FAIL (wrong page) |
| 3 | `https://en.wikipedia.org/wiki/Agra` | ❌ FAIL (not Taj Mahal page) |

### Requirements
Write a verifier that:
- Loads the URL in a browser context (Playwright/Puppeteer preferred, or manual HTML fetch is ok)
- Extracts:
  - Page heading/title
  - Location field from the infobox
- Returns pass/fail with evidence
- Handles gracefully if elements are missing

### Output Example
```json
{
  "success": true,
  "reason": "Page title contains 'Taj Mahal' and infobox location contains 'Agra'",
  "evidence": {
    "pageTitle": "Taj Mahal - Wikipedia",
    "extractedLocation": "Agra, Uttar Pradesh, India",
    "selectors": {
      "title": "h1#firstHeading",
      "location": ".infobox tr:contains('Location') td"
    }
  }
}
```

**What this tests:** Selectors, DOM traversal, handling layout variance, defensive coding.

---

# Task 3 — DOM Verifier from Snapshot (No Network)

### Goal
Same as Task 2, but using a **provided HTML file** to avoid site drift.

### Files Provided
- `snapshot_listing.html` — Should PASS
- `snapshot_listing_fail.html` — Should FAIL

### What to verify (task constraints)
- Price is **≤ 3000**
- City equals **"Pune"** (case-insensitive)
- Bedrooms = **2**

### Test Cases

| File | Expected | Reason |
|------|----------|--------|
| `snapshot_listing.html` | ✅ PASS | Price=2800, City=Pune, Bedrooms=2 |
| `snapshot_listing_fail.html` | ❌ FAIL | Price=4500, City=Mumbai, Bedrooms=3 |

### Requirements
Implement:
```javascript
verifyFromHtml(htmlString, constraints) → { success, reason, evidence }
```

- **No network calls** — parse DOM and extract fields reliably
- Handle missing elements gracefully
- Return clear reasons for failure

### Output Example (PASS)
```json
{
  "success": true,
  "reason": "All constraints satisfied: price 2800 ≤ 3000, city 'Pune' matches, bedrooms 2 = 2",
  "evidence": {
    "price": 2800,
    "city": "Pune",
    "bedrooms": 2,
    "selectors": {
      "price": "[data-price]",
      "city": "[data-city]",
      "bedrooms": "[data-bedrooms]"
    }
  }
}
```

### Output Example (FAIL)
```json
{
  "success": false,
  "reason": "Constraint violations: price 4500 > 3000, city 'Mumbai' ≠ 'Pune', bedrooms 3 ≠ 2",
  "evidence": {
    "price": 4500,
    "city": "Mumbai",
    "bedrooms": 3,
    "violations": ["price", "city", "bedrooms"]
  }
}
```

**What this tests:** Pure DOM parsing + robust extraction without relying on live site.

---

## Error Handling Requirements

Your verifiers should handle these cases gracefully:

| Scenario | Expected Behavior |
|----------|-------------------|
| Page doesn't load | Return `success: false` with reason "Failed to load page" |
| Element not found | Return `success: false` with reason specifying missing element |
| Network timeout | Return `success: false` with reason "Network timeout" |
| Malformed HTML | Return `success: false` with reason "Failed to parse HTML" |

---

## Submission Checklist

- [ ] `verifiers/` folder with 3 verifiers (one per task)
- [ ] `README.md` with:
  - How to run
  - Assumptions made
  - Selectors used + why
- [ ] Output must include **evidence** (not just true/false)
- [ ] All test cases pass/fail as expected

---

## Scoring Rubric

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Correctness** | 40% | Passes/fails correctly across all given URLs/pages |
| **Robustness** | 25% | Handles missing elements, format variations, encoding |
| **Evidence Quality** | 20% | Good extracted fields + readable reasons |
| **Code Quality** | 15% | Structure, naming, error handling, tests (optional) |

---

## Bonus Points (Optional)

- Unit tests for edge cases
- TypeScript with proper types
- Handles network timeouts gracefully
- Configurable selectors via JSON config

---

## Technical Notes

### Recommended Libraries
- **JavaScript/TypeScript:** Playwright, Puppeteer, Cheerio, JSDOM
- **Python:** BeautifulSoup4, lxml, Playwright-Python, Selenium

### Time Estimate
- Task 1: 30-60 minutes
- Task 2: 60-90 minutes
- Task 3: 45-75 minutes
- Documentation: 30 minutes

Good luck! 🚀
