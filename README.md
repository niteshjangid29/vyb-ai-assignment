# Vyb AI Nutrition Estimator

This project solves the challenge of estimating the nutrition of home-cooked Indian dishes, even when the input is partial, messy, or ambiguous. It uses open-source LLMs and LangChain to create a robust retrieval-augmented generation (RAG) system capable of understanding real-world cooking variations.

---

## Part 1: Core Pipeline

### Approach

- **Document Loading**: Nutrition DB, household unit reference, and dish category mapping are loaded using `langchain.document_loaders.CSVLoader`.
- **Text Embedding & Vector Store**: We used `sentence-transformers/all-mpnet-base-v2` as the embedding model and FAISS for vector indexing.
- **LLM Integration**: Used `mistralai/Mistral-8x7B-Instruct-v0.3` via HuggingFace and `ChatHuggingFace` wrapper for answering queries.
- **RetrievalQA Chain**: LangChain's `RetrievalQA` pulls relevant data chunks and feeds them to the LLM for question answering.
- **Prompting Strategy**: A structured query asks the model to extract ingredients, map units, resolve to Nutrition DB, calculate per-100g values, scale to 1 katori (150g), and identify the dish type.

Following is the input and output for this part:

**Input:**

```
Paneer Butter Masala
```

**Output:**

```
1. Estimated ingredients for Paneer Butter Masala:

200g Paneer (Indian Cottage Cheese)
1 tbsp Butter
1 tbsp Vegetable Oil
1 tsp Cumin Seeds
1 tsp Ginger Paste
1 tsp Garlic Paste
1 tsp Coriander Powder
1 tsp Turmeric Powder
1 tsp Red Chili Powder
1 tsp Garam Masala
1 tsp Kasuri Methi (Dried Fenugreek Leaves)
2 tbsp Tomato Puree
1 tsp Salt
1 tbsp Sugar
100ml Water
50ml Fresh Cream
Fresh Coriander Leaves for garnish

2. Converted household measurements to grams:

200g Paneer (Indian Cottage Cheese)
14g Butter
14g Vegetable Oil
1.7g Cumin Seeds
10g Ginger Paste
10g Garlic Paste
3g Coriander Powder
3g Turmeric Powder
3g Red Chili Powder
3g Garam Masala
3g Kasuri Methi (Dried Fenugreek Leaves)
60g Tomato Puree
6g Salt
6g Sugar
100ml Water
50ml Fresh Cream
Fresh Coriander Leaves for garnish

3. Map each ingredient to the Nutrition DB per 100g:

Paneer (ASC222): 145.61kcal, 6.99g protein, 8.81g fat, 9.7g carbs
Butter: ~700kcal, 0.8g protein, 81g fat, 0g
```

---

## Part 2: Messy Reality (Edge Case Handling)

### Approach

- Extended the same LangChain pipeline from Part 1 to work with "real-world messy dish names".
- Created a natural language reasoning prompt that includes **dish name + issue list** (e.g., spelling variation, missing units).
- Let the LLM infer:
  - Ingredient synonyms (e.g., jeera → cumin)
  - Unit approximations (e.g., glass → 240 ml)
  - Dish type guesses (e.g., Gobhi Sabzi → Dry Sabzi)
  - Default quantities if missing
- Added a **structured output format** to log assumptions, nutrition values, and dish type.

### Assumptions & Fallback Design

| Situation                              | Strategy                                     |
| -------------------------------------- | -------------------------------------------- |
| Ingredient synonyms (e.g., jeera, alu) | Mapped via LLM context                       |
| Unknown units (e.g., glass)            | LLM assumes typical household values         |
| Missing quantities                     | LLM uses average Indian cooking quantities   |
| Ingredient not found in nutrition DB   | Ingredient skipped and logged                |
| Mixed/hybrid dish names                | LLM infers likely type (Dry Sabzi, Curry)    |
| Hinglish or spelling variation         | LLM handles through contextual understanding |

All assumptions are recorded and logged in a structured format per dish.

Following is the input and output for this part:

**Input:**

```json
[
  {
    "dish": "Jeera Aloo (mild fried)",
    "issues": ["ingredient synonym", "quantity missing"]
  },
  {
    "dish": "Gobhi Sabzi",
    "issues": ["ambiguous dish type"]
  },
  {
    "dish": "Chana masala",
    "issues": ["missing ingredient in nutrition DB"]
  },
  {
    "dish": "Paneer Curry with capsicum",
    "issues": ["unit in 'glass'", "spelling variation"]
  },
  {
    "dish": "Mixed veg",
    "issues": ["no fixed recipe", "ambiguous serving size"]
  }
]
```

**Output:**

```
🟡 Dish: Jeera Aloo (mild fried)

1. Jeera Aloo is a Hindi term which translates to "Cumin Potatoes" in English. It is a popular Indian side dish made with potatoes, cumin seeds, and a few other spices.

2. Assumed ingredients and estimated household quantities:

- Potatoes (Aloo): 500g
- Cumin Seeds (Jeera): 1 tbsp (15ml)
- Turmeric Powder (Haldi): 1 tsp (5ml)
- Red Chilli Powder: 1 tsp (5ml)
- Coriander Powder (Dhania): 1 tsp (5ml)
- Garam Masala: 1 tsp (5ml)
- Salt: to taste (~1 tsp or 5ml)
- Vegetable Oil: 2 tbsp (30ml)
- Fresh Coriander Leaves (Dhania Patta): for garnish (~10g)

3. Unit ambiguity:

- tbsp: tablespoon
- ml: milliliter
- tsp: teaspoon
- g: gram
- katori: ~150g

4. Missing items:

- No specific quantity is given for any ingredient, so we will use estimated household quantities.

5. Mapping ingredients to nutrition DB entries:

- Potatoes (OSR104), Cumin Seeds (OSR101), Turmeric Powder (OSR105), Red Chilli Powder (OSR106), Coriander Powder (OSR107), Garam Masala (OSR108), Salt (OSR109), Vegetable Oil (OSR110), Fresh Coriander Leaves (OSR111)

6. Dish Type: Dry Sabzi

7. Nutrition (per 1 katori):

- Calories: 300-350 kcal (estimated)
- Protein: 6-8g (estimated)
- Fat: 15-20g (estimated)
- Carbs: 40-50g

🟡 Dish: Gobhi Sabzi

---

Ingredients Used:

- Cauliflower: 250g
- Onion: 100g
- Tomato: 150g
- Garlic: 10g
- Ginger: 10g
- Turmeric powder: 1tsp
- Red chili powder: 1tsp
- Coriander powder: 1tsp
- Garam masala: 1tsp
- Oil: 2tbsp
- Salt: to taste
- Water: 200ml

Nutrition (per 1 katori):

- Calories: ~160
- Protein: ~5g
- Fat: ~8g
- Carbs: ~15g

Dish Type: Dry Sabzi

Assumptions:

- Standard household measurements for ingredients.
- Nutrition values estimated based on average values for each ingredient.
- Dish type assumed to be a dry sabzi due to the absence of any liquid-based sauce.
- No specific information found about 'Gobhi Sabzi', so assumed to be a common dish with cauliflower as the main ingredient.

🟡 Dish: Chana masala

1. Chana masala is a popular Indian dish made with chickpeas (chana) and a blend of spices.

2. Assumed ingredients and estimated quantities:

- Chickpeas (2 cups)
- Onion (1 medium, diced)
- Tomatoes (2 medium, diced)
- Ginger (1 inch, minced)
- Garlic (3 cloves, minced)
- Green chili (1, chopped)
- Turmeric (1 tsp)
- Coriander powder (1 tbsp)
- Cumin powder (1 tbsp)
- Garam masala (1 tbsp)
- Red chili powder (1 tbsp)
- Salt (to taste)
- Cilantro (for garnish)
- Oil (2 tbsp)

3. Unit ambiguity:

- 1 cup chickpeas (cooked)
- 1 medium onion (~120g)
- 2 medium tomatoes (~200g)
- 1 inch ginger (~5g)
- 3 cloves garlic (~9g)
- 1 green chili (~5g)
- 1 tsp (5ml) turmeric, coriander powder, cumin powder, garam masala, red chili powder
- To taste (~5g) salt
- 1 bunch cilantro (~30g)
- 2 tbsp (30ml) oil

4. Handling missing items:

- Turmeric: 1 tsp (5ml)
- Coriander powder: 1 tbsp (15ml)
- Cumin powder: 1 tbsp (15ml)
- Garam masala: 1 tbsp (15ml)
- Red chili powder: 1 tbsp (15ml)
- Salt: to taste (~5g)

5. Mapping ingredients to nutrition DB entries:

- Chickpeas: BFP151 (Masala dosa paneer fillings)
- Onion: OSR097


🟡 Dish: Paneer Curry with capsicum

1. The dish "Paneer Curry with capsicum" is a curry dish made with paneer (Indian cottage cheese) and capsicum (bell peppers) in a gravy-like sauce. The use of Hindi and English in the dish name suggests it's a fusion dish or a common dish in Indian-English communities.

2. Assumed ingredients and estimated household quantities:

- Paneer: 200g
- Capsicum (bell pepper): 1 large (~200g)
- Onion: 1 medium (~100g)
- Tomato: 2 medium (~200g)
- Ginger: 1 inch (~5g)
- Garlic: 3 cloves (~5g)
- Turmeric powder: 1/2 tsp (~1g)
- Coriander powder: 1 tbsp (~6g)
- Cumin powder: 1 tsp (~2g)
- Red chili powder: 1 tsp (~2g)
- Garam masala: 1 tsp (~2g)
- Salt: to taste (~5g)
- Oil: 2 tbsp (~30ml)
- Water: 1 cup (~250ml)
- Fresh coriander leaves: for garnish (~10g)

3. Since there is no unit provided for 'glass', I'll assume it's a 250ml glass, which is a common household measure. I'll convert the 'glass' of oil to tbsp (1 glass = 8 tbsp).

4. For missing items, I'll provide fallback values based on common sense:

- Ginger: 1 inch (~5g)
- Garlic: 3 cloves (~5g)

5. Mapping ingredients to nutrition DB entries:

- Paneer (OSR001)
- Capsicum (OSR002)
- Onion (OSR003)
- Tomato (OSR004)
- Ginger (OSR005)

🟡 Dish: Mixed veg

---

Ingredients Used:

- Potato: 100g
- Carrot: 50g
- Peas: 50g
- Onion: 50g
- Tomato: 50g
- Spinach: 50g
- Oil: 1 tbsp
- Turmeric: 1/4 tsp
- Red chili powder: 1/2 tsp
- Coriander powder: 1/2 tsp
- Garam masala: 1/4 tsp
- Salt: 1/2 tsp
- Water: 1/2 cup

Nutrition (per 1 katori):

- Calories: ~180
- Protein: ~4g
- Fat: ~5g
- Carbs: ~30g

Dish Type: Dry Sabzi

Assumptions:

- Standard Indian cooking oil used.
- Spices used in typical Indian cooking proportions.
- All vegetables are fresh.
- Serving size is 1 katori (~150g).
- Nutrition values are approximate estimates based on the given data.
```

---

## Part 3: Manual Reasoning

### Mapping "lightly roasted jeera powder"

- Mapped to `Cumin (Jeera)`
- Reasoning: Light roasting and grinding do not significantly change macro-nutrient values. Therefore, it's valid to use the same nutrition entry as raw cumin seeds.

### Cooking Loss Ratio

- **Raw weight**: 950g
- **Cooked weight**: 700g
- **Loss ratio**:

  ```
  ((950 - 700) / 950) * 100 = 26.3%
  ```

- **Adjusted to 180g serving**:
  If nutrition is calculated for 700g, then:
  ```
  Per 180g = (180 / 700) × Total Nutrition
  ```

---

## Bonus Section

### Unit Testing

- Covered ingredients with different densities in the above parts for all the cases.

- Also included fallback behavior for unknown ingredients.
