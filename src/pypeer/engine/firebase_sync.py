import httpx
import json


class FirebaseSignaler:
    def __init__(self, base_url: str, room_id: str):
        self.base_url = f"{base_url.rstrip('/')}/rooms/{room_id}"
        self.client = httpx.AsyncClient(timeout=None)

    async def post_signal(self, key: str, data: dict):
        url = f"{self.base_url}/{key}.json"
        response = await self.client.put(url, json=data)
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
                        payload_json = json.loads(data_payload)
                        actual_data = payload_json.get("data")

                        if isinstance(actual_data, dict) and "sdp" in actual_data:
                            return actual_data

                    except (json.JSONDecodeError, TypeError):
                        continue
        return None

    async def clear_room(self):
        url = f"{self.base_url}.json"
        await self.client.delete(url)

    async def close(self):
        await self.client.aclose()
