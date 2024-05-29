from flask import Flask, request, render_template
import requests

app = Flask(__name__)

# Your API credentials
PLUGIN_ID = "plugin-1714808261"
API_KEY = "GOtemIr8R0smpWLMLHYNOwJDBObKcDjh"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_query = request.form['query']
    
    # Create Chat Session API
    url = "https://gateway-dev.on-demand.io/chat/v1/sessions"
    headers = {
        "apikey": API_KEY,  # Ensure the apikey is included
        "Content-Type": "application/json"
    }
    body = {
        "pluginIds": [PLUGIN_ID],
        "externalUserId": "replace_external_user_id"  
    }

    response = requests.post(url, headers=headers, json=body)
    print(response.text)  
    
    response_json = response.json()
    if 'chatSession' not in response_json:
        return render_template('error.html', message="Invalid response structure.", details=response.text)

    session_id = response_json['chatSession']['id']

    # Answer Query API
    query_url = f"https://gateway-dev.on-demand.io/chat/v1/sessions/{session_id}/query"
    query_body = {
        "endpointId": "predefined-openai-gpt4o",
        "query": user_query,
        "pluginIds": [PLUGIN_ID],
        "responseMode": "sync"
    }

    response = requests.post(query_url, headers=headers, json=query_body)

    if response.status_code != 200:
        return render_template('error.html', message="Failed to get query response.", details=response.text)

    response_data = response.json()

    # Extract the answer
    answer = response_data.get('chatMessage', {}).get('answer', 'No answer found')

    return render_template('result.html', query=user_query, answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
