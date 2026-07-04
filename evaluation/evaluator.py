from services.langgraph_engine import run_graph
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


TEST_CASES = [
    {
        "input": "Salary 50k spend 60k heavy shopping",
        "expected": "reduce expenses"
    },
    {
        "input": "Salary 80k spend 40k good savings habit",
        "expected": "invest surplus"
    },
    {
        "input": "Salary 30k spend 28k no savings",
        "expected": "build emergency fund"
    }
]


# -----------------------------
# LLM JUDGE (REAL FIX)
# -----------------------------
def classify_with_llm(text: str):

    prompt = f"""
You are a financial decision classifier.

Classify this financial advice into ONE label:

Labels:
1. reduce expenses
2. invest surplus
3. build emergency fund

Rules:
- Return ONLY the label
- No explanation

Text:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()


# -----------------------------
# EVALUATION LOOP
# -----------------------------
def evaluate():

    correct = 0
    total = len(TEST_CASES)

    for case in TEST_CASES:

        print("\n--- INPUT ---")
        print(case["input"])

        result = run_graph(case["input"])
        output = result.get("final_advice", "")

        predicted = classify_with_llm(output)

        print("\n--- AI OUTPUT ---")
        print(output[:300])

        print("\nPREDICTED:", predicted)
        print("EXPECTED:", case["expected"])

        if case["expected"] in predicted:
            correct += 1

    accuracy = (correct / total) * 100

    print("\n====================")
    print(f"ACCURACY: {accuracy:.2f}%")
    print("====================")


if __name__ == "__main__":
    evaluate()