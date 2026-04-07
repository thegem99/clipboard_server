from flask import Flask, request, jsonify, send_file, Response
import random, string, time
import os

app = Flask(__name__)

store = {}
EXPIRY = 300  # 5 minutes
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@app.route("/api/send", methods=["POST"])
def send():
    # ✅ Handle file upload
    if "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file"}), 400

        code = generate_code()

        filename = file.filename
        content_type = file.content_type or "application/octet-stream"

        filepath = os.path.join(UPLOAD_FOLDER, code + "_" + filename)
        file.save(filepath)

        # ✅ Store metadata
        store[code] = ("file", filepath, filename, content_type, time.time())

        return jsonify({"code": code})

    # ✅ Handle text
    if request.is_json:
        data = request.json.get("data")
        if not data:
            return jsonify({"error": "No data"}), 400

        code = generate_code()
        store[code] = ("text", data, time.time())
        return jsonify({"code": code})

    return jsonify({"error": "Invalid request"}), 400


@app.route("/api/get/<code>", methods=["GET"])
def get(code):
    if code not in store:
        return jsonify({"error": "Invalid code"}), 404

    entry = store[code]

    # ✅ Expiry check
    if time.time() - entry[-1] > EXPIRY:
        del store[code]
        return jsonify({"error": "Expired"}), 410

    if entry[0] == "text":
        return jsonify({"type": "text", "data": entry[1]})

    if entry[0] == "file":
        _, filepath, filename, content_type, _ = entry

        return Response(
            open(filepath, "rb"),
            content_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    return jsonify({"error": "Unknown type"}), 500


@app.route("/")
def home():
    return "API supports ALL file types + text"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
