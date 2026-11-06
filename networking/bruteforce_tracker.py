import ipaddress
import re

# Import core elements from the Textual framework
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, DataTable, Static, Label

# --- MOCK INFRASTRUCTURE SECURITY DATA ---
server_logs = [
    "2026-11-06 21:00:01 - SUCCESS LOGIN - User: admin - IP: 192.168.1.50",
    "2026-11-06 21:01:14 - FAILED LOGIN - User: root - IP: 198.51.100.42",
    "2026-11-06 21:01:20 - FAILED LOGIN - User: admin - IP: 198.51.100.42",
    "2026-11-06 21:02:05 - FAILED LOGIN - User: guest - IP: 203.0.113.15",
    "2026-11-06 21:02:18 - FAILED LOGIN - User: root - IP: 198.51.100.42",
    "2026-11-06 21:03:40 - SUCCESS LOGIN - User: engineer - IP: 10.0.5.12",
    "2026-11-06 21:04:11 - FAILED LOGIN - User: database - IP: 192.168.1.99",
]

threat_blacklist = {
    "Malicious_Botnet_A": "198.51.100.0/22",
    "Known_Ransomware_Group": "203.0.113.0/24"
}

def is_in_cidr(ip: str, cidr: str) -> bool:
    """Return True if ip is within cidr; guard malformed inputs and use strict=False."""
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        return False

class SecurityDashboard(App):
    """An interactive Cybersecurity monitoring dashboard built with Textual."""
    
    # CSS styles embedded directly into the application layout
    CSS = """
    Screen {
        background: #121820;
    }
    #sidebar {
        width: 35;
        background: #1c2331;
        border-right: solid #2c3e50;
        padding: 1 2;
    }
    #main-content {
        padding: 1 2;
    }
    .panel-title {
        text-style: bold;
        color: #00ffcc;
        margin-bottom: 1;
    }
    .alert-text {
        color: #ff3333;
        text-style: bold;
    }
    .safe-text {
        color: #33ff33;
    }
    """
    
    # Bind an exit hotkey to the application footer navigation
    BINDINGS = [("q", "quit", "Exit Dashboard")]

    def compose(self) -> ComposeResult:
        """Defines the visual UI layout hierarchy of the application."""
        yield Header(show_clock=True)
        
        with Horizontal():
            # Left Column: Threat Intelligence Sidebar Panel
            with Vertical(id="sidebar"):
                yield Label("THREAT INTEL BLOCKS", classes="panel-title")
                for group, subnet in threat_blacklist.items():
                    yield Static(f"• [cyan]{group}[/cyan]\n  Scope: {subnet}\n")
                
                yield Label("\nSYSTEM STATUS", classes="panel-title")
                yield Static("Engine: [bold green]ONLINE[/bold green]\nUptime: 100%\nMode: Live Analytics")
            
            # Right Column: Main Log Metrics Viewer Table Workspace
            with Vertical(id="main-content"):
                yield Label("REAL-TIME LOG PARSING ENGINE", classes="panel-title")
                yield DataTable()
                
        yield Footer()

    def on_mount(self) -> None:
        """Lifecycle hook executed instantly when the app loads onto the screen."""
        table = self.query_one(DataTable)
        
        # Configure columns inside our data view grid array matrix
        table.add_columns("Timestamp", "Event Status", "Attacker IP", "Threat Match")
        
        # Parse logs and populate row variables dynamically using Netutils logic
        for log in server_logs:
            # Basic log string token extraction
            parts = log.split(" - ")
            timestamp = parts[0]
            event_type = parts[1]
            
            # Identify the IP target from raw line string
            ip_match = re.search(r"IP:\s+(\S+)", parts[2])
            src_ip = ip_match.group(1) if ip_match else "Unknown"
            
            # Default state evaluations
            threat_status = "[gray]N/A (Success)[/gray]"
            
            if "FAILED LOGIN" in event_type:
                event_display = "[bold red]FAILED LOGIN 🚨[/bold red]"
                threat_status = "[green]Clear (Public IP)[/green]"

                # Validate IP and cross reference against blacklist safely
                if src_ip == "Unknown":
                    threat_status = "[yellow]Missing IP[/yellow]"
                else:
                    try:
                        ipaddress.ip_address(src_ip)
                        for group_name, subnet in threat_blacklist.items():
                            if is_in_cidr(src_ip, subnet):
                                threat_status = f"[bold red]MATCH: {group_name}[/bold red]"
                                break
                    except ValueError:
                        threat_status = "[yellow]Invalid IP token[/yellow]"
            else:
                event_display = "[green]SUCCESS[/green]"
                
            table.add_row(timestamp, event_display, src_ip, threat_status)

if __name__ == "__main__":
    app = SecurityDashboard()
    app.run()
