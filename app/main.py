from flask import Flask, request, jsonify, render_template
import json
import os
import openai

app = Flask(__name__)

# Load profile
with open('app/data/profile.json') as f:
    profile = json.load(f)

# OpenAI key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# To track if user has been greeted (for simplicity, global set)
greeted_users = set()

# Generate the menu options dynamically from JSON keys (except 'name' and 'summary')
def get_options_text():
    keys = [k.capitalize() for k in profile.keys() if k not in ["name", "summary"]]
    return " | ".join(keys)

def get_ai_response(user_input):
    try:
        prompt = f"""
You are a chatbot. Answer questions based on this profile:
{json.dumps(profile)}

User: {user_input}
Bot:
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None  # fallback to JSON if OpenAI fails

@app.route('/')
def home():
    return render_template('index.html', profile=profile)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message", "").strip()
    options_text = get_options_text()

    # Greet user first time
    if "first_greet" not in request.cookies:
        greeting = (
            f"Hello! 👋 Hope you are having a nice day.\n"
            f"What would you like to know about Bhagath? Here are the options:\n"
            f"{options_text}"
        )
        return jsonify({"reply": greeting})

    lower_input = user_input.lower()

    # Handle sensitive requests
    if any(word in lower_input for word in ["salary", "ctc", "pay"]):
        reply = (
            "For privacy and detailed salary discussions, please contact Bhagath via email: "
            "<your-email@example.com>"
        )
    elif any(word in lower_input for word in ["resume", "cv"]):
        reply = (
            "You can view Bhagath's resume and professional profile on LinkedIn: "
            "<your-linkedin-profile-url>"
        )
    elif any(word in lower_input for word in ["phone", "whatsapp", "contact"]):
        reply = (
            "For privacy reasons, please connect with Bhagath via email for contact details: "
            "<your-email@example.com>"
        )
    elif any(word in lower_input for word in ["bye", "exit", "end"]):
        reply = "Thank you for chatting! Have a nice day! 👋"
    else:
        # Match JSON keys dynamically
        matched = False
        for key, value in profile.items():
            if key in ["name", "summary"]:
                continue
            if key in lower_input or any(word in lower_input for word in key.split("_")):
                if isinstance(value, list):
                    reply = f"{key.capitalize()}: " + ", ".join(value)
                else:
                    reply = f"{key.capitalize()}: {value}"
                matched = True
                break

        if not matched:
            # Try OpenAI
            ai_resp = get_ai_response(user_input)
            if ai_resp:
                reply = ai_resp
            else:
                # fallback generic summary
                reply = profile.get("summary", "Sorry, I cannot answer that right now.")

    # Always append options for guided flow
    if "bye" not in lower_input and "exit" not in lower_input and "end" not in lower_input:
        reply += f"\n\nYou can also ask about: {options_text}"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
