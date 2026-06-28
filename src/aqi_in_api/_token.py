import time

import jwt

JWT_SECRET = "masai"
TOKEN_EXPIRY_SECONDS = 7 * 24 * 60 * 60


def generate_token() -> str:
    """Generate a JWT token matching the AQI.in API expectations."""
    now = int(time.time())
    payload = {
        "userID": 1,
        "iat": now,
        "exp": now + TOKEN_EXPIRY_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
