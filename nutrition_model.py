# Mock implementation of estimate_nutrition
def estimate_nutrition(dish_name):
    # Replace this with actual logic to estimate nutrition
    nutrition_data = {
        "aloo paratha": {"calories": 300, "protein": 7, "fat": 10},
        "rajma chawal": {"calories": 400, "protein": 12, "fat": 8},
    }
    if dish_name.lower() in nutrition_data:
        return nutrition_data[dish_name.lower()]
    else:
        raise ValueError("Dish not found in the database.")