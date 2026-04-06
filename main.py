from flask import Flask, request, jsonify, send_file
import random, string, time, os

app = Flask(__name__)

store = {}
EXPIRY = 300  # 5 min
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@app.route("/api/send", methods=["POST"])
def send():
    # TEXT DATA
    if request.json:
        data = request.json.get("data")

        if not data:
            return jsonify({"error": "No data"}), 400

        code = generate_code()
        store[code] = ("text", data, time.time())

        return jsonify({"code": code})

    # FILE DATA
    if "file" in request.files:
        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No file"}), 400

        code = generate_code()
        filepath = os.path.join(UPLOAD_FOLDER, code + "_" + file.filename)
        file.save(filepath)

        store[code] = ("file", filepath, time.time())

        return jsonify({"code": code})

    return jsonify({"error": "Invalid request"}), 400


@app.route("/api/get/<code>", methods=["GET"])
def get(code):
    if code not in store:
        return jsonify({"error": "Invalid code"}), 404

    dtype, value, t = store[code]

    if time.time() - t > EXPIRY:
        del store[code]
        return jsonify({"error": "Expired"}), 410

    if dtype == "text":
        return jsonify({"type": "text", "data": value})

    if dtype == "file":
        return send_file(value, as_attachment=True)

    return jsonify({"error": "Unknown type"}), 500


@app.route("/")
def home():
    return "API is running (text + image support)"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
