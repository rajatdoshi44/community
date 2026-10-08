import os
from google import genai
from google.genai import types


def getGenAIClient():
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"Using Google API Key: {api_key}")
    return genai.Client(api_key=api_key)


def llm_model(prompt, model="gemini-3.5-flash-lite", temperature=0.0, tools=[]):
    client = getGenAIClient()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=tools,
            temperature=temperature,
        ),
    )
    return response
