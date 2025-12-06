import secrets
import argparse
from app.services.auth import add_key


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--key", help="Optional API key to add (random if omitted)")
    p.add_argument("--meta", help="Optional metadata string for the key", default="pilot")
    args = p.parse_args()
    key = args.key or secrets.token_urlsafe(24)
    add_key(key, {"meta": args.meta})
    print("Added API key:", key)


if __name__ == '__main__':
    main()
