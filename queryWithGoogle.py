from colorama import Fore
import requests
from bs4 import BeautifulSoup  # Assuming BeautifulSoup is being used for scraping
from serpapi import GoogleSearch  # Assuming serpapi is used for get_organic_results
import openai  # Assuming openai is used for GPT-3 API calls
import os

os.environ['OPENAI_API_KEY'] = '************'

client = openai.Client()


def generate_google_search_query(user_input):
    """
    Uses GPT-4-turbo to convert user input into a Google Search query.
    """
    prompt = f"Convert the following user query into an optimized Google Search query: '{user_input}'"

    try:
        completion = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system",
                 "content": "You are a Google Search Expert. Your task is to convert unstructured user inputs to optimized Google search queries. Example: USER INPUT: 'Why was Sam Altman fired from OpenAI?' OPTIMIZED Google Search Query: 'Sam Altman Fired OpenAI'"},
                {"role": "user", "content": prompt}
            ]
        )

        # Accessing the response directly
        if completion.choices:
            response_message = completion.choices[0].message
            if hasattr(response_message, 'content'):
                return response_message.content.strip()
            else:
                return "No content in response."
        else:
            return "No response from GPT-4 Turbo."
    except Exception as e:
        print(f"Error in generating Google search query: {e}")
        return None


def get_organic_results(query, num_results=3, location="United States"):
    params = {
        "q": query,
        "tbm": "nws",
        "num": str(num_results),
        "location": location,
        "api_key": "*************************"
    }

    search = GoogleSearch(params)
    print(search)
    results = search.get_dict()
    print(results)
    news_results = results.get('news_results', [])

    urls = [result['link'] for result in news_results]

    return urls


# Define the function to scrape data from a URL and return a URL
def scrape_website(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        page_content = response.content
        soup = BeautifulSoup(page_content, 'html.parser')
        paragraphs = soup.find_all('p')
        scraped_data = [p.get_text() for p in paragraphs]
        formatted_data = "\n".join(scraped_data)
        return url, formatted_data  # Return both URL and content
    else:
        return url, "Failed to retrieve the webpage"


# Create an Assistant with a specific name
assistant = client.beta.assistants.create(
    name="GoogleGPT",  # Set the name of your assistant here
    instructions="You are an assistant capable of fetching and displaying news articles based on user queries.",
    model="gpt-4-1106-preview",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_organic_results",
                "description": "Fetch news URLs based on a search query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {"type": "integer", "description": "Number of results to return"},
                        "location": {"type": "string", "description": "Location for search context"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "scrape_website",
                "description": "Scrape a website and return its content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to scrape"}
                    },
                    "required": ["url"]
                }
            }
        }
        # ... possibly more tools or other configurations follow
    ]
)

while True:
    user_query = input(Fore.CYAN + "Please enter your query (type 'exit' to quit): ")
    if user_query.lower() == 'exit':
        break

    # Generate a Google Search query from the user input
    google_search_query = generate_google_search_query(user_query)
    print(f"Converted Google Search Query: {google_search_query}")

    if google_search_query:
        # Fetch news URLs based on the generated query
        news_urls = get_organic_results(google_search_query)

        # Scrape content from the first URL (for demonstration)
        if news_urls:
            url, news_content = scrape_website(news_urls[0])  # Get URL and content

            # Prepare grounding context
            grounding_context = f"Context: {news_content}\nUser Query: {user_query}"
            print(grounding_context)

            # Completion request with grounding context
            completion = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant, always return only the essential parts that answers the USER original USER query, but add 3 bullet points to backup your reasoning for the answer."},
                    {"role": "user", "content": grounding_context}
                ]
            )

            # Process and display the response
            response = completion.choices[0].message.content if completion.choices[0].message else ""
            print(Fore.YELLOW + "Response GPT-4")
            print(Fore.YELLOW + response)
        else:
            print("No news URLs found.")
    else:
        print("Failed to generate a Google search query.")
