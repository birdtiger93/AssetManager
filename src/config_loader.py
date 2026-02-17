import yaml
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.yaml")
SECRETS_FILE = os.path.join(CONFIG_DIR, "secrets.yaml")

def load_config():
    """Load settings and secrets from YAML files."""
    config = {}
    
    # Load settings
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = yaml.safe_load(f)
            if settings:
                config.update(settings)
    
    # Load secrets
    if os.path.exists(SECRETS_FILE):
        with open(SECRETS_FILE, "r", encoding="utf-8") as f:
            secrets = yaml.safe_load(f)
            if secrets:
                # Be careful not to verify secrets in logs
                # Merge secrets deeply if needed, but for now simple update is fine
                # Assuming secrets structure doesn't conflict or we want secrets to override
                # Actually, specialized handling for 'kis' key might be needed if both have it
                # For now, let's just merge.
                for key, value in secrets.items():
                    if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                         config[key].update(value)
                    else:
                        config[key] = value
                        
    return config

# Global config object
CONFIG = load_config()

def get_app_key():
    return CONFIG.get("kis", {}).get("app_key")

def get_app_secret():
    return CONFIG.get("kis", {}).get("app_secret")

def get_account_no():
    return CONFIG.get("kis", {}).get("account_no")

def get_account_code():
    return CONFIG.get("kis", {}).get("account_code")

def get_base_url():
    return CONFIG.get("api", {}).get("base_url")

def get_telegram_config():
    return CONFIG.get("telegram", {})
