import httpx
import json
import base64
import hashlib
from cryptography.fernet import Fernet
import zlib


class FirebaseSignaler:
    def __init__(self, base_url: str, room_id: str, password: str = ""):
        self.base_url = f"{base_url.rstrip('/')}/rooms/{room_id}"
        self.client = httpx.AsyncClient(timeout=None)

        secret = f"{room_id}{password}"
        key_seed = hashlib.sha256(secret.encode()).digest()
        self.cipher = Fernet(base64.urlsafe_b64encode(key_seed))

    async def post_signal(self, key: str, data: dict):
        url = f"{self.base_url}/{key}.json"

        json_data = json.dumps(data).encode()
        compressed_data = zlib.compress(json_data)
        encrypted_data = self.cipher.encrypt(compressed_data).decode()

        response = await self.client.put(url, json={"payload": encrypted_data})
        response.raise_for_status()

    async def wait_for_signal(self, key: str):
        url = f"{self.base_url}/{key}.json"
        headers = {"Accept": "text/event-stream"}

        async with self.client.stream("GET", url, headers=headers) as response:
            async for line in response.aiter_lines():
                if not line.strip() or line.startswith(":"):
                    continue
                if line.startswith("data:"):
                    data_payload = line[5:].strip()
                    if not data_payload or data_payload == "null":
                        continue
                    try:
                        wrapper = json.loads(data_payload)
                        encrypted_string = wrapper.get("data", {}).get("payload")

                        if encrypted_string:
                            decrypted_bytes = self.cipher.decrypt(encrypted_string.encode())
                            decompressed_json = zlib.decompress(decrypted_bytes)
                            actual_data = json.loads(decompressed_json)

                            if isinstance(actual_data, dict) and "sdp" in actual_data:
                                return actual_data

                    except Exception:
                        continue
        return None

    async def clear_room(self):
        url = f"{self.base_url}.json"
        try:
            await self.client.delete(url)
        except Exception:
            pass

    async def close(self):
        await self.client.aclose()
