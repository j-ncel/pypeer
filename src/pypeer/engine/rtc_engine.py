from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
import asyncio
from constants import ICE_SERVERS


class RTCEngine:
    def __init__(self, signaler):
        self.signaler = signaler
        ice_provider = [RTCIceServer(**server) for server in ICE_SERVERS]
        self.pc = RTCPeerConnection(configuration=RTCConfiguration(
            iceServers=ice_provider
        ))

        self.channel = None
        self.on_message_callback = None
        self.on_status_callback = None

        @self.pc.on("connectionstatechange")
        async def on_connectionstatechange():
            state = self.pc.connectionState
            if self.on_status_callback:
                self.on_status_callback(state.capitalize())
            if state in ["failed", "closed"]:
                await self.close()

    async def setup_as_host(self, timeout: int = 60):
        try:
            self.channel = self.pc.createDataChannel("chat")
            self._bind_channel_events(self.channel)

            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)
            await self._wait_for_ice()

            await self.signaler.post_signal("offer", {
                "sdp": self.pc.localDescription.sdp,
                "type": "offer"
            })

            # Wait for answer with a TIMEOUT
            answer_data = await asyncio.wait_for(
                self.signaler.wait_for_signal("answer"),
                timeout=timeout
            )
            await self.pc.setRemoteDescription(RTCSessionDescription(**answer_data))

        except asyncio.TimeoutError:
            if self.on_status_callback:
                self.on_status_callback("Timeout: No Peer Joined")
            await self.close()

    async def setup_as_peer(self, timeout: int = 30):
        try:
            # Wait for offer with a TIMEOUT
            offer_data = await asyncio.wait_for(
                self.signaler.wait_for_signal("offer"),
                timeout=timeout
            )
            await self.pc.setRemoteDescription(RTCSessionDescription(**offer_data))

            @self.pc.on("datachannel")
            def on_datachannel(channel):
                self.channel = channel
                self._bind_channel_events(channel)

            answer = await self.pc.createAnswer()
            await self.pc.setLocalDescription(answer)

            await self._wait_for_ice()

            await self.signaler.post_signal("answer", {
                "sdp": self.pc.localDescription.sdp,
                "type": "answer"
            })
        except asyncio.TimeoutError:
            if self.on_status_callback:
                self.on_status_callback("Timeout: Room Not Found")
            await self.close()

    async def _wait_for_ice(self):
        """Helper to wait for ICE gathering to finish."""
        while self.pc.iceGatheringState != "complete":
            await asyncio.sleep(0.1)

    def _bind_channel_events(self, channel):
        @channel.on("open")
        def on_open():
            if self.on_status_callback:
                self.on_status_callback("Live")
            asyncio.create_task(self.signaler.clear_room())

        @channel.on("message")
        def on_message(msg):
            if self.on_message_callback:
                self.on_message_callback(msg)

    def send_message(self, text: str):
        if self.channel and self.channel.readyState == "open":
            self.channel.send(text)

    async def close(self):
        """Clean resource teardown."""
        if self.channel:
            self.channel.close()
        await self.pc.close()
        await self.signaler.close()
