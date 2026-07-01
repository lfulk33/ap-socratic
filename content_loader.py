import json
import os

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content")


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
        return json.load(f)


def get_unit(subject_id, unit_id):
    data = load_subject(subject_id)
    for unit in data["units"]:
        if unit["id"] == unit_id:
            return unit
    return None
