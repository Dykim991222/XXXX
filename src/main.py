import sys
import os
from pathlib import Path
from dotenv import load_dotenv


def load_environment() -> None:
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)


def main() -> int:
    """Entry point for the application."""
    load_environment()
    
    api_key = os.getenv("YOUTUBE_DATA_API_KEY")
    
    if api_key:
        print(f"API Key loaded: {api_key[:10]}...")
    else:
        print("API Key not found!")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

