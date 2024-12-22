import os
import requests
from datetime import datetime
import json


def get_openai_response(openai_client, message: str) -> str:
    """
    Sends a message to the OpenAI API and returns the assistant's response.

    Args:
        message (str): The user's input message.

    Returns:
        str: The assistant's response.
    """
    # Create a list of messages for the conversation
    messages = [
        {"role": "user", "content": message}
    ]

    # Send the request to the OpenAI API
    response = openai_client.chat.completions.create(
        model="o1-preview",  
        messages=messages,
        temperature=0.05,
    )

    # Extract and return the assistant's response
    return response.choices[0].message.content.strip()


def query_perplexity(query: str, search_recency_filter: str = "week", retries: int = 3):
    """
    Use Perplexity to fetch the most up-to-date information.
    Adds a simple retry mechanism for graceful fault tolerance.
    """

    import time  # for adding delays between retries

    url = "https://api.perplexity.ai/chat/completions"
    api_key = os.getenv("PERPLEXITY_API_KEY")

    adage = f"!!!! Current date: {datetime.now().strftime('%Y-%m-%d')} !!!!\
    !!!! LARGE PENALTY FOR USING SECONDARY OR UNRELIABLE SOURCES, or MAKINGUP ANY FAKE INFORMATION !!!!\
    !!!! INCLUDE AS MUCH AS ACTUAL, MOST UP TO DATE NUMERICAL DATA AS POSSIBLE !!!!\
    !!!! Some of the main primary sources: wall street journal, bloomberg, financial times, reuters, cnbc, bloomberg, foreign affairs,\
    blackrock, blackstone, jpmorgan, goldman sachs, citigroup, wells fargo, american express, mastercard, visa, paypal, square, etc. !!!!\
    Use only highly reputable sources from best news and market news sources for the following query. DO NOT USE SECONDARY OR UNRELIABLE SOURCES: \n"

    query = adage + query
    payload = {
        "model": "llama-3.1-sonar-large-128k-online",
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": query}
        ],
        "temperature": 0.02,
        "top_p": 0.9,
        "return_citations": True,
        "search_domain_filter": ["perplexity.ai"],
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": search_recency_filter,
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Retry loop for graceful fault tolerance
    for attempt in range(1, retries + 1):
        try:
            response = requests.request("POST", url, json=payload, headers=headers)

            if response.status_code == 200 and response.text:
                return json.loads(response.text)
            else:
                print(f"Attempt {attempt} failed with status code {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Attempt {attempt} encountered an error: {e}")

        if attempt < retries:
            # Optional: you can implement exponential backoff
            print(f"Retrying in 2 seconds... (Attempt {attempt}/{retries})")
            time.sleep(2)

    # If all retries fail
    print(f"All {retries} attempts failed. Please try again later.")
    return "Failed to query Perplexity"