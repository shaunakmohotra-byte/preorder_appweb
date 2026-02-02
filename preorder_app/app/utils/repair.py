import json
import os

def repair_json(path, expected_type):
    """
    Repairs a JSON file if it is corrupted, unreadable, empty,
    or not matching the expected type (list or dict).

    expected_type = list  → e.g., orders.json
    expected_type = dict  → e.g., users.json
    """

    # If file missing → create fresh
    if not os.path.exists(path):
        print(f"[REPAIR] Missing file recreated: {path}")
        _write_json(path, expected_type())
        return expected_type()

    try:
        with open(path, "r") as f:
            data = json.load(f)

        # Type mismatch
        if not isinstance(data, expected_type):
            print(f"[REPAIR] Type mismatch in {path}. Resetting.")
            _write_json(path, expected_type())
            return expected_type()

        return data

    except Exception as e:
        print(f"[REPAIR] Corrupted JSON in {path}: {e}")
        _write_json(path, expected_type())
        return expected_type()


def _write_json(path, data):
    """Safely writes JSON (used by repair_json)."""
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
    except:
        print(f"[REPAIR ERROR] Could not write to {path}")
