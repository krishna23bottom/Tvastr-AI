"""Flask backend for TVASTR AI.  Run:  python app.py   then open http://127.0.0.1:5000"""
import secrets

from flask import Flask, jsonify, render_template, request, session

import prompts
from engine import TvastrEngine
from llm_client import active_provider

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
engine = TvastrEngine()
SESSIONS = {}  # sid -> {"history": [...], "context": {...}}


def _state():
    sid = session.get("sid")
    if sid not in SESSIONS:
        sid = secrets.token_hex(8)
        session["sid"] = sid
        SESSIONS[sid] = {"history": [], "context": {}}
    return SESSIONS[sid]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("message", ""), str):
        return jsonify(error="Invalid request. Send JSON like {\"message\": \"...\"}."), 400
    state = _state()
    try:
        result = engine.respond(data["message"], state["history"], state["context"])
    except Exception:
        return jsonify(error="Something went wrong on our side. Please try again."), 500
    if result["source"] not in ("validation",) and result["intent"] is not None or result["source"] == "rule":
        if data["message"].strip():
            state["history"] += [{"role": "user", "content": data["message"].strip()},
                                 {"role": "assistant", "content": result["reply"]}]
            state["history"] = state["history"][-24:]
    state["context"] = result["context"]
    result["intent_label"] = (result["intent"] or "").replace("_", " ")
    return jsonify(result)


@app.route("/api/reset", methods=["POST"])
def reset():
    state = _state()
    state["history"].clear()
    state["context"] = {}
    return jsonify(ok=True)


@app.route("/api/health")
def health():
    return jsonify(status="ok", provider=active_provider(), prompt_version=prompts.PROMPT_VERSION)


if __name__ == "__main__":
    print(f"TVASTR AI running | provider={active_provider()} | prompt={prompts.PROMPT_VERSION}")
    app.run(debug=False, port=5000)
