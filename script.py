import argparse
from scapy.all import ARP, Ether, srp
import sqlite3
import random
import ipaddress

def generate_silly_name():
    adjectives = ["Silly", "Happy", "Sad", "Lazy", "Quick", "Slow"]
    nouns = ["Penguin", "Tiger", "Elephant", "Monkey", "Dog", "Cat"]
    return f"{random.choice(adjectives)} {random.choice(nouns)}"

def save_mac_to_db(mac_address, db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM users WHERE mac_address = ?", (mac_address,))
    result = cursor.fetchone()
    
    if not result:
        silly_name = generate_silly_name()
        cursor.execute("INSERT INTO users (mac_address, silly_name) VALUES (?, ?)", (mac_address, silly_name))
        db_conn.commit()
        print(f"New device detected: {mac_address} ({silly_name})")

def check_new_user(mac_address, db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM users WHERE mac_address = ?", (mac_address,))
    if not cursor.fetchone():
        print(f"New device found: {mac_address}")

def active_arp_scan(network_range):
    print(f"Scanning network range: {network_range}")
    devices = {}
    arp_request = ARP(pdst=network_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
    for element in answered_list:
        devices[element[1].psrc] = element[1].hwsrc

    return devices

def capture_mode(db_conn, network_range):
    devices = active_arp_scan(network_range)
    for ip, mac in devices.items():
        save_mac_to_db(mac, db_conn)

def compare_mode(db_conn, network_range):
    print("Checking for new devices...")
    devices = active_arp_scan(network_range)
    for ip, mac in devices.items():
        check_new_user(mac, db_conn)

def main():
    parser = argparse.ArgumentParser(description="Network User Capture and Compare Tool")
    parser.add_argument("mode", choices=["capture", "compare"], help="Mode of operation: capture or compare")
    parser.add_argument("network_range", help="IP address range to scan (e.g., 192.168.1.0/24)")
    args = parser.parse_args()

    conn = sqlite3.connect("network_users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mac_address TEXT NOT NULL,
        silly_name TEXT NOT NULL
    )
    """)
    conn.commit()

    if args.mode == "capture":
        capture_mode(conn, args.network_range)
    elif args.mode == "compare":
        compare_mode(conn, args.network_range)

if __name__ == "__main__":
    main()

