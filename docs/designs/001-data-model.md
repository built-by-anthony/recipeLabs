# Tables

## recipes
table name: `recipes`

why: The recipes table serves as the core dimension of the data model, storing all descriptive information about a recipe so it can be referenced across cook sessions without duplication.

key fields:
- `id` - unique identifer
- `name` - the recipe name
- `cuisine` - type of food
- `prep_time` - time to prep
- `cook_time` - time to cook
- `total_time` - total time

## recipe_ingredients
table name: `recipe_ingredients`

why: Stores each ingredient as its own row rather than a single text field, so ingredients can be queried, filtered, and normalized individually later.

key fields:
- `id`
- `recipe_id` - links back to the `recipes` table
- `name` - the ingredient name (e.g., "flour")
- `quantity` - the amount (e.g., "2")
- `unit` - the measurement (e.g., "cups")

## recipe_sources
table name: `recipe_sources`

why: Tracks where each recipe came from (TheMealDB, Spoonacular, manual entry) and stores the external ID so that re-importing the same recipe doesn't create duplicates.

key fields:
- id
- `recipe_id` - links back to the `recipes` table
- source_type — e.g., "themealdb", "spoonacular", "manual"
- external_id — the ID from the external API (so you can look it up later or avoid duplicates on re-import)
- source_url — the original URL if there is one

## cook_log
table name: `cook_log`

why: Tracks each individual cook session so we can preserve history, ratings over time, and notes per cook rather than overwriting a single value.

key fields:
- id
- `recipe_id` - links back to the `recipes` table
- cooked_at — the date you cooked it
- rating — your rating that night (1-5)
- notes — freetext notes ("added more garlic")
- cooked_by — who cooked it (you or your wife)

## tags
table name: `tags`

why: To enable grouping of recipes, filtering, searching, etc.

key fields:
- id
- name - (e.g., "vegetarian", "quick")

## recipe_tags
table name: `recipe_tags`

why: to link tags back to recipes

key_fields:
- recipe_id
- tag_id
