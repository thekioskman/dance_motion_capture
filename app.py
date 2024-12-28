from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from compare_videos import compare_videos

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/compare", methods=["POST"])
def compare_endpoint():
    # Check if files are included in the request
    if "video1" not in request.files or "video2" not in request.files:
        return jsonify({"error": "Both video1 and video2 must be provided"}), 400

    # Save uploaded files
    video1 = request.files["video1"]
    video2 = request.files["video2"]
    video1_path = os.path.join(UPLOAD_FOLDER, video1.filename)
    video2_path = os.path.join(UPLOAD_FOLDER, video2.filename)
    video1.save(video1_path)
    video2.save(video2_path)

    try:
        # Compare videos
        result = compare_videos(video1_path, video2_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Delete uploaded files
        os.remove(video1_path)
        os.remove(video2_path)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)