import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.config_loader import get_app_key, get_app_secret, get_base_url
from src.auth.token_manager import TokenManager

def debug_auth():
    print("--- Debugging Auth ---")
    app_key = get_app_key()
    app_secret = get_app_secret()
    base_url = get_base_url()
    
    print(f"Base URL: {base_url}")
    print(f"App Key: {app_key[:5]}...{app_key[-5:] if app_key else 'None'}")
    print(f"App Secret (Length): {len(app_secret) if app_secret else 0}")
    
    if not app_key or not app_secret:
        print("[ERROR] Keys are missing!")
        return

    print("\nAttempting to issue token...")
    tm = TokenManager()
    
    # Force issue new token (bypass cache)
    try:
        token = tm._issue_new_token()
        if token:
            print(f"[SUCCESS] Token issued: {token[:10]}...")
        else:
            print("[FAILURE] Token is None")
    except Exception as e:
        print(f"[EXCEPTION] {e}")

if __name__ == "__main__":
    debug_auth()
