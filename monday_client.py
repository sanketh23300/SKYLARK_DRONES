import requests
from config import MONDAY_API_TOKEN

API_URL = "https://api.monday.com/v2"

HEADERS = {
    "Authorization": MONDAY_API_TOKEN
}


def fetch_board_items(board_id, limit=500):
    """Fetch all items from a board with pagination support."""
    all_items = []
    cursor = None
    board_name = None
    columns = None
    
    while True:
        if cursor:
            query = """
            query ($board_id: [ID!], $cursor: String!) {
              boards(ids: $board_id) {
                name
                columns {
                  id
                  title
                  type
                }
                items_page(limit: 500, cursor: $cursor) {
                  cursor
                  items {
                    name
                    column_values {
                      id
                      text
                    }
                  }
                }
              }
            }
            """
            variables = {"board_id": [board_id], "cursor": cursor}
        else:
            query = """
            query ($board_id: [ID!]) {
              boards(ids: $board_id) {
                name
                columns {
                  id
                  title
                  type
                }
                items_page(limit: 500) {
                  cursor
                  items {
                    name
                    column_values {
                      id
                      text
                    }
                  }
                }
              }
            }
            """
            variables = {"board_id": [board_id]}

        response = requests.post(
            API_URL,
            json={"query": query, "variables": variables},
            headers=HEADERS,
            timeout=60
        )
        
        data = response.json()
        
        if "errors" in data:
            raise Exception(f"Monday.com API error: {data['errors']}")
        
        board = data["data"]["boards"][0]
        board_name = board["name"]
        columns = board["columns"]
        
        items_page = board["items_page"]
        all_items.extend(items_page["items"])
        
        cursor = items_page.get("cursor")
        if not cursor:
            break
    
    # Return in the expected format with column metadata
    return {
        "data": {
            "boards": [{
                "name": board_name,
                "columns": columns,
                "items_page": {
                    "items": all_items
                }
            }]
        }
    }


def fetch_board_columns(board_id):
    """Fetch column metadata for a board."""
    query = """
    query ($board_id: [ID!]) {
      boards(ids: $board_id) {
        name
        columns {
          id
          title
          type
        }
      }
    }
    """
    
    variables = {"board_id": [board_id]}
    
    response = requests.post(
        API_URL,
        json={"query": query, "variables": variables},
        headers=HEADERS,
        timeout=30
    )
    
    return response.json()


def test_connection():
    """Test API connection with a simple query."""
    query = """
    query {
      me {
        name
        email
      }
    }
    """
    
    response = requests.post(
        API_URL,
        json={"query": query},
        headers=HEADERS,
        timeout=30
    )
    
    return response.json()
