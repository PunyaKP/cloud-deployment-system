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

    # Check file
    if not file or file.filename == "":
        return render_template("index.html", message="❌ No file selected")

    # Save file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Git commands
        os.system("git add .")
        os.system('git commit -m "Auto deploy commit"')
        os.system("git push origin main")

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

    except Exception as e:
        return f"Error occurred: {e}"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)