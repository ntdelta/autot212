from .autopilot import ScrapeAllocations
from .t212 import PieAllocator
import json
import argparse


def main():
    parser = argparse.ArgumentParser(description="Run my package with arguments.")
    parser.add_argument("--api-key", required=True, help="Your API key")

    args = parser.parse_args()
    API_KEY = args.api_key
    allocator = PieAllocator(API_KEY)

    # This is really useful for mapping the T212 instrument IDs to their respective symbols
    with open("stonks.txt", "w") as f:
        get_instruments = allocator.get_instruments()
        f.write(json.dumps(get_instruments))

    scraper = ScrapeAllocations()

    allocations = scraper.get_allocations()
    trackers = allocations["data"]["teamsGet"]["teams"]

    formatted_data = []
    print("Trackers:")
    for tracker in trackers:
        if tracker.get("title") == "Autopilot":
            print("->", tracker["title"])
            print("\t", tracker["description"])
            for portfolio in tracker["portfolios"]:
                print("\t->", portfolio["pilotPortfolio"]["portfolioName"])
                print("\t\t", portfolio["pilotPortfolio"]["description"])
                portfolio["pilotPortfolio"]["holdingsConnection"]["currentHoldings"]
                formatted_data.append(
                    {
                        "title": portfolio["pilotPortfolio"]["portfolioName"],
                        "description": portfolio["pilotPortfolio"]["description"],
                        "holdings": portfolio["pilotPortfolio"]["holdingsConnection"][
                            "currentHoldings"
                        ],
                    }
                )

    for tracker in formatted_data:
        success = allocator.sync_pie_with_holdings(
            pie_name=tracker.get("title"), holdings=tracker.get("holdings")
        )

        if success:
            print("Successfully synced pie with current holdings")
        else:
            print("Failed to sync pie with current holdings")


if __name__ == "__main__":
    main()
