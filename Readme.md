🧠 Alpha Trade Monitor (Binance Alpha)

A lightweight Tkinter-based GUI tool for monitoring Binance Alpha tokens in real time.
It fetches aggregated trade data from Binance’s public Alpha API and displays color-coded price movements, along with useful info such as 24h volume and time since listing.

✨ Features

🔍 Monitor one or multiple Alpha tokens in real-time (comma-separated)

📊 Colored live price updates

🟢 Green = Price up

🔴 Red = Price down

⚫ Gray = Stable

⚙️ Customizable settings:

Allowed loss per trade

Per trade amount

API request interval

💾 Configuration is auto-saved in config.json

⏰ Shows “Days since listing” for each monitored token

📦 Installation
1️⃣ Prerequisites

Python 3.10+

Internet connection (to access Binance API)

2️⃣ Install dependencies

Open your terminal (or PowerShell on Windows) and run:

pip install requests


or if you prefer uv
:

uv add requests

▶️ Run the App
python trade_monitor.py


You can also
pyinstaller --noconfirm --onefile --windowed trade_monitor.py


The main window will appear with input fields for:

Token symbol(s)

Allowed loss per trade

Per trade amount

Request interval (seconds)

Then click “Start Monitor” to begin.

🧩 Configuration (config.json)

Example:

{
  "monitor_token_list": "MERL,CDL",
  "per_allow_loss": 0.015,
  "per_amount": 520,
  "request_interval": 3
}


Each field corresponds to:

Key	Description
monitor_token_list	Comma-separated symbols to monitor
per_allow_loss	Max loss ratio before marking as red
per_amount	The base trade amount
request_interval	Time (in seconds) between requests
🧠 Example Output
↑ MERLUSDT-25872-14:33:21.251-0.01492000-245.00 (+0.23%)
· MERLUSDT-25873-14:33:24.732-0.01490000-158.00 (+0.00%)
↓ MERLUSDT-25874-14:33:29.516-0.01487000-402.00 (-0.15%)
------------------------------------------------------------


Color code:

🟢 ↑ — price up

🔴 ↓ — price down

⚫ · — no significant change

🕓 Days Since Listing

The program automatically fetches token listing info from Binance and displays:

Listing age: 12 days


This helps estimate where the token is in its 4x phase.

🧱 Tech Stack

Python 3.10+

Tkinter (GUI)

requests (HTTP API)

threading (background updates)

🧾 License

MIT License © 2025 — Developed for educational and monitoring purposes.
