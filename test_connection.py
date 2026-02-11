from monday_client import fetch_board_items
from config import WORK_ORDERS_BOARD_ID

print("Testing Monday API...")

data = fetch_board_items(WORK_ORDERS_BOARD_ID)

print("Connection successful!")
print(data)
