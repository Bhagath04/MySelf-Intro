from flask import Flask, request, jsonify, render_template
import json
import os
from openai import OpenAI
from openai.error import AuthenticationError, APIError, RateLimitError, PermissionDeniedError

app = Flask(__name__)

# Load Bhagath's profile from JSON
with open('app/data/profile.json') as f:
    profile = json.load(f)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_response(user_input):
    """Fetch AI-generated response or fallback to JSON profile."""
    try:
        prompt = f"""
You are an AI assistant that answers questions about this DevOps professional:
{json.dumps(profile, indent=2)}

Answer the user's question politely and clearly.
If the question is not related to the profile, suggest connecting with Bhagath directly.
User: {user_input}
AI:
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly and professional AI assistant helping users learn about Bhagath Gajbinkar."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except (AuthenticationError, APIError, RateLimitError, PermissionDeniedError):
        # Fallback when quota exceeded or API key invalid
        return (
            f"Sorry, I’m currently unable to access live AI responses. "
            f"But here’s a quick summary of Bhagath:\n\n"
            f"{profile['summary']}\n\n"
            f"He is a {profile['experience']} "
            f"Skilled in {', '.join(profile['skills'])}. "
            f"For more details, please connect directly with Bhagath."
        )

@app.route('/')
def home():
    return render_template('index.html', profile=profile)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat input from the frontend."""
    user_input = request.json['message']

    # Privacy and sensitive information filter
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
