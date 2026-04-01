import pytest
import json
import zlib
from unittest.mock import AsyncMock, MagicMock
from cryptography.fernet import InvalidToken
from pypeer.engine.signaler import FirebaseSignaler
from pypeer.engine.rtc_engine import RTCEngine


@pytest.mark.asyncio
async def test_post_signal_payload_structure():
    signaler = FirebaseSignaler("http://localhost", "ROOM01", "secret")

    # Mock response to prevent 'coroutine never awaited' warning on raise_for_status
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    signaler.client.put = AsyncMock(return_value=mock_response)

    await signaler.post_signal("offer", {"sdp": "test-sdp"})

    args, kwargs = signaler.client.put.call_args
    assert "payload" in kwargs["json"]
    assert isinstance(kwargs["json"]["payload"], str)


@pytest.mark.asyncio
async def test_encryption_decryption_cycle():
    room_id, password = "TEST01", "secure_pass"
    data = {"sdp": "v=0...", "type": "offer"}
    signaler = FirebaseSignaler("http://localhost", room_id, password)

    # Mimic internal encryption flow
    encrypted = signaler.cipher.encrypt(zlib.compress(json.dumps(data).encode()))

    # Decrypt and verify
    decrypted = zlib.decompress(signaler.cipher.decrypt(encrypted))
    result = json.loads(decrypted)

    assert result == data


@pytest.mark.asyncio
async def test_wrong_password_fails():
    host_signaler = FirebaseSignaler("http://localhost", "T1", "correct")
    peer_signaler = FirebaseSignaler("http://localhost", "T1", "wrong")

    encrypted = host_signaler.cipher.encrypt(zlib.compress(b'{"sdp":"msg"}'))

    with pytest.raises(InvalidToken):
        peer_signaler.cipher.decrypt(encrypted)


@pytest.mark.asyncio
async def test_engine_status_callback_on_state_change():
    engine = RTCEngine(AsyncMock())
    callback_received = []

    engine.on_status_callback = lambda status: callback_received.append(status)
    engine._notify_status("Connecting")
    engine._notify_status("Connected")

    assert callback_received == ["Connecting", "Connected"]


@pytest.mark.asyncio
async def test_signaler_clear_room_calls_delete():
    signaler = FirebaseSignaler("http://localhost", "CLEAN1", "pass")
    signaler.client.delete = AsyncMock()

    await signaler.clear_room()

    signaler.client.delete.assert_called_once_with("http://localhost/rooms/CLEAN1.json")


@pytest.mark.asyncio
async def test_wait_for_signal_raises_auth_failed():
    signaler = FirebaseSignaler("http://localhost", "ROOM01", "wrong_password")

    # Mock async generator for line streaming
    async def mock_aiter_lines():
        fake_payload = json.dumps({"data": {"payload": "invalid_token_here"}})
        yield f"data: {fake_payload}"

    mock_response = AsyncMock()
    mock_response.aiter_lines = mock_aiter_lines

    # Mock the 'async with client.stream' context manager
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
    mock_cm.__aexit__ = AsyncMock(return_value=None)
    signaler.client.stream = MagicMock(return_value=mock_cm)

    with pytest.raises(Exception) as exc:
        await signaler.wait_for_signal("offer")

    assert "AUTH_FAILED" in str(exc.value)


@pytest.mark.asyncio
async def test_engine_notification_on_disconnect():
    engine = RTCEngine(AsyncMock())
    received = []
    engine.on_status_callback = lambda s: received.append(s)

    # Simulate closing the connection
    await engine.close()

    assert engine.pc is None
    assert engine.channel is None
