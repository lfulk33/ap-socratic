from flask import Flask, render_template, request, jsonify

import db
from content_loader import list_subjects, load_subject, get_unit
from llm_client import send_message, start_conversation

app = Flask(__name__)
db.init_db()


@app.route("/")
def index():
    return render_template("index.html", subjects=list_subjects())


@app.route("/subject/<subject_id>")
def subject(subject_id):
    data = load_subject(subject_id)
    return render_template("subject.html", subject_id=subject_id, data=data)


@app.route("/subject/<subject_id>/unit/<unit_id>")
def start_unit(subject_id, unit_id):
    unit = get_unit(subject_id, unit_id)
    if unit is None:
        return "Unit not found", 404

    existing = db.get_conversation(subject_id, unit_id)
    if existing:
        messages = [m for m in existing if m["visible"]]
    else:
        opening_reply, seed_history = start_conversation(unit)
        for i, m in enumerate(seed_history):
            db.append_message(subject_id, unit_id, m["role"], m["content"], visible=(i > 0))
        messages = [{"role": "assistant", "content": opening_reply}]

    return render_template(
        "chat.html", unit=unit, subject_id=subject_id, messages=messages
    )


@app.route("/subject/<subject_id>/unit/<unit_id>/chat", methods=["POST"])
def chat(subject_id, unit_id):
    unit = get_unit(subject_id, unit_id)
    if unit is None:
        return jsonify({"error": "Unit not found"}), 404

    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    history = [{"role": m["role"], "content": m["content"]} for m in db.get_conversation(subject_id, unit_id)]
    reply = send_message(unit, history, user_message)

    db.append_message(subject_id, unit_id, "user", user_message)
    db.append_message(subject_id, unit_id, "assistant", reply)

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
