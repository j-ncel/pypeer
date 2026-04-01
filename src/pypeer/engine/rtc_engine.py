from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
import asyncio
from constants import ICE_SERVERS


class RTCEngine:
    def __init__(self, signaler):
        self.signaler = signaler
        self.pc = RTCPeerConnection(configuration=RTCConfiguration(
            iceServers=[RTCIceServer(**server) for server in ICE_SERVERS]
        ))

        self.channel = None
        self.on_message_callback = None
        self.on_status_callback = None
        self.last_status = None

        self.pc.on("connectionstatechange", self._on_connection_state_change)
        self.pc.on("datachannel", self._on_datachannel)

    async def _on_connection_state_change(self):
        if not self.pc:
            return

        state = self.pc.connectionState
        self._notify_status(state.capitalize())

        if state in ["failed", "closed", "disconnected"]:
            if self.on_status_callback:
                self.on_status_callback("Disconnected")
            await self.close()

    def _on_datachannel(self, channel):
        self.channel = channel
        self._bind_channel_events(channel)

    def _bind_channel_events(self, channel):
        @channel.on("open")
        def on_open():
            if self.on_status_callback:
                self.on_status_callback("Live")
            asyncio.create_task(self.signaler.clear_room())
            asyncio.create_task(self.keep_alive())

        @channel.on("message")
        def on_message(msg):
            if msg == "__ping__":
                return
            if self.on_message_callback:
                self.on_message_callback(msg)

    async def keep_alive(self):
        try:
            while self.channel and self.channel.readyState == "open":
                self.send_message("__ping__")
                await asyncio.sleep(15)
        except Exception:
            pass

    async def setup_as_host(self, timeout: int = 180):
        try:
            self.channel = self.pc.createDataChannel("chat")
            self._bind_channel_events(self.channel)

            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)
            await self._wait_for_ice()

            if not self.pc:
                return

            await self.signaler.post_signal("offer", {
                "sdp": self.pc.localDescription.sdp,
                "type": "offer"
            })

            answer_data = await asyncio.wait_for(
                self.signaler.wait_for_signal("answer"),
                timeout=timeout
            )
            await self.pc.setRemoteDescription(RTCSessionDescription(**answer_data))

        except asyncio.TimeoutError:
            self._notify_status("Timeout: No Peer Joined")
            await self.close()
        except Exception as e:
            self._notify_status(f"Error: {str(e)}")
            await self.close()

    async def setup_as_peer(self, timeout: int = 180):
        try:
            offer_data = await asyncio.wait_for(
                self.signaler.wait_for_signal("offer"),
                timeout=timeout
            )
            await self.pc.setRemoteDescription(RTCSessionDescription(**offer_data))

            answer = await self.pc.createAnswer()
            await self.pc.setLocalDescription(answer)
            await self._wait_for_ice()

            if not self.pc:
                return

            await self.signaler.post_signal("answer", {
                "sdp": self.pc.localDescription.sdp,
                "type": "answer"
            })
        except asyncio.TimeoutError:
            self._notify_status("Timeout: Room Not Found")
            await self.close()
        except Exception as e:
            if "AUTH_FAILED" in str(e):
                self._notify_status(f"Error: Incorrect Password")
            elif isinstance(e, asyncio.TimeoutError):
                self._notify_status("Timeout: Room Not Found")
            else:
                self._notify_status(f"Error: {str(e)}")
            await self.close()

    async def _wait_for_ice(self):
        while self.pc and self.pc.iceGatheringState != "complete":
            await asyncio.sleep(0.1)

    def _notify_status(self, message: str):
        if self.on_status_callback and message != self.last_status:
            self.last_status = message
            self.on_status_callback(message)

    def send_message(self, text: str):
        if self.channel and self.channel.readyState == "open":
            self.channel.send(text)

    async def close(self):
        if self.channel:
            try:
                self.channel.close()
            except:
                pass
            self.channel = None

        if self.pc:
            try:
                await self.pc.close()
            except:
                pass
            self.pc = None

        if self.signaler:
            try:
                await self.signaler.close()
            except:
                pass
