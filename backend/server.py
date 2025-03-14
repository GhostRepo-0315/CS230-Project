from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return jsonify({"message": "Flask backend is running!"})

@app.route("/upload", methods=["POST"])
def upload_file():
    print("\n Received an upload request!")  # Log incoming request
    print("Headers:", request.headers)
    print("Form Data:", request.form)
    print("Files:", request.files)

    if "files" not in request.files:
        print("No file received!")  # Log missing file
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["files"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    print(f"File '{file.filename}' uploaded successfully!")
    return jsonify({"message": "File uploaded successfully", "filename": file.filename})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7001)
