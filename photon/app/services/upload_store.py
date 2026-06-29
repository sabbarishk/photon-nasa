_store: dict = {}


def put(upload_id: str, data: dict) -> None:
    _store[upload_id] = data


def get(upload_id: str) -> dict:
    return _store[upload_id]  # raises KeyError if not found


def contains(upload_id: str) -> bool:
    return upload_id in _store
