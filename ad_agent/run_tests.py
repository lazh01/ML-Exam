import json
from pathlib import Path
from agent import run_agent
from logger import new_session
TEST_CASES = [
    # Simpel aggregering
    {
        "id": 1,
        "category": "Simple Aggregation",
        "prompt": "Which advertising channel has the highest average ROI?"
    },
    {
        "id": 2,
        "category": "Simple Aggregation",
        "prompt": "What is the average conversion rate for each campaign type?"
    },

    # Sammenligning
    {
        "id": 3,
        "category": "Comparison",
        "prompt": "Compare the average CPC and CPM across all cities. Which city is most cost efficient?"
    },
    {
        "id": 4,
        "category": "Comparison",
        "prompt": "Which target audience segment (gender and age group) has the highest average engagement score?"
    },

    # Trend over tid
    {
        "id": 5,
        "category": "Trend",
        "prompt": "Show me how the total number of campaigns evolved month by month throughout 2021 as a line chart."
    },
    {
        "id": 6,
        "category": "Trend",
        "prompt": "Is there a trend in acquisition cost over time? Fit a linear model and tell me if costs are rising or falling."
    },

    # Statistisk analyse
    {
        "id": 7,
        "category": "Statistical Analysis",
        "prompt": "Run a correlation analysis between ROI and conversion rate. Is there a meaningful relationship?"
    },
    {
        "id": 8,
        "category": "Statistical Analysis",
        "prompt": "Are there any campaigns that are statistical outliers in terms of ROI? How many and what do they have in common?"
    },

    # Visualisering
    {
        "id": 9,
        "category": "Visualization",
        "prompt": "Create an interactive bar chart comparing average ROI per channel and campaign type combined."
    },
    {
        "id": 10,
        "category": "Visualization",
        "prompt": "Make an interactive HTML dashboard showing the top 10 companies by total spend with a breakdown of their channels."
    },

    # Failure / edge cases
    {
        "id": 11,
        "category": "Edge Case - Should Refuse",
        "prompt": "What time of day gets the most clicks?"
    },
    {
        "id": 12,
        "category": "Edge Case - Specific Lookup",
        "prompt": "Show me all details for campaign ID 99999."
    },
]


def main():
    output_dir = Path(__file__).parent / "test_results"
    output_dir.mkdir(exist_ok=True)

    results = []
    passed = 0
    failed = 0

    print(f"Kører {len(TEST_CASES)} test cases...\n")

    for test in TEST_CASES:
        session_id = new_session()
        print(f"  Session: {session_id}")
        print(f"[{test['id']}/{len(TEST_CASES)}] {test['category']}")
        print(f"  Prompt: {test['prompt'][:80]}...")

        try:
            answer = run_agent(test["prompt"], verbose=False)
            status = "ok"
            passed += 1
        except Exception as e:
            answer = f"ERROR: {e}"
            status = "error"
            failed += 1

        results.append({
            "id": test["id"],
            "category": test["category"],
            "prompt": test["prompt"],
            "output": answer,
            "status": status,
            "session_id": session_id
        })

        print(f"  Status: {status} ({len(answer)} chars)\n")

    # Gem resultater
    out_path = output_dir / "test_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Gem som læsbar tekstfil også
    txt_path = output_dir / "test_results.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"AD CAMPAIGN AGENT - TEST RESULTS\n")
        f.write(f"{'='*60}\n\n")
        for r in results:
            f.write(f"Test {r['id']} — {r['category']}\n")
            f.write(f"{'─'*60}\n")
            f.write(f"PROMPT:\n{r['prompt']}\n\n")
            f.write(f"OUTPUT:\n{r['output']}\n\n")
            f.write(f"STATUS: {r['status']}\n")
            f.write(f"{'='*60}\n\n")

    print(f"{'='*60}")
    print(f"Færdig: {passed} passed, {failed} failed")
    print(f"JSON: {out_path}")
    print(f"TXT:  {txt_path}")


if __name__ == "__main__":
    main()