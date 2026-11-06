# ping_ip.py — TCP reachability check via netutils

A minimal script that checks TCP reachability to a target IP/hostname and port using `netutils.ping.tcp_ping`. This is a TCP connect probe, not an ICMP echo "ping".

## File Location

- Script: `AI/networking/ping_ip.py`

## Prerequisites

- Python 3.10-3.14
- A virtual environment (recommended)

## Installation

Install `netutils` into your Python environment:

```bash
python3 --version

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install netutils
```

Verify the install:

```bash
python -c "import netutils; print(netutils.__version__)"
```

## What the Script Does

- Imports `tcp_ping` from `netutils.ping`
- Attempts a TCP connection to the specified host and port with a timeout
- Prints whether the target is "alive" (TCP connect succeeded) or "not reachable"

## Configuration

Edit the script to configure a real target and parameters:

- Replace the placeholder string `"[IP_ADDRESS]"` with a real IPv4 address or a hostname (without brackets), for example `"192.0.2.10"` or `"example.com"`.
- Optionally adjust:
  - `port` (default shown in examples: `80`)
  - `timeout` in seconds (default shown in examples: `1`)

Recommended minimal structure:

```python
from netutils.ping import tcp_ping

def main():
    target_ip = "example.com"  # set to your target
    port = 80
    timeout = 1  # seconds

    try:
        is_alive = tcp_ping(target_ip, port=port, timeout=timeout)
    except (ConnectionRefusedError, OSError, ValueError):
        # Treat immediate refusal, DNS failure, bad args, etc. as not reachable
        is_alive = False

    print(f"{target_ip}:{port} is {'alive' if is_alive else 'not reachable'}.")

if __name__ == "__main__":
    main()
```

Notes for the existing script:

- Ensure `target_ip` is defined before using it in `print` statements.
- Prefer `if is_alive:` over `if is_alive == True`.

## Usage

From the project root (or the `AI/networking` directory):

```bash
source .venv/bin/activate  # if using a venv
python AI/networking/ping_ip.py
```

Expected output:

- `<target>:<port> is alive.` when TCP connect succeeds
- `<target>:<port> is not reachable.` on timeout or handled failure

## Examples

- Quick check for HTTPS (443):

```bash
python - <<'PY'
from netutils.ping import tcp_ping
print(tcp_ping("example.com", port=443, timeout=2))
PY
```

- Run the script after setting `target_ip` inside the file:

```bash
python AI/networking/ping_ip.py
```

## Important Notes and Limitations

- Not ICMP: This is a TCP reachability test, not an ICMP "ping".
- IPv4 only: `tcp_ping` uses IPv4 sockets (`AF_INET`). IPv6 targets are not supported by this function.
- Return semantics:
  - `True`: TCP connect succeeded.
  - `False`: Only for `socket.timeout`.
  - Exceptions: Closed port (`ConnectionRefusedError`), DNS issues (`socket.gaierror`), invalid inputs, etc. Catch and treat as "not reachable" if desired.
- Choose a reasonable port: Use a port expected to be open on the target (443, 22, etc.). Closed ports often raise `ConnectionRefusedError`; filtered ports commonly time out and yield `False`.

## Troubleshooting

- `NameError: target_ip is not defined`
  - Define `target_ip` before printing its value.
- `ConnectionRefusedError`
  - The target is reachable but the port is closed; catch and treat as "not reachable" if that matches your criteria.
- DNS resolution failures (`socket.gaierror`)
  - Ensure the hostname is valid or use a correct IPv4 address.
- Frequent timeouts
  - Increase `timeout` or verify firewall/network ACLs along the path.
- Need ICMP echo ping
  - `tcp_ping` is TCP-based. For ICMP, use an ICMP-capable library (for example, `icmplib`, `ping3`) or invoke the system `ping` binary with `subprocess` and appropriate privileges.
