# ========== 股票智能分析系统 ==========
import sqlite3
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import requests
from datetime import datetime

class StockDatabase:
    def __init__(self, db_file='stock_system.db'):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._initialize_db()
    def _initialize_db(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS stocks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL,
            volume INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, last_login DATETIME)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT)''')
        self.conn.commit()
    def insert_stock_data(self, data):
        try:
            self.cursor.execute('''INSERT INTO stocks (symbol, open, high, low, close, volume)
                                 VALUES (?,?,?,?,?,?)''',
                                 (data['symbol'], data['open'], data['high'],
                                  data['low'], data['close'], data['volume']))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"DB insert error: {e}")
            return False
    def get_historical_data(self, symbol, limit=100):
        try:
            self.cursor.execute('''SELECT timestamp, open, high, low, close, volume
                                 FROM stocks WHERE symbol=? ORDER BY timestamp DESC LIMIT ?''', (symbol, limit))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"DB query error: {e}")
            return []
    def user_login(self, username, password):
        hashed = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute('''UPDATE users SET last_login = datetime('now')
                             WHERE username=? AND password=? RETURNING *''', (username, hashed))
        res = self.cursor.fetchone()
        self.conn.commit()
        return res
    def get_setting(self, key):
        self.cursor.execute('SELECT value FROM settings WHERE key=?', (key,))
        r = self.cursor.fetchone()
        return r[0] if r else None
    def save_setting(self, key, value):
        try:
            self.cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)', (key, value))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Save setting error: {e}")
            return False
    def __del__(self):
        if self.conn:
            self.conn.close()

class FinancialDataAPI:
    def __init__(self, db):
        self.db = db
        self.API_BASE = db.get_setting('api_base') or "https://api.example.com/finance"
    def fetch_market_data(self, symbol):
        try:
            resp = requests.get(f"{self.API_BASE}/realtime/{symbol}", timeout=10,
                                headers={'User-Agent': 'StockSystem/5.0'})
            resp.raise_for_status()
            data = resp.json()
            return self._parse_api_data(data, symbol)
        except:
            return self._generate_mock_data(symbol)
    def _parse_api_data(self, data, symbol):
        return {'symbol': symbol, 'open': data['ohlc']['open'], 'high': data['ohlc']['high'],
                'low': data['ohlc']['low'], 'close': data['ohlc']['close'], 'volume': data['volume']['total']}
    def _generate_mock_data(self, symbol):
        base = np.random.uniform(50,200)
        return {'symbol': symbol, 'open': round(base,2), 'high': round(base*1.05,2),
                'low': round(base*0.95,2), 'close': round(base*(1+np.random.uniform(-0.03,0.03)),2),
                'volume': np.random.randint(100000,500000)}

class QuantitativeAnalyzer:
    @staticmethod
    def analyze(df):
        df = df.copy()
        df['date'] = pd.to_datetime(df['timestamp'])
        df.set_index('date', inplace=True)
        df['MA5'] = df['close'].rolling(5).mean()
        df['MA20'] = df['close'].rolling(20).mean()
        df['RSI'] = QuantitativeAnalyzer._calculate_rsi(df['close'])
        df['MACD'], df['Signal'] = QuantitativeAnalyzer._calculate_macd(df['close'])
        df['Bollinger_Upper'], df['Bollinger_Lower'] = QuantitativeAnalyzer._calculate_bollinger(df['close'])
        report = {
            'current_price': df['close'].iloc[-1],
            'price_change_1d': df['close'].pct_change().iloc[-1] * 100,
            'volatility_7d': df['close'].pct_change().std() * np.sqrt(252),
            'volume_change': (df['volume'].iloc[-1] / df['volume'].mean() - 1) * 100,
            'rsi': df['RSI'].iloc[-1],
            'macd_crossover': df['MACD'].iloc[-1] > df['Signal'].iloc[-1],
            'bollinger_position': QuantitativeAnalyzer._get_bollinger_position(df)
        }
        return df, report
    @staticmethod
    def _calculate_rsi(series, period=14):
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.ewm(alpha=1/period).mean()
        avg_loss = loss.ewm(alpha=1/period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    @staticmethod
    def _calculate_macd(series, fast=12, slow=26, signal=9):
        ema_fast = series.ewm(span=fast).mean()
        ema_slow = series.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        return macd, signal_line
    @staticmethod
    def _calculate_bollinger(series, window=20, num_std=2):
        sma = series.rolling(window).mean()
        std = series.rolling(window).std()
        return sma + (std * num_std), sma - (std * num_std)
    @staticmethod
    def _get_bollinger_position(df):
        last = df['close'].iloc[-1]
        upper = df['Bollinger_Upper'].iloc[-1]
        lower = df['Bollinger_Lower'].iloc[-1]
        if last > upper: return "突破上轨"
        if last < lower: return "突破下轨"
        return "轨道区间内"

class TradingDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("智能量化交易终端 v5.0")
        self.geometry("1366x768")
        self.configure(bg='#F5F6F7')
        self.db = StockDatabase()
        self.api = FinancialDataAPI(self.db)
        self.analyzer = QuantitativeAnalyzer()
        self.current_symbol = 'AAPL'
        self.current_user = None
        self._init_login_window()
        self._create_menu()
    def _create_menu(self):
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="导出数据", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="关于", command=lambda: messagebox.showinfo("关于", "股票分析系统 v5.0"))
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        self.config(menu=menu_bar)
    def _init_login_window(self):
        self.login_window = tk.Toplevel(self)
        self.login_window.title("用户登录")
        self.login_window.geometry("300x200")
        self.login_window.grab_set()
        ttk.Label(self.login_window, text="用户名:").pack(pady=5)
        self.username_entry = ttk.Entry(self.login_window)
        self.username_entry.pack(pady=5)
        ttk.Label(self.login_window, text="密码:").pack(pady=5)
        self.password_entry = ttk.Entry(self.login_window, show="*")
        self.password_entry.pack(pady=5)
        ttk.Button(self.login_window, text="登录", command=self._login).pack(pady=10)
    def _login(self):
        user = self.db.user_login(self.username_entry.get(), self.password_entry.get())
        if user:
            self.current_user = user
            self.login_window.destroy()
            self._init_main_ui()
        else:
            messagebox.showerror("错误", "用户名或密码错误")
    def _init_main_ui(self):
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(fill=tk.X)
        ttk.Label(control_frame, text="股票代码:").grid(row=0, column=0)
        self.symbol_entry = ttk.Entry(control_frame, width=8)
        self.symbol_entry.grid(row=0, column=1, padx=5)
        self.symbol_entry.insert(0, self.current_symbol)
        buttons = [('刷新', self.refresh_data), ('实时', self.fetch_realtime),
                   ('分析', self.show_analysis), ('历史', self.show_history)]
        for col, (text, cmd) in enumerate(buttons, start=2):
            ttk.Button(control_frame, text=text, command=cmd).grid(row=0, column=col, padx=2)
        self.data_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=('Consolas',10), height=15)
        self.data_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.figure = plt.Figure(figsize=(10,5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.status_bar = ttk.Label(self, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.update_status("就绪")
        self.refresh_data()
    def update_status(self, msg):
        self.status_bar.config(text=f"状态: {msg}")
    def refresh_data(self):
        self.current_symbol = self.symbol_entry.get().upper()
        self.show_history()
        self.update_status(f"已刷新 {self.current_symbol}")
    def fetch_realtime(self):
        data = self.api.fetch_market_data(self.current_symbol)
        if self.db.insert_stock_data(data):
            self.refresh_data()
            self.update_status(f"实时数据已更新: {self.current_symbol}")
    def show_analysis(self):
        data = self.db.get_historical_data(self.current_symbol)
        if not data:
            messagebox.showwarning("警告", "无可用数据")
            return
        df = pd.DataFrame(data, columns=['timestamp','open','high','low','close','volume'])
        processed_df, report = self.analyzer.analyze(df)
        self.ax.clear()
        processed_df['close'].plot(ax=self.ax, label='收盘价', color='#1f77b4')
        processed_df['MA5'].plot(ax=self.ax, label='5日均线', linestyle='--')
        processed_df['MA20'].plot(ax=self.ax, label='20日均线', linestyle='--')
        processed_df['Bollinger_Upper'].plot(ax=self.ax, color='green', alpha=0.5)
        processed_df['Bollinger_Lower'].plot(ax=self.ax, color='red', alpha=0.5)
        self.ax.fill_between(processed_df.index, processed_df['Bollinger_Upper'],
                             processed_df['Bollinger_Lower'], color='gray', alpha=0.1)
        self.ax.set_title(f"{self.current_symbol} 技术分析")
        self.ax.legend()
        self.canvas.draw()
        win = tk.Toplevel(self)
        win.title("分析报告")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.insert(tk.END, f"当前价格: {report['current_price']:.2f}\n日涨跌幅: {report['price_change_1d']:.2f}%\nRSI: {report['rsi']:.1f}\nMACD信号: {'买入' if report['macd_crossover'] else '卖出'}")
        text.pack(fill=tk.BOTH, expand=True)
    def show_history(self):
        data = self.db.get_historical_data(self.current_symbol)
        self.data_display.delete(1.0, tk.END)
        if not data:
            self.data_display.insert(tk.END, "无历史数据")
            return
        headers = ["时间", "开盘", "最高", "最低", "收盘", "成交量"]
        self.data_display.insert(tk.END, "\t".join(headers) + "\n")
        for rec in reversed(data):
            self.data_display.insert(tk.END, f"{rec[0][:16]}\t{rec[1]:.2f}\t{rec[2]:.2f}\t{rec[3]:.2f}\t{rec[4]:.2f}\t{rec[5]:,}\n")
    def export_csv(self):
        data = self.db.get_historical_data(self.current_symbol)
        if not data:
            messagebox.showwarning("警告", "无数据可导出")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV文件","*.csv")])
        if path:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['时间戳','开盘','最高','最低','收盘','成交量'])
                for rec in data:
                    writer.writerow([rec[0], f"{rec[1]:.2f}", f"{rec[2]:.2f}", f"{rec[3]:.2f}", f"{rec[4]:.2f}", f"{rec[5]:,}"])
            messagebox.showinfo("导出成功", f"数据已导出至 {path}")