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

    # Keywords for various categories
    experience_keywords = ["experience", "career", "worked", "background", "your experience"]
    education_keywords = ["education", "degree", "study", "qualification"]
    skills_keywords = ["skills", "technologies", "abilities"]
    certifications_keywords = ["certifications", "certified", "accreditations"]
    achievements_keywords = ["achievements", "success", "accomplishments", "awards"]
    about_keywords = ["about", "yourself", "who are you", "introduce"]

    if any(word in user_input for word in education_keywords):
        response = profile['education']
    elif any(word in user_input for word in experience_keywords):
        response = profile['experience']
    elif any(word in user_input for word in skills_keywords):
        response = f"My core skills include: {', '.join(profile['skills'])}."
    elif any(word in user_input for word in certifications_keywords):
        response = f"I am {', '.join(profile['certifications'])}."
    elif any(word in user_input for word in achievements_keywords):
        response = "I have achieved significant results in automation, CI/CD, and cloud-native deployments throughout my career."
    elif any(word in user_input for word in about_keywords):
        response = profile['summary']

    return jsonify({"reply": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
