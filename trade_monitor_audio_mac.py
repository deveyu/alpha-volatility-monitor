import time
import json
from datetime import datetime
import requests
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import os

def play_beep():
    os.system('afplay /System/Library/Sounds/Glass.aiff')

CONFIG_FILE = "config.json"

# ================= 默认配置 =================
default_config = {
    "monitor_token_list": "MERL",
    "per_allow_loss": 0.015,
    "per_amount": 520,
    "request_interval": 3
}

# ================= 加载配置 =================
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    config = default_config.copy()

# ================= Tkinter UI =================
class TradeMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alpha波动监控")
        self.root.geometry("650x650")

        # 配置输入框
        frame = tk.Frame(root)
        frame.pack(pady=5)

        tk.Label(frame, text="Token(s)").grid(row=0, column=0)
        self.token_entry = tk.Entry(frame, width=20)
        self.token_entry.grid(row=0, column=1)
        self.token_entry.insert(0, config.get("monitor_token_list", ""))

        tk.Label(frame, text="每笔允许亏损").grid(row=0, column=2)
        self.loss_entry = tk.Entry(frame, width=10)
        self.loss_entry.grid(row=0, column=3)
        self.loss_entry.insert(0, str(config.get("per_allow_loss", 0.015)))

        tk.Label(frame, text="每次交易额").grid(row=0, column=4)
        self.amount_entry = tk.Entry(frame, width=10)
        self.amount_entry.grid(row=0, column=5)
        self.amount_entry.insert(0, str(config.get("per_amount", 520)))

        tk.Label(frame, text="请求间隔(s)").grid(row=0, column=6)
        self.interval_entry = tk.Entry(frame, width=10)
        self.interval_entry.grid(row=0, column=7)
        self.interval_entry.insert(0, str(config.get("request_interval", 3)))

        # 日志显示区
        self.text_area = ScrolledText(root, state='disabled', font=("Consolas", 10))
        self.text_area.pack(expand=True, fill='both')

        # 控制按钮
        self.start_button = tk.Button(root, text="开始监控", command=self.start_monitor)
        self.start_button.pack(side='left', padx=10, pady=5)

        self.stop_button = tk.Button(root, text="停止监控", command=self.stop_monitor)
        self.stop_button.pack(side='left', padx=10, pady=5)

        # 内部状态
        self.running = False
        self.last_price = 0.0
        self.last_id = 0
        self.symbol = ""
        self.alpha_id = ""

    # ================= 日志输出 =================
    def log(self, msg, color=None):
        self.text_area.configure(state='normal')
        if color:
            self.text_area.insert(tk.END, msg + "\n", color)
            self.text_area.tag_config(color, foreground=color)
        else:
            self.text_area.insert(tk.END, msg + "\n")
        self.text_area.yview(tk.END)
        self.text_area.configure(state='disabled')

    # ================= 保存配置 =================
    def save_config(self):
        cfg = {
            "monitor_token_list": self.token_entry.get(),
            "per_allow_loss": float(self.loss_entry.get()),
            "per_amount": float(self.amount_entry.get()),
            "request_interval": float(self.interval_entry.get())
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

    # ================= 开始监控 =================
    def start_monitor(self):
        try:
            self.monitor_token_list = self.token_entry.get().split(",")
            self.per_allow_loss = float(self.loss_entry.get())
            self.per_amount = float(self.amount_entry.get())
            self.threshold_base = self.per_allow_loss / self.per_amount
            self.request_interval = float(self.interval_entry.get())
        except Exception as e:
            messagebox.showerror("输入错误", str(e))
            return

        self.save_config()
        self.running = True
        self.thread = threading.Thread(target=self.monitor, daemon=True)
        self.thread.start()

    # ================= 停止监控 =================
    def stop_monitor(self):
        self.running = False
        self.log("[已停止监控]", "purple")

    # ================= 监控逻辑 =================
    def monitor(self):
        agg_url = "https://www.binance.com/bapi/defi/v1/public/alpha-trade/agg-trades"
        try:
            token_data = requests.get(
                "https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/cex/alpha/all/token/list"
            )
            token_list = token_data.json()['data']
            monitor_tokens = [
                t for t in token_list
                if t['symbol'].upper() in [m.upper() for m in self.monitor_token_list]
            ]

            if not monitor_tokens:
                self.log("[错误] 未找到监控 token", "red")
                return

            token = monitor_tokens[0]
            self.symbol = f"{token['symbol']}USDT"
            self.alpha_id = token['alphaId']
            self.log(f"距4x结束时间: {30-(datetime.now() - datetime.fromtimestamp(token['listingTime'] / 1000)).days} 天")
            time.sleep(1)
            self.log(f"开始监控 {self.symbol} 聚合成交数据...\n")

        except Exception as e:
            self.log(f"[错误] {e}", "red")
            return

        last_movement_time = time.time()  # ✅ 新增：记录上一次波动的时间

        while self.running:
            try:
                params = {"symbol": f"{self.alpha_id}USDT"}
                if self.last_id:
                    params['fromId'] = self.last_id

                data = requests.get(agg_url, params=params, timeout=10).json().get('data', [])
                if not data:
                    time.sleep(2)
                    continue

                movement_detected = False  # ✅ 是否有显著波动
                for i, trade in enumerate(data):
                    trade_id = trade['a']
                    price = float(trade['p'])
                    qty = float(trade['q'])
                    ts = trade['T']

                    formatted_time = datetime.fromtimestamp(ts / 1000).strftime("%H:%M:%S.") + f"{int(ts % 1000):03d}"
                    delta = (price - self.last_price) / self.last_price if self.last_price != 0 else 0

                    if delta > self.threshold_base:
                        tag = f"↑ {formatted_time}-{self.symbol}-{trade_id}-{price:.8f}-{qty:.2f} ({delta:+.5%})"
                        color = "blue"
                        movement_detected = True
                    elif delta < -self.threshold_base:
                        tag = f"↓ {formatted_time}-{self.symbol}-{trade_id}-{price:.8f}-{qty:.2f} ({delta:+.5%})"
                        color = "orange"
                        movement_detected = True
                    else:
                        tag = f"· {formatted_time}-{self.symbol}-{trade_id}-{price:.8f}-{qty:.2f} ({delta:+.5%})"
                        color = "black"

                    self.log(tag, color)
                    self.last_price = price

                    if i == len(data) - 1:
                        self.last_id = trade_id + 1
                        self.log("-" * 80, "grey")

                # ✅ 如果本轮检测有显著波动，则更新时间
                if movement_detected:
                    last_movement_time = time.time()
                else: 
                    # ✅ 超过10秒没有波动 -> 播放 提示音
                    if time.time() - last_movement_time > 10:
                        play_beep()
                        self.log("[提示] 市场平静超过 10 秒", "grey")
                        last_movement_time = time.time()  # 重置计时

                time.sleep(self.request_interval)

            except requests.RequestException as e:
                self.log(f"[网络异常] {e}", "magenta")
                time.sleep(5)
            except Exception as e:
                self.log(f"[错误] {e}", "red")
                time.sleep(5)


if __name__ == "__main__":
    root = tk.Tk()
    app = TradeMonitorApp(root)
    root.mainloop()
