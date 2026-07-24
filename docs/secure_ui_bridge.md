# Secure Local UI Bridge

Status: implemented foundation on `feature/NELA-safety-spine-routing`.

## Purpose

The production WebView UI will eventually need a local bridge to talk to NELA's
runtime. That bridge must not become an unauthenticated local RPC surface.

## Current Foundation

`ui.secure_bridge.SecureLocalBridge` provides:

- Unix domain socket transport.
- Per-launch authentication token.
- Expected-origin verification.
- Token comparison with constant-time comparison.
- Automatic socket cleanup on close.

The bridge does not bind to TCP and never exposes `0.0.0.0`.

## Authority Boundary

The UI client is not trusted as the source of authority. Even a valid bridge
request must still pass through the Permission Engine before any Agent executes.

## Public API

- `start()`: creates the socket and launch token.
- `authorize_request(token, origin)`: validates request credentials.
- `close()`: closes transport and removes the socket.
- `transport`: returns the socket path and expected origin for the current run.

## Future Integration

Before replacing the temporary Tkinter shell with a WebView host, the host must:

- Receive the launch token out-of-band from the runtime.
- Use only the Unix socket path supplied for that launch.
- Send the expected origin.
- Treat permission decisions from the backend as authoritative.
