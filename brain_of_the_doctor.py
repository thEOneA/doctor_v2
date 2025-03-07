from dotenv import load_dotenv
load_dotenv()

import os
import base64
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_with_query(query, encoded_image, model="llama-3.2-11b-vision-preview"):
    # Initialize Groq client with a longer timeout
    client = Groq(api_key=GROQ_API_KEY, timeout=120.0)  # 120 seconds timeout
    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": query}]
        }
    ]
    messages[0]["content"].append({
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
    })
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: Could not connect to Groq API - {str(e)}. Please try again later."

if __name__ == "__main__":
    image_path = "acne.jpg"  # Replace with a test image path
    encoded = encode_image(image_path)
    response = analyze_image_with_query("Is there something wrong with my face?", encoded)
    print(f"Doctor's analysis (single image): {response}")