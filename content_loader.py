import json
import os

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content")

# The homeschool plan is the source of truth for what she is actually reading. This app
# keeps its own units.json for the teaching frame -- essential questions, skills -- but
# the texts come from there, so changing a text in one place changes it everywhere.
# Absent the file (a laptop, a fresh clone) the bundled example texts stand in.
CURRICULUM = os.environ.get("HOMESCHOOL_CURRICULUM",
                            "/home/ec2-user/homeschool/site/curriculum.json")


def _plan():
    try:
        with open(CURRICULUM, encoding="utf8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _overlay(subject_id, data):
    """Replace each unit's texts with what the plan says she is reading for it.

    Matched by position: both this app and the plan follow the CED's unit order, so
    unit n here is unit n there. A subject the plan does not cover is left alone.
    """
    plan = _plan().get(subject_id)
    if not plan:
        return data
    for i, unit in enumerate(data.get("units", [])):
        if i < len(plan["units"]):
            src = plan["units"][i]
            if src.get("texts"):
                unit["texts"] = src["texts"]
            unit["plan_window"] = [src.get("start"), src.get("end")]
    data["source_note"] = data.get("source_note", "") + (
        "  Texts for each unit are taken from the homeschool plan rather than fixed here.")
    return data


def list_subjects():
    subjects = []
    for name in sorted(os.listdir(CONTENT_DIR)):
        units_path = os.path.join(CONTENT_DIR, name, "units.json")
        if os.path.isfile(units_path):
            with open(units_path) as f:
                data = json.load(f)
            subjects.append({"id": name, "title": data["subject"]})
    return subjects


def load_subject(subject_id):
    units_path = os.path.join(CONTENT_DIR, subject_id, "units.json")
    with open(units_path) as f:
        return _overlay(subject_id, json.load(f))


def get_unit(subject_id, unit_id):
    data = load_subject(subject_id)
    for unit in data["units"]:
        if unit["id"] == unit_id:
            return unit
    return None
