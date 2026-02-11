import pandas as pd
import re
from datetime import datetime


def monday_json_to_dataframe(data):
    """Convert Monday.com JSON response to a pandas DataFrame with proper column names."""
    board = data["data"]["boards"][0]
    items = board["items_page"]["items"]
    
    # Build column ID to title mapping
    columns = board.get("columns", [])
    column_map = {col["id"]: col["title"] for col in columns}
    
    records = []
    
    for item in items:
        row = {"Item Name": item["name"]}
        
        for col in item["column_values"]:
            column_id = col["id"]
            # Use human-readable column title if available
            column_name = column_map.get(column_id, column_id)
            row[column_name] = col["text"]
        
        records.append(row)
    
    return pd.DataFrame(records)


def clean_dataframe(df):
    """Clean and normalize DataFrame values."""
    df = df.copy()
    
    # Fill NaN with empty string
    df = df.fillna("")
    
    # Normalize text columns - strip whitespace
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()
    
    return df


def normalize_dates(df, date_columns=None):
    """Normalize date columns to consistent format."""
    df = df.copy()
    
    if date_columns is None:
        # Try to detect date columns
        date_columns = []
        for col in df.columns:
            if 'date' in col.lower() or any(term in col.lower() for term in ['start', 'end', 'due', 'created']):
                date_columns.append(col)
    
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(parse_date)
    
    return df


def parse_date(value):
    """Parse various date formats to ISO format."""
    if not value or pd.isna(value) or value == "":
        return None
    
    # Common date formats to try
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d %b %Y",
        "%B %d, %Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(str(value).strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return value  # Return original if parsing fails


def normalize_currency(value):
    """Clean and normalize currency/numeric values."""
    if not value or pd.isna(value) or value == "":
        return None
    
    # Remove currency symbols and commas
    cleaned = re.sub(r'[₹$€£,\s]', '', str(value))
    
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_numeric_columns(df, numeric_columns=None):
    """Convert numeric columns to float, handling messy data."""
    df = df.copy()
    
    if numeric_columns is None:
        # Auto-detect numeric columns based on content
        numeric_columns = []
        for col in df.columns:
            # Check if column name suggests numeric
            if any(term in col.lower() for term in ['amount', 'value', 'price', 'cost', 'revenue', 'total', 'quantity', 'area', 'ha']):
                numeric_columns.append(col)
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].apply(normalize_currency)
    
    return df


def get_data_quality_report(df):
    """Generate a data quality report for the DataFrame."""
    report = {
        "total_rows": len(df),
        "columns": len(df.columns),
        "missing_data": {},
        "empty_rows": 0,
    }
    
    for col in df.columns:
        missing = df[col].isna().sum() + (df[col] == "").sum()
        if missing > 0:
            report["missing_data"][col] = {
                "count": int(missing),
                "percentage": round(missing / len(df) * 100, 1)
            }
    
    # Count rows with all empty values (except Item Name)
    data_cols = [c for c in df.columns if c != "Item Name"]
    if data_cols:
        report["empty_rows"] = int(((df[data_cols] == "") | df[data_cols].isna()).all(axis=1).sum())
    
    return report


def get_column_summary(df, column):
    """Get summary statistics for a column."""
    if column not in df.columns:
        return {"error": f"Column '{column}' not found"}
    
    col_data = df[column]
    summary = {
        "name": column,
        "total_values": len(col_data),
        "empty_count": int((col_data == "").sum() + col_data.isna().sum()),
    }
    
    # Try to get numeric stats
    try:
        numeric_data = pd.to_numeric(col_data, errors='coerce')
        valid_numeric = numeric_data.dropna()
        if len(valid_numeric) > 0:
            summary["numeric_stats"] = {
                "min": float(valid_numeric.min()),
                "max": float(valid_numeric.max()),
                "mean": float(valid_numeric.mean()),
                "sum": float(valid_numeric.sum()),
            }
    except:
        pass
    
    # Get unique values for categorical data
    unique_vals = col_data[col_data != ""].unique()
    if len(unique_vals) <= 20:
        summary["unique_values"] = list(unique_vals)
    else:
        summary["unique_count"] = len(unique_vals)
    
    return summary
