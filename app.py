from flask import Flask, render_template, request
import os
import time

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home page
@app.route('/')
def home():
    return render_template("index.html")

# Deploy route
@app.route('/deploy', methods=['POST'])
def deploy():
    file = request.files.get('file')

    if not file or file.filename == "":
        return render_template("index.html", message="❌ No file selected")

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Simulate pipeline
    print("Code pushed to GitHub repository")
    time.sleep(1)

    print("Running Jenkins CI/CD pipeline...")
    time.sleep(1)

    print("Building Docker image...")
    time.sleep(1)

    print("Deploying to AWS EC2...")
    time.sleep(1)

    return render_template("index.html", message="🚀 Deployment Successful! App is Live.")

if __name__ == '__main__':
    app.run(debug=True)