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
    prompt = f"""
You are a chatbot. Answer questions based on this profile:
{json.dumps(profile)}

User: {user_input}
Bot:
"""
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].text.strip()

@app.route('/')
def home():
    return render_template('index.html', profile=profile)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    response = get_ai_response(user_input)
    return jsonify({"reply": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
