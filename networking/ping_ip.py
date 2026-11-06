from netutils.ping import tcp_ping

network_inventory = [
    {"ip": "192.168.1.1", "device": "Core-Switch-01", "port": 22},
    {"ip": "192.168.1.254", "device": "Edge-Router-01", "port": 22},
    {"ip": "8.8.8.8", "device": "External-DNS", "port": 53},
]

print("Starting network ping tests...\n")

for device in network_inventory:
    status = tcp_ping(ip=device["ip"], port=device["port"], timeout=1)

    result_str = "ONLINE" if status else "OFFLINE"
    print(f"Device: {device['device']} | IP: {device['ip']} | Port: {device['port']} | Status: {result_str}")