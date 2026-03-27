import httpx
import asyncio


class FirebaseSignaler:
    def __init__(self, base_url: str, room_id: str):
        self.base_url = base_url.rstrip("/")
        self.room_id = room_id
        self.client = httpx.AsyncClient()

    async def post_signal(self, key: str, data: dict):
        """Uploads offer or answer to Firebase."""
        url = f"{self.base_url}/rooms/{self.room_id}/{key}.json"
        await self.client.put(url, json=data)

    async def wait_for_signal(self, key: str):
        """Polls Firebase until the specific key (offer/answer) exists."""
        url = f"{self.base_url}/rooms/{self.room_id}/{key}.json"
        while True:
            try:
                res = await self.client.get(url)
                data = res.json()
                if data:
                    return data
            except Exception:
                pass
            await asyncio.sleep(1)

    async def clear_room(self):
        """Cleans up the signaling data once connection is live."""
        url = f"{self.base_url}/rooms/{self.room_id}.json"
        await self.client.delete(url)

    async def close(self):
        await self.client.aclose()
