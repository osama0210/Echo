from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

# === Setup ===
load_dotenv()
app = Flask(__name__)
CORS(app)

# === Prompt voor de AI ===
SYSTEM_PROMPT = (
    "You are Echo, a friendly chatbot that helps students deal with school stress. "
    "Always respond in a calm, warm and motivating way. Give short and practical tips, "
    "and suggest small exercises like breathing or focus tricks when helpful."
)


# === Homepage route ===
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# === Chat route via OpenRouter (DeepSeek model) ===
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(force=True)
    user_msg = data.get("message", "")

    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    try:
        KEY = os.getenv("OPENROUTER_API_KEY").strip()
        if not KEY:
            return jsonify({"reply": "No OpenRouter key found."}), 500
        print("KEY:", KEY)
        headers = {
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",  # hou precies zo
            "X-Title": "echo-app"
        }
        print("KEY LADE SUCCESVOL?", bool(KEY))
        print("KEY START MET:", KEY[:8] if KEY else "GEEN KEY")

        payload = {
            "model": "deepseek/deepseek-chat-v3-0324:free",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ]
        }

        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        if r.status_code != 200:
            print("OpenRouter HTTP", r.status_code, r.text)  # debug
            return jsonify({"reply": "AI error: " + str(r.status_code)}), 500

        reply = r.json()["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception as e:
        print("OpenRouter exception:", e)
        return jsonify({"reply": "Sorry, AI is not responding right now."}), 500

    print("----  VERZONDEN HEADERS ----")
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )

    print("----  REQUEST HEADERS ----")
    print(r.request.headers)  # <- hier MOET je Authorization zien
    print("----  STATUS / BODY ----")
    print(r.status_code, r.text[:200])
# === Start server ===
if __name__ == "__main__":
    app.run(debug=True)