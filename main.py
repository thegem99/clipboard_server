from flask import Flask, request, jsonify, render_template_string
import random, string, time, os

app = Flask(__name__)

store = {}
EXPIRY = 300


def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# 🌐 WEB UI
@app.route("/")
def index():
    return render_template_string("""
    <h2>Online Clipboard</h2>

    <h3>Send</h3>
    <textarea id="data"></textarea><br>
    <button onclick="send()">Send</button>
    <p id="code"></p>

    <h3>Receive</h3>
    <input id="codeInput" placeholder="Enter code">
    <button onclick="get()">Get</button>
    <pre id="result"></pre>

    <script>
    async function send() {
        let data = document.getElementById("data").value;
        let res = await fetch('/api/send', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({data})
        });
        let json = await res.json();
        document.getElementById("code").innerText = "Code: " + json.code;
    }

    async function get() {
        let code = document.getElementById("codeInput").value;
        let res = await fetch('/api/get/' + code);
        let text = await res.text();
        document.getElementById("result").innerText = text;
    }
    </script>
    """)


@app.route("/api/send", methods=["POST"])
def send():
    data = request.json.get("data")
    code = generate_code()
    store[code] = (data, time.time())
    return jsonify({"code": code})


@app.route("/api/get/<code>")
def get(code):
    if code not in store:
        return "Invalid code", 404

    data, t = store[code]
    if time.time() - t > EXPIRY:
        del store[code]
        return "Expired", 410

    return data


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
