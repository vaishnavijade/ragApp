from flask import Flask, request, jsonify
import random

app = Flask(_name_)

# Fake stock analysis data generator
def generate_stock_insights(stock_symbol):
    # Pretend API data (Replace this logic with real stock data if available)
    trend = random.choice(["📈 Bullish", "📉 Bearish"])
    recommendation = random.choice(["✅ Buy", "❌ Sell"])
    
    insights = (
        f"The stock {stock_symbol} is currently showing a *{trend}* trend. "
        f"Our analysis suggests a *{recommendation}* recommendation. "
        "Key market factors influencing this decision include recent earnings reports, "
        "market sentiment, and macroeconomic indicators."
    )
    
    return {
        "stock_symbol": stock_symbol.upper(),
        "trend": trend,
        "recommendation": recommendation,
        "insights": insights
    }

# API Endpoint to Get Stock Data
@app.route("/", methods=["POST"])
def get_stock_data():
    data = request.get_json()
    stock_symbol = data.get("query", "").strip().upper()
    
    if not stock_symbol:
        return jsonify({"error": "Stock symbol is required"}), 400

    # Generate fake stock insights
    stock_insights = generate_stock_insights(stock_symbol)

    return jsonify({"response": stock_insights})

if _name_ == "_main_":
    app.run(debug=True)
