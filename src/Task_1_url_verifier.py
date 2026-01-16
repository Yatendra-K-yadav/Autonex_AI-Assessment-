import json
from urllib.parse import urlparse, parse_qs, unquote

def verify_url(url: str, constraints: dict) -> dict:
    parsed = urlparse(url)

    # Optional but good: basic validation
    if parsed.netloc != "github.com" or parsed.path != "/search":
        return {
            "success": False,
            "reason": "URL is not a GitHub search page",
            "evidence": {
                "netloc": parsed.netloc,
                "path": parsed.path
            }
        }

    query_params = parse_qs(parsed.query)

    # 1. Verify type=issues
    url_type = query_params.get("type", [None])[0]
    if url_type != constraints["type"]:
        return {
            "success": False,
            "reason": f"Expected type={constraints['type']}, got {url_type}",
            "evidence": {"type": url_type}
        }

    # 2. Extract and DECODE the q parameter
    raw_q = query_params.get("q", [""])[0]
    decoded_q = unquote(raw_q).lower()

    tokens = set(decoded_q.split())

    required_tokens = [
        f"repo:{constraints['repo']}",
        "is:issue",
        f"is:{constraints['state']}",
        f"label:{constraints['label']}"
    ]

    missing = [t for t in required_tokens if t not in tokens]

    if missing:
        return {
            "success": False,
            "reason": "Missing required search tokens",
            "evidence": {
                "tokens_found": sorted(tokens),
                "tokens_missing": missing
            }
        }

    return {
        "success": True,
        "reason": (
            "URL query contains repo:microsoft/playwright, "
            "is:issue, is:open, label:bug, type=issues"
        ),
        "evidence": {
            "repo": constraints["repo"],
            "type": constraints["type"],
            "tokensFound": sorted(tokens)
        }
    }



def pretty_print_result(result: dict):
    print("\n=== URL VERIFICATION RESULT ===")
    print(f"Success : {'✅ PASS' if result['success'] else '❌ FAIL'}")
    print(f"Reason  : {result['reason']}")

    evidence = result.get("evidence", {})
    if evidence:
        print("\nEvidence:")
        for key, value in evidence.items():
            print(f"  - {key}: {value}")

if __name__ == "__main__":

    constraints = {
        "repo": "microsoft/playwright",
        "type": "issues",
        "state": "open",
        "label": "bug"
    }

    test_urls = [
        ("https://github.com/search?q=repo%3Amicrosoft%2Fplaywright+is%3Aissue+is%3Aopen+label%3Abug&type=issues", True),
        ("https://github.com/search?q=repo%3Amicrosoft%2Fplaywright+is%3Apr&type=issues", False),
        ("https://github.com/search?q=repo%3Amicrosoft%2Fplaywright+is%3Aissue+label%3Adocumentation&type=issues", False),
        ("https://github.com/search?q=label%3Abug+is%3Aopen+repo%3Amicrosoft%2Fplaywright+is%3Aissue&type=issues", True),
        ("https://github.com/search?q=repo:microsoft/playwright+is:issue+is:open+label:bug&type=issues", True),
    ]

    # for i, (url, expected) in enumerate(test_urls, start=1):
    #     print(f"\n--- Test Case {i} ---")
    #     result = verify_url(url, constraints)
    #     pretty_print_result(result)

    #     # Assertion verifies expected behavior
    #     assert result["success"] == expected, (
    #         f"Test case {i} failed: expected {expected}, got {result['success']}"
    #     )
 
    # print("\n✅ All test cases passed successfully!")

    for i, (url, expected) in enumerate(test_urls, start=1):
        result = verify_url(url, constraints)

        print(json.dumps({
            "test_case": i,
            "url": url,
            **result
        }, indent=2))

        assert result["success"] == expected, (
            f"Test case {i} failed: expected {expected}, got {result['success']}"
        )

    print("\nAll test cases passed.")


