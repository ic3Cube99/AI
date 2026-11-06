# Brute-Force Tracker — Log Triage Demo

This document describes the demo script `AI/networking/bruteforce_tracker.py`, which parses sample authentication logs, highlights potential brute‑force attempts, and cross‑references attacker IPs against a local threat blacklist. Output is rendered with the Textual TUI framework.

Important: This is a demo for local experimentation and presentation. It is not a production SIEM.

## Features

- Parses in‑memory sample log lines and extracts IPs from `IP: <value>` tokens.
- Counts failed attempts per source IP and visually flags those over a threshold.
- Checks attacker IPs against a configurable blacklist of CIDR subnets.
- Presents results in an interactive terminal UI (Textual) with a sidebar and a data table.

## Requirements

- Python 3.10–3.14
- Dependencies:
  - `textual`
  - `rich` (installed with Textual, but safe to install explicitly)
  - `netutils` (optional; the script now uses a stdlib fallback and runs fine without it)

Install into a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install textual rich
# Optional helpers
python -m pip install netutils
```

## Configuration

Edit the following inside `AI/networking/bruteforce_tracker.py`:

- `server_logs`: Replace placeholder `"[IP_ADDRESS]"` tokens with real IPv4/IPv6 addresses if you want meaningful matches. The script now guards against invalid tokens but will label them as “Invalid IP token”.
- `threat_blacklist`: Map threat group names to CIDR strings, for example:

  ```python
  threat_blacklist = {
      "Malicious_Botnet_A": "203.0.113.0/22",
      "Known_Ransomware_Group": "198.51.100.0/24",
  }
  ```

- Visual tweaks: The embedded CSS uses Textual’s style rules. You can adjust colors, padding, and borders in the `CSS` string within the `SecurityDashboard` class.

## Running

From the project root (or within `AI/networking`):

```bash
source .venv/bin/activate   # if using a venv
python AI/networking/bruteforce_tracker.py
```

## What You’ll See

- Left sidebar: Lists the configured threat‑intel CIDRs and a simple status block.
- Main panel: A data table with columns for Timestamp, Event Status, Attacker IP, and Threat Match.
- Failed login rows are highlighted and show either “MATCH: <Group>” for blacklist hits, “Invalid IP token” when the IP token is malformed, or “Clear (Public IP)” when no match is found.

## Script Behavior Notes

- IP parsing: Uses a regex `r"IP:\s+(\S+)"` to capture the first non‑whitespace token after `IP:`.
- IP validation: Tokens are validated with the stdlib `ipaddress.ip_address`. Invalid entries are handled gracefully and annotated.
- Subnet checks: The helper `is_in_cidr(ip, cidr)` wraps `ipaddress.ip_network(cidr, strict=False)` and returns `False` on malformed inputs, avoiding crashes from placeholders.
- UI framework: Built with Textual (`Header`, `Footer`, `DataTable`, `Label`, `Static`) and a simple stylesheet. Bold text uses `text-style: bold` per Textual CSS.

## Limitations

- Placeholder demo data: Replace the `"[IP_ADDRESS]"` tokens to exercise real logic paths.
- No deduplication in table view: Multiple failed events from the same IP will appear as separate rows. This is desirable for an event timeline, but you can aggregate upstream if preferred.
- Minimal parsing: The regex is simplistic and assumes a consistent log format. Extend the parser for varied log sources.
- Static inputs: Logs and blacklist are defined inline; consider externalizing to files or streams for realism.

## Enhancements to Consider

- Add CLI options via `argparse` for `--log-file`, `--blacklist`, and thresholds.
- Enrich table rows with a running failure count per IP and sort by most recent or most severe.
- Add a secondary view for aggregated metrics (e.g., top N sources, time‑bucketed histograms).
- Hook into live sources (journald, syslog, or tail a file) for continuous updates.

## Troubleshooting

- “Invalid IP token” in Threat Match:
  - The captured IP value is not a valid IPv4/IPv6 address (likely a placeholder). Replace with a real address in `server_logs`.
- CSS/style warnings from Textual:
  - Use `text-style: bold` instead of `font-weight: bold`. The script already uses the correct attribute.
- ImportError for Textual:
  - Ensure `textual` is installed in your active environment and that the venv is activated.
