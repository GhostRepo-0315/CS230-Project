from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import requests
import random

# 节点服务器列表
NODE_SERVERS = [
    "http://52.53.207.217:7001",
    "http://18.144.171.222:7001",
    "http://54.67.117.71:7001"
]
with open('action_list.txt', 'r') as file:
    loaded_action_list = file.read().splitlines()
METADATA_FILE = "uploads/metadata.json"
# 加载已有的 metadata（如果有的话）
if os.path.exists(METADATA_FILE):
    try:
        with open(METADATA_FILE, "r") as f:
            content = f.read().strip()  # 读取内容并去掉空白字符
            file_metadata = json.loads(content) if content else {}  # 避免解析空文件
    except json.JSONDecodeError:
        file_metadata = {}  # 如果 JSON 解析失败，重新初始化
else:
    file_metadata = {}

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

UPLOAD_FOLDER = "uploads"
CHUNK_FOLDER = "uploads/chunks"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHUNK_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return send_from_directory(app.static_folder, 'index.html')

### **Step 1: 处理文件元数据**
@app.route("/upload/metadata", methods=["POST"])
def upload_metadata():
    data = request.json
    file_id = data.get("fileId")
    file_name = data.get("fileName")
    total_chunks = data.get("totalChunks")

    if not file_id or not file_name or total_chunks is None:
        return jsonify({"error": "Invalid metadata"}), 400

    file_metadata[file_id] = {
        "file_name": file_name,
        "total_chunks": total_chunks,
        "uploaded_chunks": [],
        "chunks": {}
    }

    # ✅ 每次写入 metadata.json
    with open(METADATA_FILE, "w") as f:
        json.dump(file_metadata, f)

    return jsonify({"message": "Metadata received", "fileId": file_id})

### **Step 2: 分配分片到节点服务器**
@app.route("/upload/assign", methods=["POST"])
def assign_chunk():
    data = request.json
    file_id = data.get("fileId")
    chunk_index = data.get("chunkIndex")

    if not file_id or chunk_index is None:
        return jsonify({"error": "Invalid request"}), 400

    # 随机选择一个节点服务器
    # node_server = random.choice(NODE_SERVERS)

    # 基于DRL agent选择节点服务器
    node_server = loaded_action_list[chunk_index]
    
    # 记录分片分配的节点服务器
    if file_id not in file_metadata:
        return jsonify({"error": "File ID not found in metadata"}), 400
    file_metadata[file_id]["chunks"][chunk_index] = node_server

    with open(METADATA_FILE, "w") as f:
        json.dump(file_metadata, f)

    return jsonify({"node_server": node_server})

### **Step 3: 处理文件分块上传**
@app.route("/upload/update", methods=["POST"])
def update_metadata():
    data = request.json
    file_id = data.get("fileId")
    chunk_index = data.get("chunkIndex")
    print(chunk_index)
    if not file_id or chunk_index is None:
        return jsonify({"error": "Invalid request"}), 400

    # 确保 metadata 文件存在
    if not os.path.exists(METADATA_FILE):
        return jsonify({"error": "metadata.json missing"}), 500

    # 读取 metadata
    try:
        with open(METADATA_FILE, "r") as f:
            content = f.read().strip()
            file_metadata = json.loads(content) if content else {}
    except Exception as e:
        return jsonify({"error": f"Failed to read metadata: {e}"}), 500

    # 确保 file_id 存在
    if file_id not in file_metadata:
        return jsonify({"error": "File ID not found"}), 400

    # 更新已上传的分片信息
    if "uploaded_chunks" not in file_metadata[file_id]:
        file_metadata[file_id]["uploaded_chunks"] = []
    if chunk_index not in file_metadata[file_id]["uploaded_chunks"]:
        file_metadata[file_id]["uploaded_chunks"].append(chunk_index)
        print(file_metadata[file_id]["uploaded_chunks"])
    # 写回 metadata
    try:
        with open(METADATA_FILE, "w") as f:
            json.dump(file_metadata, f, indent=4)
    except Exception as e:
        return jsonify({"error": f"Failed to write metadata: {e}"}), 500
    return jsonify({"message": "Metadata updated"})

### **Step 4: 合并分块**
@app.route("/upload/complete", methods=["POST"])
def complete_upload():
    file_id = request.json.get("fileId")

    # 重新读取 metadata.json，确保数据是最新的
    try:
        with open(METADATA_FILE, "r") as f:
            content = f.read().strip()
            file_metadata = json.loads(content) if content else {}
    except Exception as e:
        return jsonify({"error": f"Failed to read metadata: {e}"}), 500

    if file_id not in file_metadata:
        return jsonify({"error": "File ID not found"}), 400

    metadata = file_metadata[file_id]
    file_name = metadata["file_name"]
    total_chunks = metadata["total_chunks"]
    uploaded_chunks = metadata.get("uploaded_chunks", [])[0]

    print(f"✅ Metadata from file: {metadata}")  # 打印从文件中读取的 metadata

    # 确保所有块都已上传
    print(total_chunks, uploaded_chunks)
    missing_chunks = total_chunks - uploaded_chunks - 1
    if missing_chunks:
        return jsonify({"error": "Missing some chunks", "missing_chunks": list(missing_chunks)}), 400

    # 合并文件
    final_path = os.path.join(UPLOAD_FOLDER, file_name)
    try:
        with open(final_path, "wb") as final_file:
            for i in range(total_chunks):
                # 获取分片存储的节点服务器
                chunks = {int(k): v for k, v in file_metadata[file_id]["chunks"].items()}
                node_server = chunks[i]
                # node_server = file_metadata[file_id]["chunks"][i]
                # 从节点服务器下载分片
                chunk_url = f"{node_server}/uploads/chunks/{file_id}_chunk_{i}"
                response = requests.get(chunk_url)
                if response.status_code != 200:
                    return jsonify({"error": f"Failed to fetch chunk {i} from {node_server}"}), 500
                final_file.write(response.content)
    except Exception as e:
        import traceback
        error_message = traceback.format_exc()  # 获取详细的异常信息
        print(f"File merge failed: {error_message}")  # 打印到日志或控制台
        return jsonify({"error": f"File merge failed: {str(e)}"}), 500

    # 删除 metadata 记录
    del file_metadata[file_id]
    try:
        with open(METADATA_FILE, "w") as f:
            json.dump(file_metadata, f, indent=4)
    except Exception as e:
        return jsonify({"error": f"Failed to update metadata: {e}"}), 500

    return jsonify({"message": "File upload complete", "fileName": file_name})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7001)
