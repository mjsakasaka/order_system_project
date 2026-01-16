import hashlib

def hash_password(raw: str) -> str:
    # 最小版：先用 sha256（作品集足够）；之后你想更真实可换 passlib/bcrypt
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def verify_password(raw: str, hashed: str) -> bool:
    return hash_password(raw) == hashed
