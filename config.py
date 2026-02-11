import os
from dotenv import load_dotenv

load_dotenv()

# Try Streamlit secrets first (for cloud deployment), then fall back to .env
try:
    import streamlit as st
    MONDAY_API_TOKEN = st.secrets.get("MONDAY_API_TOKEN", os.getenv("MONDAY_API_TOKEN"))
    WORK_ORDERS_BOARD_ID = st.secrets.get("WORK_ORDERS_BOARD_ID", os.getenv("WORK_ORDERS_BOARD_ID"))
    DEALS_BOARD_ID = st.secrets.get("DEALS_BOARD_ID", os.getenv("DEALS_BOARD_ID"))
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    HF_API_TOKEN = st.secrets.get("HF_API_TOKEN", os.getenv("HF_API_TOKEN"))
except:
    # Fallback for non-Streamlit environments (testing, scripts)
    MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
    WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")
    DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    HF_API_TOKEN = os.getenv("HF_API_TOKEN")
