# Autonex Assessment — Verifiers (Tasks 1–3)

This repository contains three independent verifiers implemented in Python, each designed to validate different aspects of URLs, live web pages, and offline HTML snapshots.

All verifiers return **structured JSON output with evidence**, not just pass/fail results.

---

## 📁 Project Structure

```
AUTONEX_ASSESSMENT/
├── myenv/                         # Python virtual environment (not required for submission)
│
├── snapshots/
│   ├── snapshot_listing.html      # HTML snapshot (PASS case)
│   └── snapshot_listing_fail.html # HTML snapshot (FAIL case)
│
├── src/
│   ├── Task_1_url_verifier.py           # Task 1: GitHub URL verifier
│   ├── Task_2_DOM_Verifier.py           # Task 2: Live DOM verifier (Playwright)
│   └── Task_3_DOM_Verifier_Snapshot.py  # Task 3: Offline HTML snapshot verifier
│
├── task1_results.json              # Task 1 test outputs
├── task2_results.json              # Task 2 test outputs
├── task3_results.json              # Task 3 test outputs
│
├── ASSESSMENT_INSTRUCTIONS.md      # Original assessment instructions
├── README.md                       # Project documentation
└── requirements.txt               # Python dependencies

```

---

## 🧪 Task Overview

| Task   | Description                                             |
| ------ | ------------------------------------------------------- |
| Task 1 | Verify GitHub search URLs based on query constraints    |
| Task 2 | Verify live Wikipedia page content using DOM inspection |
| Task 3 | Verify listing attributes from offline HTML snapshots   |

---

## ▶️ How to Run

### Prerequisites

* Python **3.9+**
* pip installed

### Install Dependencies

```bash
pip install requests beautifulsoup4 lxml playwright
python -m playwright install
```

---

### Run Task 1 — URL Verifier

```bash
python src/task1_url_verifier.py
```

This validates GitHub search URLs against required constraints and prints JSON output.

---

### Run Task 2 — Live DOM Verifier (Playwright)

```bash
python src/task2_dom_verifier.py
```

This loads Wikipedia pages in a headless browser and verifies DOM content.

---

### Run Task 3 — HTML Snapshot Verifier

```bash
python src/task3_snapshot_verifier.py
```

This parses local HTML snapshots and validates listing constraints offline.

---

## 📌 Assumptions Made

### General

* Verifiers are **deterministic** and do not modify input data
* Output must always include **evidence**, even on failure
* Failures should be **explicit and explainable**

---

### Task 1

* URL query parameter order does **not** matter
* URL encoding variations (`:` vs `%3A`) are acceptable
* Extra query parameters are ignored if required ones are present

---

### Task 2

* Page title is extracted from DOM heading (`h1#firstHeading`)
* Verification stops early if the page is not about *Taj Mahal*
* Location must be found in the Wikipedia infobox
* Network timeouts and missing elements are handled gracefully

---

### Task 3

* Listing attributes are provided via `data-*` attributes
* All constraints are evaluated together (no fail-fast)
* City matching is **case-insensitive** and allows partial matches
* HTML may be malformed and must not crash the verifier

---

## 🔍 Selectors Used (and Why)

### Task 2 — Wikipedia DOM

| Purpose      | Selector                              | Reason                           |
| ------------ | ------------------------------------- | -------------------------------- |
| Page title   | `h1#firstHeading`                     | Canonical Wikipedia page heading |
| Infobox      | `table.infobox`                       | Structured metadata container    |
| Location row | `.infobox tr:contains('Location') td` | Robust against layout changes    |

---

### Task 3 — HTML Snapshots

Selectors are intentionally **data-attribute based** for stability.

| Field    | Selector          | Reason                         |
| -------- | ----------------- | ------------------------------ |
| Price    | `[data-price]`    | Avoids text parsing            |
| City     | `[data-city]`     | Explicit semantic meaning      |
| Bedrooms | `[data-bedrooms]` | Machine-readable numeric value |

These selectors are also returned in the **evidence** field for transparency.

---

## 📤 Output Format (Evidence Included)

All verifiers return structured JSON in the form:

```json
{
  "success": true,
  "reason": "...",
  "evidence": {
    "...": "..."
  }
}
```

### Example (PASS — Task 3)

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

### Example (FAIL — Task 3)

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

---

## ✅ Test Coverage & Validation

* Each task includes **explicit test cases**
* PASS and FAIL scenarios are asserted
* Execution stops if any test behaves unexpectedly
* Results are saved to JSON files for review

| Task   | PASS Case | FAIL Case |
| ------ | --------- | --------- |
| Task 1 | ✅         | ✅         |
| Task 2 | ✅         | ✅         |
| Task 3 | ✅         | ✅         |

---

## 🏁 Final Notes

* The implementation prioritizes **clarity, robustness, and spec alignment**
* Error handling follows the assessment’s required scenarios
* Code is intentionally modular and easy to extend

---
