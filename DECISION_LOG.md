# Decision Log - Monday.com Business Intelligence Agent

## Key Assumptions

### 1. Data Interpretation
- **"Energy sector"** is interpreted as **"Renewables"** in the Monday.com data, as there is no explicit "Energy" sector but "Renewables" is the closest match
- **"Revenue"** refers to the "Amount in Rupees (Excl of GST)" column from Work Orders
- **"Pipeline value"** refers to the "Masked Deal value" column from Deals board
- Sector filtering is case-insensitive and supports partial matching

### 2. Quarterly Analysis
- Fiscal quarters follow calendar year (Q1 = Jan-Mar, etc.)
- "This quarter" refers to Q1 2026 given the current date is February 2026
- Date filtering uses all available date columns (PO date, Start date, etc.)

### 3. Data Quality
- Missing values are explicitly reported to users rather than silently ignored
- The agent calculates metrics only from available (non-null) data
- Data quality caveats are included in responses when relevant (e.g., "52% of deals have no recorded value")

---

## Trade-offs Chosen

### 1. OpenAI vs Local LLM
**Chose: OpenAI GPT-4**
- **Pros**: Better reasoning, more accurate response generation, handles complex business questions well
- **Cons**: Requires API key, costs money, data sent to external service
- **Rationale**: Business intelligence requires nuanced understanding that local LLMs struggle with

### 2. API-based vs MCP Integration
**Chose: Direct API (GraphQL)**
- **Pros**: More control, easier debugging, well-documented, no additional dependencies
- **Cons**: More code to maintain, manual authentication handling
- **Rationale**: API approach is more reliable and gives better control over data fetching/pagination

### 3. Streamlit vs Custom Frontend
**Chose: Streamlit**
- **Pros**: Rapid development, built-in chat UI, easy deployment, Python-native
- **Cons**: Limited customization, not production-grade for high traffic
- **Rationale**: Perfect for prototype/demo; can scale to production later

### 4. In-Session Caching vs Database
**Chose: In-session caching (Python dict)**
- **Pros**: Simple, no additional infrastructure, fast for single-user
- **Cons**: Not persistent, re-fetches on restart
- **Rationale**: Suitable for prototype; Redis/DB can be added for production

### 5. Data Analysis Approach
**Chose: Pre-analyzed context + AI interpretation**
- Analyze data first, then pass structured results to LLM
- **Pros**: More accurate numbers, reduced hallucination risk
- **Cons**: More code complexity
- **Rationale**: Ensures accurate metrics while leveraging AI for natural language response

---

## What I'd Do Differently With More Time

### 1. Enhanced Analytics
- Add visualization charts using Plotly (revenue trends, pipeline funnel)
- Implement time-series analysis for trend detection
- Add predictive insights (forecasting deal closure, revenue projections)

### 2. Production Hardening
- Add Redis caching for data persistence
- Implement rate limiting and retry logic for API calls
- Add comprehensive logging and monitoring
- Implement user authentication

### 3. Advanced Features
- Export functionality (PDF reports, Excel downloads)
- Scheduled reports via email
- Custom alert thresholds (e.g., "Alert when pipeline < X")
- Multi-board correlation analysis

### 4. Testing
- Unit tests for data processing functions
- Integration tests for API calls
- End-to-end tests for common user flows

### 5. UX Improvements
- Auto-suggest questions based on data patterns
- Streaming responses for faster perceived performance
- Voice input support
- Mobile-responsive design

---

## Leadership Updates Interpretation

I interpreted "The agent should help prepare data for leadership updates" as:

**Definition**: A structured executive summary that provides leadership with actionable insights at a glance.

**Implementation**:
When a user asks for a "leadership update" or "executive summary", the agent generates:

1. **Executive Summary**
   - High-level status of work orders and deals
   - Key wins and losses

2. **Key Metrics**
   - Total revenue and billing status
   - Pipeline value and conversion rates
   - Sector performance breakdown

3. **Notable Insights**
   - Trends in deal stages
   - Top performing sectors
   - Revenue vs billing gaps

4. **Areas of Concern**
   - Data quality issues
   - Unbilled revenue
   - Stalled deals

**Rationale**: Leadership typically needs:
- Quick overview (< 2 minutes read)
- Numbers they can quote
- Actionable concerns to address
- Context for strategic decisions

The agent formats numbers in Indian notation (Lakhs/Crores) for readability and includes data quality caveats so leaders know the confidence level of the metrics.

---

## Technology Decisions Summary

| Component | Choice | Alternative Considered |
|-----------|--------|----------------------|
| LLM | OpenAI GPT-4 | Falcon-7B, Llama |
| Frontend | Streamlit | React, Flask |
| Data Processing | Pandas | Polars, NumPy |
| API Integration | Requests + GraphQL | Monday MCP |
| Deployment | Streamlit Cloud | Heroku, Railway |

---

*Total time spent: ~5 hours*
