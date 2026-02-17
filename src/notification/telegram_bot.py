import requests
from src.config_loader import get_telegram_config

class TelegramBot:
    def __init__(self):
        self.config = get_telegram_config()
        self.token = self.config.get("bot_token")
        self.chat_id = self.config.get("chat_id")

    def send_message(self, message: str):
        """Sends a text message to the configured Telegram chat."""
        if not self.token or not self.chat_id or self.token == "YOUR_BOT_TOKEN":
            print("[WARN] Telegram configuration missing or invalid.")
            return

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to send Telegram message: {e}")

# Global instance
bot = TelegramBot()

def send_alert(message: str):
    bot.send_message(message)
