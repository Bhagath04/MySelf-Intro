from flask import Flask, request, jsonify, render_template, make_response
import json

app = Flask(__name__)

# Load profile
with open('app/data/profile.json', encoding='utf-8') as f:
    profile = json.load(f)

@app.route('/')
def home():
    return render_template('index.html', profile=profile)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message", "").strip().lower()

    greeted = request.cookies.get("greeted")
    if not greeted:
        greeting = (
            f"Hello! 👋 Hope you are having a nice day.\n"
            f"You can ask me about Education, Experience, Skills, Certifications, or my Profile."
        )
        resp = make_response(jsonify({"reply": greeting}))
        resp.set_cookie("greeted", "yes")
        return resp

    # Greeting keywords
    if any(word in user_input for word in ["hello", "hi", "hey"]):
        reply = "Hello! 👋 Hope you are having a nice day. Ask me about my Profile, Experience, Skills, Education, or Certifications."

    # Fetch profile summary
    elif "profile" in user_input or "about" in user_input or "tell me about bhagath" in user_input:
        reply = profile.get("summary", "Summary not available.")

    # Fetch experience
    elif "experience" in user_input:
        reply = profile.get("experience", "Experience not available.")

    # Fetch certifications
    elif "certification" in user_input or "certifications" in user_input:
        reply = "Certifications: " + ", ".join(profile.get("certifications", []))

    # Fetch skills
    elif "skill" in user_input or "skills" in user_input:
        reply = "Skills: " + ", ".join(profile.get("skills", []))

    # Fetch education
    elif "education" in user_input:
        reply = profile.get("education", "Education details not available.")

    # Ending chat
    elif any(word in user_input for word in ["bye", "exit", "end"]):
        reply = "Thank you for chatting! Have a nice day! 👋"

    # Anything else
    else:
        reply = (
            "For other queries like salary, resume, or contact details, "
            "please reach out directly via email: <your-email@example.com>."
        )

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
