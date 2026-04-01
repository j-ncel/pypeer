import pytest
import asyncio
import os
from pypeer.engine.signaler import FirebaseSignaler
from pypeer.constants import FIREBASE_DB_URL


@pytest.mark.asyncio
async def test_real_firebase_handshake():
    """Verify end-to-end signal exchange using a live Firebase instance."""
    room_id = "TX1234"
    password = "test_password"
    long_sdp = "v=0\r\no=- 47239 " + ("x" * 200) + "\r\ns=-\r\nt=0 0..."
    test_data = {"sdp": long_sdp, "type": "offer"}

    host = FirebaseSignaler(FIREBASE_DB_URL, room_id, password)
    peer = FirebaseSignaler(FIREBASE_DB_URL, room_id, password)

    try:
        await host.clear_room()

        # Listen in background to mimic a remote peer
        wait_task = asyncio.create_task(peer.wait_for_signal("offer"))

        # Ensure SSE connection is established before posting
        await asyncio.sleep(2)

        await host.post_signal("offer", test_data)

        # Confirm data integrity after network roundtrip
        received_data = await asyncio.wait_for(wait_task, timeout=10.0)

        assert received_data == test_data
        assert received_data["sdp"] == test_data["sdp"]

    finally:
        await host.clear_room()
        await host.close()
        await peer.close()
