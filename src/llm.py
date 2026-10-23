
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found. Check your .env file."
    )

client = Groq(api_key=api_key)

def ask_llm(question):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful Class 10 Science tutor. "
                           "Explain concepts clearly and accurately."
            },
            {"role": "user", "content": question}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    answer = ask_llm("Explain Ohm's law in simple words.")
    print("\nAnswer:\n", answer)
