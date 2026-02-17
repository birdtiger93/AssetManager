import requests
import json
import time
from src.auth.token_manager import get_access_token
from src.config_loader import get_app_key, get_app_secret, get_base_url, get_account_no, get_account_code

class BaseAPI:
    def __init__(self):
        self.app_key = get_app_key()
        self.app_secret = get_app_secret()
        self.base_url = get_base_url()
        self.account_no = get_account_no()
        self.account_code = get_account_code()
        
    def _get_headers(self, tr_id=None, content_type="application/json"):
        access_token = get_access_token()
        if not access_token:
            raise Exception("Failed to get access token")
            
        headers = {
            "content-type": content_type,
            "authorization": f"Bearer {access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
        }
        
        if tr_id:
            headers["tr_id"] = tr_id
            
        return headers

    def call_api(self, path, params=None, data=None, method="GET", tr_id=None):
        """Standard API call with error handling."""
        url = f"{self.base_url}{path}"
        headers = self._get_headers(tr_id=tr_id)
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                # POST usually takes JSON body
                if headers.get("content-type") == "application/json" and data:
                    response = requests.post(url, headers=headers, json=data)
                elif data:
                     # Form data if not JSON
                    response = requests.post(url, headers=headers, data=data)
                else:
                    response = requests.post(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            # Check for specific API errors in response body even if HTTP 200
            # KIS API often returns 200 but with error code in body
            res_json = None
            try:
                res_json = response.json()
            except json.JSONDecodeError:
                 print(f"[WARN] Non-JSON response from {path}: {response.text}")
                 return None

            if response.status_code != 200:
                print(f"[ERROR] API Call Failed ({response.status_code}): {res_json}")
                return None
            
            # Check KIS-specific error codes
            rt_cd = res_json.get("rt_cd")
            if rt_cd and rt_cd != "0":
                msg = res_json.get("msg1")
                print(f"[ERROR] Logic Error (rt_cd={rt_cd}): {msg} in {path}")
                return None
                
            return res_json

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request Exception: {e}")
            return None
