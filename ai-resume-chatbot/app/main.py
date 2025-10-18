from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)

with open('app/data/profile.json') as f:
    profile = json.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message'].lower()
    response = "I'm not sure I understand that."

    if "education" in user_input:
        response = profile['education']
    elif "experience" in user_input or "career" in user_input:
        response = profile['experience']
    elif "skills" in user_input:
        response = f"My core skills include: {', '.join(profile['skills'])}."
    elif "certifications" in user_input:
        response = f"I’m {', '.join(profile['certifications'])}."
    elif "about" in user_input or "yourself" in user_input:
        response = profile['summary']

    return jsonify({"reply": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
