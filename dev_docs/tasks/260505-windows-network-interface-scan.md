# Task: Implement Network Interface Scanning on Windows

Date: 2026-05-05
File: `piagent/src/pia_udpnet_windows.cpp`
Function: `netbase_t::scan()` (around line 834)

## Background

`scan()` is responsible for enumerating available network adapters so EigenD can
bind and route UDP traffic to the correct interface.  On macOS/Linux this is
implemented using platform-specific APIs.  On Windows the body is an empty stub
with an explicit `#pragma message` marker.

## Current State

```cpp
void scan()
{
    pic::logmsg() << "scanning interfaces";
#pragma message ("      ****  Needs fixing for windows  ****")
}
```

Network interfaces are never discovered, so EigenD on Windows cannot select
non-loopback adapters or respond to interface availability.  Loopback (`local_`)
is always present but adapter-bound communication is not functional.

## Required Behaviour

Match the macOS/Linux implementation:
- Enumerate available IPv4 adapters.
- For each adapter, call `create_intf()` / destroy stale ones via `destroy_intf()`.
- Populate `interfaces_` map (key = adapter name, value = IP + `interface_t*`).

## Proposed Implementation

Use `GetAdaptersAddresses()` from `<iphlpapi.h>` (link with `-liphlpapi`).

```cpp
#include <iphlpapi.h>

void scan()
{
    pic::logmsg() << "scanning interfaces";

    ULONG bufLen = 15000;
    std::vector<BYTE> buf(bufLen);
    PIP_ADAPTER_ADDRESSES pAddrs = reinterpret_cast<PIP_ADAPTER_ADDRESSES>(buf.data());

    ULONG ret = GetAdaptersAddresses(AF_INET,
                                     GAA_FLAG_SKIP_ANYCAST | GAA_FLAG_SKIP_MULTICAST,
                                     nullptr, pAddrs, &bufLen);
    if (ret == ERROR_BUFFER_OVERFLOW)
    {
        buf.resize(bufLen);
        pAddrs = reinterpret_cast<PIP_ADAPTER_ADDRESSES>(buf.data());
        ret = GetAdaptersAddresses(AF_INET,
                                   GAA_FLAG_SKIP_ANYCAST | GAA_FLAG_SKIP_MULTICAST,
                                   nullptr, pAddrs, &bufLen);
    }
    if (ret != NO_ERROR)
    {
        pic::logmsg() << "GetAdaptersAddresses failed: " << ret;
        return;
    }

    std::set<std::string> seen;
    for (PIP_ADAPTER_ADDRESSES p = pAddrs; p; p = p->Next)
    {
        if (p->OperStatus != IfOperStatusUp) continue;
        for (PIP_ADAPTER_UNICAST_ADDRESS ua = p->FirstUnicastAddress; ua; ua = ua->Next)
        {
            sockaddr_in *sin = reinterpret_cast<sockaddr_in *>(ua->Address.lpSockaddr);
            unsigned long addr = ntohl(sin->sin_addr.s_addr);
            std::string name(p->AdapterName);
            seen.insert(name);
            auto it = interfaces_.find(name);
            if (it == interfaces_.end())
            {
                interface_t *intf = create_intf(addr, /* loopback= */ false);
                interfaces_[name] = std::make_pair(addr, intf);
            }
        }
    }

    // remove stale interfaces
    for (auto it = interfaces_.begin(); it != interfaces_.end(); )
    {
        if (seen.find(it->first) == seen.end())
        {
            destroy_intf(it->second.second);
            it = interfaces_.erase(it);
        }
        else ++it;
    }
}
```

## Notes

- `create_intf()` signature and semantics must be confirmed against the macOS/Linux path.
- `SConscript` needs `-liphlpapi` added to `LIBS` for the Windows build.
- Remove the `#pragma message` once implemented.

## Risk

- Low–Medium implementation risk.
- Build-time: linker change required (`-liphlpapi`).
- Runtime: adapter enumeration at startup; no crash risk if `GetAdaptersAddresses` fails (logged and returns early).
- No impact on macOS/Linux builds.
