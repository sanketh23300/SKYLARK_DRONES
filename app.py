import streamlit as st
from agent import answer_question, generate_leadership_update
from query_engine import get_data_summary, clear_cache, get_work_orders_df, get_deals_df
import pandas as pd
import json

# Page configuration
st.set_page_config(
    page_title="Monday.com BI Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    /* Fix text visibility in chat messages */
    .stChatMessage {
        background-color: #f8f9fa !important;
    }
    .stChatMessage p, .stChatMessage li, .stChatMessage span, 
    .stChatMessage h1, .stChatMessage h2, .stChatMessage h3,
    .stChatMessage h4, .stChatMessage h5, .stChatMessage h6,
    .stChatMessage strong, .stChatMessage em {
        color: #1a1a1a !important;
    }
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #1a1a1a !important;
    }
    /* Ensure chat content is visible */
    [data-testid="stChatMessageContent"] {
        color: #1a1a1a !important;
    }
    [data-testid="stChatMessageContent"] p {
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Data Overview")
    
    # Load data button
    if st.button("🔄 Refresh Data", use_container_width=True):
        clear_cache()
        st.session_state.data_loaded = False
        st.rerun()
    
    # Load and display data summary
    try:
        if not st.session_state.data_loaded:
            with st.spinner("Loading data from Monday.com..."):
                summary = get_data_summary()
                st.session_state.summary = summary
                st.session_state.data_loaded = True
        else:
            summary = st.session_state.summary
        
        st.success("✅ Connected to Monday.com")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Work Orders", summary["work_orders"]["count"])
        with col2:
            st.metric("Deals", summary["deals"]["count"])
        
        # Data quality indicators
        st.markdown("---")
        st.markdown("### 📋 Data Quality")
        
        wo_missing = len(summary["work_orders"]["quality"]["missing_data"])
        deals_missing = len(summary["deals"]["quality"]["missing_data"])
        
        if wo_missing > 0 or deals_missing > 0:
            st.warning(f"⚠️ Some columns have missing data")
        else:
            st.success("✅ All data complete")
            
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.session_state.data_loaded = False
    
    st.markdown("---")
    st.markdown("### 💡 Example Questions")
    
    example_questions = [
        "How's our pipeline looking?",
        "What's the revenue breakdown by sector?",
        "Pipeline status for energy sector?",
        "How many deals are in each stage?",
        "Generate a leadership update",
        "What's our billing status?",
    ]
    
    for q in example_questions:
        if st.button(q, key=f"example_{q}", use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()

# Main content
st.markdown('<p class="main-header">🤖 Monday.com BI Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Ask business intelligence questions about your Work Orders and Deals data</p>', unsafe_allow_html=True)

# Quick action buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📈 Pipeline Overview", use_container_width=True):
        st.session_state.pending_question = "Give me an overview of the current pipeline"
        st.rerun()
with col2:
    if st.button("💰 Revenue Summary", use_container_width=True):
        st.session_state.pending_question = "What's our total revenue and billing status?"
        st.rerun()
with col3:
    if st.button("📋 Leadership Brief", use_container_width=True):
        st.session_state.pending_question = "Prepare a leadership update with key metrics"
        st.rerun()

st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process pending question from buttons
if st.session_state.pending_question:
    prompt = st.session_state.pending_question
    st.session_state.pending_question = None
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate and display response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            try:
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in st.session_state.messages[:-1][-6:]
                ]
                response = answer_question(prompt, conversation_history)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Chat input
if prompt := st.chat_input("Ask a business question..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your data..."):
            try:
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in st.session_state.messages[:-1][-6:]
                ]
                response = answer_question(prompt, conversation_history)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Clear chat button at the bottom
if st.session_state.messages:
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Footer with data tabs
st.markdown("---")
st.markdown("### 📊 Data Explorer")

tab1, tab2, tab3 = st.tabs(["Work Orders Preview", "Deals Preview", "Data Quality"])

with tab1:
    try:
        wo_df = get_work_orders_df()
        st.dataframe(
            wo_df.head(10),
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"Showing 10 of {len(wo_df)} work orders")
    except Exception as e:
        st.error(f"Error loading work orders: {e}")

with tab2:
    try:
        deals_df = get_deals_df()
        st.dataframe(
            deals_df.head(10),
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"Showing 10 of {len(deals_df)} deals")
    except Exception as e:
        st.error(f"Error loading deals: {e}")

with tab3:
    try:
        summary = get_data_summary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Work Orders Quality")
            wo_quality = summary["work_orders"]["quality"]
            st.write(f"**Total Rows:** {wo_quality['total_rows']}")
            st.write(f"**Columns:** {wo_quality['columns']}")
            
            if wo_quality["missing_data"]:
                st.write("**Columns with missing data:**")
                for col, info in list(wo_quality["missing_data"].items())[:5]:
                    st.write(f"- {col}: {info['percentage']}% missing")
        
        with col2:
            st.markdown("#### Deals Quality")
            deals_quality = summary["deals"]["quality"]
            st.write(f"**Total Rows:** {deals_quality['total_rows']}")
            st.write(f"**Columns:** {deals_quality['columns']}")
            
            if deals_quality["missing_data"]:
                st.write("**Columns with missing data:**")
                for col, info in list(deals_quality["missing_data"].items())[:5]:
                    st.write(f"- {col}: {info['percentage']}% missing")
                    
    except Exception as e:
        st.error(f"Error loading data quality: {e}")
