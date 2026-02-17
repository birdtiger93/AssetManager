import json
import time
import os
import requests
from src.config_loader import get_app_key, get_app_secret, get_base_url, PROJECT_ROOT

TOKEN_FILE = os.path.join(PROJECT_ROOT, "token.json")

class TokenManager:
    def __init__(self):
        self.app_key = get_app_key()
        self.app_secret = get_app_secret()
        self.url_base = get_base_url()
        self._access_token = None
        self._issued_at = 0

    def get_token(self):
        """Returns a valid access token. Checks cache first."""
        # 1. Check memory cache
        if self._is_token_valid():
            return self._access_token

        # 2. Check file cache
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    token = data.get("access_token")
                    issued_at = data.get("issued_at")
                    
                    if token and issued_at:
                        # Check expiry (strictly < 23 hours to be safe)
                        if time.time() - issued_at < 23 * 3600:
                            self._access_token = token
                            self._issued_at = issued_at
                            return token
            except Exception as e:
                print(f"[WARN] Failed to read token file: {e}")

        # 3. Issue new token
        return self._issue_new_token()

    def _is_token_valid(self):
        """Checks if the in-memory token is valid."""
        if self._access_token and self._issued_at:
             if time.time() - self._issued_at < 23 * 3600:
                 return True
        return False

    def _issue_new_token(self):
        """Issues a new access token from KIS API."""
        path = "/oauth2/tokenP"
        url = f"{self.url_base}{path}"
        headers = {"content-type": "application/json"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            res = requests.post(url, headers=headers, json=data)
            res.raise_for_status() # Raise error for bad status
            
            token_info = res.json()
            access_token = token_info.get("access_token")
            
            if access_token:
                self._access_token = access_token
                self._issued_at = time.time()
                
                # Save to file
                with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                    json.dump({
                        "access_token": self._access_token,
                        "issued_at": self._issued_at
                    }, f)
                print("[INFO] New access token issued.")
                return access_token
            else:
                print(f"[ERROR] Token response missing access_token: {token_info}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to issue token: {e}")
            if hasattr(e.response, 'text') and e.response:
                 print(f"Response: {e.response.text}")
            return None

# Singleton instance
token_manager = TokenManager()

def get_access_token():
    return token_manager.get_token()
