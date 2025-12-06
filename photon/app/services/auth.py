import os
import json
import threading
from typing import Dict

_lock = threading.Lock()

KEYS_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'api_keys.json'))

def _ensure_keys_file():
    d = os.path.dirname(KEYS_PATH)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(KEYS_PATH):
        with open(KEYS_PATH, 'w', encoding='utf-8') as f:
            json.dump({}, f)

def load_keys() -> Dict[str, Dict]:
    _ensure_keys_file()
    with _lock:
        with open(KEYS_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return {}

def save_keys(keys: Dict[str, Dict]):
    _ensure_keys_file()
    with _lock:
        with open(KEYS_PATH, 'w', encoding='utf-8') as f:
            json.dump(keys, f, indent=2)

def is_valid_key(key: str) -> bool:
    if not key:
        return False
    keys = load_keys()
    return key in keys

def add_key(key: str, meta: Dict = None):
    if meta is None:
        meta = {}
    keys = load_keys()
    keys[key] = meta
    save_keys(keys)
