from flask import Flask, request, jsonify
import requests
import chromadb  # Vector database for financial news
from sentence_transformers import SentenceTransformer
import groq

# ✅ Initialize Flask App
app = Flask(_name_)

# ✅ API Keys
MARKETAUX_API_KEY = "CT6qYivb3yI0VJZw27KJijno5RQ4xP4sQ9Qmn5Ux"
GROQ_API_KEY = "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"

# ✅ Load Pretrained Embedding Model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Initialize ChromaDB for News Storage
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="finance_news")

# ✅ Fetch Latest Financial News
def fetch_financial_news():
    url = "https://api.marketaux.com/v1/news/all"
    params = {
        "api_token": MARKETAUX_API_KEY,
        "language": "en",
        "limit": 100  # Fetch more articles for better analysis
    }
    response = requests.get(url, params=params)
    return response.json().get("data", []) if response.status_code == 200 else []

# ✅ Index News Data in ChromaDB (Avoid Duplicates)
def index_news():
    news_data = fetch_financial_news()
    existing_ids = set(collection.get()["ids"])  # Get existing IDs in ChromaDB

    for article in news_data:
        article_id = article.get("url")
        if not article_id or article_id in existing_ids:
            continue  # Skip duplicates

        text = f"{article.get('title', 'No Title')} - {article.get('description', 'No Description')}"
        embedding = embedder.encode(text).tolist()

        collection.add(
            embeddings=[embedding],
            ids=[article_id],
            metadatas=[{
                "title": article.get("title", "No Title"),
                "url": article_id,
                "description": article.get("description", "No Description"),
                "date": article.get("published_at", "Unknown Date")
            }]
        )

# ✅ Retrieve Relevant News from ChromaDB
def retrieve_relevant_news(query):
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=5)

    if results and "metadatas" in results and results["metadatas"]:
        return sorted(results["metadatas"][0], key=lambda x: x.get("date", ""), reverse=True)

    return []

# ✅ Initialize Groq Client
groq_client = groq.Client(api_key=GROQ_API_KEY)

# ✅ Generate Financial Analysis Using Groq
def generate_financial_analysis(query):
    relevant_articles = retrieve_relevant_news(query)

    if not relevant_articles:
        return "No relevant news found."

    context = "\n".join([f"{a['title']}: {a['description']}" for a in relevant_articles])
    prompt = f"""
    Based on the latest financial news, provide an analysis for: {query}
    - Identify if the trend is Bullish or Bearish.
    - Give a Buy/Sell recommendation.
    - Explain the financial sentiment.
    
    Relevant News:
    {context}
    """

    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# ✅ Flask Routes
@app.route("/analyze", methods=["GET"])
def analyze_stock():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Query parameter is required."}), 400

    analysis = generate_financial_analysis(query)
    return jsonify({"query": query, "analysis": analysis})

# ✅ Index News at Startup
index_news()

# ✅ Run Flask App
if _name_ == "_main_":
    app.run(debug=True)
