import secrets
import string

ALPHABET = string.ascii_uppercase + string.digits


def generate_room_id() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(6))
