from dotenv import load_dotenv
import os

print("Testing environment variables:")
print("1. Loading .env file...")
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
print(f"2. API Key found: {api_key[:8]}..." if api_key else "2. No API key found!")

if api_key:
    print("3. API Key length:", len(api_key))
    print("4. First 8 characters:", api_key[:8])
    print("5. Does it start with 'sk-proj-'?", api_key.startswith('sk-proj-'))
