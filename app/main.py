from flask import Flask, request, jsonify, render_template, make_response
import json
import os
import openai

app = Flask(__name__)

# Load profile
with open('app/data/profile.json') as f:
    profile = json.load(f)

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_options_text():
    # Exclude 'name' and 'summary'
    keys = [k.capitalize() for k in profile.keys() if k not in ["name", "summary"]]
    return " | ".join(keys)

def get_ai_response(user_input):
    """Call OpenAI API for free-form questions."""
    try:
        prompt = f"""
You are a helpful chatbot. Answer questions based on this profile:
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
        return None

@app.route('/')
def home():
    return render_template('index.html', profile=profile)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message", "").strip()
    options_text = get_options_text()

    # Check if greeted using cookie
    greeted = request.cookies.get("greeted")

    if not greeted:
        greeting = (
            f"Hello! 👋 Hope you are having a nice day.\n"
            f"What would you like to know about Bhagath? Here are the options:\n"
            f"{options_text}"
        )
        resp = make_response(jsonify({"reply": greeting}))
        resp.set_cookie("greeted", "yes")
        return resp

    lower_input = user_input.lower()

    # Handle sensitive requests
    if any(word in lower_input for word in ["salary", "ctc", "pay"]):
        reply = "For privacy and detailed salary discussions, please contact Bhagath via email: <your-email@example.com>"
    elif any(word in lower_input for word in ["resume", "cv"]):
        reply = "You can view Bhagath's resume and professional profile on LinkedIn: <your-linkedin-profile-url>"
    elif any(word in lower_input for word in ["phone", "whatsapp", "contact"]):
        reply = "For privacy reasons, please connect with Bhagath via email for contact details: <your-email@example.com>"
    elif any(word in lower_input for word in ["bye", "exit", "end"]):
        reply = "Thank you for chatting! Have a nice day! 👋"
    else:
        # Check if user typed one of the JSON keys (Education, Experience, Skills, etc.)
        matched = False
        for key, value in profile.items():
            if key in ["name", "summary"]:
                continue
            if key.lower() in lower_input or any(word in lower_input for word in key.lower().split("_")):
                if isinstance(value, list):
                    reply = f"{key.capitalize()}: " + ", ".join(value)
                else:
                    reply = f"{key.capitalize()}: {value}"
                matched = True
                break

        # If no direct match, fallback to OpenAI
        if not matched:
            ai_resp = get_ai_response(user_input)
            if ai_resp:
                reply = ai_resp
            else:
                reply = profile.get("Sorry, seems like there is an issue at present. Please contact Bhagath directly via mail or LikedIn")

    # Always show available options unless chat ended
    if not any(word in lower_input for word in ["bye", "exit", "end"]):
        reply += f"\n\nYou can also ask about: {options_text}"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
