from flask import Flask, request, jsonify
import random
import string
import time

app = Flask(__name__)

store = {}  # code -> (data, timestamp)
EXPIRY = 300  # seconds


def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@app.route("/api/send", methods=["POST"])
def send():
    data = request.json.get("data")

    if not data:
        return jsonify({"error": "No data provided"}), 400

    code = generate_code()
    store[code] = (data, time.time())

    return jsonify({
        "status": "success",
        "code": code
    })


@app.route("/api/get/<code>", methods=["GET"])
def get(code):
    if code not in store:
        return jsonify({"error": "Invalid code"}), 404

    data, timestamp = store[code]

    # Expiry check
    if time.time() - timestamp > EXPIRY:
        del store[code]
        return jsonify({"error": "Code expired"}), 410

    return jsonify({
        "status": "success",
        "data": data
    })


@app.route("/")
def home():
    return "Clipboard API running"
    

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
