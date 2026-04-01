import httpx
import time
import asyncio
import os
import sys
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

DB_URL = os.getenv("FIREBASE_DB_URL")
DB_SECRET = os.getenv("FIREBASE_DB_SECRET")


async def clean_expired_rooms():
    """Purges WebRTC signaling rooms older than 10 minutes"""
    if not DB_URL or not DB_SECRET:
        logging.error("Missing FIREBASE_DB_URL or FIREBASE_DB_SECRET.")
        sys.exit(1)

    url = f"{DB_URL}/rooms.json?auth={DB_SECRET}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            rooms = response.json()

            if not rooms:
                return

            now_ms = int(time.time() * 1000)
            EXPIRY_MS = 10 * 60 * 1000
            purged_count = 0

            for room_id, content in rooms.items():
                offer_ts = content.get('offer', {}).get('timestamp', 0)

                if now_ms - offer_ts > EXPIRY_MS:
                    # Log activity without revealing the room_id
                    logging.info("Purging an expired signaling room...")

                    delete_url = f"{DB_URL}/rooms/{room_id}.json?auth={DB_SECRET}"
                    await client.delete(delete_url)
                    purged_count += 1

            if purged_count > 0:
                logging.info(f"Cleanup cycle finished. Total rooms purged: {purged_count}")

        except Exception as e:
            logging.exception(f"Janitor execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(clean_expired_rooms())
