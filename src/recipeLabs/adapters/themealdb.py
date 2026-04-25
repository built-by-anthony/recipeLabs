def parse_meal(meal: dict) -> dict:
    ingredients = []
    for i in range(1, 21):
        if meal[f"strIngredient{i}"] != "":
            ingredients.append(
                {
                    "name": meal[f"strIngredient{i}"],
                    "quantity": meal[f"strMeasure{i}"],
                }
            )

    return {
        "name": meal["strMeal"],
        "cuisine": meal["strArea"],
        "external_id": meal["idMeal"],
        "ingredients": ingredients,
    }
