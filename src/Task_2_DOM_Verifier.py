import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def verify_taj_mahal_page(url: str) -> dict:
    TITLE_SELECTOR = "h1#firstHeading"
    INFOBOX_SELECTOR = "table.infobox"
    LOCATION_KEYWORD = "location"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # ---- Load page ----
            try:
                page.goto(url, timeout=15000)
            except PlaywrightTimeoutError:
                return {
                    "success": False,
                    "reason": "Network timeout while loading page",
                    "evidence": {"url": url}
                }

            # ---- Extract page title (DOM heading) ----
            title_el = page.query_selector(TITLE_SELECTOR)
            if not title_el:
                return {
                    "success": False,
                    "reason": "Page title heading not found",
                    "evidence": {"selector": TITLE_SELECTOR}
                }

            page_title = title_el.inner_text().strip()

            if "taj mahal" not in page_title.lower():
                return {
                    "success": False,
                    "reason": "Page title does not contain 'Taj Mahal'",
                    "evidence": {"pageTitle": page_title}
                }

            # ---- Extract infobox ----
            infobox = page.query_selector(INFOBOX_SELECTOR)
            if not infobox:
                return {
                    "success": False,
                    "reason": "Infobox not found",
                    "evidence": {"selector": INFOBOX_SELECTOR}
                }

            rows = infobox.query_selector_all("tr")
            extracted_location = None

            for row in rows:
                header = row.query_selector("th")
                value = row.query_selector("td")

                if not header or not value:
                    continue

                if LOCATION_KEYWORD in header.inner_text().lower():
                    extracted_location = value.inner_text()
                    break

            if not extracted_location:
                return {
                    "success": False,
                    "reason": "Location field not found in infobox",
                    "evidence": {"checkedRows": len(rows)}
                }

            # ---- Clean extracted text ----
            clean_location = extracted_location.replace("\n", " ").strip()

            if "agra" not in clean_location.lower():
                return {
                    "success": False,
                    "reason": "Location does not contain 'Agra'",
                    "evidence": {"extractedLocation": clean_location}
                }

            browser.close()

            # ---- PASS ----
            return {
                "success": True,
                "reason": "Page title contains 'Taj Mahal' and infobox location contains 'Agra'",
                "evidence": {
                    "pageTitle": page_title,
                    "extractedLocation": clean_location,
                    "selectors": {
                        "title": TITLE_SELECTOR,
                        "infobox": INFOBOX_SELECTOR,
                        "location": "infobox tr > th:contains('Location') + td"
                    }
                }
            }

    except Exception as e:
        return {
            "success": False,
            "reason": "Unexpected system error",
            "evidence": {"error": str(e)}
        }


# ------------------------------
# Test runner (matches assignment)
# ------------------------------
if __name__ == "__main__":

    test_urls = [
        ("https://en.wikipedia.org/wiki/Taj_Mahal", True),
        ("https://en.wikipedia.org/wiki/Eiffel_Tower", False),
        ("https://en.wikipedia.org/wiki/Agra", False),
    ]

    all_results = []

    for i, (url, expected) in enumerate(test_urls, start=1):
        result = verify_taj_mahal_page(url)

        output = {
            "test_case": i,
            "url": url,
            **result
        }

        print(json.dumps(output, indent=2))
        all_results.append(output)

        assert result["success"] == expected, (
            f"Test case {i} failed: expected {expected}, got {result['success']}"
        )

    with open("task2_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print("\n✅ All Task 2 test cases passed. Results saved to task2_results.json")
