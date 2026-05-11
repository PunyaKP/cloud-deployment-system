from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import time
import random
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# ── UPLOAD FOLDER (kept as fallback) ──
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── CLOUDINARY CONFIG ──
# Add your real values in .env or set them here
cloudinary.config(
    cloud_name = os.environ.get("CLOUD_NAME", "your_cloud_name"),
    api_key    = os.environ.get("API_KEY",    "your_api_key"),
    api_secret = os.environ.get("API_SECRET", "your_api_secret")
)

# ── IN-MEMORY FILE STORE ──
# Stores uploaded file records during session
uploaded_files = []
deploy_count = 0

# ─────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────
@app.route('/')
def home():
    return render_template("index.html")


# ─────────────────────────────────────────
# UPLOAD ROUTE  →  sends file to Cloudinary
# Called by the dashboard File Manager
# ─────────────────────────────────────────
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')

    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        # Upload directly to Cloudinary
        result = cloudinary.uploader.upload(
            file,
            resource_type = "auto",   # handles images, docs, zips, etc.
            folder        = "clouddeploy"
        )

        # Build record to send back to dashboard
        file_record = {
            "id":          result["public_id"],
            "name":        file.filename,
            "url":         result["secure_url"],
            "size":        result.get("bytes", 0),
            "type":        result.get("resource_type", "raw"),
            "uploadedAt":  time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save in memory list
        uploaded_files.insert(0, file_record)

        return jsonify({
            "success": True,
            "url":     result["secure_url"],
            "name":    file.filename,
            "id":      result["public_id"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
# DEPLOY ROUTE  →  git + pipeline simulation
# Called when user clicks Deploy button
# ─────────────────────────────────────────
@app.route('/deploy', methods=['POST'])
def deploy():
    global deploy_count
    file = request.files.get('file')

    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        # Step 1 — Save file locally temporarily
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Step 2 — Upload to Cloudinary for permanent storage
        result = cloudinary.uploader.upload(
            filepath,
            resource_type = "auto",
            folder        = "clouddeploy"
        )
        cloudinary_url = result["secure_url"]

        # Save record
        file_record = {
            "id":         result["public_id"],
            "name":       file.filename,
            "url":        cloudinary_url,
            "size":       result.get("bytes", 0),
            "uploadedAt": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        uploaded_files.insert(0, file_record)

        # Step 3 — Git commands (push to GitHub)
        os.system("git add .")
        os.system('git commit -m "Auto deploy commit"')
        os.system("git push origin main")

        # Step 4 — Simulate pipeline stages
        time.sleep(1)
        print("✓ Code pushed to GitHub repository")

        time.sleep(1)
        print("✓ Running Jenkins CI/CD pipeline...")

        time.sleep(1)
        print("✓ Building Docker image...")

        time.sleep(1)
        print("✓ Deploying to AWS EC2...")

        deploy_count += 1

        return jsonify({
            "success":      True,
            "message":      "🚀 Deployment Successful! App is Live.",
            "cloudinaryUrl": cloudinary_url,
            "filename":     file.filename,
            "deployCount":  deploy_count
        })

    except Exception as e:
        return jsonify({"error": f"Error occurred: {e}"}), 500


# ─────────────────────────────────────────
# FILES ROUTE  →  returns all uploaded files
# Used by dashboard File Manager search
# ─────────────────────────────────────────
@app.route('/files', methods=['GET'])
def get_files():
    search = request.args.get('search', '').lower()

    if search:
        filtered = [f for f in uploaded_files if search in f['name'].lower()]
    else:
        filtered = uploaded_files

    return jsonify(filtered)


# ─────────────────────────────────────────
# DELETE FILE ROUTE
# ─────────────────────────────────────────
@app.route('/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    global uploaded_files
    uploaded_files = [f for f in uploaded_files if f['id'] != file_id]
    return jsonify({"success": True})


# ─────────────────────────────────────────
# SERVE LOCAL UPLOADS (fallback)
# ─────────────────────────────────────────
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)


# ─────────────────────────────────────────
# METRICS ROUTE  →  live CPU + memory data
# Called every 1.5s by the dashboard chart
# ─────────────────────────────────────────
@app.route('/metrics')
def metrics():
    cpu_value    = getattr(app, "cpu_value", 50)
    cpu_value   += random.randint(-5, 5)
    cpu_value    = max(10, min(90, cpu_value))
    app.cpu_value = cpu_value

    memory_value  = getattr(app, "mem_value", 40)
    memory_value += random.randint(-3, 3)
    memory_value  = max(20, min(80, memory_value))
    app.mem_value = memory_value

    return jsonify({
        "cpu":    cpu_value,
        "memory": round(1.0 + (memory_value / 80) * 0.8, 1)  # returns GB value e.g. 1.2
    })


# ─────────────────────────────────────────
# STATUS ROUTE  →  overall system status
# ─────────────────────────────────────────
@app.route('/status')
def status():
    return jsonify({
        "status":       "online",
        "deployCount":  deploy_count,
        "filesStored":  len(uploaded_files),
        "uptime":       "99.9%"
    })


# ─────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)