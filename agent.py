import json
import re
from datetime import datetime
from openai import OpenAI
from config import OPENAI_API_KEY
from query_engine import (
    get_work_orders_df,
    get_deals_df,
    get_data_summary,
    get_all_columns,
    analyze_pipeline,
    get_revenue_metrics,
    get_sector_breakdown,
    get_status_breakdown,
    filter_by_sector,
    filter_by_date_range,
    get_quarterly_data,
    clear_cache
)
from data_processor import get_data_quality_report, get_column_summary
import pandas as pd


# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def get_system_prompt():
    """Generate system prompt with current data context."""
    summary = get_data_summary()
    
    return f"""You are a Business Intelligence Agent for Monday.com data. You help founders and executives get quick, accurate answers to business questions.

You have access to two data sources:

1. **Work Orders Board** ({summary['work_orders']['count']} records):
   - Columns: {', '.join(summary['work_orders']['columns'][:15])}...
   - Contains: Project execution data, billing, revenue, status

2. **Deals Board** ({summary['deals']['count']} records):
   - Columns: {', '.join(summary['deals']['columns'])}
   - Contains: Sales pipeline, deal stages, values, sectors

IMPORTANT DATA QUALITY NOTES:
- Work orders have some missing data in: Last invoice date (51%), Collected Amount (56%)
- Deals have missing data in: Close Date (92.5% - most deals open), Deal value (52%), Closure Probability (75%)
- Always mention data quality caveats when relevant

When answering questions:
1. Interpret business intent, not just literal words
2. Provide insights, not just raw numbers
3. Mention any data quality issues
4. For queries about "this quarter", use the current date (February 2026)
5. If data is insufficient, explain what's missing and what you CAN provide

Key sector values in the data: Mining, Renewables, Powerline, Urban, Infrastructure, Agriculture

For numerical answers, format large numbers with commas and include units (e.g., ₹12,34,567 or 1,234).

If asked to prepare leadership updates, structure the response with:
- Executive Summary
- Key Metrics
- Notable Insights
- Areas of Concern
"""


def analyze_data_for_question(question):
    """Analyze the relevant data based on the question and return structured insights."""
    question_lower = question.lower()
    
    results = {
        "data_analyzed": [],
        "metrics": {},
        "insights": [],
        "caveats": []
    }
    
    # Get base data
    work_orders = get_work_orders_df()
    deals = get_deals_df()
    
    # Determine which data sources are relevant
    needs_work_orders = any(term in question_lower for term in 
                           ['work order', 'project', 'execution', 'billing', 'billed', 'revenue', 'collected'])
    needs_deals = any(term in question_lower for term in 
                     ['deal', 'pipeline', 'sales', 'prospect', 'opportunity', 'stage'])
    needs_both = any(term in question_lower for term in 
                    ['overall', 'business', 'company', 'everything', 'summary', 'leadership', 'update'])
    
    # Default to both if unclear
    if not needs_work_orders and not needs_deals:
        needs_both = True
    
    if needs_both:
        needs_work_orders = True
        needs_deals = True
    
    # Check for sector filter
    sectors = ['mining', 'energy', 'renewables', 'powerline', 'urban', 'infrastructure', 'agriculture']
    sector_filter = None
    for sector in sectors:
        if sector in question_lower:
            sector_filter = sector
            break
    
    # Energy often means renewables
    if 'energy' in question_lower:
        sector_filter = 'renewables'
    
    # Apply sector filter
    if sector_filter:
        if needs_work_orders:
            work_orders = filter_by_sector(work_orders, sector_filter)
        if needs_deals:
            deals = filter_by_sector(deals, sector_filter)
        results["metrics"]["sector_filter"] = sector_filter
    
    # Check for time filter (quarterly)
    if 'quarter' in question_lower or 'q1' in question_lower or 'q2' in question_lower or 'q3' in question_lower or 'q4' in question_lower:
        # Extract quarter if specified
        quarter = None
        year = 2026  # Current year
        
        if 'this quarter' in question_lower or 'current quarter' in question_lower:
            quarter = 1  # Feb 2026 is Q1
        elif 'q1' in question_lower:
            quarter = 1
        elif 'q2' in question_lower:
            quarter = 2
        elif 'q3' in question_lower:
            quarter = 3
        elif 'q4' in question_lower:
            quarter = 4
        
        # Check for year
        for y in range(2024, 2028):
            if str(y) in question_lower:
                year = y
                break
        
        if quarter:
            quarterly_data = get_quarterly_data(year, quarter)
            results["metrics"]["quarter"] = f"Q{quarter} {year}"
            
            if needs_work_orders and not quarterly_data["work_orders"].empty:
                work_orders = quarterly_data["work_orders"]
            if needs_deals and not quarterly_data["deals"].empty:
                deals = quarterly_data["deals"]
    
    # Analyze Work Orders
    if needs_work_orders:
        results["data_analyzed"].append("Work Orders")
        
        wo_metrics = {
            "total_work_orders": len(work_orders),
        }
        
        # Revenue metrics
        revenue_col = "Amount in Rupees (Excl of GST) (Masked)"
        if revenue_col in work_orders.columns:
            values = pd.to_numeric(work_orders[revenue_col], errors='coerce').dropna()
            if len(values) > 0:
                wo_metrics["total_revenue"] = float(values.sum())
                wo_metrics["avg_order_value"] = float(values.mean())
        
        # Billed metrics
        billed_col = "Billed Value in Rupees (Excl of GST.) (Masked)"
        if billed_col in work_orders.columns:
            values = pd.to_numeric(work_orders[billed_col], errors='coerce').dropna()
            if len(values) > 0:
                wo_metrics["total_billed"] = float(values.sum())
        
        # Status breakdown
        if "Execution Status" in work_orders.columns:
            wo_metrics["status_breakdown"] = work_orders["Execution Status"].value_counts().to_dict()
        
        # Sector breakdown
        if "Sector" in work_orders.columns:
            wo_metrics["sector_breakdown"] = work_orders["Sector"].value_counts().to_dict()
        
        results["metrics"]["work_orders"] = wo_metrics
    
    # Analyze Deals
    if needs_deals:
        results["data_analyzed"].append("Deals")
        
        deals_metrics = {
            "total_deals": len(deals),
        }
        
        # Deal value
        value_col = "Masked Deal value"
        if value_col in deals.columns:
            values = pd.to_numeric(deals[value_col], errors='coerce').dropna()
            if len(values) > 0:
                deals_metrics["total_pipeline_value"] = float(values.sum())
                deals_metrics["avg_deal_value"] = float(values.mean())
                deals_metrics["deals_with_value"] = len(values)
        
        # Stage breakdown
        if "Deal Stage" in deals.columns:
            deals_metrics["stage_breakdown"] = deals["Deal Stage"].value_counts().to_dict()
        
        # Status breakdown
        if "Deal Status" in deals.columns:
            deals_metrics["status_breakdown"] = deals["Deal Status"].value_counts().to_dict()
        
        # Sector breakdown
        sector_col = "Sector/service"
        if sector_col in deals.columns:
            deals_metrics["sector_breakdown"] = deals[sector_col].value_counts().to_dict()
        
        results["metrics"]["deals"] = deals_metrics
    
    # Add caveats
    if needs_work_orders:
        results["caveats"].append("Revenue data uses 'Amount in Rupees (Excl of GST)' column")
    if needs_deals:
        deals_full = get_deals_df()
        missing_value = pd.to_numeric(deals_full["Masked Deal value"], errors='coerce').isna().sum()
        if missing_value > 0:
            results["caveats"].append(f"Pipeline value: {missing_value} deals ({round(missing_value/len(deals_full)*100)}%) have no value recorded")
    
    return results


def format_number(value, prefix="₹"):
    """Format number in Indian lakhs/crores notation."""
    if value is None:
        return "N/A"
    
    if value >= 10000000:  # 1 crore or more
        return f"{prefix}{value/10000000:,.2f} Cr"
    elif value >= 100000:  # 1 lakh or more
        return f"{prefix}{value/100000:,.2f} L"
    else:
        return f"{prefix}{value:,.0f}"


def generate_leadership_update():
    """Generate a comprehensive leadership update."""
    work_orders = get_work_orders_df()
    deals = get_deals_df()
    
    update = {
        "date": datetime.now().strftime("%B %d, %Y"),
        "executive_summary": {},
        "work_orders_summary": {},
        "pipeline_summary": {},
        "sector_insights": {},
        "concerns": [],
        "recommendations": []
    }
    
    # Work Orders Summary
    revenue_col = "Amount in Rupees (Excl of GST) (Masked)"
    billed_col = "Billed Value in Rupees (Excl of GST.) (Masked)"
    
    total_revenue = pd.to_numeric(work_orders[revenue_col], errors='coerce').sum()
    total_billed = pd.to_numeric(work_orders[billed_col], errors='coerce').sum()
    
    status_counts = work_orders["Execution Status"].value_counts().to_dict()
    completed = status_counts.get("Completed", 0)
    ongoing = status_counts.get("Ongoing", 0) + status_counts.get("Executed until current month", 0)
    
    update["work_orders_summary"] = {
        "total_orders": len(work_orders),
        "total_value": format_number(total_revenue),
        "billed_value": format_number(total_billed),
        "billing_percentage": f"{(total_billed/total_revenue*100):.1f}%" if total_revenue > 0 else "N/A",
        "completed": completed,
        "ongoing": ongoing
    }
    
    # Pipeline Summary
    deal_value = pd.to_numeric(deals["Masked Deal value"], errors='coerce').sum()
    stage_counts = deals["Deal Stage"].value_counts().to_dict()
    status_counts = deals["Deal Status"].value_counts().to_dict()
    
    won_deals = status_counts.get("Won", 0)
    lost_deals = status_counts.get("Lost", 0)
    open_deals = status_counts.get("Open", 0)
    
    update["pipeline_summary"] = {
        "total_deals": len(deals),
        "total_value": format_number(deal_value),
        "won": won_deals,
        "lost": lost_deals,
        "open": open_deals,
        "win_rate": f"{(won_deals/(won_deals+lost_deals)*100):.1f}%" if (won_deals + lost_deals) > 0 else "N/A",
        "stages": stage_counts
    }
    
    # Sector Insights
    wo_sectors = work_orders["Sector"].value_counts().to_dict()
    deal_sectors = deals["Sector/service"].value_counts().to_dict()
    
    update["sector_insights"] = {
        "work_orders_by_sector": wo_sectors,
        "deals_by_sector": deal_sectors,
        "top_sector_work_orders": max(wo_sectors, key=wo_sectors.get) if wo_sectors else "N/A",
        "top_sector_deals": max(deal_sectors, key=deal_sectors.get) if deal_sectors else "N/A"
    }
    
    # Concerns
    unbilled = total_revenue - total_billed
    if unbilled > 0:
        update["concerns"].append(f"Unbilled amount: {format_number(unbilled)} pending billing")
    
    missing_values = len(deals) - len(pd.to_numeric(deals["Masked Deal value"], errors='coerce').dropna())
    if missing_values > len(deals) * 0.3:
        update["concerns"].append(f"{missing_values} deals ({round(missing_values/len(deals)*100)}%) missing deal value - data quality issue")
    
    return update


def answer_question(question, conversation_history=None):
    """Answer a business intelligence question using AI."""
    
    if conversation_history is None:
        conversation_history = []
    
    try:
        # Get data analysis
        data_analysis = analyze_data_for_question(question)
        
        # Check for leadership update request
        is_leadership_update = any(term in question.lower() for term in 
                                  ['leadership', 'update', 'summary', 'report', 'board meeting', 'executive'])
        
        if is_leadership_update:
            leadership_data = generate_leadership_update()
            data_context = f"""
Leadership Update Data:
{json.dumps(leadership_data, indent=2)}
"""
        else:
            data_context = f"""
Data Analysis Results:
{json.dumps(data_analysis, indent=2, default=str)}
"""
        
        # Build messages
        messages = [
            {"role": "system", "content": get_system_prompt()},
        ]
        
        # Add conversation history
        for msg in conversation_history[-6:]:  # Keep last 6 messages for context
            messages.append(msg)
        
        # Add the current question with data context
        user_message = f"""Question: {question}

{data_context}

Please provide a clear, insightful answer based on this data. Include:
1. Direct answer to the question
2. Key metrics with formatted numbers
3. Any relevant insights or patterns
4. Data quality caveats if relevant

Keep the response concise but comprehensive."""

        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        answer = response.choices[0].message.content
        
        return answer
        
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower():
            return "Error: OpenAI API key is invalid or missing. Please check your configuration."
        return f"I encountered an error while processing your question: {error_msg}\n\nPlease try rephrasing your question or check the data connection."


def get_clarifying_questions(question):
    """Generate clarifying questions if the original question is ambiguous."""
    question_lower = question.lower()
    
    clarifications = []
    
    # Check for ambiguous time references
    if 'recently' in question_lower or 'lately' in question_lower:
        clarifications.append("What time period would you like to analyze? (e.g., last month, this quarter, this year)")
    
    # Check for ambiguous metrics
    if 'how much' in question_lower or 'what is the' in question_lower:
        if not any(term in question_lower for term in ['revenue', 'billed', 'value', 'deals', 'orders']):
            clarifications.append("Are you looking for revenue, billed amount, deal pipeline value, or something else?")
    
    return clarifications


# For backward compatibility
def simple_answer(question):
    """Simple answer function for basic queries."""
    return answer_question(question)
