import streamlit as st
import requests
from bs4 import BeautifulSoup

# Plugin credentials
PLUGIN_ID = "plugin-1714808261"
API_KEY = "GOtemIr8R0smpWLMLHYNOwJDBObKcDjh"
NEWS_API_KEY = "05360b72a0324723a37579e35852fa73"

def create_chat_session():
    url = "https://gateway-dev.on-demand.io/chat/v1/sessions"
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "pluginIds": [PLUGIN_ID],
        "externalUserId": "replace_external_user_id"
    }

    response = requests.post(url, headers=headers, json=body)
    response_json = response.json()
    if 'chatSession' in response_json:
        return response_json['chatSession']['id']
    st.error(f"Failed to create chat session: {response.text}")
    return None

def submit_query(session_id, query):
    query_url = f"https://gateway-dev.on-demand.io/chat/v1/sessions/{session_id}/query"
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    query_body = {
        "endpointId": "predefined-openai-gpt4o",
        "query": query,
        "pluginIds": [PLUGIN_ID],
        "responseMode": "sync"
    }

    response = requests.post(query_url, headers=headers, json=query_body)
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get('chatMessage', {}).get('answer', 'No answer found')
    st.error(f"Failed to get query response: {response.text}")
    return None

def retrieve_text_from_url(url):
    """Extract text from the URL content after removing HTML tags."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except Exception as e:
        return f"Error retrieving text: {e}"

def get_news(api_key, company_name):
    """Fetch news articles related to the company using NewsAPI."""
    endpoint = 'https://newsapi.org/v2/everything'
    parameters = {
        'q': company_name,
        'apiKey': api_key,
        'pageSize': 5
    }
    try:
        response = requests.get(endpoint, params=parameters)
        response.raise_for_status()
        data = response.json()
        return data.get('articles', [])
    except Exception as e:
        return f"Error fetching news: {e}"

# Streamlit UI
st.title('Company News and Stock Analysis App')
company_name = st.text_input('Enter a company name:', '')

if st.button('Analyze Company'):
    if company_name:
        session_id = create_chat_session()
        if session_id:
            query = f"what is the market price of {company_name}?"
            answer = submit_query(session_id, query)
            if answer:
                st.write(f"Market price of {company_name}: {answer}")

        articles = get_news(NEWS_API_KEY, company_name)
        if isinstance(articles, str):
            st.error(articles)
        else:
            for article in articles:
                full_text = retrieve_text_from_url(article['url'])
                st.write("Article Title:", article['title'])
                st.write("Article Content:", full_text)
    else:
        st.error('Please enter a company name.')
