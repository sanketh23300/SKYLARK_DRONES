import os
from dotenv import load_dotenv

load_dotenv()

# Try Streamlit secrets first (for cloud deployment), then fall back to .env
def get_secret(key):
    """Get secret from Streamlit secrets or environment variable."""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)

MONDAY_API_TOKEN = get_secret("MONDAY_API_TOKEN")
WORK_ORDERS_BOARD_ID = get_secret("WORK_ORDERS_BOARD_ID")
DEALS_BOARD_ID = get_secret("DEALS_BOARD_ID")
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
HF_API_TOKEN = get_secret("HF_API_TOKEN")
