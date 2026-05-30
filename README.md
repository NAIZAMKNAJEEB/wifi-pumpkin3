# NYX WiFiPumpkin3 Dashboard

A premium, cyber-themed web interface for the `wifipumpkin3` framework. This project streamlines WiFi security testing with a responsive HUD, real-time log streaming, and automated attack controls.

## 🚀 Features

- **Cyber HUD Dashboard**: A modern, glassmorphic interface for real-time reconnaissance.
- **Engine Control**: One-click Launch/Stop for attack sequences.
- **Live Logs**: Integrated terminal for monitoring subprocess output and system states.
- **Cross-Platform Simulation**: Built-in simulation mode for Windows, allowing UI testing and development without Linux hardware.
- **Settings HUD**: Easy configuration of SSIDs, interfaces, and channels.

## 🛠️ Installation

### Prerequisites
- Python 3.10 or higher.
- (Optional) Linux environment for full hardware functionality (airmon-ng, hostapd, etc.).

### Setup Steps

1. **Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd "wifi pumpkin3"
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the Environment**
   - **Windows**: `.venv\Scripts\activate`
   - **Linux/macOS**: `source .venv/bin/activate`

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Dashboard**
   ```bash
   python manage.py runserver
   ```

6. **Access the HUD**
   Open your browser and navigate to `http://127.0.0.1:8000`.

## ⚙️ Configuration

- **IDE Support**: If using VS Code, ensure you select the `.venv` interpreter (`Ctrl+Shift+P` -> `Python: Select Interpreter`) to resolve module dependencies.
- **Simulation Mode**: On Windows, the engine automatically enters simulation mode, logging actions without executing hardware-level commands.

## ⚖️ Disclaimer

This tool is for educational purposes and authorized security auditing only. Unauthorized use on networks you do not own is strictly prohibited.
