from flask import Flask, request, jsonify
import random, string, time, os

app = Flask(__name__)

store = {}
EXPIRY = 300  # 5 min


def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@app.route("/api/send", methods=["POST"])
def send():
    data = request.json.get("data")

    if not data:
        return jsonify({"error": "No data"}), 400

    code = generate_code()
    store[code] = (data, time.time())

    return jsonify({
        "code": code
    })


@app.route("/api/get/<code>", methods=["GET"])
def get(code):
    if code not in store:
        return jsonify({"error": "Invalid code"}), 404

    data, t = store[code]

    if time.time() - t > EXPIRY:
        del store[code]
        return jsonify({"error": "Expired"}), 410

    return jsonify({
        "data": data
    })


@app.route("/")
def home():
    return "API is running"
    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
