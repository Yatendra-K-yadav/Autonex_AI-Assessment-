# HTML string
#  → parse DOM
#  → extract fields
#  → normalize values
#  → check constraints
#  → return result + evidence
from bs4 import BeautifulSoup
import json
import os


def verify_from_html(html_string: str, constraints: dict) -> dict:
    """
    Verifies listing details from an HTML snapshot against constraints.

    Args:
        html_string (str): HTML content
        constraints (dict): {
            max_price: int,
            city: str,
            bedrooms: int
        }

    Returns:
        dict: { success, reason, evidence }
    """

    try:
        soup = BeautifulSoup(html_string, "lxml")

        # --- Selectors (explicit, per instructions) ---
        selectors = {
            "price": "[data-price]",
            "city": "[data-city]",
            "bedrooms": "[data-bedrooms]"
        }

        price_el = soup.select_one(selectors["price"])
        city_el = soup.select_one(selectors["city"])
        bedrooms_el = soup.select_one(selectors["bedrooms"])

        # Missing required fields (graceful failure)
        if not price_el or not city_el or not bedrooms_el:
            return {
                "success": False,
                "reason": "Missing required listing fields",
                "evidence": {
                    "price": None if not price_el else price_el.get("data-price"),
                    "city": None if not city_el else city_el.get("data-city"),
                    "bedrooms": None if not bedrooms_el else bedrooms_el.get("data-bedrooms")
                }
            }

        # --- Extract values ---
        price = int(price_el.get("data-price"))
        city = city_el.get("data-city").strip()
        bedrooms = int(bedrooms_el.get("data-bedrooms"))

        violations = []
        violation_reasons = []

        # --- Constraint checks ---
        if price > constraints["max_price"]:
            violations.append("price")
            violation_reasons.append(
                f"price {price} > {constraints['max_price']}"
            )

        if constraints["city"].lower() not in city.lower():
            violations.append("city")
            violation_reasons.append(
                f"city '{city}' ≠ '{constraints['city']}'"
            )

        if bedrooms != constraints["bedrooms"]:
            violations.append("bedrooms")
            violation_reasons.append(
                f"bedrooms {bedrooms} ≠ {constraints['bedrooms']}"
            )

        # --- FAIL ---
        if violations:
            return {
                "success": False,
                "reason": "Constraint violations: " + ", ".join(violation_reasons),
                "evidence": {
                    "price": price,
                    "city": city,
                    "bedrooms": bedrooms,
                    "violations": violations
                }
            }

        # --- PASS ---
        return {
            "success": True,
            "reason": (
                f"All constraints satisfied: price {price} ≤ {constraints['max_price']}, "
                f"city '{city}' matches, bedrooms {bedrooms} = {constraints['bedrooms']}"
            ),
            "evidence": {
                "price": price,
                "city": city,
                "bedrooms": bedrooms,
                "selectors": selectors
            }
        }

    except Exception as e:
        return {
            "success": False,
            "reason": "Failed to parse HTML",
            "evidence": {"error": str(e)}
        }


# ------------------------------
# Test runner (offline snapshots)
# ------------------------------
if __name__ == "__main__":

    constraints = {
        "max_price": 3000,
        "city": "Pune",
        "bedrooms": 2
    }

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SNAPSHOT_DIR = os.path.join(BASE_DIR, "snapshots")

    files = [
        (os.path.join(SNAPSHOT_DIR, "snapshot_listing.html"), True),
        (os.path.join(SNAPSHOT_DIR, "snapshot_listing_fail.html"), False)
    ]

    all_results = []

    for i, (filename, expected) in enumerate(files, start=1):
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()

        result = verify_from_html(html, constraints)

        output = {
            "test_case": i,
            "file": filename,
            **result
        }

        print(json.dumps(output, indent=2, ensure_ascii=False))
        all_results.append(output)

        assert result["success"] == expected, (
            f"Test case {i} failed: expected {expected}, got {result['success']}"
        )

    with open("task3_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print("\n✅ All Task 3 test cases passed. Results saved to task3_results.json")
