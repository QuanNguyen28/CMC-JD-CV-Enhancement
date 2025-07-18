
import os
import google.generativeai as genai
from dotenv import load_dotenv

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

API_KEY = os.getenv("GEMINI_API_KEY")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "text-embedding-004")

# In thông tin debug để kiểm tra
print(f"DEBUG: .env path = {env_path}")
if API_KEY:
    print(f"DEBUG: API_KEY loaded: Yes (starts with {API_KEY[:5]}..., ends with ...{API_KEY[-4:]})")
else:
    print(f"DEBUG: API_KEY loaded: No")
print(f"DEBUG: EMBED_MODEL = {EMBED_MODEL}")

# Cấu hình genai với API key
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("⚠️ WARNING: GEMINI_API_KEY is not set. The embedding function will fail.")

def embed_text(chunks: list[str], model=EMBED_MODEL, task_type="RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """
    Embeds a batch of text chunks using the Gemini API.
    This function will raise an exception if the API call fails.
    """
    if not API_KEY:
        raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file.")

    print(f"INFO: Embedding {len(chunks)} chunks using model '{model}'...")
    try:
        result = genai.embed_content(
            model=model,
            content=chunks,
            task_type=task_type
        )
        
        print(f"✅ Successfully generated {len(result['embedding'])} embeddings.")
        return result['embedding']

    except Exception as e:
        print(f"❌ An error occurred during the Gemini API call: {e}")
        raise


