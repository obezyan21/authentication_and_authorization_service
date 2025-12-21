import os
from typing import Dict, Any

from dotenv import load_dotenv

load_dotenv()

def get_auth_data() -> Dict[str, Any]:
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("Не установлен секретны ключ")
    return {"secret_key": secret_key, "algorithm": os.getenv("ALGORITHM")}
