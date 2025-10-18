# app/main.py
from flask import Flask, request, jsonify, render_template
import json
import os
import openai

app = Flask(__name__)

# Load profile
with open('app/data/profile.json') as f:
    profile = json.load(f)

# OpenAI key from environment variable (use GitHub Secrets)
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_response(user_input):
    """
    Sends the user's question and profile data to OpenAI Chat API
    and returns the response.
    """
    if not openai.api_key:
        return "OpenAI API key not configured. Please set the environment variable OPENAI_API_KEY."

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": f"Answer questions based on this profile:\n{json.dumps(profile, indent=2)}\nUser asked: {user_input}"}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use gpt-4 if you have access
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, something went wrong: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html', profile=profile)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    if not user_input:
        return jsonify({"reply": "Please enter a question."})

    response = get_ai_response(user_input)
    return jsonify({"reply": response})

if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible externally (Render requirement)
    app.run(host='0.0.0.0', port=5000)
