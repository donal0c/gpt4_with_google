
from serpapi import GoogleSearch
import json

def get_organic_results(query, num_results=3, location="United States"):
    print(f"Debug: Performing search with query: {query}")
    params = {
        "q": query,
        "tbm": "nws",
        "num": str(num_results),
        "location": location,
        "api_key": "your-serpapi-key"  # Replace with your actual SerpApi key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    print(f"Debug: Raw SerpApi response: {json.dumps(results, indent=2)}")

    news_results = results.get('news_results', [])

    if not news_results:
        print("Debug: No news results found in the SerpApi response.")
    else:
        print(f"Debug: Found {len(news_results)} news results.")

    urls = [result['link'] for result in news_results]

    return urls

# Test the function with a sample query to see if it's working correctly.
sample_query = "OpenAI launches new model"
get_organic_results(sample_query)  # This is a sample test call and should not be in the production code.
