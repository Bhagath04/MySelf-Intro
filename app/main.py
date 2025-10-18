from flask import Flask, request, jsonify, render_template
import json
import os
import openai

app = Flask(__name__)

# Load profile
with open('app/data/profile.json') as f:
    profile = json.load(f)

# OpenAI key from environment variable (GitHub Secrets)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Track first interaction
first_interaction_done = False

def get_ai_response(user_input):
    """
    Uses OpenAI to respond. If quota is exceeded or error, fallback to JSON profile.
    """
    # Define keyword mapping for JSON fallback
    fallback_map = {
        "experience": profile["experience"],
        "education": profile.get("education", ""),
        "skills": ", ".join(profile.get("skills", [])),
        "certifications": ", ".join(profile.get("certifications", [])),
        "summary": profile["summary"],
        "name": profile["name"]
    }

    # If user asks about contact details
    if any(word in user_input.lower() for word in ["phone", "number", "contact", "whatsapp"]):
        return (
            "For privacy and detailed discussions, please connect directly via phone or WhatsApp. "
            "Bhagath will be happy to assist you personally."
        )

    # If user ends chat
    if any(word in user_input.lower() for word in ["bye", "exit", "thank"]):
        return "It was nice chatting with you! Have a great day! 👋"

    # Fallback to profile if keywords match
    for key in fallback_map:
        if key in user_input.lower():
            return fallback_map[key]

    # Try OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant answering questions about Bhagath Gajbinkar using this profile: {json.dumps(profile)}"},
                {"role": "user", "content": user_input}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception:
        # fallback to generic answer from profile
        return profile["summary"]


@app.route('/')
def home():
    return render_template('index.html', profile=profile)


@app.route('/chat', methods=['POST'])
def chat():
    global first_interaction_done
    user_input = request.json['message']

    # Add greeting on first user message
    if not first_interaction_done:
        first_interaction_done = True
        greeting = (
            "Hello! 👋 Hope you are having a nice day. "
        )
        reply = greeting + " " + get_ai_response(user_input)
    else:
        reply = get_ai_response(user_input)

    return jsonify({"reply": reply})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
