import os

from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter

nutrition_loader = CSVLoader(file_path="Assignment Inputs - Nutrition source.csv")
unit_loader = CSVLoader(file_path="Assignment Inputs - Unit of measurements.csv")
category_loader = CSVLoader(file_path="Assignment Inputs - Food categories.csv")

docs = nutrition_loader.load() + unit_loader.load() + category_loader.load()

text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=10)
split_docs = text_splitter.split_documents(docs)

split_docs[2].page_content

model_name = "sentence-transformers/all-mpnet-base-v2"

vectorstore = FAISS.from_documents(split_docs, embedding=HuggingFaceEmbeddings(model_name=model_name))

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# .env file contains HUGGINGFACEHUB_API_TOKEN for authentication
from dotenv import load_dotenv
load_dotenv()
import os
# Load the environment variables from the .env file
# Load the Hugging Face API token from the environment variable
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")

llm = HuggingFaceEndpoint(
    repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1",
    task = "text-generation",
    temperature=0.5
)
model = ChatHuggingFace(llm=llm)

from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)

#Part 1

def estimate_nutrition(dish_name):
    query = f"""
    Given the dish "{dish_name}", perform the following:
    1. Estimate likely ingredients and their household measurements.
    2. Convert household measurements to grams.
    3. Map each ingredient to the Nutrition DB per 100g.
    4. Estimate total nutrition (calories, protein, fat, carbs).
    5. Identify the type of dish (e.g., Wet Sabzi, Dry Sabzi).
    6. Output nutrition per 1 katori (~150g).
    """
    result = qa_chain.invoke(query)
    return result

doc = estimate_nutrition("Paneer Butter Masala")

doc['result']

#Part 2

def messy_dish_prompt(dish_name, issues):
    return f"""
You are an intelligent food analyst working with noisy, incomplete data.

Dish: "{dish_name}"
Issues: {', '.join(issues)}

Your task:
1. Interpret the dish, including Hindi/English mix.
2. List assumed ingredients and estimated household quantities.
3. Resolve unit ambiguity (e.g., 'glass', 'pinch', etc).
4. Handle missing items by giving fallback values (based on common sense).
5. Map ingredients to nutrition DB entries.
6. Guess dish type (e.g., Dry Sabzi, Curry, etc).
7. Output nutrition per 1 katori (~150g), based on estimates.
8. Finally, clearly log all assumptions you made.

Make no hard-coded assumptions. Think like a human cook and use natural reasoning.
Give final output in this format:

---
Ingredients Used:
- [ingredient name]: [estimated quantity and unit]

Nutrition (per 1 katori):
- Calories: ...
- Protein: ...
- Fat: ...
- Carbs: ...

Dish Type: ...

Assumptions:
- ...
- ...
"""

def estimate_messy_dish(dish_name, issues):
    prompt = messy_dish_prompt(dish_name, issues)
    response = qa_chain.invoke(prompt)
    return response

test_inputs = [
    { "dish": "Jeera Aloo (mild fried)", "issues": ["ingredient synonym", "quantity missing"] },
    { "dish": "Gobhi Sabzi", "issues": ["ambiguous dish type"] },
    { "dish": "Chana masala", "issues": ["missing ingredient in nutrition DB"] },
    { "dish": "Paneer Curry with capsicum", "issues": ["unit in 'glass'", "spelling variation"] },
    { "dish": "Mixed veg", "issues": ["no fixed recipe", "ambiguous serving size"] }
]

results = {}
for entry in test_inputs:
    dish = entry["dish"]
    issues = entry["issues"]
    results[dish] = estimate_messy_dish(dish, issues)

for dish, output in results.items():
    print(f"\n🟡 Dish: {dish}")
    print(output['result'])  # or output['answer'] depending on your LangChain version