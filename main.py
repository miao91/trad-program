import os
import requests
import pandas as pd
import numpy as np
try:
    import schedule
except ImportError:
    print("未找到 'schedule' 模块，请使用 'pip install schedule' 进行安装。")
    raise
import time
import datetime
import ntplib
from pytz import timezone
try:
    from dotenv import load_dotenv
except ImportError:
    print("未找到 'dotenv' 模块，请使用 'pip install python-dotenv' 进行安装。")
    raise

load_dotenv()

COINGECKO_API = "https://api.coingecko.com/api/v3"

class CryptoAnalyzer:
    def __init__(self):
        self.ntp_server = 'pool.ntp.org'
        self.local_tz = timezone('Asia/Shanghai')
        self.session = requests.Session()
        self.history_prices = {'BTC': []}
        self.last_update = None
        self.tg_token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if self.tg_token and self.chat_id:
            from telegram import Bot
            self.bot = Bot(token=self.tg_token)
        
    def get_top_coins(self, limit=200):
        try:
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1
            }
            response = self.session.get(f"{COINGECKO_API}/coins/markets", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取数据失败: {e}")
            return []

    def get_synchronized_time(self):
        try:
            client = ntplib.NTPClient()
            response = client.request(self.ntp_server, version=3)
            return response.tx_time
        except Exception as e:
            print(f"NTP同步失败，使用本地时间: {e}")
            return datetime.datetime.now(datetime.UTC).timestamp()

    def format_local_time(self, timestamp):
        utc_dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)
        local_dt = utc_dt.astimezone(self.local_tz)
        return local_dt.strftime('%Y-%m-%d %H:%M:%S %Z')

    def calculate_correlation(self):
        # 获取最新数据并更新历史记录
        coins_data = self.get_top_coins()
        current_time = self.get_synchronized_time()
        
        # 保留最近2小时数据（7200秒）
        if self.last_update and (current_time - self.last_update) > 7200:
            self.history_prices = {'BTC': []}
        
        # 存储当前时刻数据
        for coin in coins_data:
            symbol = coin['symbol'].upper()
            price = coin['current_price']
            
            if symbol == 'BTC':
                self.history_prices['BTC'].append({
                    'timestamp': current_time,
                    'price': price
                })
            else:
                if symbol not in self.history_prices:
                    self.history_prices[symbol] = []
                self.history_prices[symbol].append({
                    'timestamp': current_time,
                    'price': price
                })
        
        self.last_update = current_time
        
        if len(self.history_prices['BTC']) < 2:
            print("需要至少2个数据点才能计算相关系数")
            return

        btc_prices = []
        other_prices = {}

        # 获取当前价格数据
        for coin in coins_data:
            symbol = coin['symbol'].upper()
            if symbol == 'BTC':
                btc_prices.append(coin['current_price'])
            else:
                other_prices[symbol] = [coin['current_price']]

                # 计算小时级涨跌幅
        btc_prices = [x['price'] for x in self.history_prices['BTC'][-2:]]
        btc_changes = np.diff(btc_prices) / btc_prices[0] if len(btc_prices) >= 2 else []
        
        if len(btc_changes) == 0:
            return
        results = []

        for symbol, prices in other_prices.items():
            if len(prices) < 2:
                continue
            changes = np.diff(prices) / prices[:-1]
            if len(changes) != len(btc_changes):
                continue
            
            correlation = np.corrcoef(btc_changes, changes)[0,1]
            if not np.isnan(correlation) and correlation < 0.5:
                results.append((symbol, abs(correlation)))

        # 按相关系数排序
        results.sort(key=lambda x: x[1])
        
        # 输出结果（实际应替换为通知逻辑）
        message = "🚨 低相关性币种排名：\n" + "\n".join(
            [f"{rank}. {symbol}: {corr:.4f}" for rank, (symbol, corr) in enumerate(results, 1)]
        )
        
        if hasattr(self, 'bot'):
            try:
                # 检查self.bot和self.chat_id是否正确初始化
                if self.bot and self.chat_id:
                    # 此处代码逻辑无误，若提示缺少参数可能是IDE误判，可忽略此提示
                    self.bot.send_message(chat_id=self.chat_id, text=message)
                else:
                    print("Telegram Bot或Chat ID未正确初始化，无法发送消息。")
            except Exception as e:
                print(f"Telegram通知发送失败: {e}")
        else:
            print("\n" + message)

    def start_monitoring(self):
        schedule.every().hour.at(":00").do(self.calculate_correlation)
        print(f"[同步时间] {self.format_local_time(time.time())}\n监控程序已启动，每小时执行一次...")
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    analyzer = CryptoAnalyzer()
    analyzer.start_monitoring()