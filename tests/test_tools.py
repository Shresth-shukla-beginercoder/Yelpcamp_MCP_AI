# Offline tool tests. The MCP tools are async (they await the data-access
# layer), so each test drives them with asyncio and relies on the mock adapter
# (no YELPCAMP_API_URL set -> no network).
import asyncio
import os

os.environ.pop("YELPCAMP_API_URL", None)  # force the mock adapter

from tools.campground_tools import (
    search_campgrounds,
    get_campground_details,
    list_reviews,
    recommend_campgrounds,
    explain_yelpcamp,
)


def test_search_keyword():
    results = asyncio.run(search_campgrounds(keyword="Sunny"))
    assert len(results) == 1
    assert results[0]["name"] == "Sunny Pines"


def test_list_reviews():
    reviews = asyncio.run(list_reviews("c1"))
    assert len(reviews) == 2
    assert "Great place!" in reviews


def test_details():
    details = asyncio.run(get_campground_details("c1"))
    assert details["name"] == "Sunny Pines"


def test_recommend_by_location():
    results = asyncio.run(recommend_campgrounds(location="Arizona"))
    assert len(results) == 1
    assert results[0]["name"] == "Desert Oasis"


def test_explain():
    # explain_yelpcamp has no data access, so it stays synchronous.
    explanation = explain_yelpcamp()
    assert "YelpCamp" in explanation


if __name__ == "__main__":
    test_search_keyword()
    test_list_reviews()
    test_details()
    test_recommend_by_location()
    test_explain()
    print("Tool tests passed!")
