from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return jsonify({"message": "Flask backend is running!"})

# 接收文件分片
@app.route("/upload/chunk", methods=["POST"])
def upload_chunk():
    file_id = request.form.get("fileId")
    chunk_index = request.form.get("chunkIndex")
    chunk = request.files.get("chunk")

    if not file_id or chunk_index is None or not chunk:
        return jsonify({"error": "Missing chunk data"}), 400

    chunk_filename = f"{file_id}_chunk_{chunk_index}"
    chunk_path = os.path.join(UPLOAD_FOLDER, chunk_filename)

    try:
        chunk.save(chunk_path)
        # 将分片存储到 HDFS（这里假设 HDFS 已经配置好）
        # 例如：使用 Hadoop 的 Python API 或调用 HDFS 命令
        # 这里仅模拟存储
        print(f"Storing chunk {chunk_index} to HDFS...")
    except Exception as e:
        return jsonify({"error": f"Failed to save chunk: {e}"}), 500

    return jsonify({"message": f"Chunk {chunk_index} uploaded"})

from flask import send_from_directory

# 提供分片文件下载
@app.route("/uploads/chunks/<filename>", methods=["GET"])
def download_chunk(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7001)
