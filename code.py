import pathway as pw
import requests
import chromadb  # Using Chroma for vector storage
from sentence_transformers import SentenceTransformer
import groq
import pandas as pd

# ✅ Load Pretrained Embedding Model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Initialize ChromaDB Client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="finance_news")

# ✅ Fetch Financial News (All Categories)
def fetch_financial_news():
    url = "https://api.marketaux.com/v1/news/all"
    params = {
        "api_token": "api_key",  # Replace with actual API key
        "language": "en",
        "limit": 100  # Fetch more articles to ensure coverage
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

# ✅ Index News Data in ChromaDB (Avoiding Duplicates)
news_data = fetch_financial_news()
print("Fetched news articles:", news_data[:5])  # Debugging API response

existing_ids = set(collection.get()["ids"])  # Get existing IDs in ChromaDB

for article in news_data:
    article_id = article.get("url")  # Use URL as unique ID
    if not article_id or article_id in existing_ids:
        continue  # Skip duplicates or missing URL

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

print("Indexed News Count:", len(collection.get()["ids"]))  # Debugging ChromaDB storage

# ✅ Retrieve Relevant News
def retrieve_relevant_news(query):
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(query_embedding, n_results=5)  # Fetch top 5 relevant articles

    if results and "metadatas" in results and results["metadatas"]:
        articles = results["metadatas"][0]  # Extract metadata
        return sorted(articles, key=lambda x: x.get("date", ""), reverse=True)  # Sort by latest date

    print("No relevant news found. Expanding search criteria...")  # Debugging retrieval
    return []

# ✅ Generate Answer Using Groq
GROQ_API_KEY = "groq-api-key"  # Replace with actual API key
groq_client = groq.Client(api_key=GROQ_API_KEY)

def generate_response(query):
    relevant_articles = retrieve_relevant_news(query)

    if not relevant_articles:
        return "No relevant news found for the query."

    context = "\n".join([f"{a['title']}: {a['description']}" for a in relevant_articles])
    prompt = f"Based on the following financial news articles, provide a well-explained answer to the query: {query}\n\n{context}"

    response = groq_client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "system", "content": "You are a financial assistant."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content  # ✅ Extract response text correctly

# ✅ Store Data in Pathway Table for Streaming
df = pd.DataFrame({
    "title": [article["title"] for article in news_data],
    "url": [article["url"] for article in news_data]
})

news_table = pw.debug.table_from_pandas(df)  # ✅ Corrected Pathway Method

pw.debug.compute_and_print(news_table)
pw.run()

# ✅ Example Queries
queries = [
    "Latest news on Apple (AAPL) stock",
    "S&P 500 performance this week",
    "Can you show me the stock market news from last week?"
]

for query in queries:
    print(f"\nQuery: {query}")
    print("Generated Answer:", generate_response(query))
