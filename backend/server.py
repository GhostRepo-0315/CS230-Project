from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json

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

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

UPLOAD_FOLDER = "uploads"
CHUNK_FOLDER = "uploads/chunks"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHUNK_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return jsonify({"message": "Flask backend is running!"})

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
        "uploaded_chunks": [],  # 使用列表代替 set 以便 JSON 序列化
    }

    # ✅ 每次写入 metadata.json
    with open(METADATA_FILE, "w") as f:
        json.dump(file_metadata, f)

    print("qnmd")

    return jsonify({"message": "Metadata received", "fileId": file_id})

### **Step 2: 处理文件分块上传**
# @app.route("/upload/chunk", methods=["POST"])
# def upload_chunk():
#     file_id = request.form.get("fileId")
#     chunk_index = request.form.get("chunkIndex")
#     chunk = request.files.get("chunk")

#     print(f"\n🔹 Received chunk {chunk_index} for file ID: {file_id}")
    
#     if not file_id or chunk_index is None or not chunk:
#         return jsonify({"error": "Missing chunk data"}), 400

#     chunk_index = int(chunk_index)
#     chunk_filename = f"{file_id}_chunk_{chunk_index}"
#     chunk_path = os.path.join(CHUNK_FOLDER, chunk_filename)

#     # chunk.save(chunk_path)  # 保存分块

#     # # 记录已上传的块
#     # if file_id in file_metadata:
#     #     file_metadata[file_id]["uploaded_chunks"].append(chunk_index)

#      # ✅ 保存分块
#     try:
#         chunk.save(chunk_path)
#         print(f"✅ Chunk {chunk_index} saved to {chunk_path}")  # 打印成功信息
#     except Exception as e:
#         print(f"❌ Failed to save chunk: {e}")
#         return jsonify({"error": "Failed to save chunk"}), 500

#     # ✅ 读取 metadata.json 并更新已上传的分块
#     with open(METADATA_FILE, "r") as f:
#         content = f.read().strip()
#         file_metadata = json.loads(content) if content else {}

#     if file_id in file_metadata:
#         if chunk_index not in file_metadata[file_id]["uploaded_chunks"]:
#             file_metadata[file_id]["uploaded_chunks"].append(chunk_index)

#     # ✅ 更新 metadata.json
#     with open(METADATA_FILE, "w") as f:
#         json.dump(file_metadata, f, indent=4)

#     return jsonify({"message": f"Chunk {chunk_index} uploaded"})
@app.route("/upload/chunk", methods=["POST"])
# def upload_chunk():
#     file_id = request.form.get("fileId")
#     chunk_index = request.form.get("chunkIndex")
#     chunk = request.files.get("chunk")

#     if not file_id or chunk_index is None or not chunk:
#         return jsonify({"error": "Missing chunk data"}), 400

#     chunk_index = int(chunk_index)
#     chunk_filename = f"{file_id}_chunk_{chunk_index}"
#     chunk_path = os.path.join(CHUNK_FOLDER, chunk_filename)

#     # ✅ 保存分块
#     chunk.save(chunk_path)
#     print(f"✅ Chunk {chunk_index} saved to {chunk_path}")

#     # ✅ 读取 metadata.json，避免数据丢失
#     try:
#         with open(METADATA_FILE, "r") as f:
#             content = f.read().strip()
#             file_metadata = json.loads(content) if content else {}
#     except Exception as e:
#         print(f"❌ Failed to read metadata.json: {e}")
#         file_metadata = {}

#     # ✅ 确保 `file_id` 存在
#     if file_id not in file_metadata:
#         print(f"⚠️ File ID {file_id} not found in metadata, creating new entry.")
#         file_metadata[file_id] = {
#             "file_name": file_id,
#             "total_chunks": 0,  # 🚨 这里要正确填充
#             "uploaded_chunks": []
#         }

#     # ✅ 确保 `uploaded_chunks` 是一个 **列表**
#     if "uploaded_chunks" not in file_metadata[file_id]:
#         file_metadata[file_id]["uploaded_chunks"] = []

#     # ✅ 只添加 `chunkIndex`，避免重复
#     if chunk_index not in file_metadata[file_id]["uploaded_chunks"]:
#         file_metadata[file_id]["uploaded_chunks"].append(chunk_index)

#     # 记录已上传的 chunk
#     if file_id in file_metadata:
#         file_metadata[file_id]["uploaded_chunks"].append(chunk_index)

#     # 🚀 **保存 metadata.json**
#     try:
#         with open(METADATA_FILE, "w") as f:
#             json.dump(file_metadata, f, indent=4)
#         print(f"✅ metadata.json updated successfully for {file_id}")
#     except Exception as e:
#         print(f"❌ Failed to write metadata.json: {e}")

#     return jsonify({"message": f"Chunk {chunk_index} uploaded"})
def upload_chunk():
    file_id = request.form.get("fileId")
    chunk_index = request.form.get("chunkIndex")
    chunk = request.files.get("chunk")

    if not file_id or chunk_index is None or not chunk:
        return jsonify({"error": "Missing chunk data"}), 400

    chunk_index = int(chunk_index)
    chunk_filename = f"{file_id}_chunk_{chunk_index}"
    chunk_path = os.path.join(CHUNK_FOLDER, chunk_filename)

    # ✅ **保存分块**
    chunk.save(chunk_path)
    print(f"✅ Chunk {chunk_index} saved to {chunk_path}")

    # ✅ **读取 metadata.json**
    try:
        with open(METADATA_FILE, "r") as f:
            content = f.read().strip()
            file_metadata = json.loads(content) if content else {}
    except Exception as e:
        print(f"❌ Failed to read metadata.json: {e}")
        file_metadata = {}

    # ✅ **确保 `file_id` 存在**
    if file_id not in file_metadata:
        print(f"⚠️ File ID {file_id} not found in metadata, creating new entry.")
        file_metadata[file_id] = {
            "file_name": file_id,
            "total_chunks": 0,  # **这必须要更新**
            "uploaded_chunks": []
        }

    # ✅ **确保 `uploaded_chunks` 是列表**
    if "uploaded_chunks" not in file_metadata[file_id]:
        file_metadata[file_id]["uploaded_chunks"] = []

    # ✅ **避免重复添加 chunkIndex**
    if chunk_index not in file_metadata[file_id]["uploaded_chunks"]:
        file_metadata[file_id]["uploaded_chunks"].append(chunk_index)

    # ✅ **更新 `total_chunks`**
    total_chunks = int(request.form.get("totalChunks", 0))
    if total_chunks > 0:
        file_metadata[file_id]["total_chunks"] = total_chunks
    print(f"total_chunks: {total_chunks}")

    # ✅ **写回 metadata.json**
    try:
        with open(METADATA_FILE, "w") as f:
            json.dump(file_metadata, f, indent=4)
        print(f"✅ metadata.json updated successfully for {file_id}")
    except Exception as e:
        print(f"❌ Failed to write metadata.json: {e}")

    return jsonify({"message": f"Chunk {chunk_index} uploaded"})


### **Step 3: 合并分块**
# @app.route("/upload/complete", methods=["POST"])
# def complete_upload():
#     file_id = request.json.get("fileId")

#     if file_id not in file_metadata:
#         return jsonify({"error": "File ID not found"}), 400

#     metadata = file_metadata[file_id]
#     file_name = metadata["file_name"]
#     total_chunks = metadata["total_chunks"]
#     uploaded_chunks = metadata["uploaded_chunks"]

#     print(f"📌 Checking file completion: {file_id}")
#     print(f"✅ Expected total chunks: {total_chunks}")
#     print(f"✅ Uploaded chunks: {uploaded_chunks}")

#     if len(uploaded_chunks) != total_chunks:
#         missing_chunks = set(range(total_chunks)) - set(uploaded_chunks)
#         print(f"❌ Missing chunks: {missing_chunks}")  # 🔥 这里打印缺失的分块
#         return jsonify({"error": "Missing some chunks", "missing_chunks": list(missing_chunks)}), 400

#     # if len(uploaded_chunks) != total_chunks:
#     #     return jsonify({"error": "Missing some chunks"}), 400

#     final_path = os.path.join(UPLOAD_FOLDER, file_name)

#     with open(final_path, "wb") as final_file:
#         for i in range(total_chunks):
#             chunk_path = os.path.join(CHUNK_FOLDER, f"{file_id}_chunk_{i}")
#             with open(chunk_path, "rb") as chunk_file:
#                 final_file.write(chunk_file.read())
#             os.remove(chunk_path)  # 删除分块

#     del file_metadata[file_id]  # 清理 metadata

#     return jsonify({"message": "File upload complete", "fileName": file_name})

@app.route("/upload/complete", methods=["POST"])
def complete_upload():
    print("nmd")
    file_id = request.json.get("fileId")

    print(f"\n📌 Checking file completion: {file_id}")

    # ✅ 确保 metadata.json 存在
    if not os.path.exists(METADATA_FILE):
        print("❌ metadata.json not found!")
        return jsonify({"error": "metadata.json missing"}), 500

    # ✅ 重新读取 metadata.json，确保数据完整
    try:
        with open(METADATA_FILE, "r") as f:
            content = f.read().strip()
            file_metadata = json.loads(content) if content else {}
    except Exception as e:
        print(f"❌ Failed to read metadata.json: {e}")
        return jsonify({"error": "Failed to read metadata.json"}), 500

    # ✅ 确保 `file_id` 存在
    if file_id not in file_metadata:
        print(f"❌ File ID {file_id} not found in metadata.json")
        return jsonify({"error": "File ID not found"}), 400

    metadata = file_metadata[file_id]
    file_name = metadata["file_name"]
    total_chunks = metadata["total_chunks"]
    uploaded_chunks = metadata.get("uploaded_chunks", [])

    print(f"✅ Expected total chunks: {total_chunks}")
    print(f"✅ Uploaded chunks from metadata: {uploaded_chunks}")

    # ✅ 确保 `uploaded_chunks` 是 **列表**
    if not isinstance(uploaded_chunks, list):
        print(f"❌ uploaded_chunks has invalid type: {type(uploaded_chunks)}")
        return jsonify({"error": "Invalid uploaded_chunks format"}), 500

    # ✅ 确保所有块都已上传
    missing_chunks = set(range(total_chunks)) - set(uploaded_chunks)
    if missing_chunks:
        print(f"❌ Missing chunks: {missing_chunks}")
        return jsonify({"error": "Missing some chunks", "missing_chunks": list(missing_chunks)}), 400

    # ✅ 确保 chunks 真的存在
    for i in range(total_chunks):
        chunk_path = os.path.join(CHUNK_FOLDER, f"{file_id}_chunk_{i}")
        if not os.path.exists(chunk_path):
            print(f"❌ Missing chunk file: {chunk_path}")
            return jsonify({"error": "Missing chunk file", "chunk": i}), 500

    # ✅ **合并文件**
    final_path = os.path.join(UPLOAD_FOLDER, file_name)
    try:
        with open(final_path, "wb") as final_file:
            for i in range(total_chunks):
                chunk_path = os.path.join(CHUNK_FOLDER, f"{file_id}_chunk_{i}")
                with open(chunk_path, "rb") as chunk_file:
                    final_file.write(chunk_file.read())
                os.remove(chunk_path)  # ✅ **删除分块**
    except Exception as e:
        print(f"❌ Error merging file: {e}")
        return jsonify({"error": "File merge failed"}), 500

    print(f"✅ File {file_name} successfully merged and saved to {final_path}")

    # ✅ **删除 metadata 记录**
    del file_metadata[file_id]
    try:
        with open(METADATA_FILE, "w") as f:
            json.dump(file_metadata, f, indent=4)
        print(f"✅ metadata.json cleaned up for {file_id}")
    except Exception as e:
        print(f"❌ Failed to update metadata.json: {e}")

    return jsonify({"message": "File upload complete", "fileName": file_name})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7001)
