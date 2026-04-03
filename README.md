<p align="center">
    <img alt="pypeer Logo" src="https://raw.githubusercontent.com/j-ncel/pypeer/refs/heads/main/docs/pypeer.png" width="400" />
</p>

<p align="center">
    <b>A Python Terminal-based P2P Messaging Application.</b>
</p>

`pypeer` is a lightweight TUI application that enables direct, encrypted communication between peers. It leverages **WebRTC** for decentralized data transfer and **Firebase RTDB** as an ephemeral signaling server.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/P2P-WebRTC-orange.svg" alt="Technology">
</p>

<p align="center">
  <table align="center">
    <tr>
      <td align="center">
        <b>Start Screen</b><br>
        <img alt="pypeer home" src="https://raw.githubusercontent.com/j-ncel/pypeer/main/docs/start.png" width="400" />
      </td>
      <td align="center">
        <b>Host Setup</b><br>
        <img alt="pypeer host" src="https://raw.githubusercontent.com/j-ncel/pypeer/main/docs/host.png" width="400" />
      </td>
    </tr>
    <tr>
      <td align="center">
        <b>Join Room</b><br>
        <img alt="pypeer join" src="https://raw.githubusercontent.com/j-ncel/pypeer/main/docs/join.png" width="400" />
      </td>
      <td align="center">
        <b>Messaging Screen</b><br>
        <img alt="pypeer messaging" src="https://raw.githubusercontent.com/j-ncel/pypeer/main/docs/messaging.png" width="400" />
      </td>
    </tr>
  </table>
</p>

### Installation & Usage

<div align="left">
<table style="border-collapse: collapse; border-spacing: 0; width: 500px;">
<tr>
<td style="background-color: #21252b; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px;">
<span style="color: #ff5f56;">●</span>
<span style="color: #ffbd2e;">●</span>
<span style="color: #27c93f;">●</span>
</td>
</tr>
<tr>
<td style="background-color: #1e1e1e; padding: 20px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; font-family: 'Fira Code', monospace; font-size: 16px;">
<span style="color: #27c93f;">$</span>
<span style="color: #ffffff;">pip install</span>
<span style="color: #e06c75;">pypeer</span>
</td>
</tr>
</table>
</div>

After installation launch the application by simply typing:

<div align="left">
<table style="border-collapse: collapse; border-spacing: 0; width: 500px;">
<tr>
<td style="background-color: #21252b; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px;">
<span style="color: #ff5f56;">●</span>
<span style="color: #ffbd2e;">●</span>
<span style="color: #27c93f;">●</span>
</td>
</tr>
<tr>
<td style="background-color: #1e1e1e; padding: 20px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; font-family: 'Fira Code', monospace; font-size: 16px;">
<span style="color: #27c93f;">$</span>
<span style="color: #ffffff;">pypeer</span>
</td>
</tr>
</table>
</div>

**How to use:**

1.  **Host a Room:** Click "Host", set a password, and share the generated 6-character Room ID.
2.  **Join a Room:** Click "Join", enter the Room ID and the password.
3.  **Chat:** Once connected, start messaging.

---

### How it Works

1.  **Encrypted Signaling:** Before a direct connection is established, peers must exchange handshake metadata (SDP and ICE candidates). `pypeer` uses `Firebase RTDB` as an ephemeral signaling server that acts as a temporary bulletin board.
    - **Key Derivation:** A 32-byte key is derived using `SHA-256` from a combination of the `Room ID` and the `User Password`.
    - **Layered Security:** The connection metadata is cryptographically unreadable to anyone even the data provider that do not have the specific Room ID and Password.
      - **Compression:** Raw SDP strings are compressed using `zlib` to reduce payload size and obfuscate data structure.
      - **Encryption:** Compressed data is encrypted via **AES-128 (Fernet)**,ensuring that only the intended peer can decrypt the handshake.

2.  **The WebRTC Handshake:** Once the encrypted metadata is exchanged, the terminals move from "talking to the cloud" to "talking to each other":
    - **Firewall Navigation:** The app uses Google's STUN servers to navigate through home routers and firewalls and determine the best route between peers.
    - **Encrypted DataChannel:** A dedicated tunnel is established between peers. Unlike traditional TCP sockets, SCTP over WebRTC provides native encryption, reliability, and ordered delivery without the need for a central server.

3.  **Secure Direct Messaging:** Once connected, the chat enters a serverless state:
    - **Zero-Trace Handshake:** The signaling data on Firebase RTDB is deleted. The peers remain connected directly, ensuring that no trace of the handshake remains on the cloud.
    - **P2P Memory-to-Memory:** Messages are sent directly between terminal memories. No history is stored on any server, and no middleman can intercept the traffic once the P2P tunnel is established.
    - **Volatile Sessions:** Your messages exist only as long as your terminal window is open. Once you quit, the session is wiped from your RAM.

4.  **Automated Cleanup:** To maintain a a clean and secure signaling bridge, `pypeer` employs a two-tier cleanup strategy:
    - **Host-Led Deletion:** Under normal conditions, the host cleans up the signaling metadata as soon as the handshake is complete.
    - **GitHub Action Janitor:** As a failsafe, a scheduled GitHub Action acts as a "Janitor," running every hour to automatically purge any stale or abandoned rooms left behind by interrupted connections.

### Tech Stack

| Core Components  | Implementation                                       | Purpose                                                |
| :--------------- | :--------------------------------------------------- | :----------------------------------------------------- |
| **TUI Engine**   | [Textual](https://github.com/textualize/textual/)    | Powers the modern, responsive terminal interface.      |
| **P2P Protocol** | [aiortc](https://github.com/aiortc/aiortc)           | Handles WebRTC stack, ICE gathering, and DataChannels. |
| **Signaling**    | [Firebase RTDB](https://firebase.google.com/)        | Used as a temporary, real-time bridge for handshakes.  |
| **Encryption**   | [Fernet (AES)](https://github.com/pyca/cryptography) | Encrypts signaling payloads so metadata never leaks.   |
| **Async Core**   | `asyncio`                                            | Manages concurrent networking and UI updates.          |

## License

This project is licensed under the **MIT License**.
