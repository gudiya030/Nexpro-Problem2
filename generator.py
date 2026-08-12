
import os, sys
from dotenv import load_dotenv
from google import genai
load_dotenv()

def generate(prompt):
    key=os.getenv("GEMINI_API_KEY")
    if not key: raise RuntimeError("GEMINI_API_KEY missing")
    model=os.getenv("GENERATOR_MODEL","gemini-2.5-flash")
    client=genai.Client(api_key=key)
    r=client.models.generate_content(model=model, contents=prompt)
    return r.text or ""

if __name__=="__main__":
    prompt=" ".join(sys.argv[1:]) or "Explain overfitting in two sentences."
    print(generate(prompt))
