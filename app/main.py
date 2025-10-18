from flask import Flask, request, jsonify, render_template
import json
import os
import openai
from openai.error import OpenAIError, AuthenticationError, RateLimitError

app = Flask(__name__)

# --- Load profile ---
with open('app/data/profile.json', 'r', encoding='utf-8') as f:
    profile = json.load(f)

# --- Load resume text if available ---
resume_text = ""
resume_path = "app/data/Bhagath Gajbinkar_Resume.txt"
if os.path.exists(resume_path):
    with open(resume_path, 'r', encoding='utf-8') as r:
        resume_text = r.read()

# --- Set OpenAI API key from environment (Render/GitHub Secret) ---
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_response(user_input):
    """
    Gets chatbot response from OpenAI API.
    Falls back to local profile/resume data on quota or auth errors.
    """
    try:
        prompt = f"""
You are Bhagath Gajbinkar’s AI assistant. 
Answer based on the following profile and resume information:

PROFILE:
{json.dumps(profile, indent=2)}

RESUME:
{resume_text}

User: {user_input}
Bot:
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message['content'].strip()

    except openai.error.RateLimitError:
        # When quota or rate limit is exceeded
        return (
            f"Currently I’m unable to access AI responses. "
            f"Here’s some info about Bhagath:\n\n"
            f"{profile['summary']}\n\n"
            f"For more detailed discussions or project collaborations, "
            f"please connect with him directly via phone or WhatsApp."
        )
    except openai.error.AuthenticationError:
        return (
            "Authentication error occurred — the API key may be missing or invalid. "
            "Please check the deployment configuration."
        )
    except Exception as e:
        return f"Sorry, something went wrong: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html', profile=profile)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    # Add logic to detect if user is asking too many details
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
