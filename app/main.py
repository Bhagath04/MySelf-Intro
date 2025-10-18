from flask import Flask, request, jsonify, render_template
import json
import os
import openai
from openai.error import OpenAIError, AuthenticationError, RateLimitError

app = Flask(__name__)

# Load profile
with open('app/data/profile.json') as f:
    profile = json.load(f)

# OpenAI key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def fallback_response(user_input):
    """
    Generate a natural response from the local profile.json
    if OpenAI API fails.
    """
    user_input = user_input.lower()

    if "education" in user_input:
        return f"I completed {profile['education']}."
    elif "experience" in user_input or "career" in user_input:
        return f"{profile['experience']}"
    elif "skills" in user_input:
        return f"My core skills include: {', '.join(profile['skills'])}."
    elif "certifications" in user_input:
        return f"I am certified in {', '.join(profile['certifications'])}."
    elif "about" in user_input or "yourself" in user_input:
        return profile['summary']
    elif "achievement" in user_input:
        return "I have successfully managed DevOps teams and implemented automation for cloud-native deployments, improving efficiency and reliability."
    else:
        return "I’m Bhagath Gajbinkar, a DevOps professional. Feel free to ask me about my experience, skills, or education!"

def get_ai_response(user_input):
    """
    Use OpenAI ChatCompletion to respond to the user.
    If quota exceeded, fallback to local response.
    """
    if not openai.api_key:
        return fallback_response(user_input)

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": f"Answer questions based on this profile:\n{json.dumps(profile, indent=2)}\nUser asked: {user_input}"}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except (RateLimitError, OpenAIError) as e:
        # If quota exceeded or any OpenAI error, use fallback
        return fallback_response(user_input)

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
    app.run(host='0.0.0.0', port=5000)
