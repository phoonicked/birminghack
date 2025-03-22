import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("NEUPHONIC_API_KEY", "default_api_key_if_not_set")

