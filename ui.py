import streamlit as st
import requests

# Flask API Endpoint
FLASK_API_URL = "https://268c-34-72-244-151.ngrok-free.app/"

# Streamlit page setup
st.set_page_config(page_title="📈 Stock Market Insights", page_icon="📊", layout="wide")

# Function to fetch stock analysis data from Flask API
def get_stock_analysis(stock_symbol):
    payload = {"query": stock_symbol.upper()}

    try:
        response = requests.post(FLASK_API_URL, json=payload, timeout=10)
        response.raise_for_status()
        response_data = response.json()
        return response_data  # Return full response data
    except requests.exceptions.RequestException:
        return None  # API error

# Streamlit UI Layout
st.title("📊 Stock Market Trend & AI Recommendations")
st.markdown("""
    Get insights on whether to **buy or sell* a stock!*  
    Enter a stock symbol to analyze market trends.
""")

# User input for stock symbol
stock_symbol = st.text_input("🔍 Enter Stock Symbol (e.g., AAPL, TSLA, GOOGL):", key="stock_input")

# Submit button
if st.button("Get Stock Analysis"):
    if stock_symbol.strip():
        with st.spinner("🔄 Fetching stock insights..."):
            stock_analysis = get_stock_analysis(stock_symbol)

        if stock_analysis:
            trend = stock_analysis.get("trend", "❓ Unknown")
            recommendation = stock_analysis.get("recommendation", "❓ Unknown")
            analysis_summary = stock_analysis.get("analysis_summary", "No insights available.")

            # Display results
            st.success("✅ Stock Analysis")
            st.markdown(f"### *Market Trend: {trend}*")
            st.markdown(f"### *Investment Recommendation: {recommendation}*")
            st.markdown("----")
            st.markdown(analysis_summary, unsafe_allow_html=True)
        else:
            st.error("⚠ Unable to fetch stock data. Please try again later.")
    else:
        st.warning("⚠ Please enter a stock symbol before submitting.")

# Footer with branding
st.markdown("""
    ---
    ### 🚀 Powered by Flask API  
    Bringing real-time stock insights.
""")
