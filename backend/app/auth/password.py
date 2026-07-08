import bcrypt

# passlib's CryptContext is unmaintained and its bcrypt backend self-test breaks
# against bcrypt>=4.1 (incompatible with the bcrypt==5.0.0 pinned in requirements.txt),
# so we call the bcrypt library directly instead.
_BCRYPT_MAX_BYTES = 72


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
