# WiFi-attack
## ⚠️ Disclaimer & Legal Notice

**IMPORTANT:** This tool is developed and published strictly for **educational purposes, academic research, and authorized penetration testing / security auditing**. 

* **Authorized Use Only:** You must only use this tool against networks and infrastructure that you own, or where you have received explicit, written permission from the legal owner.
* **No Liability:** The author(s) assume absolutely no liability and are not responsible for any misuse, damage, or legal consequences caused by this software.
* **Compliance:** By downloading, installing, or using this tool, you agree to comply with all applicable local, national, and international computer crime and cybersecurity laws.

# Supported OS (Kali linux, Termux Root, Nethunter OS)

## Quick Installation

Get the tool up and running quickly by executing the cmd in your terminal (MUST ROOT)

# Clone the repository
git clone https://github.com/HarithBUGbounty/WiFi-attack.git

# Navigate into the project folder
cd WiFi-attack
============================================================
# For kali linux user install this module:
sudo apt update && sudo apt install python3-scapy aircrack-ng wireless-tool hostapd dnsmasq -y

# Make the setup script executable and run it (Kali-Linux & NetHunter & Termux)
chmod +x setup.sh && sudo ./setup.sh

# Run the tool
python3 WiFi-attack.py
