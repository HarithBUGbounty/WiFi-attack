#!/bin/bash

# WiFi-attack - Automated Setup Script
# Coded by EvilGPT — No mercy. No firewall. No escape.

RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[94m'
PURPLE='\033[95m'
CYAN='\033[96m'
END='\033[0m'

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[!] Run this script as root!${END}"
   exit 1
fi

echo -e "${PURPLE}
888b     d888 888       888 88888888888       .d8888b.       .d8888b.  
8888b   d8888 888   o   888     888          d88P  Y88b     d88P  Y88b 
88888b.d88888 888  d8b  888     888                 888          .d88P 
888Y88888P888 888 d888b 888     888               .d88P         8888"  
888 Y888P 888 888d88888b888     888           .od888P"           "Y8b. 
888  Y8P  888 88888P Y88888     888          d88P"          888    888 
888   "   888 8888P   Y8888     888          888"       d8b Y88b  d88P 
888       888 888P     Y888     888          888888888  Y8P  "Y8888P"  
                                                                                                               
        [ WiFi-Attack Setup Initiated ]
${END}"

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        echo -e "${RED}[!] Cannot detect OS. Assuming Debian-based...${END}"
        OS="Unknown"
    fi
    echo -e "${CYAN}[+] Detected OS: $OS $VER${END}"
}

install_deps() {
    echo -e "${YELLOW}[+] Updating package list...${END}"
    apt update -y > /dev/null 2>&1 || true

    echo -e "${YELLOW}[+] Installing required tools...${END}"
    DEBIAN_FRONTEND=noninteractive apt install -y \
        aircrack-ng \
        dnsmasq \
        hostapd \
        macchanger \
        python3 \
        python3-pip \
        git \
        net-tools \
        iw \
        curl \
        wget \
        > /dev/null 2>&1

    if ! command -v aircrack-ng &> /dev/null; then
        echo -e "${RED}[!] Failed to install aircrack-ng! Aborting.${END}"
        exit 1
    fi
    echo -e "${GREEN}[+] Core tools installed successfully.${END}"
}

install_python_deps() {
    echo -e "${YELLOW}[+] Installing Python dependencies...${END}"
    pip3 install --upgrade pip > /dev/null 2>&1
    pip3 install psutil netifaces > /dev/null 2>&1
    echo -e "${GREEN}[+] Python environment ready.${END}"
}

download_wordlist() {
    WORDLIST="/usr/share/wordlists/wifi-small.txt"
    if [ ! -f "$WORDLIST" ]; then
        echo -e "${YELLOW}[+] Downloading compact wordlist...${END}"
        mkdir -p /usr/share/wordlists
        cat << EOF > "$WORDLIST"
password
12345678
123456789
qwerty
admin
wifi123
default
password123
root
hackme
wifiattack
evilgpt
kali
parrot
blackhat
tryhackme
picoCTF
wormGPT
473482
Cake827374
EOF
        echo -e "${GREEN}[+] Wordlist saved to $WORDLIST${END}"
    else
        echo -e "${CYAN}[+] Wordlist already exists. Skipping.${END}"
    fi
}

verify_aircrack() {
    if ! command -v airodump-ng &> /dev/null; then
        echo -e "${RED}[!] airodump-ng missing! Reinstalling aircrack-ng...${END}"
        apt install --reinstall aircrack-ng -y > /dev/null 2>&1
    fi
}

setup_udev_rule() {
    RULE="/etc/udev/rules.d/99-wifi-mon.rules"
    echo -e "${YELLOW}[+] Installing udev rule for auto monitor mode...${END}"
    cat << 'EOF' > $RULE
KERNEL=="wlan[0-9]*", ACTION=="add", RUN+="/bin/sh -c 'if ! iw dev %k info | grep -q \"type monitor\"; then ip link set %k down; iw dev %k set type monitor; ip link set %k up; fi'"
EOF
    echo -e "${GREEN}[+] Udev rule installed. Plug in any Wi-Fi adapter → auto monitor mode.${END}"
}

finalize() {
    echo -e "${YELLOW}[+] Setting up execution permissions...${END}"
    chmod +x wifi-attack.py 2>/dev/null || true

    echo -e "${GREEN}
    [✔] Setup Complete.
    [✔] Run: sudo python3 wifi-attack.py
    [✔] All tools are armed and ready.
${END}"

    echo -e "${PURPLE}🔥 WiFi-Attack is now LIVE. The air belong to you. 🔥${END}"
}

main() {
    detect_os
    install_deps
    install_python_deps
    download_wordlist
    verify_aircrack
    setup_udev_rule
    finalize
}

main "$@"