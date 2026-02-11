# Monday.com Business Intelligence Agent

An AI-powered business intelligence agent that answers founder-level business questions by integrating with Monday.com boards containing work orders and deals data.

## 🚀 Features

- **Natural Language Queries**: Ask business questions in plain English
- **Cross-Board Analysis**: Query data from both Work Orders and Deals boards
- **Data Resilience**: Handles missing/null values gracefully
- **Leadership Updates**: Generate comprehensive executive summaries
- **Conversational Interface**: Chat-based UI with context memory
- **Data Quality Reporting**: Transparent about data completeness

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                        │
│  - Conversational chat interface                                │
│  - Data explorer tabs                                           │
│  - Quick action buttons                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Agent (agent.py)                          │
│  - OpenAI GPT-4 integration                                     │
│  - Question interpretation                                      │
│  - Data analysis orchestration                                  │
│  - Response generation                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Query Engine (query_engine.py)                  │
│  - Data caching                                                 │
│  - Filtering (sector, date, quarter)                            │
│  - Metrics calculation                                          │
│  - Pipeline analysis                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│  Data Processor (data_processor.py)  │  Monday Client (monday_client.py)  │
│  - JSON to DataFrame conversion      │  - GraphQL API integration          │
│  - Data cleaning & normalization     │  - Pagination handling              │
│  - Date/currency parsing             │  - Column metadata fetching         │
│  - Quality reporting                 │  - Error handling                   │
└───────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Monday.com API                               │
│  - Work Orders Board                                            │
│  - Deals Board                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.9+
- Monday.com account with API access
- OpenAI API key

### 1. Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd monday_bi_agent

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
MONDAY_API_TOKEN=your_monday_api_token
WORK_ORDERS_BOARD_ID=your_work_orders_board_id
DEALS_BOARD_ID=your_deals_board_id
OPENAI_API_KEY=your_openai_api_key
```

### 3. Monday.com Board Setup

#### Work Orders Board
Import the Work Orders CSV and ensure these columns exist:
- **Item Name**: Project/order name
- **Execution Status**: Current status (Completed, Ongoing, etc.)
- **Sector**: Industry sector (Mining, Renewables, etc.)
- **Type of Work**: Type of service provided
- **Amount in Rupees (Excl of GST)**: Order value
- **Billed Value in Rupees (Excl of GST.)**: Amount billed
- **Date of PO/LOI**: Order date
- **Probable Start/End Date**: Project timeline

#### Deals Board
Import the Deals CSV and ensure these columns exist:
- **Item Name**: Deal name
- **Deal Status**: Current status (Open, Won, Lost, etc.)
- **Deal Stage**: Pipeline stage
- **Masked Deal value**: Deal monetary value
- **Sector/service**: Target sector
- **Owner code**: Sales representative code
- **Tentative Close Date**: Expected close date

### 4. Run the Application

```bash
# Test the connection first
python test_connection.py

# Start the Streamlit app
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## 💬 Example Questions

- "How's our pipeline looking?"
- "What's the revenue breakdown by sector?"
- "How many deals are in each stage?"
- "Pipeline status for energy sector this quarter?"
- "Generate a leadership update"
- "What's our billing status?"
- "How many work orders are completed vs ongoing?"

## 📊 Data Handling

### Missing Data
The agent handles missing data gracefully:
- Reports data quality issues when relevant
- Calculates metrics only with available data
- Clearly states caveats in responses

### Supported Filters
- **Sector**: Mining, Renewables, Powerline, Urban, Infrastructure, Agriculture
- **Time Period**: This quarter, Q1-Q4, specific years
- **Status**: Various deal stages and execution statuses

## 🏗️ Technical Stack

- **Frontend**: Streamlit
- **AI/LLM**: OpenAI GPT-4
- **Data Processing**: Pandas
- **API Integration**: Requests (GraphQL)
- **Configuration**: python-dotenv

## 📁 File Structure

```
monday_bi_agent/
├── app.py              # Streamlit UI
├── agent.py            # AI agent logic
├── query_engine.py     # Data querying and analysis
├── data_processor.py   # Data cleaning and transformation
├── monday_client.py    # Monday.com API client
├── config.py           # Configuration management
├── test_connection.py  # Connection testing script
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not in repo)
└── README.md           # This file
```

## 🔧 Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Add environment variables in Streamlit Cloud secrets
4. Deploy

### Other Platforms

The app can be deployed on:
- Heroku
- Railway
- AWS/GCP/Azure
- Any platform supporting Python + Streamlit

## ⚠️ Known Limitations

1. **Data Freshness**: Data is cached in-session; use "Refresh Data" button for latest
2. **Rate Limits**: Monday.com API has rate limits; large boards may require pagination
3. **Missing Values**: Some deal values and dates may be incomplete in source data

## 📝 License

MIT License
