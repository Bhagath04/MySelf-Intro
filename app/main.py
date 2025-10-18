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
    """
    Try OpenAI API for dynamic responses.
    If it fails, fallback to JSON-based intelligent answers.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional AI assistant answering questions about Bhagath Gajbinkar's profile."
                },
                {
                    "role": "user",
                    "content": f"Answer based on this profile:\n{json.dumps(profile)}\nUser question: {user_input}"
                }
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message['content'].strip()
    except openai.error.OpenAIError:
        # Fallback: check for specific keywords in JSON
        user_input_lower = user_input.lower()
        if "experience" in user_input_lower or "career" in user_input_lower:
            return f"Hello! Regarding my experience: {profile.get('experience', '')}"
        elif "education" in user_input_lower or "degree" in user_input_lower:
            return f"My education background: {profile.get('education', '')}"
        elif "skills" in user_input_lower:
            return f"My skills include: {', '.join(profile.get('skills', []))}."
        elif "certifications" in user_input_lower:
            return f"My certifications: {', '.join(profile.get('certifications', []))}."
        elif "about" in user_input_lower or "yourself" in user_input_lower:
            return profile.get('summary', '')
        else:
            return (
                f"Sorry, I can't answer that with AI right now. "
                f"Here's some info from my profile: {profile.get('summary', '')}"
            )

@app.route('/')
def home():
    return render_template('index.html', profile=profile)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')

    # Detect private/contact questions
    if any(word in user_input.lower() for word in ["salary", "phone", "number", "contact", "whatsapp"]):
        response = (
            "For privacy and detailed discussions, please connect directly via phone or WhatsApp. "
            "Bhagath will be happy to assist you personally."
        )
    # Detect initial greeting (empty message or first connection)
    elif user_input.strip() == "":
        response = (
            "Hello! 👋 I am Bhagath's AI assistant. You can ask me about his experience, skills, certifications, or any professional details."
        )
    else:
        response = get_ai_response(user_input)

    return jsonify({"reply": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
