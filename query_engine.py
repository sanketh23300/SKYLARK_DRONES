from monday_client import fetch_board_items
from data_processor import (
    monday_json_to_dataframe, 
    clean_dataframe,
    normalize_dates,
    normalize_numeric_columns,
    get_data_quality_report,
    get_column_summary
)
from config import WORK_ORDERS_BOARD_ID, DEALS_BOARD_ID
import pandas as pd
from datetime import datetime


# Cache for dataframes to avoid repeated API calls
_cache = {}


def get_work_orders_df(force_refresh=False):
    """Get Work Orders DataFrame with caching."""
    if "work_orders" not in _cache or force_refresh:
        data = fetch_board_items(WORK_ORDERS_BOARD_ID)
        df = monday_json_to_dataframe(data)
        df = clean_dataframe(df)
        _cache["work_orders"] = df
    return _cache["work_orders"].copy()


def get_deals_df(force_refresh=False):
    """Get Deals DataFrame with caching."""
    if "deals" not in _cache or force_refresh:
        data = fetch_board_items(DEALS_BOARD_ID)
        df = monday_json_to_dataframe(data)
        df = clean_dataframe(df)
        _cache["deals"] = df
    return _cache["deals"].copy()


def clear_cache():
    """Clear the data cache."""
    _cache.clear()


def get_all_columns():
    """Get all column names from both boards."""
    work_orders = get_work_orders_df()
    deals = get_deals_df()
    
    return {
        "work_orders": list(work_orders.columns),
        "deals": list(deals.columns)
    }


def analyze_pipeline():
    """Analyze the deals pipeline."""
    deals = get_deals_df()
    
    result = {
        "total_deals": len(deals),
        "unique_sectors": 0,
        "sectors": [],
        "stages": {},
    }
    
    # Find sector column (might have different names)
    sector_col = None
    for col in deals.columns:
        if 'sector' in col.lower():
            sector_col = col
            break
    
    if sector_col and sector_col in deals.columns:
        sectors = deals[sector_col]
        sectors = sectors[sectors != ""]
        result["sectors"] = sectors.unique().tolist()
        result["unique_sectors"] = len(result["sectors"])
    
    # Find stage/status column
    stage_col = None
    for col in deals.columns:
        if any(term in col.lower() for term in ['stage', 'status', 'state']):
            stage_col = col
            break
    
    if stage_col and stage_col in deals.columns:
        result["stages"] = deals[stage_col].value_counts().to_dict()
    
    return result


def get_revenue_metrics(df, revenue_col=None):
    """Calculate revenue metrics from a DataFrame."""
    if revenue_col is None:
        # Try to find revenue column
        for col in df.columns:
            if any(term in col.lower() for term in ['value', 'amount', 'revenue', 'total', 'price']):
                revenue_col = col
                break
    
    if not revenue_col or revenue_col not in df.columns:
        return {"error": "No revenue column found"}
    
    # Convert to numeric
    values = pd.to_numeric(df[revenue_col], errors='coerce')
    values = values.dropna()
    
    if len(values) == 0:
        return {"error": "No valid numeric values found"}
    
    return {
        "total": float(values.sum()),
        "average": float(values.mean()),
        "min": float(values.min()),
        "max": float(values.max()),
        "count": len(values),
        "column_used": revenue_col
    }


def get_sector_breakdown(board="deals"):
    """Get breakdown by sector."""
    if board == "deals":
        df = get_deals_df()
    else:
        df = get_work_orders_df()
    
    # Find sector column
    sector_col = None
    for col in df.columns:
        if 'sector' in col.lower():
            sector_col = col
            break
    
    if not sector_col:
        return {"error": "No sector column found"}
    
    breakdown = df[sector_col].value_counts().to_dict()
    
    return {
        "column": sector_col,
        "breakdown": breakdown
    }


def get_status_breakdown(board="work_orders"):
    """Get breakdown by status."""
    if board == "work_orders":
        df = get_work_orders_df()
    else:
        df = get_deals_df()
    
    # Find status column
    status_col = None
    for col in df.columns:
        if any(term in col.lower() for term in ['status', 'stage', 'state']):
            status_col = col
            break
    
    if not status_col:
        return {"error": "No status column found"}
    
    breakdown = df[status_col].value_counts().to_dict()
    
    return {
        "column": status_col,
        "breakdown": breakdown
    }


def filter_by_sector(df, sector):
    """Filter DataFrame by sector (case-insensitive, partial match)."""
    sector_col = None
    for col in df.columns:
        if 'sector' in col.lower():
            sector_col = col
            break
    
    if not sector_col:
        return df
    
    mask = df[sector_col].str.lower().str.contains(sector.lower(), na=False)
    return df[mask]


def filter_by_date_range(df, start_date=None, end_date=None, date_column=None):
    """Filter DataFrame by date range."""
    if date_column is None:
        # Try to find a date column
        for col in df.columns:
            if 'date' in col.lower():
                date_column = col
                break
    
    if not date_column or date_column not in df.columns:
        return df
    
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    
    if start_date:
        start = pd.to_datetime(start_date)
        df = df[df[date_column] >= start]
    
    if end_date:
        end = pd.to_datetime(end_date)
        df = df[df[date_column] <= end]
    
    return df


def get_quarterly_data(year=None, quarter=None):
    """Get data for a specific quarter."""
    if year is None:
        year = datetime.now().year
    
    quarter_ranges = {
        1: (f"{year}-01-01", f"{year}-03-31"),
        2: (f"{year}-04-01", f"{year}-06-30"),
        3: (f"{year}-07-01", f"{year}-09-30"),
        4: (f"{year}-10-01", f"{year}-12-31"),
    }
    
    if quarter is None:
        month = datetime.now().month
        quarter = (month - 1) // 3 + 1
    
    start_date, end_date = quarter_ranges[quarter]
    
    deals = get_deals_df()
    work_orders = get_work_orders_df()
    
    return {
        "quarter": f"Q{quarter} {year}",
        "start_date": start_date,
        "end_date": end_date,
        "deals": filter_by_date_range(deals, start_date, end_date),
        "work_orders": filter_by_date_range(work_orders, start_date, end_date)
    }


def get_data_summary():
    """Get a comprehensive summary of all data."""
    work_orders = get_work_orders_df()
    deals = get_deals_df()
    
    return {
        "work_orders": {
            "count": len(work_orders),
            "columns": list(work_orders.columns),
            "quality": get_data_quality_report(work_orders)
        },
        "deals": {
            "count": len(deals),
            "columns": list(deals.columns),
            "quality": get_data_quality_report(deals)
        }
    }
