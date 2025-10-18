import os
import json
import openai
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Load profile
with open('app/data/profile.json') as f:
    profile = json.load(f)

# OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_response(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional AI assistant that answers questions about Bhagath Gajbinkar's profile."
                },
                {
                    "role": "user",
                    "content": f"Answer questions based on this profile:\n{json.dumps(profile)}\nUser: {user_input}"
                }
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message['content'].strip()
    except openai.error.OpenAIError:
        # Fallback response if API fails (quota exceeded etc.)
        return (
            "I’m currently unable to answer detailed questions at present. "
            "For more information, please connect with me via phone or WhatsApp."
        )

@app.route('/')
def home():
    return render_template('index.html', profile=profile)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']

    # Handle sensitive/private info questions
    if any(word in user_input.lower() for word in ["salary", "phone", "number", "contact", "whatsapp"]):
        response = (
            "For privacy and detailed discussions, please connect directly via phone or WhatsApp. "
            "Bhagath will be happy to assist you personally."
        )
    else:
        response = get_ai_response(user_input)

    return jsonify({"reply": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
