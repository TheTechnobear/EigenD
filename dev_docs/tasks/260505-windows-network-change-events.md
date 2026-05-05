# Task: Implement Network Change Event Monitoring on Windows

Date: 2026-05-05
File: `piagent/src/pia_udpnet_windows.cpp`
Function: `pia::udpnet_t::impl_t::setup_kev()` (around line 867)

## Background

`setup_kev()` is responsible for setting up a socket/kernel-event monitor so that
EigenD can react to runtime network topology changes (adapter arrival/removal,
IP address assignment).  On macOS/Linux a kernel-event socket (`PF_ROUTE` /
`RTMGRP_IPV4_IFADDR`) is used.  On Windows the body is an empty stub.

## Current State

```cpp
void setup_kev()
{
    // todo: set socket filter for network change events.
#pragma message ("      ****  Needs fixing for windows  network change events ****")
}
```

`kevsock_` is created but never configured.  `process_monitor()` always returns
`false`, so network topology changes are silently ignored for the lifetime of the
process.

## Required Behaviour

- Subscribe `kevsock_` to network address-change notifications.
- When `process_monitor()` is called (already in the select loop) and the socket
  is readable, trigger a re-scan of interfaces via `scan()`.

## Proposed Implementation

Use `WSAIoctl(SIO_ADDRESS_LIST_CHANGE)` to arm the socket for address-list
changes, then re-arm after each event (the notification is one-shot).

```cpp
void setup_kev()
{
    DWORD dummy = 0;
    // Arm the socket for address-list-change notification (one-shot, non-blocking).
    if (WSAIoctl(kevsock_.fd, SIO_ADDRESS_LIST_CHANGE,
                 nullptr, 0, nullptr, 0, &dummy,
                 nullptr, nullptr) == SOCKET_ERROR)
    {
        int err = WSAGetLastError();
        // WSAEWOULDBLOCK is expected when no change is pending; any other error is real.
        if (err != WSAEWOULDBLOCK)
            pic::logmsg() << "setup_kev WSAIoctl failed: " << err;
    }
}
```

And update `process_monitor()` to re-arm and re-scan:

```cpp
virtual bool process_monitor(fd_set *r)
{
    if (!FD_ISSET(kevsock_.fd, r)) return false;
    pic::logmsg() << "network change event – rescanning interfaces";
    scan();
    setup_kev();   // re-arm for next event
    return true;
}
```

## Alternative: `NotifyAddrChange()` (async, thread-based)

`NotifyAddrChange()` is simpler but uses a separate thread or overlapped I/O,
which does not integrate cleanly with the existing `select`-based event loop.
`SIO_ADDRESS_LIST_CHANGE` on the existing socket is therefore preferred.

## Notes

- `populate_monitor()` already adds `kevsock_.fd` to the `fd_set`; no change needed there.
- Remove the `#pragma message` and the `//todo` comment once implemented.
- Depends on `scan()` being implemented first (see task `260505-windows-network-interface-scan.md`).

## Risk

- Low–Medium implementation risk.
- No new dependencies or linker changes required (`WSAIoctl` is in `ws2_32`).
- Re-arming is one-shot; a missed re-arm after an error would simply stop monitoring — not crash.
- No impact on macOS/Linux builds.
