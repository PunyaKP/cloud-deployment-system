from flask import Flask, render_template, request,jsonify, send_from_directory
import os
import time
import random

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
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

    print("Saved at:", filepath)

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
    from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/metrics')
def metrics():
    cpu_value = getattr(app, "cpu_value", 50)
    cpu_value += random.randint(-5, 5)
    cpu_value = max(10, min(90, cpu_value))
    app.cpu_value = cpu_value

    memory_value = getattr(app, "mem_value", 40)
    memory_value += random.randint(-3, 3)
    memory_value = max(20, min(80, memory_value))
    app.mem_value = memory_value

    return jsonify({
        "cpu": cpu_value,
        "memory": memory_value
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

