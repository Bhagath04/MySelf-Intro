from flask import Flask, render_template
import json
import os

app = Flask(__name__)

# Path to your JSON file
PROFILE_PATH = os.path.join(os.path.dirname(__file__), "data", "profile.json")

# Load data from JSON file
def load_profile():
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)

@app.route("/")
def home():
    profile = load_profile()
    return render_template("index.html", profile=profile)

if __name__ == "__main__":
    app.run(debug=True)
