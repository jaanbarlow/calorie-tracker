"""
USDA FoodData Central API client.

Searches the external API and returns simplified nutrient data
(calories, protein, carbs, fat — all per 100 g).
"""

import os
from typing import Any

import requests

USDA_API_KEY: str = os.getenv("USDA_API_KEY", "DEMO_KEY")
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# Maps USDA nutrient names → our simplified keys
_NUTRIENT_MAP: dict[str, str] = {
    "Energy": "calories",
    "Protein": "protein",
    "Carbohydrate, by difference": "carbs",
    "Total lipid (fat)": "fat",
}


def search_foods(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """
    Search the USDA FoodData Central API and return up to *max_results*
    simplified food entries.

    Each entry contains:
        fdc_id, name, calories, protein, carbs, fat
    """
    resp = requests.get(
        USDA_SEARCH_URL,
        params={
            "query": query,
            "api_key": USDA_API_KEY,
            "pageSize": max_results,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    results: list[dict[str, Any]] = []
    for food in data.get("foods", [])[:max_results]:
        nutrients: dict[str, float] = {v: 0.0 for v in _NUTRIENT_MAP.values()}
        for n in food.get("foodNutrients", []):
            key = _NUTRIENT_MAP.get(n.get("nutrientName"))
            if key is not None:
                nutrients[key] = round(n.get("value", 0.0), 2)

        results.append(
            {
                "fdc_id": food["fdcId"],
                "name": food["description"],
                **nutrients,
            }
        )

    return results
