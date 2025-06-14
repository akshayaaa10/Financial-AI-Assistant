import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

class Config:
    # API keys from .env
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '66884a0f1b474b9ca70cf1aa9d034052')
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')  # Optional

    # Open source models
    LLM_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    SMALL_LLM_MODEL = "microsoft/DialoGPT-medium"
    LIGHTWEIGHT_EMBEDDING = "sentence-transformers/all-MiniLM-L6-v2"

    # Model config
    MAX_TOKENS = 2048
    TEMPERATURE = 0.1
    TOP_P = 0.9
    DEVICE = "cuda" if os.system("nvidia-smi") == 0 else "cpu"

    # Vector DB
    VECTOR_DB_PATH = "vector_db"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    # Data settings
    MAX_NEWS_ARTICLES = 20
    MAX_DOCUMENT_LENGTH = 8000

    # Flask app
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = True

    # Cache
    CACHE_DIR = "cache"
    CACHE_EXPIRY_HOURS = 6
